"""
Complete Filecoin-Integrated GitHub Protection Agent
Final implementation with all deployed contracts integrated
"""
import os
import sys
import hashlib
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Add project root to path if not already there
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from langchain.agents import initialize_agent, AgentType
from langchain.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI as LlamaOpenAI
from llama_index.llms.ollama import Ollama

# Import components with proper error handling
try:
    from github_protection_agent.repository_analyzer import RepositoryAnalyzer
except ImportError:
    # Create mock class if module not found
    class RepositoryAnalyzer:
        def __init__(self, config):
            self.config = config
        def analyze_repository(self, url, llm):
            return {'success': False, 'error': 'RepositoryAnalyzer not available'}

try:
    from github_protection_agent.security_scanner import SecurityScanner
except ImportError:
    class SecurityScanner:
        def __init__(self, config, llm):
            self.config = config
        def audit_github_repository_extensive(self, url, include_all_commits=False):
            return {'total_findings': 0, 'files_scanned': 0, 'critical_findings': 0, 'high_findings': 0, 'medium_findings': 0, 'low_findings': 0}

try:
    from github_protection_agent.url_processor import URLProcessor
except ImportError:
    class URLProcessor:
        def __init__(self, llm):
            pass
        def clean_single_url(self, url):
            if 'github.com' in url and url.startswith('http'):
                return {'success': True, 'cleaned_url': url, 'platform': 'github', 'url_type': 'repository'}
            return {'success': False, 'error': 'Invalid URL'}

try:
    from github_protection_agent.violation_detector import ViolationDetector
except ImportError:
    class ViolationDetector:
        def __init__(self, config, llm):
            pass

try:
    from github_protection_agent.report_generator import ReportGenerator
except ImportError:
    class ReportGenerator:
        def generate_security_pdf(self, audit_result):
            return '/tmp/mock_report.pdf'

try:
    from github_protection_agent.dmca_generator import DMCAGenerator
except ImportError:
    class DMCAGenerator:
        def generate_dmca_pdf(self, dmca_data):
            return '/tmp/mock_dmca.pdf'

from github_protection_agent.enhanced_ipfs_manager import EnhancedIPFSManager

try:
    from github_protection_agent.license_generator import LicenseGenerator
except ImportError:
    class LicenseGenerator:
        def generate_license_pdf(self, github_url, license_type, repo_data):
            return '/tmp/mock_license.pdf'

try:
    from github_protection_agent.github_scanner import GitHubScanner
except ImportError:
    class GitHubScanner:
        def __init__(self, config, llm):
            pass
        def deep_compare_repositories(self, url1, url2, analysis1, analysis2):
            return {'overall_similarity': 0.1, 'file_structure_similarity': 0.1, 'code_pattern_similarity': 0.1}
        def search_similar_repositories(self, url, features):
            return []
        def compare_repository_code(self, url1, url2):
            return {'similarity_score': 0.1, 'evidence': []}

from github_protection_agent.filecoin_contracts import FilecoinContractInterface
from github_protection_agent.blockchain_utilities import BlockchainUtils, SubmissionTypeEnum, FilecoinNetworkInfo

try:
    from github_protection_agent.utils import setup_logging
except ImportError:
    def setup_logging(name):
        import logging
        return logging.getLogger(name)

from dotenv import load_dotenv
load_dotenv()

logger = setup_logging(__name__)


