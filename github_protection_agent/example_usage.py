#!/usr/bin/env python3
"""
Complete Example Usage Script for Filecoin GitHub Protection Agent
Demonstrates all features including blockchain integration
"""
import os
import sys
import time
import json
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from github_protection_agent.complete_filecoin_agent import CompleteFilecoinAgent
from github_protection_agent.setup_validator import SetupValidator


class ExampleUsageDemo:
    """Demonstrates complete usage of the Filecoin GitHub Protection Agent"""
    
    def __init__(self):
        self.config = {
            'USE_LOCAL_MODEL': os.getenv('USE_LOCAL_MODEL', 'false').lower() == 'true',
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN'),
            'PRIVATE_KEY': os.getenv('PRIVATE_KEY'),
            'FILECOIN_RPC_URL': os.getenv('FILECOIN_RPC_URL', 'https://rpc.ankr.com/filecoin_testnet'),
            'PINATA_API_KEY': os.getenv('PINATA_API_KEY'),
            'PINATA_API_SECRET': os.getenv('PINATA_API_SECRET'),
            'WEB3_STORAGE_TOKEN': os.getenv('WEB3_STORAGE_TOKEN')
        }
        
        self.agent = None
        
        # Example repositories for demonstration
        self.example_repos = [
            'https://github.com/octocat/Hello-World',
            'https://github.com/microsoft/vscode',
            'https://github.com/facebook/react'
        ]
    
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "="*80)
        print(f"🛡️  {title}")
        print("="*80)
    
    def print_step(self, step: str, description: str):
        """Print formatted step"""
        print(f"\n📋 Step {step}: {description}")
        print("-" * 50)
    
    def print_result(self, success: bool, message: str):
        """Print formatted result"""
        icon = "✅" if success else "❌"
        print(f"{icon} {message}")
    
    def wait_for_user(self, message: str = "Press Enter to continue..."):
        """Wait for user input"""
        input(f"\n💡 {message}")
    
    def initialize_agent(self) -> bool:
        """Initialize the Filecoin agent"""
        self.print_step("1", "Initializing Filecoin GitHub Protection Agent")
        
        try:
            self.agent = CompleteFilecoinAgent(self.config)
            self.print_result(True, "Agent initialized successfully")
            return True
        except Exception as e:
            self.print_result(False, f"Agent initialization failed: {e}")
            return False
    
    def validate_setup(self) -> bool:
        """Validate system setup"""
        self.print_step("2", "Validating System Setup")
        
        try:
            validator = SetupValidator()
            results = validator.run_full_validation()
            
            # Check for critical issues
            critical_issues = any([
                results['environment'].get('issues'),
                results['dependencies'].get('missing'),
                not results['network'].get('connected'),
                not results['wallet'].get('valid'),
                not results['ai'].get('available')
            ])
            
            if critical_issues:
                self.print_result(False, "Setup validation failed - please fix issues before continuing")
                return False
            else:
                self.print_result(True, "Setup validation passed")
                return True
                
        except Exception as e:
            self.print_result(False, f"Validation error: {e}")
            return False
    
    def demonstrate_blockchain_status(self):
        """Demonstrate blockchain status checking"""
        self.print_step("3", "Checking Blockchain Status")
        
        try:
            status = self.agent.get_complete_status()
            
            if status['success']:
                blockchain = status['system_status']['blockchain']
                ipfs = status['system_status']['ipfs']
                
                print(f"⛓️  Network: {blockchain['network']}")
                print(f"🔗 Account: {blockchain['account_address']}")
                print(f"💰 Balance: {blockchain['balance_tfil']:.6f} tFIL")
                print(f"📊 Registered Repos: {blockchain['total_registered_repos']}")
                
                ipfs_available = sum(1 for s in ipfs.values() if s.get('available', False))
                print(f"🌐 IPFS Services: {ipfs_available} available")
                
                self.print_result(True, "Blockchain status retrieved successfully")
            else:
                self.print_result(False, f"Status check failed: {status['error']}")
                
        except Exception as e:
            self.print_result(False, f"Status check error: {e}")
    
    def demonstrate_repository_registration(self):
        """Demonstrate repository registration"""
        self.print_step("4", "Repository Registration with Blockchain")
        
        # Use a safe example repository
        example_repo = self.example_repos[0]
        
        print(f"📝 Registering repository: {example_repo}")
        print("📄 License type: MIT")
        print("🌐 IPFS storage: Enabled")
        print("⛓️  Blockchain recording: Enabled")
        
        self.wait_for_user("This will register the repository on Filecoin. Continue?")
        
        try:
            result = self.agent.register_repository_complete(example_repo, "MIT")
            
            if result['success']:
                print(f"\n✅ Repository Registration Successful!")
                print(f"📋 Repository ID: {result['repo_id']}")
                print(f"⛓️  Transaction Hash: {result['blockchain']['tx_hash']}")
                print(f"📦 Block Number: {result['blockchain']['block_number']}")
                print(f"⛽ Gas Used: {result['blockchain']['gas_used']:,}")
                print(f"📄 License IPFS Hash: {result['license']['ipfs_hash']}")
                print(f"🌐 License URL: {result['license']['ipfs_url']}")
                
                # Store repo ID for later use
                self.registered_repo_id = result['repo_id']
                
                self.print_result(True, "Repository successfully registered on Filecoin blockchain")
                return True
            else:
                self.print_result(False, f"Registration failed: {result['error']}")
                return False
                
        except Exception as e:
            self.print_result(False, f"Registration error: {e}")
            return False
    
    def demonstrate_repository_analysis(self):
        """Demonstrate repository analysis and comparison"""
        self.print_step("5", "Repository Analysis and Comparison")
        
        repo1 = self.example_repos[0]
        repo2 = self.example_repos[1]
        
        print(f"🔍 Comparing repositories:")
        print(f"   Repository 1: {repo1}")
        print(f"   Repository 2: {repo2}")
        
        try:
            result = self.agent.analyze_and_compare_repos(repo1, repo2)
            
            if result['success']:
                comparison = result['comparison']
                similarity = comparison['similarity']['overall_similarity']
                
                print(f"\n📊 Analysis Results:")
                print(f"   Overall Similarity: {similarity:.2%}")
                print(f"   File Structure Similarity: {comparison['similarity'].get('file_structure_similarity', 0):.2%}")
                print(f"   Code Pattern Similarity: {comparison['similarity'].get('code_pattern_similarity', 0):.2%}")
                print(f"   Language Match: {'✅' if comparison['similarity'].get('language_match') else '❌'}")
                
                print(f"\n💡 Recommendation:")
                print(f"   {comparison['recommendation']}")
                
                if comparison['blockchain_matches']:
                    print(f"\n⛓️  Blockchain Matches:")
                    for match in comparison['blockchain_matches']:
                        print(f"   • Repo ID {match['repo_id']}: {match['url']}")
                
                print(f"\n📋 Suggested Actions:")
                for action in result['next_actions']:
                    print(f"   • {action}")
                
                self.print_result(True, "Repository analysis completed")
            else:
                self.print_result(False, f"Analysis failed: {result['error']}")
                
        except Exception as e:
            self.print_result(False, f"Analysis error: {e}")
    
    def demonstrate_security_audit(self):
        """Demonstrate comprehensive security audit"""
        self.print_step("6", "Comprehensive Security Audit")
        
        example_repo = self.example_repos[0]
        
        print(f"🔒 Running security audit on: {example_repo}")
        print("🕵️ Scanning for secrets and vulnerabilities")
        print("📊 Including commit history analysis")
        print("📄 Generating blockchain-backed evidence report")
        
        try:
            result = self.agent.comprehensive_security_audit(example_repo, include_commits=True)
            
            if result['success']:
                audit = result['audit_results']
                
                print(f"\n🔍 Security Audit Results:")
                print(f"   Files Scanned: {audit['files_scanned']}")
                print(f"   Commits Scanned: {audit.get('commits_scanned', 'N/A')}")
                print(f"   Total Findings: {audit['total_findings']}")
                print(f"   🔴 Critical: {audit['critical_findings']}")
                print(f"   🟠 High: {audit['high_findings']}")
                print(f"   🟡 Medium: {audit['medium_findings']}")
                print(f"   🟢 Low: {audit['low_findings']}")
                
                if result.get('blockchain_evidence'):
                    evidence = result['blockchain_evidence']
                    print(f"\n📄 Evidence Report:")
                    print(f"   IPFS Hash: {evidence['ipfs_hash']}")
                    print(f"   Report URL: {evidence['ipfs_url']}")
                    print(f"   Blockchain Pinned: {'✅' if evidence['blockchain_pinned'] else '❌'}")
                
                # Show sample findings
                if audit.get('findings'):
                    print(f"\n🚨 Sample Findings:")
                    for i, finding in enumerate(audit['findings'][:3], 1):
                        print(f"   {i}. {finding.get('pattern_name', 'Unknown')}")
                        print(f"      Severity: {finding.get('severity', 'Unknown')}")
                        print(f"      File: {finding.get('file_path', 'N/A')}")
                
                self.print_result(True, "Security audit completed with blockchain evidence")
            else:
                self.print_result(False, f"Audit failed: {result['error']}")
                
        except Exception as e:
            self.print_result(False, f"Audit error: {e}")
    
    def demonstrate_violation_scanning(self):
        """Demonstrate violation scanning and DMCA generation"""
        self.print_step("7", "Violation Scanning and DMCA Generation")
        
        if not hasattr(self, 'registered_repo_id'):
            print("⚠️ No registered repository found. Skipping violation scan.")
            return
        
        print(f"🔎 Scanning for violations of registered repository ID: {self.registered_repo_id}")
        print("📄 Automatically generating DMCA notices for violations")
        print("⛓️ Filing notices on blockchain")
        
        try:
            result = self.agent.scan_and_report_violations(self.registered_repo_id)
            
            if result['success']:
                scan = result['scan_results']
                
                print(f"\n📊 Violation Scan Results:")
                print(f"   Repositories Scanned: {scan['repositories_scanned']}")
                print(f"   Violations Found: {scan['violations_found']}")
                print(f"   DMCA Notices Filed: {scan['dmca_notices_filed']}")
                
                if scan['violations_found'] > 0:
                    print(f"\n🚨 Detected Violations:")
                    for i, violation in enumerate(scan['violations'][:3], 1):
                        print(f"   {i}. {violation['infringing_url']}")
                        print(f"      Similarity: {violation['similarity_score']:.2%}")
                        if violation.get('blockchain_filed'):
                            print(f"      DMCA Filed: ✅ (Notice ID: {violation.get('dmca_notice_id')})")
                
                if scan['dmca_notices']:
                    print(f"\n📄 DMCA Notices Generated:")
                    for notice in scan['dmca_notices'][:2]:
                        print(f"   • Notice ID: {notice['dmca_id']}")
                        print(f"     Target: {notice['infringing_url']}")
                        print(f"     IPFS: {notice['ipfs_url']}")
                        print(f"     Blockchain TXs: {notice['blockchain_transactions']}")
                
                self.print_result(True, "Violation scanning completed")
            else:
                self.print_result(False, f"Scan failed: {result['error']}")
                
        except Exception as e:
            self.print_result(False, f"Scan error: {e}")
    
    def demonstrate_bounty_system(self):
        """Demonstrate bounty system for reporting infringements"""
        self.print_step("8", "Community Bounty System")
        
        print("💰 Demonstrating infringement bounty reporting")
        print("🔍 Community members can earn rewards for reporting violations")
        print("⛓️ Automated verification and payment system")
        
        # Example infringement URL (fictional)
        example_infringement = "https://github.com/example/potential-infringement"
        
        print(f"\n📋 Example bounty claim:")
        print(f"   Infringing Repository: {example_infringement}")
        print(f"   Original Repository ID: {getattr(self, 'registered_repo_id', 1)}")
        
        try:
            # This is a demonstration - would normally require real infringement
            print("\n💡 Note: This is a demonstration of the bounty system interface.")
            print("   In practice, this would:")
            print("   • Analyze similarity between repositories")
            print("   • Generate DMCA notice if similarity > 70%")
            print("   • File notice on blockchain")
            print("   • Award bounty to reporter")
            print("   • Typical bounty: 1-2 tFIL depending on similarity score")
            
            self.print_result(True, "Bounty system demonstration completed")
            
        except Exception as e:
            self.print_result(False, f"Bounty demo error: {e}")
    
    def demonstrate_full_workflow(self):
        """Demonstrate complete protection workflow"""
        self.print_step("9", "Complete Protection Workflow")
        
        # Use a different example repository
        workflow_repo = self.example_repos[2]
        
        print(f"🚀 Running complete protection workflow for: {workflow_repo}")
        print("📋 This includes:")
        print("   1. Repository registration with license generation")
        print("   2. Comprehensive security audit")
        print("   3. Violation detection and DMCA filing")
        print("   4. Blockchain evidence storage")
        print("   5. IPFS document pinning")
        
        self.wait_for_user("This will perform all protection steps. Continue?")
        
        try:
            result = self.agent.run_full_protection_workflow(workflow_repo)
            
            if result['success']:
                summary = result['workflow_results']['summary']
                
                print(f"\n✅ Complete Protection Workflow Successful!")
                print(f"📋 Repository ID: {summary['repo_id']}")
                print(f"⛓️ Blockchain Confirmed: {'✅' if summary['blockchain_confirmed'] else '❌'}")
                print(f"📄 License Generated: {'✅' if summary['license_generated'] else '❌'}")
                print(f"🌐 IPFS Stored: {'✅' if summary['ipfs_stored'] else '❌'}")
                print(f"🔒 Security Findings: {summary['security_findings']}")
                print(f"⚠️ Violations Found: {summary['violations_found']}")
                print(f"📄 DMCA Notices Filed: {summary['dmca_notices_filed']}")
                print(f"🛡️ Protection Level: {summary['protection_level'].upper()}")
                print(f"✅ Workflow Completed: {'✅' if summary['workflow_completed'] else '❌'}")
                
                self.print_result(True, "Complete protection workflow finished successfully")
            else:
                self.print_result(False, f"Workflow failed: {result['error']}")
                
        except Exception as e:
            self.print_result(False, f"Workflow error: {e}")
    
    def demonstrate_blockchain_queries(self):
        """Demonstrate blockchain data queries"""
        self.print_step("10", "Blockchain Data Queries")
        
        print("📊 Querying registered repositories from blockchain")
        
        try:
            result = self.agent.query_blockchain_data('repositories', limit=5)
            
            if result['success']:
                print(f"\n📚 Blockchain Repository Data:")
                print(f"   Total Repositories: {result['total_count']}")
                print(f"   Showing: {result['returned_count']} repositories")
                
                for i, repo in enumerate(result['data'], 1):
                    print(f"\n   {i}. Repository ID: {repo['id']}")
                    print(f"      URL: {repo['github_url']}")
                    print(f"      Owner: {repo['owner']}")
                    print(f"      License: {repo['license_type']}")
                    print(f"      Active: {'✅' if repo['is_active'] else '❌'}")
                
                self.print_result(True, "Blockchain query completed")
            else:
                self.print_result(False, f"Query failed: {result['error']}")
                
        except Exception as e:
            self.print_result(False, f"Query error: {e}")
    
    def run_complete_demo(self):
        """Run the complete demonstration"""
        self.print_header("COMPLETE FILECOIN GITHUB PROTECTION AGENT DEMONSTRATION")
        
        print("🎯 This demonstration will showcase all features of the agent:")
        print("   • Blockchain integration with Filecoin smart contracts")
        print("   • IPFS decentralized storage")
        print("   • AI-powered code analysis")
        print("   • Automated license and DMCA generation")
        print("   • Community bounty system")
        print("   • Comprehensive security auditing")
        
        self.wait_for_user("Ready to begin demonstration?")
        
        # Run demonstration steps
        steps = [
            self.initialize_agent,
            self.validate_setup,
            self.demonstrate_blockchain_status,
            self.demonstrate_repository_registration,
            self.demonstrate_repository_analysis,
            self.demonstrate_security_audit,
            self.demonstrate_violation_scanning,
            self.demonstrate_bounty_system,
            self.demonstrate_full_workflow,
            self.demonstrate_blockchain_queries
        ]
        
        successful_steps = 0
        
        for step in steps:
            try:
                if callable(step):
                    if step() is not False:  # Consider None as success
                        successful_steps += 1
                else:
                    step()
                    successful_steps += 1
                
                time.sleep(1)  # Brief pause between steps
                
            except KeyboardInterrupt:
                print("\n\n🛑 Demonstration interrupted by user")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error in demonstration: {e}")
                continue
        
        # Final summary
        self.print_header("DEMONSTRATION SUMMARY")
        
        print(f"📊 Steps Completed: {successful_steps}/{len(steps)}")
        
        if successful_steps == len(steps):
            print("🎉 Complete demonstration finished successfully!")
            print("\n🚀 The Filecoin GitHub Protection Agent is fully operational and ready for use.")
        else:
            print(f"⚠️ Demonstration completed with {len(steps) - successful_steps} issues.")
            print("💡 Check configuration and network connectivity for any failed steps.")
        
        print("\n📚 Next Steps:")
        print("   1. Register your repositories: register-blockchain <url>")
        print("   2. Monitor for violations: scan")
        print("   3. Run security audits: audit <url> --extensive")
        print("   4. Check system status: status")
        
        print("\n🔗 Resources:")
        print("   • Filecoin Faucet: https://faucet.calibration.fildev.network/")
        print("   • Agent Documentation: README.md")
        print("   • Support: legal@kreonlabs.com")


def main():
    """Main demonstration function"""
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("Filecoin GitHub Protection Agent - Complete Example Usage")
        print("")
        print("This script demonstrates all features of the agent including:")
        print("  • Blockchain integration")
        print("  • IPFS storage")
        print("  • AI analysis")
        print("  • Security auditing")
        print("  • DMCA generation")
        print("  • Bounty system")
        print("")
        print("Usage: python example_usage.py")
        print("")
        print("Make sure to set up your .env file with required credentials first.")
        return
    
    # Check if required environment variables are set
    required_vars = ['PRIVATE_KEY']
    if not os.getenv('USE_LOCAL_MODEL', '').lower() == 'true':
        required_vars.append('OPENAI_API_KEY')
    
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   • {var}")
        print("\n💡 Please set these in your .env file before running the demo")
        print("   See .env.example for reference")
        return
    
    # Run the demonstration
    demo = ExampleUsageDemo()
    demo.run_complete_demo()


if __name__ == "__main__":
    main()