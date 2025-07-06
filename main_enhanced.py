"""
Blockchain-Enhanced Main Entry Point for GitHub Protection Agent
Integrates with Filecoin smart contracts for decentralized protection
"""
import os
import sys
from github_protection_agent.blockchain_enhanced_agent import BlockchainEnhancedGitHubProtectionAgent
from github_protection_agent.utils import setup_logging

logger = setup_logging(__name__)


def print_banner():
    """Print welcome banner with blockchain features"""
    print("\n" + "="*90)
    print("🛡️  BLOCKCHAIN-ENHANCED GitHub Repository Protection Agent v5.0")
    print("="*90)
    print("✨ New Blockchain Features:")
    print("   • 🔗 Filecoin Calibration Testnet Integration")
    print("   • ⛓️ Smart Contract Repository Registration")
    print("   • 📄 IPFS License & DMCA Storage")
    print("   • 💰 Infringement Bounty System")
    print("   • 🔒 Immutable Evidence Storage")
    print("   • 🌐 Decentralized Protection Network")
    print("\n📊 Contract Addresses:")
    print("   GitHubRepoProtection: 0x19054030669efBFc413bA3729b63eCfD3Bdc22B5")
    print("   LinkRegistry:         0x5fa19b4a48C20202055c8a6fdf16688633617D50")
    print("   InfringementBounty:   0xA2cD4CC41b8DCE00D002Aa4B29050f2d53705400")
    print("="*90 + "\n")


def print_help():
    """Print help information with blockchain commands"""
    print("\n📚 Available Commands:")
    print("-" * 70)
    print("🔗 BLOCKCHAIN COMMANDS:")
    print("blockchain-status")
    print("   Check Filecoin network connection and account balance")
    print("   Example: blockchain-status")
    print()
    print("register-blockchain <url> [license_type]")
    print("   Register repository on Filecoin blockchain")
    print("   License types: MIT, Apache-2.0, GPL-3.0, BSD-3-Clause, AGPL-3.0, Custom-AI")
    print("   Example: register-blockchain https://github.com/user/repo MIT")
    print()
    print("query-repos [start_id] [limit]")
    print("   Query repositories registered on blockchain")
    print("   Example: query-repos 1 5")
    print()
    print("workflow-blockchain <url>")
    print("   Run complete blockchain-backed protection workflow")
    print("   Example: workflow-blockchain github.com/user/repo")
    print()
    print("report-bounty <infringing_url> <license_cid> <dmca_cid>")
    print("   Report infringement and earn bounty rewards")
    print("   Example: report-bounty github.com/bad/repo QmLicense123 QmDMCA456")
    print()
    print("💡 ENHANCED ANALYSIS COMMANDS:")
    print("analyze <url1> <url2>")
    print("   Compare repositories with blockchain verification")
    print("   Example: analyze github.com/user1/repo1 github.com/user2/repo2")
    print()
    print("audit <url> [--extensive]")
    print("   Security audit with blockchain evidence storage")
    print("   Example: audit github.com/user/repo --extensive")
    print()
    print("scan [repo_id]")
    print("   Scan for violations with blockchain DMCA filing")
    print("   Example: scan 1")
    print()
    print("🔧 UTILITY COMMANDS:")
    print("list")
    print("   List cached repositories")
    print()
    print("help")
    print("   Show this help message")
    print()
    print("quit/exit")
    print("   Exit the agent")
    print("-" * 70 + "\n")


def print_setup_guide():
    """Print setup guide for blockchain functionality"""
    print("\n⚙️ BLOCKCHAIN SETUP GUIDE:")
    print("-" * 50)
    print("1. Set up environment variables:")
    print("   PRIVATE_KEY=your_private_key_here")
    print("   FILECOIN_RPC_URL=https://rpc.ankr.com/filecoin_testnet")
    print("   PINATA_API_KEY=your_pinata_key")
    print("   PINATA_API_SECRET=your_pinata_secret")
    print()
    print("2. Get tFIL testnet tokens:")
    print("   Visit: https://faucet.calibration.fildev.network/")
    print()
    print("3. Optional for local development:")
    print("   USE_LOCAL_MODEL=true (uses Ollama instead of OpenAI)")
    print()
    print("4. Required for OpenAI mode:")
    print("   OPENAI_API_KEY=your_openai_key")
    print("   GITHUB_TOKEN=your_github_token")
    print("-" * 50 + "\n")


