"""
Comprehensive Test Suite for Filecoin GitHub Protection Agent
Tests all components including blockchain integration
"""
import os
import sys
import unittest
import asyncio
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List
import requests

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from github_protection_agent.complete_filecoin_agent import CompleteFilecoinAgent
from github_protection_agent.filecoin_contracts import FilecoinContractInterface
from github_protection_agent.enhanced_ipfs_manager import EnhancedIPFSManager
from github_protection_agent.blockchain_utilities import BlockchainUtils, IPFSUtils
from github_protection_agent.setup_validator import SetupValidator


class TestBlockchainUtils(unittest.TestCase):
    """Test blockchain utility functions"""
    
    def setUp(self):
        self.utils = BlockchainUtils()
        self.sample_repo_data = {
            'github_url': 'https://github.com/test/repo',
            'name': 'test-repo',
            'description': 'Test repository',
            'language': 'Python',
            'created_at': '2024-01-01T00:00:00Z',
            'files': ['main.py', 'README.md', 'requirements.txt']
        }
    
    def test_generate_repo_hash(self):
        """Test repository hash generation"""
        hash1 = self.utils.generate_repo_hash(self.sample_repo_data)
        hash2 = self.utils.generate_repo_hash(self.sample_repo_data)
        
        # Same data should produce same hash
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)  # SHA256 hex length
        
        # Different data should produce different hash
        modified_data = self.sample_repo_data.copy()
        modified_data['name'] = 'different-name'
        hash3 = self.utils.generate_repo_hash(modified_data)
        self.assertNotEqual(hash1, hash3)
    
    def test_generate_fingerprint(self):
        """Test fingerprint generation"""
        fingerprint = self.utils.generate_fingerprint(
            self.sample_repo_data['github_url'],
            self.sample_repo_data
        )
        
        self.assertEqual(len(fingerprint), 64)
        self.assertTrue(fingerprint.isalnum())
    
    def test_format_key_features(self):
        """Test key features formatting"""
        # Test string input
        features_str = "Feature 1\nFeature 2\nFeature 3\nFeature 4\nFeature 5\nFeature 6"
        formatted = self.utils.format_key_features(features_str)
        
        self.assertEqual(len(formatted), 5)  # Max 5 features
        self.assertTrue(all(len(f) <= 100 for f in formatted))  # Max 100 chars each
        
        # Test list input
        features_list = ['Feature A', 'Feature B', 'Feature C']
        formatted = self.utils.format_key_features(features_list)
        
        self.assertEqual(len(formatted), 3)
        self.assertEqual(formatted, features_list)
    
    def test_validate_ethereum_address(self):
        """Test Ethereum address validation"""
        # Valid addresses
        valid_addresses = [
            '0x19054030669efBFc413bA3729b63eCfD3Bdc22B5',
            '0x5fa19b4a48C20202055c8a6fdf16688633617D50',
            '0x0000000000000000000000000000000000000000'
        ]
        
        for addr in valid_addresses:
            self.assertTrue(self.utils.validate_ethereum_address(addr))
        
        # Invalid addresses
        invalid_addresses = [
            '19054030669efBFc413bA3729b63eCfD3Bdc22B5',  # No 0x prefix
            '0x19054030669efBFc413bA3729b63eCfD3Bdc22B',  # Too short
            '0x19054030669efBFc413bA3729b63eCfD3Bdc22B55',  # Too long
            '0xGGGG030669efBFc413bA3729b63eCfD3Bdc22B5',  # Invalid hex
            '',  # Empty
            None  # None
        ]
        
        for addr in invalid_addresses:
            self.assertFalse(self.utils.validate_ethereum_address(addr))


class TestIPFSUtils(unittest.TestCase):
    """Test IPFS utility functions"""
    
    def test_validate_ipfs_hash(self):
        """Test IPFS hash validation"""
        # Valid hashes
        valid_hashes = [
            'QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG',
            'bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi',
            'local://path/to/file'
        ]
        
        for hash_val in valid_hashes:
            self.assertTrue(IPFSUtils.validate_ipfs_hash(hash_val))
        
        # Invalid hashes
        invalid_hashes = [
            'invalid_hash',
            'Qm',  # Too short
            '',
            None
        ]
        
        for hash_val in invalid_hashes:
            self.assertFalse(IPFSUtils.validate_ipfs_hash(hash_val))
    
    def test_extract_cid_from_url(self):
        """Test CID extraction from URLs"""
        test_cases = [
            ('https://ipfs.io/ipfs/QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG', 
             'QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG'),
            ('https://gateway.pinata.cloud/ipfs/QmTest123/file.pdf', 'QmTest123'),
            ('https://example.com/not-ipfs-url', None)
        ]
        
        for url, expected_cid in test_cases:
            with patch.object(IPFSUtils, 'validate_ipfs_hash', return_value=True):
                result = IPFSUtils.extract_cid_from_url(url)
                if expected_cid:
                    self.assertEqual(result, expected_cid)
                else:
                    self.assertIsNone(result)


