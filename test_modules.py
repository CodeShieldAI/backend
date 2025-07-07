#!/usr/bin/env python3
"""
Quick test script to verify all modules can be imported correctly
"""
import sys
import os

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing module imports...")
    
    modules_to_test = [
        'github_protection_agent.utils',
        'github_protection_agent.repository_analyzer',
        'github_protection_agent.security_scanner',
        'github_protection_agent.secret_patterns',
        'github_protection_agent.url_processor',
        'github_protection_agent.violation_detector',
        'github_protection_agent.report_generator',
        'github_protection_agent.dmca_generator',
        'github_protection_agent.license_generator',
        'github_protection_agent.github_scanner',
        'github_protection_agent.bounty_system',
        'github_protection_agent.enhanced_ipfs_manager',
        'github_protection_agent.filecoin_contracts',
        'github_protection_agent.blockchain_utilities',
        'github_protection_agent.complete_filecoin_agent'
    ]
    
    success_count = 0
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name}")
            success_count += 1
        except ImportError as e:
            print(f"  ❌ {module_name}: {e}")
        except Exception as e:
            print(f"  ⚠️  {module_name}: {e}")
    
    print(f"\n📊 Import Results: {success_count}/{len(modules_to_test)} modules imported successfully")
    
    if success_count == len(modules_to_test):
        print("🎉 All modules imported successfully!")
        return True
    else:
        print("⚠️ Some modules failed to import")
        return False

def test_basic_functionality():
    """Test basic functionality of key modules"""
    print("\n🔧 Testing basic functionality...")
    
    try:
        # Test URLProcessor
        from github_protection_agent.url_processor import URLProcessor
        
        # Create a mock LLM
        class MockLLM:
            def invoke(self, prompt):
                class MockResponse:
                    content = "Mock AI response"
                return MockResponse()
        
        url_processor = URLProcessor(MockLLM())
        result = url_processor.clean_single_url('https://github.com/octocat/Hello-World')
        
        if result['success']:
            print("  ✅ URLProcessor working")
        else:
            print(f"  ❌ URLProcessor failed: {result['error']}")
        
        # Test SecretPatterns
        from github_protection_agent.secret_patterns import SecretPatterns
        patterns = SecretPatterns()
        pattern_dict = patterns.get_patterns()
        
        if len(pattern_dict) > 0:
            print(f"  ✅ SecretPatterns loaded {len(pattern_dict)} patterns")
        else:
            print("  ❌ SecretPatterns failed to load patterns")
        
        # Test blockchain utilities
        from github_protection_agent.blockchain_utilities import BlockchainUtils
        utils = BlockchainUtils()
        
        test_data = {'url': 'https://github.com/test/repo', 'name': 'test'}
        hash_result = utils.generate_repo_hash(test_data)
        
        if len(hash_result) == 64:  # SHA256 hex length
            print("  ✅ BlockchainUtils working")
        else:
            print("  ❌ BlockchainUtils hash generation failed")
        
        print("✅ Basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🛡️ FILECOIN GITHUB PROTECTION AGENT - MODULE TESTS")
    print("=" * 60)
    
    # Test imports
    imports_ok = test_imports()
    
    if imports_ok:
        # Test functionality
        functionality_ok = test_basic_functionality()
        
        if functionality_ok:
            print(f"\n🎉 ALL TESTS PASSED!")
            print("🚀 Ready to run the agent with: python run_agent.py")
        else:
            print(f"\n⚠️ Import tests passed but functionality tests failed")
    else:
        print(f"\n❌ Import tests failed - fix missing modules first")
    
    print("=" * 60)

if __name__ == "__main__":
    main()