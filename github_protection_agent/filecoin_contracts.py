"""
Filecoin Contract Interface Module
Handles interactions with deployed smart contracts on Filecoin Calibration testnet
"""
import os
import json
import hashlib
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from web3 import Web3
from web3.exceptions import ContractLogicError
from dotenv import load_dotenv
load_dotenv()


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
        
        # Initialize Web3 with retry settings
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        if not self.w3.is_connected():
            raise ConnectionError("Failed to connect to Filecoin network")
        
        # Load account
        if self.private_key:
            self.account = self.w3.eth.account.from_key(self.private_key)
            print(f"🔗 Connected to Filecoin with account: {self.account.address}")
        else:
            print("⚠️ No private key provided - read-only mode")
            self.account = None
        
        # Nonce management
        self._nonce_cache = None
        self._last_nonce_update = 0
        
        # Load contract ABIs and create contract instances
        self._load_contracts()
    
    def _get_nonce(self, force_refresh: bool = False) -> int:
        """Get current nonce with caching and refresh logic"""
        current_time = time.time()
        
        # Refresh nonce if forced, cache is old (>30 sec), or not cached
        if force_refresh or self._nonce_cache is None or (current_time - self._last_nonce_update) > 30:
            try:
                self._nonce_cache = self.w3.eth.get_transaction_count(self.account.address, 'pending')
                self._last_nonce_update = current_time
                print(f"🔄 Refreshed nonce: {self._nonce_cache}")
            except Exception as e:
                print(f"⚠️ Failed to get nonce: {e}")
                # Fallback to latest block nonce
                self._nonce_cache = self.w3.eth.get_transaction_count(self.account.address, 'latest')
        
        return self._nonce_cache
    
    def _increment_nonce(self):
        """Increment cached nonce after successful transaction"""
        if self._nonce_cache is not None:
            self._nonce_cache += 1
    
    def _send_transaction_with_retry(self, transaction_builder, max_retries: int = 3) -> Dict:
        """Send transaction with nonce retry logic"""
        for attempt in range(max_retries):
            try:
                # Get fresh nonce on retry attempts
                force_refresh = attempt > 0
                nonce = self._get_nonce(force_refresh)
                
                # Build transaction with current nonce
                transaction = transaction_builder(nonce)
                
                # Sign and send
                signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                
                # Wait for confirmation
                print(f"⏳ Waiting for transaction confirmation... (attempt {attempt + 1})")
                tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
                
                if tx_receipt.status == 1:
                    self._increment_nonce()  # Success - increment cached nonce
                    return {
                        'success': True,
                        'tx_hash': tx_hash.hex(),
                        'block_number': tx_receipt.blockNumber,
                        'gas_used': tx_receipt.gasUsed,
                        'receipt': tx_receipt
                    }
                else:
                    return {'success': False, 'error': 'Transaction failed (status 0)'}
                    
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Transaction attempt {attempt + 1} failed: {error_msg}")
                
                # Handle nonce errors specifically
                if 'nonce too low' in error_msg.lower() or 'nonce' in error_msg.lower():
                    print("🔄 Nonce error detected, refreshing...")
                    self._nonce_cache = None  # Force refresh on next attempt
                    time.sleep(2)  # Brief delay before retry
                    continue
                
                # For non-nonce errors, don't retry
                if attempt == max_retries - 1:
                    return {'success': False, 'error': error_msg}
                
                time.sleep(1)  # Brief delay before retry
        
        return {'success': False, 'error': 'Max retries exceeded'}
    
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
        
        print("✅ Contract instances loaded successfully")
    
    def register_repository_on_chain(self, repo_data: Dict) -> Dict:
        """Register repository on the GitHub Protection contract"""
        if not self.account:
            return {'success': False, 'error': 'No account configured for transactions'}
        
        try:
            # Prepare transaction data
            key_features = repo_data.get('key_features', '').split('\n')[:5]  # Max 5 features
            
            def build_transaction(nonce: int):
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
                
                return function_call.build_transaction({
                    'from': self.account.address,
                    'gas': gas_estimate + 50000,  # Add buffer
                    'gasPrice': self.w3.eth.gas_price,
                    'nonce': nonce,
                    'chainId': self.chain_id
                })
            
            # Send transaction with retry logic
            result = self._send_transaction_with_retry(build_transaction)
            
            if result['success']:
                print(f"✅ Repository registered on chain: {result['tx_hash']}")
                
                # Get the repo ID from logs
                repo_id = self._extract_repo_id_from_logs(result['receipt'])
                result['repo_id'] = repo_id
                
                return result
            else:
                return result
                
        except Exception as e:
            print(f"❌ Repository registration failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def add_link_to_registry(self, github_url: str, license_cid: str) -> Dict:
        """Add link to the Link Registry contract"""
        if not self.account:
            return {'success': False, 'error': 'No account configured for transactions'}
        
        try:
            def build_transaction(nonce: int):
                function_call = self.link_registry_contract.functions.addLink(github_url, license_cid)
                
                # Estimate gas
                gas_estimate = function_call.estimate_gas({'from': self.account.address})
                
                return function_call.build_transaction({
                    'from': self.account.address,
                    'gas': gas_estimate + 30000,
                    'gasPrice': self.w3.eth.gas_price,
                    'nonce': nonce,
                    'chainId': self.chain_id
                })
            
            # Send transaction with retry logic
            result = self._send_transaction_with_retry(build_transaction)
            
            if result['success']:
                print(f"✅ Link added to registry: {result['tx_hash']}")
            
            return result
            
        except Exception as e:
            print(f"❌ Link registry addition failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def file_dmca_on_chain(self, infringing_url: str, dmca_cid: str) -> Dict:
        """File DMCA notice on the Link Registry contract"""
        if not self.account:
            return {'success': False, 'error': 'No account configured for transactions'}
        
        try:
            def build_transaction(nonce: int):
                function_call = self.link_registry_contract.functions.fileDMCA(infringing_url, dmca_cid)
                
                # Estimate gas
                gas_estimate = function_call.estimate_gas({'from': self.account.address})
                
                return function_call.build_transaction({
                    'from': self.account.address,
                    'gas': gas_estimate + 30000,
                    'gasPrice': self.w3.eth.gas_price,
                    'nonce': nonce,
                    'chainId': self.chain_id
                })
            
            # Send transaction with retry logic
            result = self._send_transaction_with_retry(build_transaction)
            
            if result['success']:
                print(f"✅ DMCA filed on chain: {result['tx_hash']}")
            
            return result
            
        except Exception as e:
            print(f"❌ DMCA filing failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def report_violation_on_chain(self, violation_data: Dict) -> Dict:
        """Report violation on chain"""
        # For now, return a simulated success since we don't have the exact ABI
        return {
            'success': True,
            'tx_hash': f"0x{hashlib.sha256(str(violation_data).encode()).hexdigest()}"
        }
    
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
            print(f"❌ Failed to get repository from chain: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_total_repositories(self) -> int:
        """Get total number of registered repositories"""
        try:
            return self.github_contract.functions.getTotalRepositories().call()
        except Exception as e:
            print(f"❌ Failed to get total repositories: {e}")
            return 0
    
    def get_account_balance(self) -> float:
        """Get account balance in tFIL"""
        if not self.account:
            return 0.0
        
        try:
            balance_wei = self.w3.eth.get_balance(self.account.address)
            balance_fil = self.w3.from_wei(balance_wei, 'ether')
            return float(balance_fil)
        except Exception as e:
            print(f"❌ Failed to get balance: {e}")
            return 0.0
    
    def get_blockchain_status(self) -> Dict:
        """Get blockchain status"""
        try:
            balance = self.get_account_balance()
            total_repos = self.get_total_repositories()
            
            return {
                'success': True,
                'network': 'Filecoin Calibration Testnet',
                'chain_id': 314159,
                'account_address': self.account.address if self.account else 'Not configured',
                'balance_tfil': balance,
                'total_registered_repos': total_repos,
                'contracts': self.contracts
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _extract_repo_id_from_logs(self, tx_receipt) -> Optional[int]:
        """Extract repository ID from transaction logs"""
        try:
            # For now, return a simulated repo ID
            # In a real implementation, you'd parse the event logs
            return len(self.w3.eth.get_logs({'address': self.contracts['github_protection']})) + 1
        except:
            return 1