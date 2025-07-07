"""
Utility functions for the GitHub Protection Agent
"""
import logging
import os
import sys
from datetime import datetime
from typing import Optional


def setup_logging(name: str, level: str = None) -> logging.Logger:
    """
    Set up logging for the application
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger instance
    """
    # Determine log level
    if level is None:
        level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Create logger
    logger = logging.getLogger(name)
    
    # Don't add handlers if they already exist
    if logger.handlers:
        return logger
    
    # Set level
    numeric_level = getattr(logging, level, logging.INFO)
    logger.setLevel(numeric_level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False
    
    return logger


def get_project_root() -> str:
    """Get the project root directory"""
    current_file = os.path.abspath(__file__)
    return os.path.dirname(os.path.dirname(current_file))


def ensure_directory_exists(directory_path: str) -> bool:
    """
    Ensure a directory exists, create it if it doesn't
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        True if directory exists or was created successfully
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        logger = setup_logging(__name__)
        logger.error(f"Failed to create directory {directory_path}: {e}")
        return False


def format_timestamp(timestamp: Optional[float] = None) -> str:
    """
    Format timestamp as ISO string
    
    Args:
        timestamp: Unix timestamp (uses current time if None)
        
    Returns:
        ISO formatted timestamp string
    """
    if timestamp is None:
        timestamp = datetime.now().timestamp()
    
    return datetime.fromtimestamp(timestamp).isoformat()


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for cross-platform compatibility
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for all platforms
    """
    # Characters to remove or replace
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    
    sanitized = filename
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    # Ensure it's not empty
    if not sanitized:
        sanitized = 'unnamed_file'
    
    return sanitized


def validate_url(url: str) -> bool:
    """
    Basic URL validation
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL appears valid
    """
    if not url or not isinstance(url, str):
        return False
    
    url = url.strip()
    
    # Check for basic URL structure
    if not (url.startswith('http://') or url.startswith('https://')):
        return False
    
    # Basic domain check
    if '.' not in url or len(url) < 10:
        return False
    
    return True


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated string
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def safe_get_env(key: str, default: str = None, required: bool = False) -> str:
    """
    Safely get environment variable with validation
    
    Args:
        key: Environment variable key
        default: Default value if not found
        required: Whether the variable is required
        
    Returns:
        Environment variable value or default
        
    Raises:
        ValueError: If required variable is missing
    """
    value = os.getenv(key, default)
    
    if required and not value:
        raise ValueError(f"Required environment variable '{key}' is not set")
    
    return value


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


class ConfigValidator:
    """Validate configuration settings"""
    
    @staticmethod
    def validate_private_key(private_key: str) -> bool:
        """Validate Ethereum private key format"""
        if not private_key:
            return False
        
        # Remove 0x prefix if present
        if private_key.startswith('0x'):
            private_key = private_key[2:]
        
        # Check length (64 hex characters)
        if len(private_key) != 64:
            return False
        
        # Check if all characters are hex
        try:
            int(private_key, 16)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_api_key(api_key: str, service: str = "generic") -> bool:
        """Validate API key format"""
        if not api_key or not isinstance(api_key, str):
            return False
        
        api_key = api_key.strip()
        
        # Service-specific validation
        if service.lower() == "openai":
            return api_key.startswith("sk-") and len(api_key) > 10
        elif service.lower() == "github":
            return (api_key.startswith("ghp_") or 
                   api_key.startswith("github_pat_")) and len(api_key) > 10
        elif service.lower() == "pinata":
            return len(api_key) > 10  # Basic length check
        
        # Generic validation
        return len(api_key) > 5


# Global logger for the module
logger = setup_logging(__name__)