"""
Blockchain Utilities and Helper Functions
"""
import hashlib
import json
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from web3 import Web3

from .utils import setup_logging

logger = setup_logging(__name__)


class BlockchainUtils:
    """Utility functions for blockchain operations"""
    
    @staticmethod
    def generate_repo_hash(repo_data: Dict) -> str:
        """Generate deterministic hash for repository"""
        hash_data = {
            'url': repo_data.get('github_url', ''),
            'name': repo_data.get('name', ''),
            'description': repo_data.get('description', ''),
            'language': repo_data.get('language', ''),
            'created_at': repo_data.get('created_at', ''),
            'files': sorted(repo_data.get('files', [])[:10])  # Top 10 files
        }
        
        return hashlib.sha256(
            json.dumps(hash_data, sort_keys=True).encode()
        ).hexdigest()
    
    @staticmethod
    def generate_fingerprint(repo_url: str, metadata: Dict) -> str:
        """Generate unique fingerprint for repository"""
        fingerprint_data = f"{repo_url}:{metadata.get('created_at', '')}:{metadata.get('size', 0)}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    @staticmethod
    def format_key_features(features: str) -> List[str]:
        """Format key features for smart contract storage"""
        if isinstance(features, str):
            # Split by newlines and clean up
            feature_list = [f.strip() for f in features.split('\n') if f.strip()]
            # Limit to 5 features max, 100 chars each
            return [f[:100] for f in feature_list[:5]]
        elif isinstance(features, list):
            return [str(f)[:100] for f in features[:5]]
        else:
            return [str(features)[:100]]
    
    @staticmethod
    def calculate_similarity_score_int(similarity: float) -> int:
        """Convert similarity score to integer for smart contract"""
        return int(min(100, max(0, similarity * 100)))
    
    @staticmethod
    def format_evidence_hash(violation_data: Dict) -> str:
        """Generate evidence hash for violation"""
        evidence = {
            'violating_url': violation_data.get('violating_url', ''),
            'similarity_score': violation_data.get('similarity_score', 0),
            'timestamp': violation_data.get('timestamp', datetime.now().isoformat()),
            'evidence': violation_data.get('evidence', [])[:5]  # Top 5 evidence items
        }
        
        return hashlib.sha256(
            json.dumps(evidence, sort_keys=True).encode()
        ).hexdigest()
    
    @staticmethod
    def validate_ethereum_address(address: str) -> bool:
        """Validate Ethereum address format"""
        if not address or not isinstance(address, str):
            return False
        
        if not address.startswith('0x'):
            return False
        
        if len(address) != 42:
            return False
        
        try:
            int(address[2:], 16)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def format_transaction_result(tx_receipt) -> Dict:
        """Format transaction receipt for display"""
        return {
            'transaction_hash': tx_receipt.transactionHash.hex(),
            'block_number': tx_receipt.blockNumber,
            'gas_used': tx_receipt.gasUsed,
            'status': 'success' if tx_receipt.status == 1 else 'failed',
            'from_address': tx_receipt['from'] if 'from' in tx_receipt else None,
            'to_address': tx_receipt.to,
            'logs_count': len(tx_receipt.logs)
        }
    
    @staticmethod
    def estimate_total_cost(gas_used: int, gas_price: int) -> Dict:
        """Estimate transaction cost in various units"""
        cost_wei = gas_used * gas_price
        cost_fil = Web3.from_wei(cost_wei, 'ether')
        
        return {
            'gas_used': gas_used,
            'gas_price_wei': gas_price,
            'gas_price_gwei': Web3.from_wei(gas_price, 'gwei'),
            'total_cost_wei': cost_wei,
            'total_cost_fil': float(cost_fil),
            'total_cost_tfil': float(cost_fil)  # Same as FIL for testnet
        }
    
    @staticmethod
    def retry_transaction(func, max_retries: int = 3, delay: float = 2.0):
        """Retry transaction with exponential backoff"""
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                wait_time = delay * (2 ** attempt)
                logger.warning(f"Transaction attempt {attempt + 1} failed: {e}")
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
    
    @staticmethod
    def parse_contract_events(tx_receipt, contract, event_name: str) -> List[Dict]:
        """Parse specific events from transaction receipt"""
        events = []
        
        try:
            event_filter = getattr(contract.events, event_name)
            processed_logs = event_filter().processReceipt(tx_receipt)
            
            for log in processed_logs:
                events.append({
                    'event': event_name,
                    'args': dict(log.args),
                    'address': log.address,
                    'block_number': log.blockNumber,
                    'transaction_hash': log.transactionHash.hex()
                })
        except Exception as e:
            logger.warning(f"Failed to parse {event_name} events: {e}")
        
        return events


class IPFSUtils:
    """Utility functions for IPFS operations"""
    
    @staticmethod
    def validate_ipfs_hash(ipfs_hash: str) -> bool:
        """Validate IPFS hash format"""
        if not ipfs_hash or not isinstance(ipfs_hash, str):
            return False
        
        # Basic validation for IPFS CID
        if ipfs_hash.startswith('Qm') and len(ipfs_hash) == 46:
            return True
        if ipfs_hash.startswith('b') and len(ipfs_hash) >= 50:
            return True
        elif ipfs_hash.startswith('local://'):
            return True
        
        return False
    
    @staticmethod
    def extract_cid_from_url(url: str) -> Optional[str]:
        """Extract CID from IPFS URL"""
        if '/ipfs/' in url:
            parts = url.split('/ipfs/')
            if len(parts) > 1:
                cid = parts[1].split('/')[0]
                return cid if IPFSUtils.validate_ipfs_hash(cid) else None
        
        return None
    
    @staticmethod
    def generate_ipfs_urls(ipfs_hash: str) -> List[str]:
        """Generate multiple IPFS gateway URLs"""
        if not IPFSUtils.validate_ipfs_hash(ipfs_hash):
            return []
        
        if ipfs_hash.startswith('local://'):
            return [ipfs_hash]
        
        gateways = [
            f"https://ipfs.io/ipfs/{ipfs_hash}",
            f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}",
            f"https://cloudflare-ipfs.com/ipfs/{ipfs_hash}",
            f"https://dweb.link/ipfs/{ipfs_hash}"
        ]
        
        return gateways