def main():
    """Enhanced main function with blockchain support"""
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
    
    # Validate required configuration
    if not config['USE_LOCAL_MODEL'] and not config['OPENAI_API_KEY']:
        logger.error("❌ Please set OPENAI_API_KEY or USE_LOCAL_MODEL=true")
        print_setup_guide()
        return
    
    if not config['PRIVATE_KEY']:
        logger.warning("⚠️ No PRIVATE_KEY set - running in read-only mode")
    
    try:
        agent = BlockchainEnhancedGitHubProtectionAgent(config)
        print_banner()
        
        # Show blockchain status
        status = agent.get_blockchain_status()
        if status['success']:
            print("🔗 Blockchain Status:")
            print(f"   Network: {status['network']}")
            print(f"   Account: {status['account_address']}")
            print(f"   Balance: {status['balance_tfil']:.4f} tFIL")
            print(f"   Registered Repos: {status['total_registered_repos']}")
            
            # Show gas estimates
            if status.get('gas_estimates', {}).get('success'):
                gas_info = status['gas_estimates']
                print(f"   Gas Price: {gas_info['gas_price_gwei']:.2f} Gwei")
                print(f"   Register Cost: ~{gas_info['operations']['register_repository']['cost_fil']:.6f} tFIL")
        else:
            print(f"⚠️ Blockchain connection issue: {status['error']}")
        
        print_help()
        
        while True:
            try:
                user_input = input("🔗 Blockchain Agent> ").strip()
                
                if not user_input:
                    continue
                
                parts = user_input.split()
                command = parts[0].lower()
                
                if command in ['quit', 'exit']:
                    print("👋 Goodbye!")
                    break
                
                elif command == 'help':
                    print_help()
                
                elif command == 'setup':
                    print_setup_guide()
                
                elif command == 'blockchain-status':
                    print("🔍 Checking blockchain status...")
                    status = agent.get_blockchain_status()
                    
                    if status['success']:
                        print(f"\n✅ Blockchain Connection Status")
                        print(f"🌐 Network: {status['network']}")
                        print(f"🔗 Chain ID: {status['chain_id']}")
                        print(f"👤 Account: {status['account_address']}")
                        print(f"💰 Balance: {status['balance_tfil']:.6f} tFIL")
                        print(f"📊 Total Registered Repos: {status['total_registered_repos']}")
                        
                        print(f"\n📋 Contract Addresses:")
                        for name, address in status['contracts'].items():
                            print(f"   {name}: {address}")
                        
                        if status.get('gas_estimates', {}).get('success'):
                            gas_info = status['gas_estimates']
                            print(f"\n⛽ Gas Estimates:")
                            print(f"   Current Gas Price: {gas_info['gas_price_gwei']:.2f} Gwei")
                            for op_name, op_info in gas_info['operations'].items():
                                print(f"   {op_name.replace('_', ' ').title()}: ~{op_info['cost_fil']:.6f} tFIL")
                    else:
                        print(f"❌ Error: {status['error']}")
                
                elif command == 'register-blockchain':
                    if len(parts) < 2:
                        print("❌ Usage: register-blockchain <url> [license_type]")
                        continue
                    
                    license_type = parts[2] if len(parts) > 2 else "MIT"
                    print(f"⛓️ Registering repository on blockchain with {license_type} license...")
                    
                    result = agent.register_repository_blockchain(parts[1], license_type)
                    
                    if result['success']:
                        print(f"\n✅ Repository Registered on Blockchain!")
                        print(f"📋 Repo ID: {result['repo_id']}")
                        print(f"⛓️ Main TX: {result['tx_hash']}")
                        print(f"🔗 Link Registry TX: {result['link_registry_tx']}")
                        print(f"📦 Block: {result['block_number']}")
                        print(f"⛽ Gas Used: {result['gas_used']:,}")
                        print(f"📄 License PDF: {result['license']['pdf_path']}")
                        print(f"🌐 IPFS URL: {result['license']['ipfs_url']}")
                        print(f"💰 Estimated Cost: {result['gas_used'] * 0.000000001:.6f} tFIL")
                    else:
                        print(f"❌ Error: {result['error']}")
                
                elif command == 'query-repos':
                    start_id = int(parts[1]) if len(parts) > 1 else 1
                    limit = int(parts[2]) if len(parts) > 2 else 10
                    
                    print(f"📊 Querying blockchain repositories (starting from ID {start_id})...")
                    result = agent.query_registered_repositories(start_id, limit)
                    
                    if result['success']:
                        print(f"\n📚 Blockchain Registered Repositories ({result['query_range']}):")
                        print(f"Total on blockchain: {result['total_repositories']}")
                        print("-" * 80)
                        
                        for repo in result['repositories']:
                            print(f"ID: {repo['id']}")
                            print(f"   URL: {repo['github_url']}")
                            print(f"   Owner: {repo['owner']}")
                            print(f"   License: {repo['license_type']}")
                            print(f"   Registered: {repo['registered_at']}")
                            print(f"   IPFS: {repo['ipfs_metadata'][:20]}..." if repo['ipfs_metadata'] else "   IPFS: N/A")
                            print(f"   Active: {'✅' if repo['is_active'] else '❌'}")
                            print()
                    else:
                        print(f"❌ Error: {result['error']}")
                
                elif command == 'workflow-blockchain':
                    if len(parts) < 2:
                        print("❌ Usage: workflow-blockchain <url>")
                        continue
                    
                    print("🚀 Running complete blockchain protection workflow...")
                    result = agent.run_protection_workflow_blockchain(parts[1])
                    
                    if result.get('success'):
                        print(f"\n✅ Blockchain Workflow Complete!")
                        summary = result['summary']
                        print(f"📋 Repo ID: {summary['repo_id']}")
                        print(f"⛓️ Blockchain Confirmed: {summary['blockchain_confirmed']}")
                        print(f"🔒 Security Findings: {summary['security_findings']}")
                        print(f"⚠️ Violations Found: {summary['violations_found']}")
                        print(f"📄 DMCA Notices Filed: {summary['dmca_notices_filed']}")
                        print(f"🔗 Total Transactions: {summary['total_blockchain_transactions']}")
                        print(f"✅ Protection Active: {summary['protection_active']}")
                        
                        print(f"\n⛓️ Blockchain Transactions:")
                        for i, tx in enumerate(result['blockchain_transactions'], 1):
                            print(f"   {i}. {tx['type'].replace('_', ' ').title()}: {tx['tx_hash']}")
                    else:
                        print(f"❌ Error: {result.get('error', 'Unknown error')}")
                
                elif command == 'report-bounty':
                    if len(parts) < 4:
                        print("❌ Usage: report-bounty <infringing_url> <license_cid> <dmca_cid>")
                        continue
                    
                    print("💰 Reporting infringement for bounty...")
                    result = agent.report_infringement_with_bounty(parts[1], parts[2], parts[3])
                    
                    if result['success']:
                        print(f"\n✅ Infringement Reported!")
                        print(f"🔗 URL: {result['infringing_url']}")
                        print(f"⛓️ Add Link TX: {result['add_link_tx']}")
                        print(f"📄 DMCA TX: {result['dmca_tx']}")
                        print(f"💰 Bounty Earned: {result['bounty_earned']} {result['bounty_currency']}")
                    else:
                        print(f"❌ Error: {result['error']}")
                
                elif command == 'analyze':
                    if len(parts) < 3:
                        print("❌ Usage: analyze <url1> <url2>")
                        continue
                    
                    print("🔍 Analyzing repositories with blockchain verification...")
                    result = agent.analyze_repositories(parts[1], parts[2])
                    
                    if result['success']:
                        print(f"\n✅ Analysis Complete")
                        print(f"📊 Overall Similarity: {result['similarity_analysis']['overall_similarity']:.2%}")
                        print(f"🔗 {result['recommendation']}")
                        
                        if result['blockchain_matches']:
                            print(f"\n⛓️ Found {len(result['blockchain_matches'])} blockchain-registered repositories with similarities!")
                            for match in result['blockchain_matches']:
                                print(f"   Repo ID {match['repo_id']}: {match['similarity']:.2%} similar")
                    else:
                        print(f"❌ Error: {result['error']}")
                
                elif command == 'audit':
                    if len(parts) < 2:
                        print("❌ Usage: audit <url> [--extensive]")
                        continue
                    
                    extensive = '--extensive' in parts
                    mode = "EXTENSIVE (all commits)" if extensive else "standard"
                    print(f"🔒 Running {mode} security audit with blockchain evidence storage...")
                    
                    result = agent.comprehensive_audit(parts[1], include_all_commits=extensive)
                    
                    if result['success']:
                        print(f"\n✅ Audit Complete")
                        print(f"📁 Files scanned: {result['files_scanned']}")
                        print(f"📊 Commits scanned: {result.get('commits_scanned', 'N/A')}")
                        print(f"🚨 Total findings: {result['total_findings']}")
                        print(f"   Critical: {result['critical_findings']}")
                        print(f"   High: {result['high_findings']}")
                        print(f"   Medium: {result['medium_findings']}")
                        print(f"   Low: {result['low_findings']}")
                        
                        if result.get('report'):
                            print(f"\n📄 Blockchain Evidence Report:")
                            print(f"   IPFS: {result['report']['ipfs_url']}")
                            if result['report'].get('blockchain_pin'):
                                pin_info = result['report']['blockchain_pin']
                                print(f"   Blockchain TX: {pin_info.get('transaction_hash', 'N/A')}")
                    else:
                        print(f"❌ Error: {result['error']}")
                
                elif command == 'scan':
                    repo_id = int(parts[1]) if len(parts) > 1 else None
                    target = f"repository {repo_id}" if repo_id else "all blockchain registered repositories"
                    print(f"🔎 Scanning GitHub for violations of {target}...")
                    
                    result = agent.scan_github_for_violations(repo_id)
                    
                    if result['success']:
                        print(f"\n✅ Scan Complete")
                        print(f"📊 Repositories scanned: {result['repositories_scanned']}")
                        print(f"⚠️ Violations found: {result['violations_found']}")
                        print(f"📄 DMCA notices generated: {result['dmca_notices_generated']}")
                        print(f"⛓️ Blockchain backed: {result['blockchain_backed']}")
                        
                        for notice in result['dmca_notices']:
                            print(f"\n🚨 DMCA Notice #{notice['id']}:")
                            print(f"   Infringing URL: {notice['infringing_url']}")
                            print(f"   Similarity: {notice['similarity_score']:.2%}")
                            print(f"   IPFS: {notice['ipfs_url']}")
                            print(f"   DMCA TX: {notice['dmca_blockchain_tx']}")
                            print(f"   Violation TX: {notice['violation_blockchain_tx']}")
                    else:
                        print(f"❌ Error: {result['error']}")
                
                elif command == 'list':
                    if not agent.repositories:
                        print("📭 No repositories in local cache")
                        print("💡 Use 'query-repos' to see blockchain registered repositories")
                    else:
                        print(f"\n📚 Cached Repositories ({len(agent.repositories)}):")
                        print("-" * 60)
                        for repo_id, repo_data in agent.repositories.items():
                            print(f"ID: {repo_id}")
                            print(f"   URL: {repo_data['github_url']}")
                            print(f"   License: {repo_data['license_type']}")
                            print(f"   Registered: {repo_data['registered_at'][:10]}")
                            print(f"   Blockchain: {'✅' if repo_data.get('blockchain_confirmed') else '❌'}")
                            if repo_data.get('tx_hash'):
                                print(f"   TX: {repo_data['tx_hash'][:16]}...")
                            print()
                
                else:
                    print(f"❌ Unknown command: {command}")
                    print("💡 Type 'help' for available commands")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"❌ Error: {e}")
                print(f"❌ An error occurred: {e}")
                
    except Exception as e:
        logger.error(f"Failed to initialize blockchain agent: {e}")
        print(f"❌ Failed to initialize agent: {e}")
        print("\n💡 Common issues:")
        print("   1. Check your PRIVATE_KEY environment variable")
        print("   2. Ensure you have tFIL testnet tokens")
        print("   3. Verify Filecoin RPC connection")
        print("   4. Run 'setup' command for detailed guide")
        sys.exit(1)


if __name__ == "__main__":
    main()