class TestFilecoinContractInterface(unittest.TestCase):
    """Test Filecoin contract interface"""
    
    def setUp(self):
        self.config = {
            'PRIVATE_KEY': '0x' + '1' * 64,  # Mock private key
            'FILECOIN_RPC_URL': 'https://rpc.ankr.com/filecoin_testnet'
        }
    
    @patch('github_protection_agent.filecoin_contracts.Web3')
    def test_initialization(self, mock_web3):
        """Test contract interface initialization"""
        mock_w3_instance = Mock()
        mock_w3_instance.is_connected.return_value = True
        mock_web3.return_value = mock_w3_instance
        
        mock_account = Mock()
        mock_account.address = '0x742d35Cc6631C0532925a3b8D42C85f5c7456d0f'
        mock_w3_instance.eth.account.from_key.return_value = mock_account
        
        interface = FilecoinContractInterface(self.config)
        
        self.assertEqual(interface.chain_id, 314159)
        self.assertIn('github_protection', interface.contracts)
        self.assertTrue(mock_w3_instance.is_connected.called)
    
    @patch('github_protection_agent.filecoin_contracts.Web3')
    def test_get_account_balance(self, mock_web3):
        """Test account balance retrieval"""
        mock_w3_instance = Mock()
        mock_w3_instance.is_connected.return_value = True
        mock_w3_instance.eth.get_balance.return_value = 1000000000000000000  # 1 ETH in wei
        mock_w3_instance.from_wei.return_value = 1.0
        mock_web3.return_value = mock_w3_instance
        
        mock_account = Mock()
        mock_account.address = '0x742d35Cc6631C0532925a3b8D42C85f5c7456d0f'
        mock_w3_instance.eth.account.from_key.return_value = mock_account
        
        interface = FilecoinContractInterface(self.config)
        balance = interface.get_account_balance()
        
        self.assertEqual(balance, 1.0)


class TestEnhancedIPFSManager(unittest.TestCase):
    """Test enhanced IPFS manager"""
    
    def setUp(self):
        self.config = {
            'PINATA_API_KEY': 'test_key',
            'PINATA_API_SECRET': 'test_secret'
        }
        self.manager = EnhancedIPFSManager(self.config)
    
    def test_service_priority_determination(self):
        """Test IPFS service priority determination"""
        # With Pinata configured
        priority = self.manager._determine_service_priority()
        self.assertIn('pinata', priority)
        self.assertEqual(priority[0], 'pinata')  # Should be first priority
    
    def test_get_file_type(self):
        """Test file type detection"""
        test_cases = [
            ('document.pdf', 'document'),
            ('data.json', 'metadata'),
            ('image.png', 'image'),
            ('unknown.xyz', 'unknown')
        ]
        
        for filename, expected_type in test_cases:
            result = self.manager._get_file_type(filename)
            self.assertEqual(result, expected_type)
    
    @patch('requests.post')
    def test_pinata_authentication_check(self, mock_post):
        """Test Pinata authentication"""
        # Mock successful authentication
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        status = self.manager.get_service_status()
        
        self.assertTrue(status['pinata']['available'])
        self.assertTrue(status['pinata']['authenticated'])


class TestCompleteFilecoinAgent(unittest.TestCase):
    """Test complete Filecoin agent integration"""
    
    def setUp(self):
        self.config = {
            'USE_LOCAL_MODEL': True,  # Use local model for testing
            'PRIVATE_KEY': '0x' + '1' * 64,
            'FILECOIN_RPC_URL': 'https://rpc.ankr.com/filecoin_testnet',
            'PINATA_API_KEY': 'test_key',
            'PINATA_API_SECRET': 'test_secret'
        }
    
    @patch('github_protection_agent.complete_filecoin_agent.FilecoinContractInterface')
    @patch('github_protection_agent.complete_filecoin_agent.EnhancedIPFSManager')
    def test_agent_initialization(self, mock_ipfs, mock_contract):
        """Test agent initialization"""
        # Mock the contract interface
        mock_contract_instance = Mock()
        mock_contract_instance.get_account_balance.return_value = 1.0
        mock_contract.return_value = mock_contract_instance
        
        # Mock IPFS manager
        mock_ipfs_instance = Mock()
        mock_ipfs.return_value = mock_ipfs_instance
        
        agent = CompleteFilecoinAgent(self.config)
        
        self.assertIsNotNone(agent.contract_interface)
        self.assertIsNotNone(agent.ipfs_manager)
        self.assertEqual(len(agent.tools), 8)  # Should have 8 tools
    
    @patch('github_protection_agent.complete_filecoin_agent.FilecoinContractInterface')
    def test_url_validation(self, mock_contract):
        """Test URL cleaning and validation"""
        mock_contract_instance = Mock()
        mock_contract.return_value = mock_contract_instance
        
        agent = CompleteFilecoinAgent(self.config)
        
        # Test valid URL
        valid, url, error = agent._clean_and_validate_url('https://github.com/user/repo')
        self.assertTrue(valid)
        self.assertEqual(url, 'https://github.com/user/repo')
        self.assertEqual(error, '')
        
        # Test invalid URL
        valid, url, error = agent._clean_and_validate_url('not-a-url')
        self.assertFalse(valid)
        self.assertNotEqual(error, '')


