#!/usr/bin/env python3
"""
Final Main Entry Point - Complete Filecoin GitHub Protection Agent
Integrates with deployed contracts on Filecoin Calibration testnet
"""
import os
import sys
from typing import Dict, List

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from github_protection_agent.complete_filecoin_agent import CompleteFilecoinAgent
from github_protection_agent.setup_validator import SetupValidator

try:
    from github_protection_agent.utils import setup_logging
except ImportError:
    def setup_logging(name):
        import logging
        return logging.getLogger(name)

logger = setup_logging(__name__)


def print_banner():
    """Print comprehensive banner"""
    print("\n" + "="*95)
    print("🛡️  COMPLETE FILECOIN GITHUB PROTECTION AGENT v5.0")
    print("="*95)
    print("🌟 Full Blockchain Integration:")
    print("   • ⛓️  Filecoin Calibration Testnet Smart Contracts")
    print("   • 🌐 IPFS Decentralized Storage (Pinata/Web3.Storage)")
    print("   • 📄 Automated License & DMCA Generation")
    print("   • 🔒 Comprehensive Security Auditing")
    print("   • 💰 Community Bounty System")
    print("   • 🔍 AI-Powered Code Analysis")
    print("   • 📊 Real-time Blockchain Monitoring")
    print("\n🏗️ Deployed Contracts (Filecoin Calibration):")
    print("   GitHubRepoProtection: 0x19054030669efBFc413bA3729b63eCfD3Bdc22B5")
    print("   LinkRegistry:         0x5fa19b4a48C20202055c8a6fdf16688633617D50")
    print("   InfringementBounty:   0xA2cD4CC41b8DCE00D002Aa4B29050f2d53705400")
    print("="*95 + "\n")


def print_quick_help():
    """Print quick command reference"""
    print("🚀 QUICK START COMMANDS:")
    print("-" * 50)
    print("validate          - Run system validation")
    print("status           - Check blockchain & IPFS status")
    print("register <url>   - Register repository on blockchain")
    print("analyze <url1> <url2> - Compare two repositories")
    print("audit <url>      - Comprehensive security audit")
    print("scan [id]        - Scan for violations & file DMCA")
    print("workflow <url>   - Complete protection workflow")
    print("query            - Query blockchain repositories")
    print("help             - Full command reference")
    print("-" * 50)


def print_full_help():
    """Print complete help information"""
    print("\n📚 COMPLETE COMMAND REFERENCE:")
    print("-" * 80)
    
    print("\n🔧 SYSTEM COMMANDS:")
    print("validate")
    print("   Run complete system validation (blockchain, IPFS, AI)")
    print("   Example: validate")
    print()
    print("status")
    print("   Check blockchain connection, account balance, IPFS services")
    print("   Example: status")
    print()
    
    print("🔗 BLOCKCHAIN COMMANDS:")
    print("register <url> [license_type]")
    print("   Register repository on Filecoin with license generation")
    print("   License types: MIT, Apache-2.0, GPL-3.0, BSD-3-Clause, Custom-AI")
    print("   Example: register https://github.com/user/repo MIT")
    print()
    print("query [start_id] [limit]")
    print("   Query repositories from blockchain")
    print("   Example: query 1 10")
    print()
    print("workflow <url>")
    print("   Run complete protection workflow (register + audit + scan)")
    print("   Example: workflow https://github.com/user/repo")
    print()
    
    print("🔍 ANALYSIS COMMANDS:")
    print("analyze <url1> <url2>")
    print("   Compare two repositories for similarity")
    print("   Example: analyze github.com/user1/repo1 github.com/user2/repo2")
    print()
    print("audit <url> [--extensive]")
    print("   Security audit with blockchain evidence storage")
    print("   Example: audit github.com/user/repo --extensive")
    print()
    print("scan [repo_id]")
    print("   Scan for violations and file DMCA notices")
    print("   Example: scan 1")
    print()
    
    print("💰 BOUNTY COMMANDS:")
    print("bounty <infringing_url> [original_repo_id]")
    print("   Report infringement for bounty rewards")
    print("   Example: bounty github.com/bad/repo 1")
    print()
    
    print("ℹ️  UTILITY COMMANDS:")
    print("help             - Show this help")
    print("quit/exit        - Exit the agent")
    print("-" * 80)


