#!/usr/bin/env python3
"""
Setup Validator and Quick Start Script
Validates configuration and tests Filecoin integration
"""
import os
import sys
from typing import Dict, List, Tuple
from web3 import Web3
import requests
from dotenv import load_dotenv

load_dotenv()


class SetupValidator:
    """Validates system setup for Filecoin integration"""
    
    def __init__(self):
        self.checks = []
        self.warnings = []
        self.errors = []
        
        # Contract addresses
        self.contracts = {
            'github_protection': '0x19054030669efBFc413bA3729b63eCfD3Bdc22B5',
            'link_registry': '0x5fa19b4a48C20202055c8a6fdf16688633617D50',
            'link_registry_deals': '0x25bc04a49997e25B7482eEcbeB2Ec67740AEd5a6',
            'infringement_bounty': '0xA2cD4CC41b8DCE00D002Aa4B29050f2d53705400',
            'deal_client': '0x592eC554ec3Af631d76981a680f699F9618B5687'
        }
        
        # Filecoin Calibration testnet
        self.rpc_url = 'https://rpc.ankr.com/filecoin_testnet'
        self.chain_id = 314159
    
    def run_full_validation(self) -> Dict:
        """Run complete validation suite"""
        print("🔧 Starting Filecoin Agent Setup Validation...")
        print("=" * 60)
        
        # 1. Check environment variables
        env_result = self.check_environment_variables()
        
        # 2. Check Python dependencies
        deps_result = self.check_dependencies()
        
        # 3. Check Filecoin network connection
        network_result = self.check_filecoin_network()
        
        # 4. Check wallet and balance
        wallet_result = self.check_wallet_balance()
        
        # 5. Check contract accessibility
        contracts_result = self.check_contract_access()
        
        # 6. Check IPFS services
        ipfs_result = self.check_ipfs_services()
        
        # 7. Check AI model access
        ai_result = self.check_ai_models()
        
        # Compile results
        all_results = {
            'environment': env_result,
            'dependencies': deps_result,
            'network': network_result,
            'wallet': wallet_result,
            'contracts': contracts_result,
            'ipfs': ipfs_result,
            'ai': ai_result
        }
        
        # Generate summary
        self.print_summary(all_results)
        
        return all_results
    
    def check_environment_variables(self) -> Dict:
        """Check required environment variables"""
        print("\n🔍 Checking Environment Variables...")
        
        required_vars = {
            'PRIVATE_KEY': 'Filecoin wallet private key',
            'OPENAI_API_KEY': 'OpenAI API key (or USE_LOCAL_MODEL=true)',
            'GITHUB_TOKEN': 'GitHub API token (optional but recommended)'
        }
        
        optional_vars = {
            'PINATA_API_KEY': 'Pinata IPFS service',
            'PINATA_API_SECRET': 'Pinata IPFS service',
            'WEB3_STORAGE_TOKEN': 'Alternative IPFS service',
            'USE_LOCAL_MODEL': 'Use local Ollama model instead of OpenAI'
        }
        
        results = {'required': {}, 'optional': {}, 'issues': []}
        
        # Check required variables
        for var, description in required_vars.items():
            value = os.getenv(var)
            
            if var == 'OPENAI_API_KEY' and os.getenv('USE_LOCAL_MODEL', '').lower() == 'true':
                results['required'][var] = {'set': True, 'note': 'Skipped (using local model)'}
                print(f"  ✅ {var}: Using local model instead")
            elif value:
                # Mask sensitive values
                masked_value = f"{value[:8]}..." if len(value) > 8 else "***"
                results['required'][var] = {'set': True, 'value': masked_value}
                print(f"  ✅ {var}: {masked_value}")
            else:
                results['required'][var] = {'set': False}
                results['issues'].append(f"Missing required variable: {var}")
                print(f"  ❌ {var}: Not set ({description})")
        
        # Check optional variables
        for var, description in optional_vars.items():
            value = os.getenv(var)
            if value:
                results['optional'][var] = {'set': True}
                print(f"  🔵 {var}: Set")
            else:
                results['optional'][var] = {'set': False}
                print(f"  ⚪ {var}: Not set ({description})")
        
        return results
    
    def check_dependencies(self) -> Dict:
        """Check Python package dependencies"""
        print("\n🐍 Checking Python Dependencies...")
        
        required_packages = [
            'web3', 'openai', 'langchain', 'requests', 'reportlab',
            'git', 'llama_index', 'sentence_transformers'
        ]
        
        results = {'installed': {}, 'missing': []}
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                results['installed'][package] = True
                print(f"  ✅ {package}")
            except ImportError:
                results['missing'].append(package)
                print(f"  ❌ {package} - Not installed")
        
        if results['missing']:
            print(f"\n  💡 Install missing packages: pip install {' '.join(results['missing'])}")
        
        return results
    
    def check_filecoin_network(self) -> Dict:
        """Check Filecoin network connectivity"""
        print("\n🌐 Checking Filecoin Network Connection...")
        
        try:
            w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            
            if w3.is_connected():
                block_number = w3.eth.block_number
                chain_id = w3.eth.chain_id
                
                if chain_id == self.chain_id:
                    print(f"  ✅ Connected to Filecoin Calibration (Block: {block_number})")
                    return {
                        'connected': True,
                        'block_number': block_number,
                        'chain_id': chain_id,
                        'rpc_url': self.rpc_url
                    }
                else:
                    print(f"  ❌ Wrong network (Chain ID: {chain_id}, expected: {self.chain_id})")
                    return {'connected': False, 'error': 'Wrong network'}
            else:
                print(f"  ❌ Failed to connect to Filecoin network")
                return {'connected': False, 'error': 'Connection failed'}
                
        except Exception as e:
            print(f"  ❌ Network error: {e}")
            return {'connected': False, 'error': str(e)}
    
    def check_wallet_balance(self) -> Dict:
        """Check wallet balance and validity"""
        print("\n💰 Checking Wallet and Balance...")
        
        private_key = os.getenv('PRIVATE_KEY')
        
        if not private_key:
            print("  ❌ No private key configured")
            return {'valid': False, 'error': 'No private key'}
        
        try:
            w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            account = w3.eth.account.from_key(private_key)
            address = account.address
            
            balance_wei = w3.eth.get_balance(address)
            balance_fil = w3.from_wei(balance_wei, 'ether')
            
            print(f"  ✅ Address: {address}")
            print(f"  💎 Balance: {balance_fil:.6f} tFIL")
            
            if balance_fil < 0.01:
                print("  ⚠️  Low balance - get more tFIL from faucet")
                print("     Faucet: https://faucet.calibration.fildev.network/")
            
            return {
                'valid': True,
                'address': address,
                'balance_fil': float(balance_fil),
                'balance_wei': balance_wei
            }
            
        except Exception as e:
            print(f"  ❌ Wallet error: {e}")
            return {'valid': False, 'error': str(e)}
    
    def check_contract_access(self) -> Dict:
        """Check access to deployed contracts"""
        print("\n⛓️  Checking Smart Contract Access...")
        
        try:
            w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            results = {}
            
            for name, address in self.contracts.items():
                try:
                    # Check if contract exists (has bytecode)
                    code = w3.eth.get_code(address)
                    
                    if len(code) > 2:  # More than just '0x'
                        print(f"  ✅ {name}: {address}")
                        results[name] = {'accessible': True, 'address': address}
                    else:
                        print(f"  ❌ {name}: No contract at {address}")
                        results[name] = {'accessible': False, 'address': address, 'error': 'No bytecode'}
                        
                except Exception as e:
                    print(f"  ❌ {name}: Error checking {address} - {e}")
                    results[name] = {'accessible': False, 'address': address, 'error': str(e)}
            
            return results
            
        except Exception as e:
            print(f"  ❌ Contract check failed: {e}")
            return {'error': str(e)}
    
    def check_ipfs_services(self) -> Dict:
        """Check IPFS service availability"""
        print("\n🌐 Checking IPFS Services...")
        
        results = {}
        
        # Check Pinata
        pinata_key = os.getenv('PINATA_API_KEY')
        pinata_secret = os.getenv('PINATA_API_SECRET')
        
        if pinata_key and pinata_secret:
            try:
                headers = {
                    'pinata_api_key': pinata_key,
                    'pinata_secret_api_key': pinata_secret
                }
                response = requests.get(
                    'https://api.pinata.cloud/data/testAuthentication',
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    print("  ✅ Pinata: Authenticated")
                    results['pinata'] = {'available': True, 'authenticated': True}
                else:
                    print(f"  ❌ Pinata: Authentication failed ({response.status_code})")
                    results['pinata'] = {'available': True, 'authenticated': False}
                    
            except Exception as e:
                print(f"  ❌ Pinata: Error - {e}")
                results['pinata'] = {'available': False, 'error': str(e)}
        else:
            print("  ⚪ Pinata: Not configured")
            results['pinata'] = {'available': False, 'reason': 'Not configured'}
        
        # Check Web3.Storage
        web3_token = os.getenv('WEB3_STORAGE_TOKEN')
        
        if web3_token:
            try:
                headers = {'Authorization': f'Bearer {web3_token}'}
                response = requests.get(
                    'https://api.web3.storage/user/account',
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    print("  ✅ Web3.Storage: Authenticated")
                    results['web3_storage'] = {'available': True, 'authenticated': True}
                else:
                    print(f"  ❌ Web3.Storage: Authentication failed ({response.status_code})")
                    results['web3_storage'] = {'available': True, 'authenticated': False}
                    
            except Exception as e:
                print(f"  ❌ Web3.Storage: Error - {e}")
                results['web3_storage'] = {'available': False, 'error': str(e)}
        else:
            print("  ⚪ Web3.Storage: Not configured")
            results['web3_storage'] = {'available': False, 'reason': 'Not configured'}
        
        # Check local IPFS
        try:
            response = requests.post('http://localhost:5001/api/v0/id', timeout=5)
            if response.status_code == 200:
                node_id = response.json().get('ID', 'Unknown')
                print(f"  ✅ Local IPFS: Running (ID: {node_id[:12]}...)")
                results['local_ipfs'] = {'available': True, 'node_id': node_id}
            else:
                print("  ❌ Local IPFS: Not responding")
                results['local_ipfs'] = {'available': False}
        except:
            print("  ⚪ Local IPFS: Not running")
            results['local_ipfs'] = {'available': False}
        
        return results
    
    def check_ai_models(self) -> Dict:
        """Check AI model access"""
        print("\n🤖 Checking AI Model Access...")
        
        use_local = os.getenv('USE_LOCAL_MODEL', '').lower() == 'true'
        
        if use_local:
            # Check Ollama
            try:
                response = requests.get('http://localhost:11434/api/tags', timeout=10)
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    llama_models = [m for m in models if 'llama3.2:3b' in m.get('name', '')]
                    
                    if llama_models:
                        print("  ✅ Ollama: llama3.2:3b model available")
                        return {'type': 'local', 'available': True, 'model': 'llama3.2:3b'}
                    else:
                        print("  ❌ Ollama: llama3.2:3b model not found")
                        print("     Run: ollama pull llama3.2:3b")
                        return {'type': 'local', 'available': False, 'error': 'Model not found'}
                else:
                    print("  ❌ Ollama: Service not responding")
                    return {'type': 'local', 'available': False, 'error': 'Service not running'}
            except:
                print("  ❌ Ollama: Not running")
                print("     Install: https://ollama.ai/")
                return {'type': 'local', 'available': False, 'error': 'Not installed'}
        else:
            # Check OpenAI
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                try:
                    import openai
                    client = openai.OpenAI(api_key=api_key)
                    
                    # Test with a simple completion
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": "Test"}],
                        max_tokens=5
                    )
                    
                    print("  ✅ OpenAI: API access confirmed")
                    return {'type': 'openai', 'available': True, 'model': 'gpt-4o-mini'}
                    
                except Exception as e:
                    print(f"  ❌ OpenAI: API error - {e}")
                    return {'type': 'openai', 'available': False, 'error': str(e)}
            else:
                print("  ❌ OpenAI: No API key configured")
                return {'type': 'openai', 'available': False, 'error': 'No API key'}
    
    def print_summary(self, results: Dict):
        """Print validation summary"""
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        
        # Count issues
        total_checks = 0
        passed_checks = 0
        critical_issues = []
        warnings = []
        
        # Environment variables
        env_issues = len(results['environment'].get('issues', []))
        if env_issues == 0:
            passed_checks += 1
        else:
            critical_issues.extend(results['environment']['issues'])
        total_checks += 1
        
        # Dependencies
        missing_deps = len(results['dependencies'].get('missing', []))
        if missing_deps == 0:
            passed_checks += 1
        else:
            critical_issues.append(f"Missing {missing_deps} required packages")
        total_checks += 1
        
        # Network
        if results['network'].get('connected'):
            passed_checks += 1
        else:
            critical_issues.append("Cannot connect to Filecoin network")
        total_checks += 1
        
        # Wallet
        if results['wallet'].get('valid'):
            passed_checks += 1
            if results['wallet'].get('balance_fil', 0) < 0.01:
                warnings.append("Low wallet balance - get more tFIL from faucet")
        else:
            critical_issues.append("Wallet configuration invalid")
        total_checks += 1
        
        # Contracts
        if isinstance(results['contracts'], dict) and not results['contracts'].get('error'):
            accessible_contracts = sum(1 for c in results['contracts'].values() if c.get('accessible'))
            if accessible_contracts == len(self.contracts):
                passed_checks += 1
            else:
                warnings.append(f"Only {accessible_contracts}/{len(self.contracts)} contracts accessible")
        else:
            critical_issues.append("Cannot access smart contracts")
        total_checks += 1
        
        # IPFS
        ipfs_services = sum(1 for s in results['ipfs'].values() if s.get('available'))
        if ipfs_services > 0:
            passed_checks += 1
            if ipfs_services == 1:
                warnings.append("Only one IPFS service available - consider adding backup")
        else:
            critical_issues.append("No IPFS services available")
        total_checks += 1
        
        # AI
        if results['ai'].get('available'):
            passed_checks += 1
        else:
            critical_issues.append("AI model not accessible")
        total_checks += 1
        
        # Print results
        print(f"✅ Passed: {passed_checks}/{total_checks} checks")
        
        if critical_issues:
            print(f"\n❌ Critical Issues ({len(critical_issues)}):")
            for issue in critical_issues:
                print(f"   • {issue}")
        
        if warnings:
            print(f"\n⚠️  Warnings ({len(warnings)}):")
            for warning in warnings:
                print(f"   • {warning}")
        
        # Overall status
        if critical_issues:
            print(f"\n🚫 SETUP INCOMPLETE - Fix critical issues before proceeding")
            print("   See setup guide: https://github.com/your-repo/setup-guide")
        elif warnings:
            print(f"\n⚠️  SETUP READY WITH WARNINGS - Agent will work but consider fixing warnings")
        else:
            print(f"\n🎉 SETUP COMPLETE - Ready to run Filecoin Agent!")
        
        print("\n📚 Next Steps:")
        if not critical_issues:
            print("   1. Run: python -m github_protection_agent.main_blockchain")
            print("   2. Try: register-blockchain https://github.com/your/repo")
            print("   3. Monitor: blockchain-status")
        else:
            print("   1. Fix critical issues listed above")
            print("   2. Re-run validation: python setup_validator.py")
            print("   3. Check documentation for help")
        
        print("\n💡 Resources:")
        print("   • Filecoin Faucet: https://faucet.calibration.fildev.network/")
        print("   • Pinata IPFS: https://app.pinata.cloud/")
        print("   • OpenAI API: https://platform.openai.com/api-keys")
        print("   • Ollama: https://ollama.ai/")


def main():
    """Main validation function"""
    validator = SetupValidator()
    results = validator.run_full_validation()
    
    # Return exit code based on results
    critical_issues = any([
        results['environment'].get('issues'),
        results['dependencies'].get('missing'),
        not results['network'].get('connected'),
        not results['wallet'].get('valid'),
        not results['ai'].get('available')
    ])
    
    sys.exit(1 if critical_issues else 0)


if __name__ == "__main__":
    main()