class TestSetupValidator(unittest.TestCase):
    """Test setup validation"""
    
    def setUp(self):
        self.validator = SetupValidator()
    
    def test_contract_addresses(self):
        """Test that contract addresses are valid"""
        for name, address in self.validator.contracts.items():
            self.assertTrue(BlockchainUtils.validate_ethereum_address(address),
                          f"Invalid contract address for {name}: {address}")
    
    def test_network_configuration(self):
        """Test network configuration"""
        self.assertEqual(self.validator.chain_id, 314159)
        self.assertIn('filecoin_testnet', self.validator.rpc_url)
    
    @patch.dict(os.environ, {'PRIVATE_KEY': '0x' + '1' * 64, 'OPENAI_API_KEY': 'test'})
    def test_environment_check(self):
        """Test environment variable checking"""
        result = self.validator.check_environment_variables()
        
        self.assertIn('required', result)
        self.assertIn('PRIVATE_KEY', result['required'])
        self.assertTrue(result['required']['PRIVATE_KEY']['set'])


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        self.config = {
            'USE_LOCAL_MODEL': True,
            'PRIVATE_KEY': os.getenv('TEST_PRIVATE_KEY', '0x' + '1' * 64),
            'FILECOIN_RPC_URL': 'https://rpc.ankr.com/filecoin_testnet'
        }
    
    @unittest.skipUnless(os.getenv('RUN_INTEGRATION_TESTS'), "Integration tests disabled")
    def test_blockchain_connection(self):
        """Test actual blockchain connection"""
        from web3 import Web3
        
        w3 = Web3(Web3.HTTPProvider(self.config['FILECOIN_RPC_URL']))
        self.assertTrue(w3.is_connected(), "Cannot connect to Filecoin testnet")
        
        chain_id = w3.eth.chain_id
        self.assertEqual(chain_id, 314159, f"Wrong chain ID: {chain_id}")
    
    @unittest.skipUnless(os.getenv('RUN_INTEGRATION_TESTS'), "Integration tests disabled")
    def test_contract_accessibility(self):
        """Test that deployed contracts are accessible"""
        from web3 import Web3
        
        w3 = Web3(Web3.HTTPProvider(self.config['FILECOIN_RPC_URL']))
        
        contracts = {
            'github_protection': '0x19054030669efBFc413bA3729b63eCfD3Bdc22B5',
            'link_registry': '0x5fa19b4a48C20202055c8a6fdf16688633617D50'
        }
        
        for name, address in contracts.items():
            code = w3.eth.get_code(address)
            self.assertGreater(len(code), 2, 
                             f"No contract bytecode found at {address} for {name}")


class TestPerformance(unittest.TestCase):
    """Performance tests"""
    
    def test_hash_generation_performance(self):
        """Test hash generation performance"""
        import time
        
        utils = BlockchainUtils()
        sample_data = {
            'github_url': 'https://github.com/test/repo',
            'name': 'test-repo',
            'description': 'Test repository',
            'files': ['file1.py', 'file2.py'] * 100  # Large file list
        }
        
        start_time = time.time()
        for _ in range(1000):
            utils.generate_repo_hash(sample_data)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 1000
        self.assertLess(avg_time, 0.01, "Hash generation too slow")  # < 10ms per hash


def run_test_suite():
    """Run the complete test suite"""
    print("🧪 Running Filecoin GitHub Protection Agent Test Suite")
    print("=" * 60)
    
    # Test discovery
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestBlockchainUtils,
        TestIPFSUtils,
        TestFilecoinContractInterface,
        TestEnhancedIPFSManager,
        TestCompleteFilecoinAgent,
        TestSetupValidator,
        TestIntegration,
        TestPerformance
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print(f"\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  • {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  • {test}: {traceback.split('Exception:')[-1].strip()}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print(f"\n✅ ALL TESTS PASSED!")
    else:
        print(f"\n❌ SOME TESTS FAILED!")
    
    return success


if __name__ == '__main__':
    # Set up test environment
    os.environ['TESTING'] = 'true'
    
    # Check if integration tests should run
    if '--integration' in sys.argv:
        os.environ['RUN_INTEGRATION_TESTS'] = 'true'
    
    # Run the test suite
    success = run_test_suite()
    sys.exit(0 if success else 1)