"""
Security Scanner Module
Handles comprehensive security scanning of GitHub repositories
"""
import re
import requests
import base64
from typing import Dict, List
from datetime import datetime
from github_protection_agent.utils import setup_logging
from github_protection_agent.secret_patterns import SecretPatterns
from dotenv import load_dotenv
load_dotenv()

logger = setup_logging(__name__)


class SecurityScanner:
    """Handles security scanning and vulnerability detection"""
    
    def __init__(self, config: Dict, llm):
        self.config = config
        self.llm = llm
        self.github_token = config.get('GITHUB_TOKEN')
        self.secret_patterns = SecretPatterns()
        
    def audit_github_repository_extensive(self, github_url: str, include_all_commits: bool = False) -> Dict:
        """Perform comprehensive security audit of GitHub repository"""
        try:
            logger.info(f"🔒 Starting security audit of {github_url}")
            
            repo_parts = github_url.replace('https://github.com/', '').split('/')
            if len(repo_parts) < 2:
                return {'success': False, 'error': 'Invalid GitHub URL'}
            
            owner, repo = repo_parts[0], repo_parts[1]
            
            headers = {}
            if self.github_token:
                headers['Authorization'] = f"token {self.github_token}"
            
            audit_result = {
                'audit_id': f"audit_{int(datetime.now().timestamp())}",
                'timestamp': datetime.now().isoformat(),
                'input_url': github_url,
                'platform': 'github',
                'files_scanned': 0,
                'commits_scanned': 0 if not include_all_commits else 'N/A',
                'total_findings': 0,
                'critical_findings': 0,
                'high_findings': 0,
                'medium_findings': 0,
                'low_findings': 0,
                'findings': [],
                'ai_summary': ''
            }
            
            # Scan repository files
            file_findings = self._scan_repository_files(owner, repo, headers)
            audit_result['files_scanned'] = file_findings['files_scanned']
            audit_result['findings'].extend(file_findings['findings'])
            
            # Scan commit history if requested
            if include_all_commits:
                commit_findings = self._scan_commit_history(owner, repo, headers)
                audit_result['commits_scanned'] = commit_findings['commits_scanned']
                audit_result['findings'].extend(commit_findings['findings'])
            
            # Categorize findings by severity
            for finding in audit_result['findings']:
                severity = finding.get('severity', 'low').lower()
                if severity == 'critical':
                    audit_result['critical_findings'] += 1
                elif severity == 'high':
                    audit_result['high_findings'] += 1
                elif severity == 'medium':
                    audit_result['medium_findings'] += 1
                else:
                    audit_result['low_findings'] += 1
            
            audit_result['total_findings'] = len(audit_result['findings'])
            
            # Generate AI summary
            if audit_result['findings']:
                audit_result['ai_summary'] = self._generate_ai_summary(audit_result)
            
            logger.info(f"✅ Security audit completed: {audit_result['total_findings']} findings")
            return audit_result
            
        except Exception as e:
            logger.error(f"Security audit failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'audit_id': f"failed_{int(datetime.now().timestamp())}",
                'timestamp': datetime.now().isoformat()
            }
    
    def _scan_repository_files(self, owner: str, repo: str, headers: Dict) -> Dict:
        """Scan repository files for security issues"""
        findings = []
        files_scanned = 0
        
        try:
            # Get repository tree
            tree_response = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1",
                headers=headers
            )
            
            if tree_response.status_code != 200:
                # Try master branch
                tree_response = requests.get(
                    f"https://api.github.com/repos/{owner}/{repo}/git/trees/master?recursive=1",
                    headers=headers
                )
            
            if tree_response.status_code == 200:
                tree_data = tree_response.json()
                
                for item in tree_data.get('tree', [])[:50]:  # Limit to first 50 files
                    if item['type'] == 'blob':
                        file_findings = self._scan_file(owner, repo, item['path'], headers)
                        findings.extend(file_findings)
                        files_scanned += 1
            
        except Exception as e:
            logger.error(f"Error scanning repository files: {e}")
        
        return {
            'findings': findings,
            'files_scanned': files_scanned
        }
    
    def _scan_file(self, owner: str, repo: str, file_path: str, headers: Dict) -> List[Dict]:
        """Scan individual file for security issues"""
        findings = []
        
        try:
            # Get file content
            file_response = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}",
                headers=headers
            )
            
            if file_response.status_code == 200:
                file_data = file_response.json()
                
                # Decode content
                if file_data.get('encoding') == 'base64':
                    try:
                        content = base64.b64decode(file_data['content']).decode('utf-8')
                    except:
                        return findings  # Skip binary files
                else:
                    content = file_data.get('content', '')
                
                # Scan for secrets
                secret_findings = self._scan_for_secrets(content, file_path)
                findings.extend(secret_findings)
                
                # Scan for other security issues
                security_findings = self._scan_for_security_issues(content, file_path)
                findings.extend(security_findings)
                
        except Exception as e:
            logger.debug(f"Error scanning file {file_path}: {e}")
        
        return findings
    
    def _scan_for_secrets(self, content: str, file_path: str) -> List[Dict]:
        """Scan content for secret patterns"""
        findings = []
        patterns = self.secret_patterns.get_patterns()
        
        for pattern_name, pattern_info in patterns.items():
            pattern = pattern_info['pattern']
            
            try:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                
                for match in matches:
                    matched_text = match.group()
                    
                    # Validate if it's likely a real secret
                    if self.secret_patterns.is_likely_real_secret(matched_text, pattern_name):
                        line_number = content[:match.start()].count('\n') + 1
                        
                        findings.append({
                            'type': 'secret',
                            'pattern_name': pattern_name,
                            'severity': pattern_info['severity'],
                            'description': pattern_info['description'],
                            'recommendation': pattern_info['recommendation'],
                            'file_path': file_path,
                            'line_number': line_number,
                            'matched_text': matched_text[:50] + '...' if len(matched_text) > 50 else matched_text
                        })
                        
            except Exception as e:
                logger.debug(f"Error scanning pattern {pattern_name}: {e}")
        
        return findings
    
    def _scan_for_security_issues(self, content: str, file_path: str) -> List[Dict]:
        """Scan for general security issues"""
        findings = []
        
        # Security anti-patterns
        security_patterns = {
            'sql_injection': {
                'pattern': r'(?i)(SELECT|INSERT|UPDATE|DELETE).*(\+|%s|\$\{)',
                'severity': 'high',
                'description': 'Potential SQL injection vulnerability'
            },
            'command_injection': {
                'pattern': r'(?i)(exec|system|shell_exec|eval)\s*\(',
                'severity': 'high',
                'description': 'Potential command injection vulnerability'
            },
            'hardcoded_password': {
                'pattern': r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']{3,}["\']',
                'severity': 'medium',
                'description': 'Hardcoded password detected'
            },
            'debug_code': {
                'pattern': r'(?i)(console\.log|print\(|debug|TODO|FIXME)',
                'severity': 'low',
                'description': 'Debug code or TODO comments found'
            }
        }
        
        for issue_name, issue_info in security_patterns.items():
            try:
                matches = re.finditer(issue_info['pattern'], content, re.IGNORECASE | re.MULTILINE)
                
                for match in matches:
                    line_number = content[:match.start()].count('\n') + 1
                    
                    findings.append({
                        'type': 'security_issue',
                        'pattern_name': issue_name,
                        'severity': issue_info['severity'],
                        'description': issue_info['description'],
                        'recommendation': f'Review and remediate {issue_name}',
                        'file_path': file_path,
                        'line_number': line_number,
                        'matched_text': match.group()[:100] + '...' if len(match.group()) > 100 else match.group()
                    })
                    
            except Exception as e:
                logger.debug(f"Error scanning security pattern {issue_name}: {e}")
        
        return findings
    
    def _scan_commit_history(self, owner: str, repo: str, headers: Dict) -> Dict:
        """Scan commit history for secrets (limited scan)"""
        findings = []
        commits_scanned = 0
        
        try:
            # Get recent commits (limit to 20 for performance)
            commits_response = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}/commits",
                headers=headers,
                params={'per_page': 20}
            )
            
            if commits_response.status_code == 200:
                commits = commits_response.json()
                
                for commit in commits:
                    try:
                        # Get commit details
                        commit_response = requests.get(commit['url'], headers=headers)
                        if commit_response.status_code == 200:
                            commit_data = commit_response.json()
                            
                            # Scan commit message
                            message_findings = self._scan_for_secrets(
                                commit_data.get('commit', {}).get('message', ''),
                                f"commit:{commit['sha'][:8]}"
                            )
                            findings.extend(message_findings)
                            
                            commits_scanned += 1
                            
                    except Exception as e:
                        logger.debug(f"Error scanning commit {commit['sha']}: {e}")
                        
        except Exception as e:
            logger.error(f"Error scanning commit history: {e}")
        
        return {
            'findings': findings,
            'commits_scanned': commits_scanned
        }
    
    def _generate_ai_summary(self, audit_result: Dict) -> str:
        """Generate AI summary of security audit"""
        try:
            findings_summary = []
            for finding in audit_result['findings'][:5]:  # Top 5 findings
                findings_summary.append(
                    f"- {finding['severity'].upper()}: {finding['description']} in {finding['file_path']}"
                )
            
            summary_prompt = f"""
            Analyze this security audit report and provide a brief summary:
            
            Repository: {audit_result['input_url']}
            Total Findings: {audit_result['total_findings']}
            Critical: {audit_result['critical_findings']}
            High: {audit_result['high_findings']}
            Medium: {audit_result['medium_findings']}
            Low: {audit_result['low_findings']}
            
            Sample Findings:
            {chr(10).join(findings_summary)}
            
            Provide a concise security assessment and top recommendations.
            """
            
            response = self.llm.invoke(summary_prompt)
            return response.content
            
        except Exception as e:
            logger.error(f"AI summary generation failed: {e}")
            return "Security audit completed. Manual review of findings recommended."