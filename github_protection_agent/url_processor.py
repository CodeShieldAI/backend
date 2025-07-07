"""
URL Processing Module
Handles URL cleaning, validation, and processing
"""
import re
from urllib.parse import urlparse, parse_qs
from typing import Dict
from github_protection_agent.utils import setup_logging
from dotenv import load_dotenv
load_dotenv()

logger = setup_logging(__name__)


class URLProcessor:
    """Handles URL processing and validation"""
    
    def __init__(self, llm):
        self.llm = llm
        
        # Supported platforms and their patterns
        self.platform_patterns = {
            'github': {
                'domains': ['github.com', 'www.github.com'],
                'repo_pattern': r'^https?://(?:www\.)?github\.com/([^/]+)/([^/]+)/?(?:\?.*)?$',
                'user_pattern': r'^https?://(?:www\.)?github\.com/([^/]+)/?(?:\?.*)?$'
            },
            'gitlab': {
                'domains': ['gitlab.com', 'www.gitlab.com'],
                'repo_pattern': r'^https?://(?:www\.)?gitlab\.com/([^/]+)/([^/]+)/?(?:\?.*)?$'
            },
            'bitbucket': {
                'domains': ['bitbucket.org', 'www.bitbucket.org'],
                'repo_pattern': r'^https?://(?:www\.)?bitbucket\.org/([^/]+)/([^/]+)/?(?:\?.*)?$'
            }
        }
    
    def clean_single_url(self, url: str) -> Dict:
        """Clean and validate a single URL"""
        try:
            if not url or not isinstance(url, str):
                return {'success': False, 'error': 'Invalid URL input'}
            
            # Basic cleanup
            url = url.strip()
            
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                if url.startswith('www.') or '.' in url:
                    url = 'https://' + url
                else:
                    return {'success': False, 'error': 'Invalid URL format'}
            
            # Parse URL
            try:
                parsed = urlparse(url)
                if not parsed.netloc:
                    return {'success': False, 'error': 'Invalid URL format'}
            except Exception:
                return {'success': False, 'error': 'Failed to parse URL'}
            
            # Identify platform and type
            platform_info = self._identify_platform(url)
            if not platform_info['platform']:
                return {'success': False, 'error': 'Unsupported platform'}
            
            # Clean the URL based on platform
            cleaned_url = self._clean_platform_url(url, platform_info)
            
            return {
                'success': True,
                'original_url': url,
                'cleaned_url': cleaned_url,
                'platform': platform_info['platform'],
                'url_type': platform_info['url_type'],
                'owner': platform_info.get('owner'),
                'repo': platform_info.get('repo')
            }
            
        except Exception as e:
            logger.error(f"URL cleaning failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def clean_multiple_urls(self, urls: list) -> Dict:
        """Clean multiple URLs"""
        results = []
        
        for url in urls:
            result = self.clean_single_url(url)
            results.append(result)
        
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        return {
            'total_processed': len(urls),
            'successful': len(successful),
            'failed': len(failed),
            'results': results,
            'cleaned_urls': [r['cleaned_url'] for r in successful]
        }
    
    def _identify_platform(self, url: str) -> Dict:
        """Identify the platform and URL type"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        for platform, config in self.platform_patterns.items():
            if domain in config['domains']:
                # Check if it's a repository URL
                repo_match = re.match(config['repo_pattern'], url, re.IGNORECASE)
                if repo_match:
                    owner, repo = repo_match.groups()
                    return {
                        'platform': platform,
                        'url_type': 'repository',
                        'owner': owner,
                        'repo': repo
                    }
                
                # Check if it's a user profile
                if 'user_pattern' in config:
                    user_match = re.match(config['user_pattern'], url, re.IGNORECASE)
                    if user_match:
                        owner = user_match.group(1)
                        return {
                            'platform': platform,
                            'url_type': 'user',
                            'owner': owner
                        }
                
                # Default to platform homepage
                return {
                    'platform': platform,
                    'url_type': 'unknown'
                }
        
        return {'platform': None, 'url_type': None}
    
    def _clean_platform_url(self, url: str, platform_info: Dict) -> str:
        """Clean URL based on platform"""
        platform = platform_info['platform']
        url_type = platform_info['url_type']
        
        if platform == 'github' and url_type == 'repository':
            # Clean GitHub repository URL
            owner = platform_info['owner']
            repo = platform_info['repo']
            return f"https://github.com/{owner}/{repo}"
        
        elif platform == 'github' and url_type == 'user':
            # Clean GitHub user URL
            owner = platform_info['owner']
            return f"https://github.com/{owner}"
        
        elif platform == 'gitlab' and url_type == 'repository':
            # Clean GitLab repository URL
            owner = platform_info['owner']
            repo = platform_info['repo']
            return f"https://gitlab.com/{owner}/{repo}"
        
        elif platform == 'bitbucket' and url_type == 'repository':
            # Clean Bitbucket repository URL
            owner = platform_info['owner']
            repo = platform_info['repo']
            return f"https://bitbucket.org/{owner}/{repo}"
        
        # Default: return original URL
        return url
    
    def extract_repo_info(self, url: str) -> Dict:
        """Extract detailed repository information from URL"""
        result = self.clean_single_url(url)
        
        if not result['success'] or result['url_type'] != 'repository':
            return {'success': False, 'error': 'Not a valid repository URL'}
        
        return {
            'success': True,
            'platform': result['platform'],
            'owner': result['owner'],
            'repository': result['repo'],
            'full_name': f"{result['owner']}/{result['repo']}",
            'url': result['cleaned_url']
        }
    
    def validate_repository_url(self, url: str) -> bool:
        """Validate if URL is a repository URL"""
        result = self.clean_single_url(url)
        return result['success'] and result['url_type'] == 'repository'
    
    def normalize_github_url(self, url: str) -> str:
        """Normalize GitHub URL to standard format"""
        if not url:
            return url
            
        # Handle various GitHub URL formats
        patterns = [
            (r'github\.com/([^/]+)/([^/]+)\.git', r'github.com/\1/\2'),
            (r'github\.com/([^/]+)/([^/]+)/.*', r'github.com/\1/\2'),
            (r'www\.github\.com', r'github.com'),
        ]
        
        cleaned = url
        for pattern, replacement in patterns:
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        
        # Ensure https protocol
        if not cleaned.startswith(('http://', 'https://')):
            cleaned = 'https://' + cleaned
        
        return cleaned
    
    def extract_urls_from_text(self, text: str) -> list:
        """Extract URLs from text"""
        # URL pattern
        url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
        
        urls = re.findall(url_pattern, text, re.IGNORECASE)
        
        # Clean and validate found URLs
        valid_urls = []
        for url in urls:
            result = self.clean_single_url(url)
            if result['success']:
                valid_urls.append(result['cleaned_url'])
        
        return valid_urls
    
    def get_platform_api_url(self, url: str) -> str:
        """Convert web URL to API URL"""
        result = self.clean_single_url(url)
        
        if not result['success'] or result['url_type'] != 'repository':
            return None
        
        platform = result['platform']
        owner = result['owner']
        repo = result['repo']
        
        if platform == 'github':
            return f"https://api.github.com/repos/{owner}/{repo}"
        elif platform == 'gitlab':
            return f"https://gitlab.com/api/v4/projects/{owner}%2F{repo}"
        
        return None