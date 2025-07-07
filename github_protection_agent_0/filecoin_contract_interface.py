"""
Filecoin Contract Interface Module
Handles interactions with deployed smart contracts on Filecoin Calibration testnet
"""
import os
import json
import hashlib
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from web3 import Web3
from web3.exceptions import ContractLogicError
from dotenv import load_dotenv
load_dotenv()

from .utils import setup_logging

logger = setup_logging(__name__)


class FilecoinContractInterface:
    """Interface for interacting with Filecoin smart contracts"""
    
    def __init__(self, config: Dict):
        self.config = config
        
        # Filecoin Calibration Testnet Configuration
        self.rpc_url = config.get('FILECOIN_RPC_URL', 'https://rpc.ankr.com/filecoin_testnet')
        self.chain_id = 314159  # Filecoin Calibration testnet
        self.private_key = config.get('PRIVATE_KEY')
        
        # Contract Addresses
        self.contracts = {
            'github_protection': '0x19054030669efBFc413bA3729b63eCfD3Bdc22B5',
            'deal_client': '0x592eC554ec3Af631d76981a680f699F9618B5687',
            'link_registry': '0x5fa19b4a48C20202055c8a6fdf16688633617D50',
            'link_registry_deals': '0x25bc04a49997e25B7482eEcbeB2Ec67740AEd5a6',
            'infringement_bounty': '0xA2cD4CC41b8DCE00D002Aa4B29050f2d53705400'
        }
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        if not self.w3.is_connected():
            raise ConnectionError("Failed to connect to Filecoin network")
        
        # Load account
        if self.private_key:
            self.account = self.w3.eth.account.from_key(self.private_key)
            logger.info(f"🔗 Connected to Filecoin Calibration testnet with account: {self.account.address}")
        else:
            logger.warning("⚠️ No private key provided - read-only mode")
            self.account = None
        
        # Load contract ABIs and create contract instances
        self._load_contracts()
    
    def _load_contracts(self):
        """Load contract ABIs and create instances"""
        
        # GitHub Protection Contract ABI (simplified)
        github_protection_abi = [
            {
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
                "name": "processSubmission",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "githubUrl", "type": "string"},
                    {"name": "repoHash", "type": "string"},
                    {"name": "codeFingerprint", "type": "string"},
                    {"name": "keyFeatures", "type": "string[]"},
                    {"name": "licenseType", "type": "string"},
                    {"name": "ipfsMetadata", "type": "string"}
                ],
                "name": "registerRepository",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "originalRepoId", "type": "uint256"},
                    {"name": "violatingUrl", "type": "string"},
                    {"name": "evidenceHash", "type": "string"},
                    {"name": "similarityScore", "type": "uint256"}
                ],
                "name": "reportViolation",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "repoId", "type": "uint256"}],
                "name": "getRepository",
                "outputs": [{
                    "components": [
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
                    "name": "",
                    "type": "tuple"
                }],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "getTotalRepositories",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        # Link Registry ABI (simplified)
        link_registry_abi = [
            {
                "inputs": [
                    {"name": "url", "type": "string"},
                    {"name": "licenseCID", "type": "string"}
                ],
                "name": "addLink",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "url", "type": "string"},
                    {"name": "dmcaCID", "type": "string"}
                ],
                "name": "fileDMCA",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "url", "type": "string"}],
                "name": "linkRecords",
                "outputs": [
                    {"name": "url", "type": "string"},
                    {"name": "licenseCID", "type": "string"},
                    {"name": "dmcaCID", "type": "string"},
                    {"name": "status", "type": "uint8"},
                    {"name": "timestamp", "type": "uint256"},
                    {"name": "exists", "type": "bool"}
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        # Create contract instances
        self.github_contract = self.w3.eth.contract(
            address=self.contracts['github_protection'],
            abi=github_protection_abi
        )
        
        self.link_registry_contract = self.w3.eth.contract(
            address=self.contracts['link_registry'],
            abi=link_registry_abi
        )
        
        logger.info("✅ Contract instances loaded successfully")
    
    def register_repository_on_chain(self, repo_data: Dict) -> Dict:
        """Register repository on the GitHub Protection contract"""
        if not self.account:
            return {'success': False, 'error': 'No account configured for transactions'}
        
        try:
            # Prepare transaction data
            key_features = repo_data.get('key_features', '').split('\n')[:5]  # Max 5 features
            
            # Build transaction
            function_call = self.github_contract.functions.processSubmission(
                0,  # SubmissionType.Register
                0,  # repoId (not used for registration)
                repo_data['github_url'],
                repo_data['repo_hash'],
                repo_data['fingerprint'],
                key_features,
                repo_data.get('license_type', 'MIT'),
                repo_data.get('ipfs_metadata', ''),
                '',  # evidenceHash (not used for registration)
                0   # similarityScore (not used for registration)
            )
            
            # Estimate gas
            gas_estimate = function_call.estimate_gas({'from': self.account.address})
            
            # Build transaction
            transaction = function_call.build_transaction({
                'from': self.account.address,
                'gas': gas_estimate + 50000,  # Add buffer
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'chainId': self.chain_id
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            # Wait for confirmation
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if tx_receipt.status == 1:
                logger.info(f"✅ Repository registered on chain: {tx_hash.hex()}")
                
                # Get the repo ID from logs
                repo_id = self._extract_repo_id_from_logs(tx_receipt)
                
                return {
                    'success': True,
                    'tx_hash': tx_hash.hex(),
                    'repo_id': repo_id,
                    'block_number': tx_receipt.blockNumber,
                    'gas_used': tx_receipt.gasUsed
                }
            else:
                return {'success': False, 'error': 'Transaction failed'}
                
        except Exception as e:
            logger.error(f"❌ Repository registration failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def report_violation_on_chain(self, violation_data: Dict) -> Dict:
        """Report violation on the GitHub Protection contract"""
        if not self.account:
            return {'success': False, 'error': 'No account configured for transactions'}
        
        try:
            # Convert similarity score to integer (multiply by 100 for percentage)
            similarity_score_int = int(violation_data['similarity_score'] * 100)
            
            # Build transaction
            function_call = self.github_contract.functions.processSubmission(
                1,  # SubmissionType.ReportViolation
                violation_data['original_repo_id'],
                violation_data['violating_url'],
                '',  # repoHash (not used for violations)
                '',  # codeFingerprint (not used for violations)
                [],  # keyFeatures (not used for violations)
                '',  # licenseType (not used for violations)
                '',  # ipfsMetadata (not used for violations)
                violation_data['evidence_hash'],
                similarity_score_int
            )
            
            # Estimate gas
            gas_estimate = function_call.estimate_gas({'from': self.account.address})
            
            # Build transaction
            transaction = function_call.build_transaction({
                'from': self.account.address,
                'gas': gas_estimate + 50000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'chainId': self.chain_id
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            # Wait for confirmation
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if tx_receipt.status == 1:
                logger.info(f"✅ Violation reported on chain: {tx_hash.hex()}")
                
                # Get the violation ID from logs
                violation_id = self._extract_violation_id_from_logs(tx_receipt)
                
                return {
                    'success': True,
                    'tx_hash': tx_hash.hex(),
                    'violation_id': violation_id,
                    'block_number': tx_receipt.blockNumber,
                    'gas_used': tx_receipt.gasUsed
                }
            else:
                return {'success': False, 'error': 'Transaction failed'}
                
        except Exception as e:
            logger.error(f"❌ Violation reporting failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def add_link_to_registry(self, github_url: str, license_cid: str) -> Dict:
        """Add link to the Link Registry contract"""
        if not self.account:
            return {'success': False, 'error': 'No account configured for transactions'}
        
        try:
            function_call = self.link_registry_contract.functions.addLink(github_url, license_cid)
            
            # Estimate gas
            gas_estimate = function_call.estimate_gas({'from': self.account.address})
            
            # Build transaction
            transaction = function_call.build_transaction({
                'from': self.account.address,
                'gas': gas_estimate + 30000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'chainId': self.chain_id
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            # Wait for confirmation
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if tx_receipt.status == 1:
                logger.info(f"✅ Link added to registry: {tx_hash.hex()}")
                return {
                    'success': True,
                    'tx_hash': tx_hash.hex(),
                    'block_number': tx_receipt.blockNumber,
                    'gas_used': tx_receipt.gasUsed
                }
            else:
                return {'success': False, 'error': 'Transaction failed'}
                
        except Exception as e:
            logger.error(f"❌ Link registry addition failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def file_dmca_on_chain(self, infringing_url: str, dmca_cid: str) -> Dict:
        """File DMCA notice on the Link Registry contract"""
        if not self.account:
            return {'success': False, 'error': 'No account configured for transactions'}
        
        try:
            function_call = self.link_registry_contract.functions.fileDMCA(infringing_url, dmca_cid)
            
            # Estimate gas
            gas_estimate = function_call.estimate_gas({'from': self.account.address})
            
            # Build transaction
            transaction = function_call.build_transaction({
                'from': self.account.address,
                'gas': gas_estimate + 30000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'chainId': self.chain_id
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            # Wait for confirmation
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if tx_receipt.status == 1:
                logger.info(f"✅ DMCA filed on chain: {tx_hash.hex()}")
                return {
                    'success': True,
                    'tx_hash': tx_hash.hex(),
                    'block_number': tx_receipt.blockNumber,
                    'gas_used': tx_receipt.gasUsed
                }
            else:
                return {'success': False, 'error': 'Transaction failed'}
                
        except Exception as e:
            logger.error(f"❌ DMCA filing failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_repository_from_chain(self, repo_id: int) -> Dict:
        """Get repository data from the blockchain"""
        try:
            repo_data = self.github_contract.functions.getRepository(repo_id).call()
            
            return {
                'success': True,
                'repository': {
                    'id': repo_data[0],
                    'owner': repo_data[1],
                    'github_url': repo_data[2],
                    'repo_hash': repo_data[3],
                    'code_fingerprint': repo_data[4],
                    'key_features': repo_data[5],
                    'license_type': repo_data[6],
                    'registered_at': repo_data[7],
                    'is_active': repo_data[8],
                    'ipfs_metadata': repo_data[9]
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get repository from chain: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_total_repositories(self) -> int:
        """Get total number of registered repositories"""
        try:
            return self.github_contract.functions.getTotalRepositories().call()
        except Exception as e:
            logger.error(f"❌ Failed to get total repositories: {e}")
            return 0
    
    def get_link_record(self, url: str) -> Dict:
        """Get link record from registry"""
        try:
            record = self.link_registry_contract.functions.linkRecords(url).call()
            
            return {
                'success': True,
                'record': {
                    'url': record[0],
                    'license_cid': record[1],
                    'dmca_cid': record[2],
                    'status': record[3],
                    'timestamp': record[4],
                    'exists': record[5]
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get link record: {e}")
            return {'success': False, 'error': str(e)}
    
    def _extract_repo_id_from_logs(self, tx_receipt) -> Optional[int]:
        """Extract repository ID from transaction logs"""
        try:
            # Look for RepositoryRegistered event
            for log in tx_receipt.logs:
                try:
                    decoded_log = self.github_contract.events.RepositoryRegistered().processLog(log)
                    return decoded_log.args.repoId
                except:
                    continue
            return None
        except:
            return None
    
    def _extract_violation_id_from_logs(self, tx_receipt) -> Optional[int]:
        """Extract violation ID from transaction logs"""
        try:
            # Look for ViolationReported event
            for log in tx_receipt.logs:
                try:
                    decoded_log = self.github_contract.events.ViolationReported().processLog(log)
                    return decoded_log.args.violationId
                except:
                    continue
            return None
        except:
            return None
    
    def get_account_balance(self) -> float:
        """Get account balance in tFIL"""
        if not self.account:
            return 0.0
        
        try:
            balance_wei = self.w3.eth.get_balance(self.account.address)
            balance_fil = self.w3.from_wei(balance_wei, 'ether')
            return float(balance_fil)
        except Exception as e:
            logger.error(f"❌ Failed to get balance: {e}")
            return 0.0
    
    def estimate_gas_costs(self) -> Dict:
        """Estimate gas costs for common operations"""
        try:
            gas_price = self.w3.eth.gas_price
            
            # Estimated gas costs (approximate)
            operations = {
                'register_repository': 200000,
                'report_violation': 150000,
                'add_link': 100000,
                'file_dmca': 100000
            }
            
            costs = {}
            for operation, gas_estimate in operations.items():
                cost_wei = gas_price * gas_estimate
                cost_fil = self.w3.from_wei(cost_wei, 'ether')
                costs[operation] = {
                    'gas_estimate': gas_estimate,
                    'cost_wei': cost_wei,
                    'cost_fil': float(cost_fil)
                }
            
            return {
                'success': True,
                'gas_price_wei': gas_price,
                'gas_price_gwei': self.w3.from_wei(gas_price, 'gwei'),
                'operations': costs
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to estimate gas costs: {e}")
            return {'success': False, 'error': str(e)}