class SubmissionTypeEnum:
    """Enum for smart contract submission types"""
    REGISTER = 0
    REPORT_VIOLATION = 1
    UPDATE_LICENSE = 2
    
    @classmethod
    def get_name(cls, value: int) -> str:
        """Get name for submission type value"""
        mapping = {
            0: "Register",
            1: "ReportViolation", 
            2: "UpdateLicense"
        }
        return mapping.get(value, "Unknown")
    
    @classmethod
    def validate(cls, value: int) -> bool:
        """Validate submission type value"""
        return value in [0, 1, 2]


class ContractEventMonitor:
    """Monitor and parse contract events"""
    
    def __init__(self, w3: Web3, contract_address: str, contract_abi: List):
        self.w3 = w3
        self.contract = w3.eth.contract(address=contract_address, abi=contract_abi)
        
    def get_latest_events(self, event_name: str, from_block: int = None, to_block: int = None) -> List[Dict]:
        """Get latest events of specified type"""
        try:
            if from_block is None:
                from_block = max(0, self.w3.eth.block_number - 1000)  # Last 1000 blocks
            
            if to_block is None:
                to_block = 'latest'
            
            event_filter = getattr(self.contract.events, event_name)
            events = event_filter.createFilter(fromBlock=from_block, toBlock=to_block).get_all_entries()
            
            parsed_events = []
            for event in events:
                parsed_events.append({
                    'event': event_name,
                    'args': dict(event.args),
                    'address': event.address,
                    'block_number': event.blockNumber,
                    'transaction_hash': event.transactionHash.hex(),
                    'log_index': event.logIndex
                })
            
            return parsed_events
            
        except Exception as e:
            logger.error(f"Failed to get {event_name} events: {e}")
            return []
    
    def monitor_repository_registrations(self) -> List[Dict]:
        """Monitor repository registration events"""
        return self.get_latest_events('RepositoryRegistered')
    
    def monitor_violation_reports(self) -> List[Dict]:
        """Monitor violation report events"""
        return self.get_latest_events('ViolationReported')
    
    def monitor_license_updates(self) -> List[Dict]:
        """Monitor license update events"""
        return self.get_latest_events('LicenseUpdated')


class FilecoinNetworkInfo:
    """Information about Filecoin Calibration network"""
    
    CHAIN_ID = 314159
    CURRENCY = "tFIL"
    BLOCK_TIME = 30  # seconds
    
    NETWORK_INFO = {
        'name': 'Filecoin Calibration Testnet',
        'chain_id': CHAIN_ID,
        'currency': CURRENCY,
        'block_time': BLOCK_TIME,
        'explorer': 'https://calibration.filscan.io',
        'faucet': 'https://faucet.calibration.fildev.network/'
    }
    
    RPC_ENDPOINTS = [
        'https://rpc.ankr.com/filecoin_testnet',
        'https://api.calibration.node.glif.io/rpc/v1',
        'https://filecoin-calibration.chainup.net/rpc/v1'
    ]
    
    @classmethod
    def get_network_info(cls) -> Dict:
        """Get complete network information"""
        return cls.NETWORK_INFO.copy()
    
    @classmethod
    def get_explorer_url(cls, tx_hash: str = None, address: str = None) -> str:
        """Get explorer URL for transaction or address"""
        base_url = cls.NETWORK_INFO['explorer']
        
        if tx_hash:
            return f"{base_url}/tx/{tx_hash}"
        elif address:
            return f"{base_url}/address/{address}"
        else:
            return base_url
    
    @classmethod
    def test_rpc_endpoints(cls) -> Dict:
        """Test all RPC endpoints and return status"""
        results = {}
        
        for endpoint in cls.RPC_ENDPOINTS:
            try:
                w3 = Web3(Web3.HTTPProvider(endpoint))
                if w3.is_connected():
                    block_number = w3.eth.block_number
                    results[endpoint] = {
                        'status': 'connected',
                        'block_number': block_number,
                        'latency': 'unknown'  # Could add timing
                    }
                else:
                    results[endpoint] = {'status': 'failed', 'error': 'Connection failed'}
            except Exception as e:
                results[endpoint] = {'status': 'error', 'error': str(e)}
        
        return results


def format_currency(amount: float, currency: str = "tFIL", decimals: int = 6) -> str:
    """Format currency amount for display"""
    return f"{amount:.{decimals}f} {currency}"


def format_gas(gas_amount: int) -> str:
    """Format gas amount for display"""
    if gas_amount >= 1_000_000:
        return f"{gas_amount / 1_000_000:.2f}M gas"
    elif gas_amount >= 1_000:
        return f"{gas_amount / 1_000:.1f}K gas"
    else:
        return f"{gas_amount:,} gas"


def calculate_time_ago(timestamp: int) -> str:
    """Calculate time ago from timestamp"""
    now = int(time.time())
    diff = now - timestamp
    
    if diff < 60:
        return f"{diff}s ago"
    elif diff < 3600:
        return f"{diff // 60}m ago"
    elif diff < 86400:
        return f"{diff // 3600}h ago"
    else:
        return f"{diff // 86400}d ago"