def validate_setup() -> bool:
    """Quick setup validation"""
    print("🔧 Validating setup...")
    
    validator = SetupValidator()
    
    # Quick checks
    required_env = ['PRIVATE_KEY']
    if not os.getenv('USE_LOCAL_MODEL', '').lower() == 'true':
        required_env.append('OPENAI_API_KEY')
    
    missing = [var for var in required_env if not os.getenv(var)]
    
    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        print("💡 Run 'validate' command for detailed setup check")
        return False
    
    # Quick network test
    try:
        from web3 import Web3
        w3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/filecoin_testnet'))
        if not w3.is_connected():
            print("❌ Cannot connect to Filecoin network")
            return False
    except Exception as e:
        print(f"❌ Network connection error: {e}")
        return False
    
    print("✅ Basic setup validated")
    return True


def main():
    """Enhanced main function with deployed contract integration"""
    
    # Configuration from environment
    config = {
        'USE_LOCAL_MODEL': os.getenv('USE_LOCAL_MODEL', 'false').lower() == 'true',
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN'),
        'PRIVATE_KEY': os.getenv('PRIVATE_KEY'),
        'FILECOIN_RPC_URL': os.getenv('FILECOIN_RPC_URL', 'https://rpc.ankr.com/filecoin_testnet'),
        'PINATA_API_KEY': os.getenv('PINATA_API_KEY'),
        'PINATA_API_SECRET': os.getenv('PINATA_API_SECRET'),
        'WEB3_STORAGE_TOKEN': os.getenv('WEB3_STORAGE_TOKEN')
    }
    
    print_banner()
    
    # Handle special commands before agent initialization
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'validate':
            validator = SetupValidator()
            validator.run_full_validation()
            return
        elif command in ['help', '--help', '-h']:
            print_full_help()
            return
        elif command == 'version':
            print("GitHub Protection Agent v5.0.0 (Filecoin Edition)")
            return
    
    # Quick validation
    if not validate_setup():
        print("\n💡 Run 'python github_protection_agent/main.py validate' for detailed diagnostics")
        return
    
    try:
        # Initialize complete agent
        print("🚀 Initializing Filecoin GitHub Protection Agent...")
        agent = CompleteFilecoinAgent(config)
        
        # Show initial status
        status = agent.get_complete_status()
        if status['success']:
            sys_status = status['system_status']
            blockchain = sys_status['blockchain']
            
            print("🔗 Blockchain Status:")
            print(f"   Network: {blockchain['network']}")
            print(f"   Account: {blockchain['account_address']}")
            print(f"   Balance: {blockchain['balance_tfil']:.6f} tFIL")
            print(f"   Repositories: {blockchain['total_registered_repos']}")
            
            # Show IPFS status
            ipfs_status = sys_status['ipfs']
            ipfs_available = sum(1 for s in ipfs_status.values() if s.get('available', False))
            print(f"   IPFS Services: {ipfs_available} available")
        
        print_quick_help()
        
        # Interactive command loop
        while True:
            try:
                user_input = input("\n🛡️  FilecoinAgent> ").strip()
                
                if not user_input:
                    continue
                
                parts = user_input.split()
                command = parts[0].lower()
                
                if command in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                elif command == 'help':
                    print_full_help()
                
                elif command == 'validate':
                    validator = SetupValidator()
                    validator.run_full_validation()
                
                elif command == 'status':
                    print("🔍 Checking complete system status...")
                    result = agent.get_complete_status()
                    
                    if result['success']:
                        status = result['system_status']
                        
                        # Blockchain
                        blockchain = status['blockchain']
                        print(f"\n⛓️  BLOCKCHAIN:")
                        print(f"   Network: {blockchain['network']}")
                        print(f"   Chain ID: {blockchain['chain_id']}")
                        print(f"   Account: {blockchain['account_address']}")
                        print(f"   Balance: {blockchain['balance_tfil']:.6f} tFIL")
                        print(f"   Repos: {blockchain['total_registered_repos']}")
                        
                        # IPFS
                        ipfs = status['ipfs']
                        print(f"\n🌐 IPFS SERVICES:")
                        for service, info in ipfs.items():
                            status_icon = "✅" if info.get('available') else "❌"
                            auth_info = " (authenticated)" if info.get('authenticated') else ""
                            print(f"   {status_icon} {service.replace('_', ' ').title()}{auth_info}")
                        
                        # Cache
                        cache = status['cache']
                        print(f"\n💾 CACHE:")
                        print(f"   Repositories: {cache['repositories_cached']}")
                        print(f"   Violations: {cache['violations_cached']}")
                    else:
                        print(f"❌ Error: {result['error']}")
                
                elif command == 'register':
                    if len(parts) < 2:
                        print("❌ Usage: register <url> [license_type]")
                        continue
                    
                    license_type = parts[2] if len(parts) > 2 else "MIT"
                    print(f"⛓️  Registering repository with {license_type} license...")
                    
                    result = agent.register_repository_complete(parts[1], license_type)
                    
                    if result['success']:
                        print(f"\n✅ Repository Registered Successfully!")
                        print(f"📋 Repo ID: {result['repo_id']}")
                        print(f"⛓️  Blockchain TX: {result['blockchain']['tx_hash']}")
                        print(f"📦 Block: {result['blockchain']['block_number']}")
                        print(f"⛽ Gas Used: {result['blockchain']['gas_used']:,}")
                        print(f"📄 License IPFS: {result['license']['ipfs_hash']}")
                        print(f"🌐 License URL: {result['license']['ipfs_url']}")
                        print(f"📌 IPFS Pinned: {'✅' if result['ipfs_pinning']['success'] else '❌'}")
                    else:
                        print(f"❌ Error: {result['error']}")
                
                elif command == 'analyze':
                    if len(parts) < 3:
                        print("❌ Usage: analyze <url1> <url2>")
                        continue
                    
                    print("🔍 Analyzing repositories with blockchain verification...")
                    result = agent.analyze_and_compare_repos(parts[1], parts[2])
                    
                    if result['success']:
                        comp = result['comparison']
                        similarity = comp['similarity']['overall_similarity']
                        
                        print(f"\n✅ Analysis Complete")
                        print(f"📊 Overall Similarity: {similarity:.2%}")
                        print(f"💡 {comp['recommendation']}")
                        
                        if comp['blockchain_matches']:
                            print(f"\n⛓️  Blockchain Matches Found:")
                            for match in comp['blockchain_matches']:
                                print(f"   • Repo ID {match['repo_id']}: {match['url']}")
                        
                        print(f"\n📋 Suggested Next Actions:")
                        for action in result['next_actions']:
                            print(f"   • {action}")
                    else:
                        print(f"❌ Error: {result['error']}")
                
                elif command == 'audit':
                    if len(parts) < 2:
                        print("❌ Usage: audit <url> [--extensive]")
                        continue
                    
                    extensive = '--extensive' in parts
                    mode = "extensive (all commits)" if extensive else "standard"
                    print(f"🔒 Running {mode} security audit...")
                    
                    result = agent.comprehensive_security_audit(parts[1], extensive)
                    
                    if result['success']:
                        audit = result['audit_results']
                        
                        print(f"\n✅ Security Audit Complete")
                        print(f"📁 Files: {audit['files_scanned']}")
                        print(f"📊 Commits: {audit.get('commits_scanned', 'N/A')}")
                        print(f"🚨 Findings: {audit['total_findings']}")
                        print(f"   🔴 Critical: {audit['critical_findings']}")
                        print(f"   🟠 High: {audit['high_findings']}")
                        print(f"   🟡 Medium: {audit['medium_findings']}")
                        print(f"   🟢 Low: {audit['low_findings']}")
                        
                        if result.get('blockchain_evidence'):
                            evidence = result['blockchain_evidence']
                            print(f"\n📄 Evidence Report:")
                            print(f"   IPFS: {evidence['ipfs_url']}")
                            if evidence.get('pin_transaction'):
                                print(f"   Blockchain: {evidence['pin_transaction']}")
                    else:
                        print(f"❌ Error: {result['error']}")
                
                elif command == 'scan':
                    repo_id = int(parts[1]) if len(parts) > 1 else None
                    target = f"repository {repo_id}" if repo_id else "all registered repositories"
                    print(f"🔎 Scanning for violations of {target}...")
                    
                    result = agent.scan_and_report_violations(repo_id)
                    
                    if result['success']:
                        scan = result['scan_results']
                        
                        print(f"\n✅ Violation Scan Complete")
                        print(f"📊 Repositories Scanned: {scan['repositories_scanned']}")
                        print(f"⚠️  Violations Found: {scan['violations_found']}")
                        print(f"📄 DMCA Notices Filed: {scan['dmca_notices_filed']}")
                        
                        for notice in scan.get('dmca_notices', []):
                            print(f"\n🚨 DMCA Notice #{notice['dmca_id']}:")
                            print(f"   Target: {notice['infringing_url']}")
                            print(f"   IPFS: {notice['ipfs_url']}")
                            print(f"   Blockchain TXs: {notice['blockchain_transactions']}")
                    else:
                        print(f"❌ Error: {result['error']}")
                
                elif command == 'workflow':
                    if len(parts) < 2:
                        print("❌ Usage: workflow <url>")
                        continue
                    
                    print("🚀 Running complete protection workflow...")
                    result = agent.run_full_protection_workflow(parts[1])
                    
                    if result['success']:
                        summary = result['workflow_results']['summary']
                        
                        print(f"\n✅ Protection Workflow Complete!")
                        print(f"📋 Repository ID: {summary['repo_id']}")
                        print(f"⛓️  Blockchain: {'✅' if summary['blockchain_confirmed'] else '❌'}")
                        print(f"📄 License: {'✅' if summary['license_generated'] else '❌'}")
                        print(f"🌐 IPFS: {'✅' if summary['ipfs_stored'] else '❌'}")
                        print(f"🔒 Security Findings: {summary['security_findings']}")
                        print(f"⚠️  Violations: {summary['violations_found']}")
                        print(f"📄 DMCA Notices: {summary['dmca_notices_filed']}")
                        print(f"🛡️  Protection Level: {summary['protection_level'].upper()}")
                    else:
                        print(f"❌ Error: {result['error']}")
                
                elif command == 'query':
                    start_id = int(parts[1]) if len(parts) > 1 else 1
                    limit = int(parts[2]) if len(parts) > 2 else 10
                    
                    print(f"📊 Querying blockchain repositories...")
                    result = agent.query_blockchain_data('repositories', limit)
                    
                    if result['success']:
                        print(f"\n📚 Blockchain Repositories (showing {result['returned_count']}/{result['total_count']}):")
                        print("-" * 80)
                        
                        for repo in result['data']:
                            print(f"ID: {repo['id']}")
                            print(f"   URL: {repo['github_url']}")
                            print(f"   Owner: {repo['owner']}")
                            print(f"   License: {repo['license_type']}")
                            print(f"   Active: {'✅' if repo['is_active'] else '❌'}")
                            print()
                    else:
                        print(f"❌ Error: {result['error']}")
                
                elif command == 'bounty':
                    if len(parts) < 2:
                        print("❌ Usage: bounty <infringing_url> [original_repo_id]")
                        continue
                    
                    original_id = int(parts[2]) if len(parts) > 2 else None
                    print("💰 Processing bounty claim...")
                    
                    result = agent.report_infringement_bounty(parts[1], original_id)
                    
                    if result['success']:
                        bounty = result['bounty_claim']
                        
                        print(f"\n✅ Bounty Claim Submitted!")
                        print(f"💰 Amount: {bounty['amount']} {bounty['currency']}")
                        print(f"📊 Similarity: {bounty['similarity_score']:.2%}")
                        print(f"📄 DMCA Notice: {bounty['dmca_notice']['dmca_id']}")
                        print(f"🔄 Status: {bounty['status']}")
                    else:
                        print(f"❌ Error: {result['error']}")
                
                else:
                    print(f"❌ Unknown command: {command}")
                    print("💡 Type 'help' for available commands")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"Command error: {e}")
                print(f"❌ Error executing command: {e}")
                
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        print(f"❌ Failed to initialize agent: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Run 'validate' to check configuration")
        print("   2. Verify environment variables are set")
        print("   3. Check Filecoin network connectivity")
        print("   4. Ensure wallet has sufficient tFIL balance")
        sys.exit(1)


if __name__ == "__main__":
    main()