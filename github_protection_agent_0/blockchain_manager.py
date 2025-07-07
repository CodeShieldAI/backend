"""
Blockchain Manager Module
Handles Filecoin Calibration testnet contract interactions
"""
import os
import json
from typing import Dict, List, Optional, Tuple
from web3 import Web3
from eth_account import Account
import requests

from .utils import setup_logging

logger = setup_logging(__name__)


class BlockchainManager:
    """Manages blockchain interactions with Filecoin contracts"""
    
    def __init__(self, config: Dict):
        self.config = config
        
        # Filecoin Calibration testnet RPC
        self.rpc_url = config.get('FILECOIN_RPC_URL', 'https://rpc.ankr.com/filecoin_testnet')
        self.chain_id = 314159  # Filecoin Calibration testnet
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Private key for transactions
        self.private_key = config.get('WALLET_PRIVATE_KEY')
        if self.private_key:
            self.account = Account.from_key(self.private_key)
            self.address = self.account.address
        else:
            logger.warning("⚠️ No private key configured - read-only mode")
            self.account = None
            self.address = None
        
        # Contract addresses
        self.contracts = {
            'DealClient': '0x592eC554ec3Af631d76981a680f699F9618B5687',
            'LinkRegistry': '0x5fa19b4a48C20202055c8a6fdf16688633617D50',
            'LinkRegistryWithDeals': '0x25bc04a49997e25B7482eEcbeB2Ec67740AEd5a6',
            'InfringementBounty': '0xA2cD4CC41b8DCE00D002Aa4B29050f2d53705400',
            'GitHubRepoProtection': config.get('GITHUB_PROTECTION_CONTRACT')  # Your new contract
        }
        
        # Load ABIs
        self.abis = self._load_abis()
        
        # Initialize contract instances
        self.link_registry = self._get_contract('LinkRegistry')
        self.link_registry_deals = self._get_contract('LinkRegistryWithDeals')
        self.infringement_bounty = self._get_contract('InfringementBounty')
        self.deal_client = self._get_contract('DealClient')
        
        if self.contracts['GitHubRepoProtection']:
            self.github_protection = self._get_contract('GitHubRepoProtection')
    
    def _load_abis(self) -> Dict:
        """Load contract ABIs"""
        # Simplified ABIs - you should load full ABIs from files
        return {
            'LinkRegistry': [
                {
                    "name": "addLink",
                    "type": "function",
                    "inputs": [
                        {"name": "url", "type": "string"},
                        {"name": "licenseCID", "type": "string"}
                    ],
                    "outputs": []
                },
                {
                    "name": "fileDMCA",
                    "type": "function",
                    "inputs": [
                        {"name": "url", "type": "string"},
                        {"name": "dmcaCID", "type": "string"}
                    ],
                    "outputs": []
                },
                {
                    "name": "linkRecords",
                    "type": "function",
                    "inputs": [{"name": "", "type": "string"}],
                    "outputs": [
                        {"name": "url", "type": "string"},
                        {"name": "licenseCID", "type": "string"},
                        {"name": "dmcaCID", "type": "string"},
                        {"name": "status", "type": "uint8"},
                        {"name": "timestamp", "type": "uint256"},
                        {"name": "exists", "type": "bool"}
                    ],
                    "stateMutability": "view"
                }
            ],
            'LinkRegistryWithDeals': [
                {
                    "name": "addLinkWithDeal",
                    "type": "function",
                    "inputs": [
                        {"name": "url", "type": "string"},
                        {"name": "licenseCID", "type": "string"},
                        {"name": "size", "type": "uint64"}
                    ],
                    "outputs": []
                },
                {
                    "name": "fileDMCAWithDeal",
                    "type": "function",
                    "inputs": [
                        {"name": "url", "type": "string"},
                        {"name": "dmcaCID", "type": "string"},
                        {"name": "size", "type": "uint64"}
                    ],
                    "outputs": []
                }
            ],
            'InfringementBounty': [
                {
                    "name": "reportInfringement",
                    "type": "function",
                    "inputs": [
                        {"name": "url", "type": "string"},
                        {"name": "licenseCID", "type": "string"},
                        {"name": "dmcaCID", "type": "string"}
                    ],
                    "outputs": []
                },
                {
                    "name": "rewards",
                    "type": "function",
                    "inputs": [{"name": "", "type": "address"}],
                    "outputs": [{"name": "", "type": "uint256"}],
                    "stateMutability": "view"
                },
                {
                    "name": "withdraw",
                    "type": "function",
                    "inputs": [],
                    "outputs": []
                }
            ],
            'GitHubRepoProtection': [
                {
                    "name": "processSubmission",
                    "type": "function",
                    "inputs": [
                        {"name": "submissionType", "type": "uint8"},
                        {"name": "repoId", "type": "uint256"},
                        {"name": "githubUrl", "type": "string"},
                        {"name": "repoHash", "type": "string"},
                        {"name": "codeFingerprint", "type": "string"},
                        {"name": "keyFeatures", "type": "string[]"},
                        {"name": "licenseType", "type": "string"},
                        {"name": "ipfsMetadata", "type": "string"},
                        {"name": "evidenceHash", "type": "string"},
                        {"name": "similarityScore", "type": "uint256"}
                    ],
                    "outputs": []
                },
                {
                    "name": "getRepository",
                    "type": "function",
                    "inputs": [{"name": "repoId", "type": "uint256"}],
                    "outputs": [
                        {"name": "id", "type": "uint256"},
                        {"name": "owner", "type": "address"},
                        {"name": "githubUrl", "type": "string"},
                        {"name": "repoHash", "type": "string"},
                        {"name": "codeFingerprint", "type": "string"},
                        {"name": "keyFeatures", "type": "string[]"},
                        {"name": "licenseType", "type": "string"},
                        {"name": "registeredAt", "type": "uint256"},
                        {"name": "isActive", "type": "bool"},
                        {"name": "ipfsMetadata", "type": "string"}
                    ],
                    "stateMutability": "view"
                }
            ]
        }
    
    def _get_contract(self, name: str):
        """Get contract instance"""
        if name not in self.contracts or not self.contracts[name]:
            return None
        
        address = self.contracts[name]
        abi = self.abis.get(name, [])
        
        return self.w3.eth.contract(
            address=Web3.to_checksum_address(address),
            abi=abi
        )
    
    def register_repository_onchain(self, repo_data: Dict, ipfs_metadata: str) -> Dict:
        """Register repository on GitHubRepoProtection contract"""
        try:
            if not self.github_protection:
                # Fallback to LinkRegistry
                return self.register_link(repo_data['github_url'], repo_data['license_ipfs_hash'])
            
            if not self.account:
                return {'success': False, 'error': 'No wallet configured'}
            
            # Prepare transaction
            submission_type = 0  # Register
            key_features = repo_data['key_features'].split('\n')[:5]  # Max 5 features
            
            tx = self.github_protection.functions.processSubmission(
                submission_type,
                0,  # repoId (not used for registration)
                repo_data['github_url'],
                repo_data['repo_hash'],
                repo_data['fingerprint'],
                key_features,
                repo_data['license_type'],
                ipfs_metadata,
                "",  # evidenceHash (not used)
                0    # similarityScore (not used)
            ).build_transaction({
                'from': self.address,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'gas': 500000,
                'gasPrice': self.w3.eth.gas_price,
                'chainId': self.chain_id
            })
            
            # Sign and send transaction
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            logger.info(f"✅ Repository registered on-chain: {tx_hash.hex()}")
            
            return {
                'success': True,
                'tx_hash': tx_hash.hex(),
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed']
            }
            
        except Exception as e:
            logger.error(f"Blockchain registration failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def register_link(self, url: str, license_cid: str, use_deals: bool = False) -> Dict:
        """Register link with license CID on LinkRegistry"""
        try:
            if not self.account:
                return {'success': False, 'error': 'No wallet configured'}
            
            if use_deals and self.link_registry_deals:
                # Get file size from IPFS (mock for now)
                file_size = 1024 * 1024  # 1MB default
                
                tx = self.link_registry_deals.functions.addLinkWithDeal(
                    url,
                    license_cid,
                    file_size
                ).build_transaction({
                    'from': self.address,
                    'nonce': self.w3.eth.get_transaction_count(self.address),
                    'gas': 300000,
                    'gasPrice': self.w3.eth.gas_price,
                    'chainId': self.chain_id
                })
            else:
                tx = self.link_registry.functions.addLink(
                    url,
                    license_cid
                ).build_transaction({
                    'from': self.address,
                    'nonce': self.w3.eth.get_transaction_count(self.address),
                    'gas': 200000,
                    'gasPrice': self.w3.eth.gas_price,
                    'chainId': self.chain_id
                })
            
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            logger.info(f"✅ Link registered: {tx_hash.hex()}")
            
            return {
                'success': True,
                'tx_hash': tx_hash.hex(),
                'block_number': receipt['blockNumber']
            }
            
        except Exception as e:
            logger.error(f"Link registration failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def file_dmca(self, url: str, dmca_cid: str, use_deals: bool = False) -> Dict:
        """File DMCA for a link"""
        try:
            if not self.account:
                return {'success': False, 'error': 'No wallet configured'}
            
            if use_deals and self.link_registry_deals:
                file_size = 512 * 1024  # 512KB default
                
                tx = self.link_registry_deals.functions.fileDMCAWithDeal(
                    url,
                    dmca_cid,
                    file_size
                ).build_transaction({
                    'from': self.address,
                    'nonce': self.w3.eth.get_transaction_count(self.address),
                    'gas': 300000,
                    'gasPrice': self.w3.eth.gas_price,
                    'chainId': self.chain_id
                })
            else:
                tx = self.link_registry.functions.fileDMCA(
                    url,
                    dmca_cid
                ).build_transaction({
                    'from': self.address,
                    'nonce': self.w3.eth.get_transaction_count(self.address),
                    'gas': 200000,
                    'gasPrice': self.w3.eth.gas_price,
                    'chainId': self.chain_id
                })
            
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            logger.info(f"✅ DMCA filed: {tx_hash.hex()}")
            
            return {
                'success': True,
                'tx_hash': tx_hash.hex(),
                'block_number': receipt['blockNumber']
            }
            
        except Exception as e:
            logger.error(f"DMCA filing failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def report_infringement_for_bounty(self, url: str, license_cid: str, dmca_cid: str) -> Dict:
        """Report infringement through bounty contract"""
        try:
            if not self.account:
                return {'success': False, 'error': 'No wallet configured'}
            
            tx = self.infringement_bounty.functions.reportInfringement(
                url,
                license_cid,
                dmca_cid
            ).build_transaction({
                'from': self.address,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'gas': 400000,
                'gasPrice': self.w3.eth.gas_price,
                'chainId': self.chain_id
            })
            
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            logger.info(f"✅ Infringement reported for bounty: {tx_hash.hex()}")
            
            return {
                'success': True,
                'tx_hash': tx_hash.hex(),
                'block_number': receipt['blockNumber'],
                'bounty_eligible': True
            }
            
        except Exception as e:
            logger.error(f"Bounty reporting failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def check_link_status(self, url: str) -> Dict:
        """Check if a link is already registered"""
        try:
            result = self.link_registry.functions.linkRecords(url).call()
            
            return {
                'exists': result[5],  # exists field
                'url': result[0],
                'license_cid': result[1],
                'dmca_cid': result[2],
                'status': result[3],
                'timestamp': result[4]
            }
            
        except Exception as e:
            logger.error(f"Link status check failed: {e}")
            return {'exists': False, 'error': str(e)}
    
    def get_bounty_balance(self, address: str = None) -> int:
        """Get bounty balance for an address"""
        try:
            if not address:
                address = self.address
            
            if not address:
                return 0
            
            balance = self.infringement_bounty.functions.rewards(address).call()
            return balance
            
        except Exception as e:
            logger.error(f"Bounty balance check failed: {e}")
            return 0
    
    def withdraw_bounty(self) -> Dict:
        """Withdraw accumulated bounty rewards"""
        try:
            if not self.account:
                return {'success': False, 'error': 'No wallet configured'}
            
            # Check balance first
            balance = self.get_bounty_balance()
            if balance == 0:
                return {'success': False, 'error': 'No bounty to withdraw'}
            
            tx = self.infringement_bounty.functions.withdraw().build_transaction({
                'from': self.address,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price,
                'chainId': self.chain_id
            })
            
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            logger.info(f"✅ Bounty withdrawn: {Web3.from_wei(balance, 'ether')} FIL")
            
            return {
                'success': True,
                'tx_hash': tx_hash.hex(),
                'amount': Web3.from_wei(balance, 'ether')
            }
            
        except Exception as e:
            logger.error(f"Bounty withdrawal failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_filecoin_deal(self, cid: str, size: int, label: str) -> Dict:
        """Create a Filecoin storage deal"""
        try:
            if not self.account:
                return {'success': False, 'error': 'No wallet configured'}
            
            # Convert CID string to bytes
            cid_bytes = Web3.to_bytes(text=cid)
            
            # Prepare deal parameters
            current_epoch = int(self.w3.eth.block_number)
            
            deal_request = {
                'piece_cid': cid_bytes,
                'piece_size': size,
                'verified_deal': False,
                'label': label,
                'start_epoch': current_epoch + 520,  # ~4 hours from now
                'end_epoch': current_epoch + 518400,  # ~180 days
                'storage_price_per_epoch': 0,
                'provider_collateral': 0,
                'client_collateral': 0
            }
            
            tx = self.deal_client.functions.makeDealProposal(
                deal_request
            ).build_transaction({
                'from': self.address,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'gas': 500000,
                'gasPrice': self.w3.eth.gas_price,
                'chainId': self.chain_id
            })
            
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            logger.info(f"✅ Filecoin deal created: {tx_hash.hex()}")
            
            return {
                'success': True,
                'tx_hash': tx_hash.hex(),
                'block_number': receipt['blockNumber']
            }
            
        except Exception as e:
            logger.error(f"Deal creation failed: {e}")
            return {'success': False, 'error': str(e)}