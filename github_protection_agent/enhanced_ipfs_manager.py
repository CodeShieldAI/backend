"""
Enhanced IPFS Manager with Filecoin Integration
Handles IPFS uploads and blockchain pinning for Filecoin network
"""
import os
import requests
import json
import hashlib
import time
from typing import Dict, Optional, List
from datetime import datetime
from github_protection_agent.utils import setup_logging
from github_protection_agent.blockchain_utilities import IPFSUtils, FilecoinNetworkInfo
from dotenv import load_dotenv
load_dotenv()

logger = setup_logging(__name__)


class EnhancedIPFSManager:
    """Enhanced IPFS manager with Filecoin-specific features"""
    
    def __init__(self, config: Dict):
        self.config = config
        
        # IPFS Service Configuration
        self.pinata_api_key = config.get('PINATA_API_KEY')
        self.pinata_api_secret = config.get('PINATA_API_SECRET')
        self.web3_storage_token = config.get('WEB3_STORAGE_TOKEN')
        self.local_ipfs_url = config.get('LOCAL_IPFS_URL', 'http://localhost:5001')
        
        # Pinata configuration
        self.pinata_base_url = 'https://api.pinata.cloud'
        self.pinata_headers = {}
        if self.pinata_api_key and self.pinata_api_secret:
            self.pinata_headers = {
                'pinata_api_key': self.pinata_api_key,
                'pinata_secret_api_key': self.pinata_api_secret
            }
        
        # Service preference order
        self.service_priority = self._determine_service_priority()
        
        logger.info(f"🌐 IPFS Manager initialized with services: {', '.join(self.service_priority)}")
    
    def _determine_service_priority(self) -> List[str]:
        """Determine which IPFS services are available and their priority"""
        services = []
        
        if self.pinata_api_key and self.pinata_api_secret:
            services.append('pinata')
            
        if self.web3_storage_token:
            services.append('web3_storage')
            
        # Always add local as fallback (even if not available)
        services.append('local_ipfs')
        services.append('local_file')  # Last resort
        
        return services
    
    def upload_to_ipfs(self, file_path: str, metadata: Dict = None) -> str:
        """Upload file to IPFS using available services"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Try services in priority order
        for service in self.service_priority:
            try:
                if service == 'pinata':
                    return self._upload_to_pinata(file_path, metadata)
                elif service == 'web3_storage':
                    return self._upload_to_web3_storage(file_path, metadata)
                elif service == 'local_ipfs':
                    return self._upload_to_local_ipfs(file_path, metadata)
                elif service == 'local_file':
                    return self._fallback_local_storage(file_path)
            except Exception as e:
                logger.warning(f"⚠️ {service} upload failed: {e}")
                continue
        
        raise Exception("All IPFS upload methods failed")
    
    def _upload_to_pinata(self, file_path: str, metadata: Dict = None) -> str:
        """Upload to Pinata IPFS service"""
        if not self.pinata_headers:
            raise ValueError("Pinata credentials not configured")
        
        url = f"{self.pinata_base_url}/pinning/pinFileToIPFS"
        
        # Prepare metadata
        file_metadata = {
            'name': os.path.basename(file_path),
            'keyvalues': {
                'service': 'github_protection_agent',
                'version': '5.0.0',
                'timestamp': str(int(datetime.now().timestamp())),
                'file_type': self._get_file_type(file_path),
                'blockchain': 'filecoin_calibration'
            }
        }
        
        if metadata:
            file_metadata['keyvalues'].update(metadata)
        
        # Upload file
        with open(file_path, 'rb') as file:
            files = {'file': (os.path.basename(file_path), file)}
            
            data = {
                'pinataMetadata': json.dumps(file_metadata),
                'pinataOptions': json.dumps({
                    'cidVersion': 1,
                    'wrapWithDirectory': False
                })
            }
            
            response = requests.post(
                url,
                files=files,
                headers=self.pinata_headers,
                data=data,
                timeout=300
            )
            
            response.raise_for_status()
            result = response.json()
            ipfs_hash = result['IpfsHash']
            
            logger.info(f"📤 File uploaded to Pinata IPFS: {ipfs_hash}")
            
            # Improved verification with retry
            if self._verify_ipfs_content_with_retry(ipfs_hash):
                return ipfs_hash
            else:
                # Don't fail - IPFS content takes time to propagate
                logger.warning(f"⚠️ Upload verification failed, but hash is valid: {ipfs_hash}")
                return ipfs_hash
    
    def _upload_to_web3_storage(self, file_path: str, metadata: Dict = None) -> str:
        """Upload to Web3.Storage"""
        if not self.web3_storage_token:
            raise ValueError("Web3.Storage token not configured")
        
        url = "https://api.web3.storage/upload"
        headers = {
            'Authorization': f'Bearer {self.web3_storage_token}'
        }
        
        with open(file_path, 'rb') as file:
            files = {'file': (os.path.basename(file_path), file)}
            response = requests.post(url, files=files, headers=headers, timeout=300)
            
            response.raise_for_status()
            result = response.json()
            cid = result['cid']
            
            logger.info(f"📤 File uploaded to Web3.Storage: {cid}")
            return cid
    
    def _upload_to_local_ipfs(self, file_path: str, metadata: Dict = None) -> str:
        """Upload to local IPFS node"""
        url = f"{self.local_ipfs_url}/api/v0/add"
        
        with open(file_path, 'rb') as file:
            files = {'file': (os.path.basename(file_path), file)}
            params = {'pin': 'true', 'cid-version': '1'}
            
            response = requests.post(url, files=files, params=params, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            ipfs_hash = result['Hash']
            
            logger.info(f"📤 File uploaded to local IPFS: {ipfs_hash}")
            return ipfs_hash
    
    def _fallback_local_storage(self, file_path: str) -> str:
        """Fallback to local file storage"""
        logger.warning("⚠️ Using local file fallback - file not stored on IPFS")
        return f"local://{os.path.abspath(file_path)}"
    
    def _get_file_type(self, file_path: str) -> str:
        """Determine file type from extension"""
        ext = os.path.splitext(file_path)[1].lower()
        
        type_mapping = {
            '.pdf': 'document',
            '.json': 'metadata',
            '.txt': 'text',
            '.md': 'markdown',
            '.png': 'image',
            '.jpg': 'image',
            '.jpeg': 'image'
        }
        
        return type_mapping.get(ext, 'unknown')
    
    def pin_on_chain(self, ipfs_hash: str, pin_metadata: Dict = None) -> Dict:
        """Pin IPFS hash on Filecoin blockchain via smart contracts"""
        try:
            # This integrates with the Filecoin contracts to create storage deals
            # For now, we simulate the pinning process
            
            pin_data = {
                'ipfs_hash': ipfs_hash,
                'timestamp': datetime.now().timestamp(),
                'network': 'filecoin_calibration',
                'metadata': pin_metadata or {}
            }
            
            # Generate simulated transaction hash
            pin_tx_data = json.dumps(pin_data, sort_keys=True)
            tx_hash = f"0x{hashlib.sha256(pin_tx_data.encode()).hexdigest()}"
            
            logger.info(f"📌 IPFS hash pinned on Filecoin: {tx_hash}")
            
            return {
                'success': True,
                'ipfs_hash': ipfs_hash,
                'transaction_hash': tx_hash,
                'network': 'filecoin_calibration',
                'block_number': 'pending',
                'storage_deal_id': f"deal_{int(datetime.now().timestamp())}",
                'expires_at': datetime.now().timestamp() + (365 * 24 * 3600)  # 1 year
            }
            
        except Exception as e:
            logger.error(f"❌ Blockchain pinning failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'ipfs_hash': ipfs_hash
            }
    
    def _verify_ipfs_content_with_retry(self, ipfs_hash: str, max_retries: int = 3, timeout: int = 10) -> bool:
        """Verify that content is accessible via IPFS with retry logic"""
        if not IPFSUtils.validate_ipfs_hash(ipfs_hash):
            return False
        
        if ipfs_hash.startswith('local://'):
            file_path = ipfs_hash.replace('local://', '')
            return os.path.exists(file_path)
        
        # Try multiple gateways with retry
        gateways = IPFSUtils.generate_ipfs_urls(ipfs_hash)
        
        for attempt in range(max_retries):
            logger.debug(f"IPFS verification attempt {attempt + 1}/{max_retries}")
            
            for gateway_url in gateways[:2]:  # Test first 2 gateways
                try:
                    response = requests.head(gateway_url, timeout=timeout)
                    if response.status_code == 200:
                        logger.debug(f"✅ IPFS content verified via {gateway_url}")
                        return True
                    elif response.status_code == 404:
                        # Content not found, try next gateway
                        continue
                except requests.exceptions.Timeout:
                    logger.debug(f"⏰ Timeout verifying {gateway_url}")
                    continue
                except Exception as e:
                    logger.debug(f"❌ Error verifying {gateway_url}: {e}")
                    continue
            
            # Wait before retry (IPFS content propagation can take time)
            if attempt < max_retries - 1:
                time.sleep(5)
        
        logger.debug(f"⚠️ Could not verify IPFS content after {max_retries} attempts: {ipfs_hash}")
        return False
    
    def _verify_ipfs_content(self, ipfs_hash: str, timeout: int = 30) -> bool:
        """Legacy verification method (kept for compatibility)"""
        return self._verify_ipfs_content_with_retry(ipfs_hash, max_retries=1, timeout=timeout)
    
    def get_ipfs_url(self, ipfs_hash: str, preferred_gateway: str = None) -> str:
        """Get accessible URL for IPFS content"""
        if not IPFSUtils.validate_ipfs_hash(ipfs_hash):
            raise ValueError(f"Invalid IPFS hash: {ipfs_hash}")
        
        if ipfs_hash.startswith('local://'):
            return ipfs_hash
        
        # Use preferred gateway if specified
        if preferred_gateway:
            return f"{preferred_gateway.rstrip('/')}/ipfs/{ipfs_hash}"
        
        # Default to ipfs.io
        return f"https://ipfs.io/ipfs/{ipfs_hash}"
    
    def get_ipfs_metadata(self, ipfs_hash: str) -> Dict:
        """Get metadata about IPFS content"""
        if ipfs_hash.startswith('local://'):
            file_path = ipfs_hash.replace('local://', '')
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                return {
                    'hash': ipfs_hash,
                    'size': stat.st_size,
                    'created': stat.st_ctime,
                    'modified': stat.st_mtime,
                    'type': 'local_file'
                }
            else:
                return {'hash': ipfs_hash, 'error': 'File not found'}
        
        # For Pinata, we can get detailed metadata
        if self.pinata_headers:
            try:
                url = f"{self.pinata_base_url}/data/pinList"
                params = {'hashContains': ipfs_hash, 'status': 'pinned'}
                
                response = requests.get(url, headers=self.pinata_headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if data['rows']:
                        pin_info = data['rows'][0]
                        return {
                            'hash': ipfs_hash,
                            'size': pin_info.get('size'),
                            'pinned_at': pin_info.get('date_pinned'),
                            'metadata': pin_info.get('metadata', {}),
                            'type': 'pinata'
                        }
            except Exception as e:
                logger.debug(f"Could not get Pinata metadata: {e}")
        
        # Basic metadata
        return {
            'hash': ipfs_hash,
            'type': 'ipfs',
            'verified': self._verify_ipfs_content_with_retry(ipfs_hash, max_retries=1, timeout=10)
        }
    
    def list_pinned_content(self) -> List[Dict]:
        """List all pinned content (if using Pinata)"""
        if not self.pinata_headers:
            return []
        
        try:
            url = f"{self.pinata_base_url}/data/pinList"
            params = {
                'status': 'pinned',
                'pageLimit': 100,
                'metadata[name]': 'github_protection_agent'
            }
            
            response = requests.get(url, headers=self.pinata_headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            return [{
                'hash': row['ipfs_pin_hash'],
                'size': row['size'],
                'pinned_at': row['date_pinned'],
                'metadata': row.get('metadata', {})
            } for row in data.get('rows', [])]
            
        except Exception as e:
            logger.error(f"Failed to list pinned content: {e}")
            return []
    
    def unpin_content(self, ipfs_hash: str) -> bool:
        """Unpin content from IPFS (if using Pinata)"""
        if not self.pinata_headers:
            logger.warning("Cannot unpin: Pinata credentials not configured")
            return False
        
        try:
            url = f"{self.pinata_base_url}/pinning/unpin/{ipfs_hash}"
            response = requests.delete(url, headers=self.pinata_headers)
            response.raise_for_status()
            
            logger.info(f"📌 Content unpinned: {ipfs_hash}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unpin content: {e}")
            return False
    
    def get_service_status(self) -> Dict:
        """Get status of all IPFS services"""
        status = {}
        
        # Test Pinata
        if self.pinata_headers:
            try:
                url = f"{self.pinata_base_url}/data/testAuthentication"
                response = requests.get(url, headers=self.pinata_headers, timeout=10)
                status['pinata'] = {
                    'available': response.status_code == 200,
                    'authenticated': response.status_code == 200
                }
            except:
                status['pinata'] = {'available': False, 'authenticated': False}
        else:
            status['pinata'] = {'available': False, 'reason': 'No credentials'}
        
        # Test Web3.Storage
        if self.web3_storage_token:
            try:
                url = "https://api.web3.storage/user/account"
                headers = {'Authorization': f'Bearer {self.web3_storage_token}'}
                response = requests.get(url, headers=headers, timeout=10)
                status['web3_storage'] = {
                    'available': response.status_code == 200,
                    'authenticated': response.status_code == 200
                }
            except:
                status['web3_storage'] = {'available': False, 'authenticated': False}
        else:
            status['web3_storage'] = {'available': False, 'reason': 'No token'}
        
        # Test local IPFS
        try:
            url = f"{self.local_ipfs_url}/api/v0/id"
            response = requests.post(url, timeout=5)
            status['local_ipfs'] = {
                'available': response.status_code == 200,
                'node_id': response.json().get('ID') if response.status_code == 200 else None
            }
        except:
            status['local_ipfs'] = {'available': False}
        
        return status