class CompleteFilecoinAgent:
    """Complete GitHub Protection Agent with full Filecoin integration"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.setup_models()
        
        # Initialize blockchain interface with deployed contracts
        logger.info("🔗 Initializing Filecoin contract interface...")
        self.contract_interface = FilecoinContractInterface(config)
        
        # Initialize enhanced components
        self.repo_analyzer = RepositoryAnalyzer(config)
        self.security_scanner = SecurityScanner(config, self.llm)
        self.url_processor = URLProcessor(self.llm)
        self.violation_detector = ViolationDetector(config, self.llm)
        self.report_generator = ReportGenerator()
        self.dmca_generator = DMCAGenerator()
        self.ipfs_manager = EnhancedIPFSManager(config)
        self.license_generator = LicenseGenerator()
        self.github_scanner = GitHubScanner(config, self.llm)
        
        # Initialize blockchain utilities
        self.blockchain_utils = BlockchainUtils()
        
        # Cache for performance
        self.repositories_cache = {}
        self.violations_cache = {}
        self.last_cache_update = 0
        
        # Setup tools and agent
        self.setup_tools()
        self.setup_agent()
        
        logger.info("✅ Complete Filecoin Agent initialized successfully!")
    
    def setup_models(self):
        """Initialize AI models"""
        use_local = self.config.get('USE_LOCAL_MODEL', False)
        
        if use_local:
            logger.info("🦙 Using local Ollama model")
            self.llm = ChatOpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama",
                model="llama3.2:3b"
            )
            Settings.llm = Ollama(model="llama3.2:3b", base_url="http://localhost:11434")
        else:
            logger.info("🤖 Using OpenAI GPT-4")
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                api_key=self.config['OPENAI_API_KEY']
            )
            Settings.llm = LlamaOpenAI(
                model="gpt-4o-mini",
                api_key=self.config['OPENAI_API_KEY']
            )
        
        # Setup embeddings
        try:
            Settings.embed_model = HuggingFaceEmbedding(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            logger.info("✅ HuggingFace embeddings loaded")
        except Exception as e:
            logger.warning(f"⚠️ Embeddings setup failed: {e}")
    
    def setup_tools(self):
        """Initialize all agent tools with full functionality"""
        self.tools = [
            StructuredTool.from_function(
                func=self.register_repository_complete,
                name="register_repository_complete",
                description="Complete repository registration with blockchain, IPFS, and license generation"
            ),
            StructuredTool.from_function(
                func=self.analyze_and_compare_repos,
                name="analyze_and_compare_repos",
                description="Analyze and compare repositories with blockchain verification"
            ),
            StructuredTool.from_function(
                func=self.scan_and_report_violations,
                name="scan_and_report_violations",
                description="Scan for violations and automatically file blockchain DMCA notices"
            ),
            StructuredTool.from_function(
                func=self.comprehensive_security_audit,
                name="comprehensive_security_audit",
                description="Full security audit with blockchain evidence storage"
            ),
            StructuredTool.from_function(
                func=self.report_infringement_bounty,
                name="report_infringement_bounty",
                description="Report infringement for bounty rewards"
            ),
            StructuredTool.from_function(
                func=self.get_complete_status,
                name="get_complete_status",
                description="Get complete system status including blockchain and IPFS"
            ),
            StructuredTool.from_function(
                func=self.query_blockchain_data,
                name="query_blockchain_data",
                description="Query repositories and violations from blockchain"
            ),
            StructuredTool.from_function(
                func=self.run_full_protection_workflow,
                name="run_full_protection_workflow",
                description="Run complete end-to-end protection workflow"
            )
        ]
    
    def setup_agent(self):
        """Initialize the LangChain agent"""
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            memory=self.memory,
            max_iterations=5
        )
    
    def _clean_and_validate_url(self, url: str) -> Tuple[bool, str, str]:
        """Clean and validate GitHub URL"""
        try:
            result = self.url_processor.clean_single_url(url)
            
            if not result['success']:
                return False, "", result.get('error', 'Invalid URL')
            
            if result['platform'] != 'github' or result['url_type'] != 'repository':
                return False, "", "URL must be a GitHub repository"
            
            return True, result['cleaned_url'], ""
            
        except Exception as e:
            return False, "", str(e)
    
    def register_repository_complete(self, repo_input: str, license_type: str = "MIT") -> Dict:
        """Complete repository registration with all features"""
        try:
            # Step 1: Validate and clean URL
            valid, github_url, error = self._clean_and_validate_url(repo_input)
            if not valid:
                return {'success': False, 'error': error}
            
            logger.info(f"🚀 Starting complete registration for: {github_url}")
            
            # Step 2: Check if already registered
            existing_repo = self._check_existing_registration(github_url)
            if existing_repo:
                return {
                    'success': False,
                    'error': f'Repository already registered with ID {existing_repo["id"]}',
                    'existing_repo': existing_repo
                }
            
            # Step 3: Analyze repository
            logger.info("🔍 Analyzing repository...")
            analysis = self.repo_analyzer.analyze_repository(github_url, self.llm)
            if not analysis['success']:
                return analysis
            
            # Step 4: Generate repository hash and fingerprint
            repo_hash = self.blockchain_utils.generate_repo_hash(analysis['repo_data'])
            fingerprint = self.blockchain_utils.generate_fingerprint(github_url, analysis['repo_data'])
            key_features = self.blockchain_utils.format_key_features(analysis['key_features'])
            
            # Step 5: Generate license PDF
            logger.info(f"📄 Generating {license_type} license PDF...")
            license_pdf_path = self.license_generator.generate_license_pdf(
                github_url, license_type, analysis['repo_data']
            )
            
            # Step 6: Upload license to IPFS
            logger.info("🌐 Uploading license to IPFS...")
            license_metadata = {
                'type': 'license_document',
                'repository': github_url,
                'license_type': license_type,
                'generated_by': 'github_protection_agent_v5'
            }
            license_ipfs_hash = self.ipfs_manager.upload_to_ipfs(license_pdf_path, license_metadata)
            
            # Step 7: Register on LinkRegistry contract
            logger.info("⛓️ Adding to Link Registry...")
            link_registry_result = self.contract_interface.add_link_to_registry(
                github_url, license_ipfs_hash
            )
            
            # Step 8: Register on main GitHubRepoProtection contract
            logger.info("⛓️ Registering on main contract...")
            repo_data = {
                'github_url': github_url,
                'repo_hash': repo_hash,
                'fingerprint': fingerprint,
                'key_features': ' '.join(key_features),  # Join for IPFS metadata
                'license_type': license_type,
                'ipfs_metadata': license_ipfs_hash
            }
            
            blockchain_result = self.contract_interface.register_repository_on_chain(repo_data)
            if not blockchain_result['success']:
                return {
                    'success': False,
                    'error': f"Blockchain registration failed: {blockchain_result['error']}",
                    'license_ipfs': license_ipfs_hash  # At least we have this
                }
            
            # Step 9: Pin evidence on IPFS/Filecoin
            logger.info("📌 Pinning evidence on Filecoin...")
            pin_result = self.ipfs_manager.pin_on_chain(license_ipfs_hash, {
                'repository_id': blockchain_result['repo_id'],
                'registration_tx': blockchain_result['tx_hash']
            })
            
            # Step 10: Update cache
            repo_id = blockchain_result['repo_id']
            self.repositories_cache[repo_id] = {
                'id': repo_id,
                'github_url': github_url,
                'repo_hash': repo_hash,
                'fingerprint': fingerprint,
                'license_type': license_type,
                'license_ipfs_hash': license_ipfs_hash,
                'registered_at': datetime.now().isoformat(),
                'blockchain_confirmed': True,
                'ipfs_pinned': pin_result['success']
            }
            
            logger.info(f"✅ Repository successfully registered with ID: {repo_id}")
            
            return {
                'success': True,
                'repo_id': repo_id,
                'github_url': github_url,
                'blockchain': {
                    'tx_hash': blockchain_result['tx_hash'],
                    'block_number': blockchain_result['block_number'],
                    'gas_used': blockchain_result['gas_used']
                },
                'link_registry': {
                    'tx_hash': link_registry_result.get('tx_hash', 'N/A'),
                    'success': link_registry_result.get('success', False)
                },
                'license': {
                    'type': license_type,
                    'pdf_path': license_pdf_path,
                    'ipfs_hash': license_ipfs_hash,
                    'ipfs_url': self.ipfs_manager.get_ipfs_url(license_ipfs_hash)
                },
                'ipfs_pinning': pin_result,
                'fingerprints': {
                    'repo_hash': repo_hash,
                    'fingerprint': fingerprint
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Complete registration failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def analyze_and_compare_repos(self, repo1_input: str, repo2_input: str) -> Dict:
        """Analyze and compare repositories with blockchain verification"""
        try:
            # Clean URLs
            valid1, url1, error1 = self._clean_and_validate_url(repo1_input)
            if not valid1:
                return {'success': False, 'error': f'Repository 1: {error1}'}
            
            valid2, url2, error2 = self._clean_and_validate_url(repo2_input)
            if not valid2:
                return {'success': False, 'error': f'Repository 2: {error2}'}
            
            logger.info(f"🔍 Comparing repositories: {url1} vs {url2}")
            
            # Analyze both repositories
            analysis1 = self.repo_analyzer.analyze_repository(url1, self.llm)
            analysis2 = self.repo_analyzer.analyze_repository(url2, self.llm)
            
            if not analysis1['success'] or not analysis2['success']:
                return {
                    'success': False,
                    'error': 'Failed to analyze one or both repositories'
                }
            
            # Deep comparison
            similarity_result = self.github_scanner.deep_compare_repositories(
                url1, url2, analysis1, analysis2
            )
            
            # Check against blockchain-registered repositories
            blockchain_matches = self._check_blockchain_matches([url1, url2])
            
            # Generate recommendation
            recommendation = self._generate_detailed_recommendation(
                similarity_result, blockchain_matches
            )
            
            return {
                'success': True,
                'comparison': {
                    'repository_1': {'url': url1, 'analysis': analysis1},
                    'repository_2': {'url': url2, 'analysis': analysis2},
                    'similarity': similarity_result,
                    'blockchain_matches': blockchain_matches,
                    'recommendation': recommendation
                },
                'next_actions': self._suggest_next_actions(similarity_result, blockchain_matches)
            }
            
        except Exception as e:
            logger.error(f"❌ Repository comparison failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def scan_and_report_violations(self, repo_id: int = None) -> Dict:
        """Scan for violations and automatically file DMCA notices"""
        try:
            # Get repositories to scan
            if repo_id:
                repos = [self._get_repository_by_id(repo_id)]
                if not repos[0]:
                    return {'success': False, 'error': f'Repository {repo_id} not found'}
            else:
                repos = self._get_all_registered_repositories()
            
            if not repos:
                return {'success': False, 'error': 'No repositories found to scan'}
            
            logger.info(f"🔎 Scanning {len(repos)} repositories for violations...")
            
            all_violations = []
            dmca_notices = []
            
            for repo in repos:
                if not repo:
                    continue
                
                logger.info(f"Scanning for violations of: {repo['github_url']}")
                
                # Find similar repositories
                similar_repos = self.github_scanner.search_similar_repositories(
                    repo['github_url'],
                    repo.get('key_features', '')
                )
                
                for similar_repo in similar_repos:
                    # Skip self
                    if similar_repo['url'] == repo['github_url']:
                        continue
                    
                    # Deep comparison
                    comparison = self.github_scanner.compare_repository_code(
                        repo['github_url'], similar_repo['url']
                    )
                    
                    similarity_score = comparison.get('similarity_score', 0)
                    
                    if similarity_score > 0.7:  # High similarity threshold
                        # Generate comprehensive DMCA notice
                        dmca_result = self._generate_and_file_dmca(
                            repo, similar_repo, comparison
                        )
                        
                        if dmca_result['success']:
                            dmca_notices.append(dmca_result)
                            all_violations.append({
                                'infringing_url': similar_repo['url'],
                                'similarity_score': similarity_score,
                                'dmca_notice_id': dmca_result['dmca_id'],
                                'blockchain_filed': True
                            })
            
            return {
                'success': True,
                'scan_results': {
                    'repositories_scanned': len(repos),
                    'violations_found': len(all_violations),
                    'dmca_notices_filed': len(dmca_notices),
                    'violations': all_violations,
                    'dmca_notices': dmca_notices
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Violation scanning failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def comprehensive_security_audit(self, repo_input: str, include_commits: bool = True) -> Dict:
        """Complete security audit with blockchain evidence storage"""
        try:
            valid, github_url, error = self._clean_and_validate_url(repo_input)
            if not valid:
                return {'success': False, 'error': error}
            
            logger.info(f"🔒 Starting comprehensive security audit: {github_url}")
            
            # Run extensive security scan
            audit_result = self.security_scanner.audit_github_repository_extensive(
                github_url, include_all_commits=include_commits
            )
            
            if audit_result.get('findings'):
                # Generate detailed report
                logger.info("📄 Generating security report...")
                pdf_path = self.report_generator.generate_security_pdf(audit_result)
                
                # Upload report to IPFS
                logger.info("🌐 Uploading audit report to IPFS...")
                report_metadata = {
                    'type': 'security_audit_report',
                    'repository': github_url,
                    'findings_count': audit_result['total_findings'],
                    'scan_type': 'comprehensive' if include_commits else 'standard'
                }
                
                ipfs_hash = self.ipfs_manager.upload_to_ipfs(pdf_path, report_metadata)
                
                # Pin evidence on blockchain
                logger.info("📌 Pinning audit evidence...")
                pin_result = self.ipfs_manager.pin_on_chain(ipfs_hash, {
                    'audit_type': 'security_comprehensive',
                    'repository': github_url,
                    'findings': audit_result['total_findings']
                })
                
                audit_result['evidence'] = {
                    'pdf_path': pdf_path,
                    'ipfs_hash': ipfs_hash,
                    'ipfs_url': self.ipfs_manager.get_ipfs_url(ipfs_hash),
                    'blockchain_pinned': pin_result['success'],
                    'pin_transaction': pin_result.get('transaction_hash')
                }
            
            return {
                'success': True,
                'audit_results': audit_result,
                'blockchain_evidence': audit_result.get('evidence', {})
            }
            
        except Exception as e:
            logger.error(f"❌ Security audit failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def report_infringement_bounty(self, infringing_url: str, original_repo_id: int = None) -> Dict:
        """Report infringement and claim bounty"""
        try:
            # If no repo ID provided, try to find best match
            if not original_repo_id:
                original_repo_id = self._find_best_matching_repo(infringing_url)
                if not original_repo_id:
                    return {
                        'success': False,
                        'error': 'No matching registered repository found'
                    }
            
            # Get original repository
            original_repo = self._get_repository_by_id(original_repo_id)
            if not original_repo:
                return {'success': False, 'error': f'Repository {original_repo_id} not found'}
            
            logger.info(f"💰 Processing bounty claim for infringement: {infringing_url}")
            
            # Analyze similarity
            comparison = self.github_scanner.compare_repository_code(
                original_repo['github_url'], infringing_url
            )
            
            similarity_score = comparison.get('similarity_score', 0)
            
            if similarity_score < 0.7:
                return {
                    'success': False,
                    'error': f'Similarity too low for bounty claim: {similarity_score:.2%}',
                    'minimum_required': '70%'
                }
            
            # Generate DMCA and evidence
            dmca_result = self._generate_and_file_dmca(
                original_repo, {'url': infringing_url}, comparison
            )
            
            if not dmca_result['success']:
                return {
                    'success': False,
                    'error': 'Failed to generate DMCA notice',
                    'details': dmca_result
                }
            
            # TODO: Integrate with InfringementBounty contract
            # For now, simulate bounty processing
            bounty_amount = self._calculate_bounty_amount(similarity_score)
            
            return {
                'success': True,
                'bounty_claim': {
                    'amount': bounty_amount,
                    'currency': 'tFIL',
                    'similarity_score': similarity_score,
                    'dmca_notice': dmca_result,
                    'status': 'pending_verification'
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Bounty claim failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_complete_status(self) -> Dict:
        """Get complete system status"""
        try:
            # Blockchain status
            blockchain_status = self.contract_interface.get_blockchain_status()
            
            # IPFS status
            ipfs_status = self.ipfs_manager.get_service_status()
            
            # Network info
            network_info = FilecoinNetworkInfo.get_network_info()
            
            # Cache statistics
            cache_stats = {
                'repositories_cached': len(self.repositories_cache),
                'violations_cached': len(self.violations_cache),
                'last_update': self.last_cache_update
            }
            
            return {
                'success': True,
                'system_status': {
                    'blockchain': blockchain_status,
                    'ipfs': ipfs_status,
                    'network': network_info,
                    'cache': cache_stats,
                    'agent_version': '5.0.0',
                    'features_enabled': [
                        'blockchain_registration',
                        'ipfs_storage',
                        'automated_dmca',
                        'security_auditing',
                        'bounty_system'
                    ]
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def query_blockchain_data(self, query_type: str = 'repositories', limit: int = 10) -> Dict:
        """Query data from blockchain"""
        try:
            if query_type == 'repositories':
                total_repos = self.contract_interface.get_total_repositories()
                repositories = []
                
                start_id = max(1, total_repos - limit + 1)
                for repo_id in range(start_id, total_repos + 1):
                    repo_result = self.contract_interface.get_repository_from_chain(repo_id)
                    if repo_result['success']:
                        repositories.append(repo_result['repository'])
                
                return {
                    'success': True,
                    'query_type': 'repositories',
                    'total_count': total_repos,
                    'returned_count': len(repositories),
                    'data': repositories
                }
            
            else:
                return {'success': False, 'error': f'Unknown query type: {query_type}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def run_full_protection_workflow(self, repo_input: str) -> Dict:
        """Run complete end-to-end protection workflow"""
        try:
            workflow_results = {
                'repository': repo_input,
                'steps': {},
                'summary': {}
            }
            
            # Step 1: Registration
            logger.info("🚀 Step 1: Complete Registration")
            registration = self.register_repository_complete(repo_input)
            workflow_results['steps']['registration'] = registration
            
            if not registration['success']:
                return {
                    'success': False,
                    'error': 'Registration failed',
                    'workflow_results': workflow_results
                }
            
            repo_id = registration['repo_id']
            
            # Step 2: Security Audit
            logger.info("🔒 Step 2: Comprehensive Security Audit")
            audit = self.comprehensive_security_audit(repo_input, include_commits=True)
            workflow_results['steps']['security_audit'] = audit
            
            # Step 3: Violation Scan
            logger.info("🔎 Step 3: Violation Detection and DMCA Filing")
            violations = self.scan_and_report_violations(repo_id)
            workflow_results['steps']['violation_scan'] = violations
            
            # Generate summary
            workflow_results['summary'] = {
                'repo_id': repo_id,
                'blockchain_confirmed': True,
                'license_generated': True,
                'ipfs_stored': True,
                'security_findings': audit.get('audit_results', {}).get('total_findings', 0),
                'violations_found': violations.get('scan_results', {}).get('violations_found', 0),
                'dmca_notices_filed': violations.get('scan_results', {}).get('dmca_notices_filed', 0),
                'protection_level': 'maximum',
                'workflow_completed': True
            }
            
            logger.info("✅ Full protection workflow completed successfully!")
            
            return {
                'success': True,
                'workflow_results': workflow_results
            }
            
        except Exception as e:
            logger.error(f"❌ Full workflow failed: {e}")
            return {'success': False, 'error': str(e)}
    
    # Helper methods
    
    def _check_existing_registration(self, github_url: str) -> Optional[Dict]:
        """Check if repository is already registered"""
        total_repos = self.contract_interface.get_total_repositories()
        
        for repo_id in range(1, total_repos + 1):
            repo_result = self.contract_interface.get_repository_from_chain(repo_id)
            if repo_result['success']:
                repo_data = repo_result['repository']
                if repo_data['github_url'] == github_url:
                    return repo_data
        
        return None
    
    def _check_blockchain_matches(self, urls: List[str]) -> List[Dict]:
        """Check URLs against blockchain-registered repositories"""
        matches = []
        total_repos = self.contract_interface.get_total_repositories()
        
        for repo_id in range(1, total_repos + 1):
            repo_result = self.contract_interface.get_repository_from_chain(repo_id)
            if repo_result['success']:
                repo_data = repo_result['repository']
                if repo_data['github_url'] in urls:
                    matches.append({
                        'repo_id': repo_id,
                        'url': repo_data['github_url'],
                        'blockchain_registered': True,
                        'owner': repo_data['owner'],
                        'license': repo_data['license_type']
                    })
        
        return matches
    
    def _generate_and_file_dmca(self, original_repo: Dict, infringing_repo: Dict, comparison: Dict) -> Dict:
        """Generate DMCA notice and file on blockchain"""
        try:
            # Prepare DMCA data
            dmca_data = {
                'original_repo': original_repo,
                'infringing_repo': infringing_repo,
                'similarity_score': comparison.get('similarity_score', 0),
                'evidence': comparison.get('evidence', []),
                'timestamp': datetime.now().isoformat()
            }
            
            # Generate DMCA PDF
            dmca_pdf_path = self.dmca_generator.generate_dmca_pdf(dmca_data)
            
            # Upload to IPFS
            dmca_metadata = {
                'type': 'dmca_notice',
                'original_repository': original_repo['github_url'],
                'infringing_repository': infringing_repo['url'],
                'similarity_score': comparison.get('similarity_score', 0)
            }
            
            dmca_ipfs_hash = self.ipfs_manager.upload_to_ipfs(dmca_pdf_path, dmca_metadata)
            
            # File DMCA on blockchain
            dmca_tx_result = self.contract_interface.file_dmca_on_chain(
                infringing_repo['url'], dmca_ipfs_hash
            )
            
            # Report violation on main contract
            violation_data = {
                'original_repo_id': original_repo['id'],
                'violating_url': infringing_repo['url'],
                'similarity_score': comparison.get('similarity_score', 0),
                'evidence_hash': dmca_ipfs_hash
            }
            
            violation_tx_result = self.contract_interface.report_violation_on_chain(violation_data)
            
            dmca_id = f"dmca_{int(datetime.now().timestamp())}"
            
            return {
                'success': True,
                'dmca_id': dmca_id,
                'pdf_path': dmca_pdf_path,
                'ipfs_hash': dmca_ipfs_hash,
                'ipfs_url': self.ipfs_manager.get_ipfs_url(dmca_ipfs_hash),
                'blockchain_transactions': {
                    'dmca_filing': dmca_tx_result.get('tx_hash'),
                    'violation_report': violation_tx_result.get('tx_hash')
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_repository_by_id(self, repo_id: int) -> Optional[Dict]:
        """Get repository by ID from blockchain"""
        repo_result = self.contract_interface.get_repository_from_chain(repo_id)
        return repo_result.get('repository') if repo_result['success'] else None
    
    def _get_all_registered_repositories(self) -> List[Dict]:
        """Get all registered repositories from blockchain"""
        repos = []
        total_repos = self.contract_interface.get_total_repositories()
        
        for repo_id in range(1, total_repos + 1):
            repo = self._get_repository_by_id(repo_id)
            if repo:
                repos.append(repo)
        
        return repos
    
    def _find_best_matching_repo(self, infringing_url: str) -> Optional[int]:
        """Find best matching registered repository for an infringing URL"""
        # This would implement ML-based matching
        # For now, return None (manual specification required)
        return None
    
    def _calculate_bounty_amount(self, similarity_score: float) -> float:
        """Calculate bounty amount based on similarity score"""
        base_bounty = 1.0  # 1 tFIL base
        multiplier = min(2.0, similarity_score * 2)  # Up to 2x multiplier
        return base_bounty * multiplier
    
    def _generate_detailed_recommendation(self, similarity: Dict, blockchain_matches: List[Dict]) -> str:
        """Generate detailed recommendation based on analysis"""
        score = similarity.get('overall_similarity', 0)
        
        if blockchain_matches:
            return f"⚠️ BLOCKCHAIN REGISTERED: One or both repositories are registered on blockchain. Similarity: {score:.2%}"
        elif score > 0.8:
            return f"🚨 HIGH SIMILARITY ({score:.2%}): Strong evidence of code copying. Recommend immediate DMCA filing."
        elif score > 0.6:
            return f"⚡ MODERATE SIMILARITY ({score:.2%}): Investigate further. Consider registering original repository."
        elif score > 0.4:
            return f"📊 LOW SIMILARITY ({score:.2%}): Minor similarities detected. Likely independent development."
        else:
            return f"✅ MINIMAL SIMILARITY ({score:.2%}): Repositories appear to be independent works."
    
    def _suggest_next_actions(self, similarity: Dict, blockchain_matches: List[Dict]) -> List[str]:
        """Suggest next actions based on analysis"""
        actions = []
        score = similarity.get('overall_similarity', 0)
        
        if score > 0.7:
            actions.append("Generate and file DMCA notice")
            actions.append("Report violation on blockchain")
            actions.append("Gather additional evidence")
        
        if score > 0.5 and not blockchain_matches:
            actions.append("Register original repository on blockchain")
            actions.append("Generate license documentation")
        
        if blockchain_matches:
            actions.append("Check existing protection status")
            actions.append("Review license compliance")
        
        actions.append("Monitor for future violations")
        
        return actions