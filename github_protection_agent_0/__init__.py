"""
Blockchain-Enhanced GitHub Protection Agent Package
Integrates with Filecoin smart contracts for decentralized IP protection
"""

# Core agent classes
from .blockchain_enhanced_agent import BlockchainEnhancedGitHubProtectionAgent
from .agent_core_enhanced import EnhancedGitHubProtectionAgent  # Legacy support

# Blockchain integration
from .filecoin_contracts import FilecoinContractInterface

# Analysis & Security Components
from .repository_analyzer import RepositoryAnalyzer
from .security_scanner import SecurityScanner, EnhancedSecurityScanner
from .url_processor import URLProcessor
from .violation_detector import ViolationDetector
from .github_scanner import GitHubScanner

# Document Generation & Storage
from .report_generator import ReportGenerator
from .dmca_generator import DMCAGenerator
from .license_generator import LicenseGenerator
from .ipfs_manager import IPFSManager

# Utility Modules
from .secret_patterns import SecretPatterns
from .utils import setup_logging, calculate_security_score

# Version and metadata
__version__ = "5.0.0"
__author__ = "GitHub Protection Agent Team"
__description__ = "Blockchain-enhanced intellectual property protection for GitHub repositories"
__blockchain_version__ = "1.0.0"
__supported_networks__ = ["Filecoin Calibration Testnet"]

# Contract addresses (Filecoin Calibration Testnet)
CONTRACT_ADDRESSES = {
    "filecoin_calibration": {
        "github_protection": "0x19054030669efBFc413bA3729b63eCfD3Bdc22B5",
        "deal_client": "0x592eC554ec3Af631d76981a680f699F9618B5687",
        "link_registry": "0x5fa19b4a48C20202055c8a6fdf16688633617D50",
        "link_registry_deals": "0x25bc04a49997e25B7482eEcbeB2Ec67740AEd5a6",
        "infringement_bounty": "0xA2cD4CC41b8DCE00D002Aa4B29050f2d53705400"
    }
}

# Network configuration
NETWORK_CONFIG = {
    "filecoin_calibration": {
        "name": "Filecoin Calibration Testnet",
        "chain_id": 314159,
        "rpc_url": "https://rpc.ankr.com/filecoin_testnet",
        "explorer": "https://calibration.filscan.io",
        "faucet": "https://faucet.calibration.fildev.network/",
        "currency": "tFIL"
    }
}

# Export all components
__all__ = [
    # Main agent classes
    "BlockchainEnhancedGitHubProtectionAgent",
    "EnhancedGitHubProtectionAgent",
    
    # Blockchain integration
    "FilecoinContractInterface",
    
    # Core components
    "RepositoryAnalyzer",
    "SecurityScanner",
    "EnhancedSecurityScanner",
    "URLProcessor",
    "ViolationDetector",
    "GitHubScanner",
    
    # Document generation
    "ReportGenerator",
    "DMCAGenerator",
    "LicenseGenerator",
    "IPFSManager",
    
    # Utilities
    "SecretPatterns",
    "setup_logging",
    "calculate_security_score",
    
    # Configuration
    "CONTRACT_ADDRESSES",
    "NETWORK_CONFIG"
]


def get_agent(blockchain_enabled: bool = True, config: dict = None) -> object:
    """
    Factory function to create the appropriate agent instance
    
    Args:
        blockchain_enabled (bool): Whether to use blockchain features
        config (dict): Configuration dictionary
    
    Returns:
        Agent instance (blockchain-enhanced or legacy)
    """
    if config is None:
        config = {}
    
    if blockchain_enabled:
        return BlockchainEnhancedGitHubProtectionAgent(config)
    else:
        return EnhancedGitHubProtectionAgent(config)


def check_blockchain_requirements() -> dict:
    """
    Check if blockchain requirements are satisfied
    
    Returns:
        dict: Status of blockchain requirements
    """
    requirements = {
        "web3_installed": False,
        "private_key_set": False,
        "rpc_url_accessible": False,
        "ipfs_configured": False
    }
    
    try:
        import web3
        requirements["web3_installed"] = True
    except ImportError:
        pass
    
    import os
    requirements["private_key_set"] = bool(os.getenv("PRIVATE_KEY"))
    requirements["ipfs_configured"] = bool(
        os.getenv("PINATA_API_KEY") or 
        os.getenv("WEB3_STORAGE_TOKEN") or 
        os.getenv("LOCAL_IPFS_URL")
    )
    
    # Test RPC connection
    if requirements["web3_installed"]:
        try:
            from web3 import Web3
            rpc_url = os.getenv("FILECOIN_RPC_URL", "https://rpc.ankr.com/filecoin_testnet")
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            requirements["rpc_url_accessible"] = w3.is_connected()
        except:
            pass
    
    return requirements


def get_setup_instructions() -> str:
    """
    Get setup instructions for blockchain functionality
    
    Returns:
        str: Formatted setup instructions
    """
    instructions = """
🔧 BLOCKCHAIN SETUP INSTRUCTIONS:

1. Install requirements:
   pip install -r requirements.txt

2. Set environment variables:
   export PRIVATE_KEY="your_private_key_here"
   export FILECOIN_RPC_URL="https://rpc.ankr.com/filecoin_testnet"
   export PINATA_API_KEY="your_pinata_api_key"
   export PINATA_API_SECRET="your_pinata_secret"
   export OPENAI_API_KEY="your_openai_key"
   export GITHUB_TOKEN="your_github_token"

3. Get testnet tokens:
   Visit: https://faucet.calibration.fildev.network/

4. Test connection:
   python -c "from github_protection_agent import check_blockchain_requirements; print(check_blockchain_requirements())"

5. Run the agent:
   python -m github_protection_agent.main_blockchain

For local development without OpenAI:
   export USE_LOCAL_MODEL=true
   # Requires Ollama with llama3.2:3b model
"""
    return instructions


# Package initialization message
def _init_message():
    """Print initialization message when package is imported"""
    import os
    
    if os.getenv("GITHUB_PROTECTION_AGENT_QUIET") != "true":
        print(f"🛡️ GitHub Protection Agent v{__version__} (Blockchain-Enhanced)")
        print(f"⛓️ Filecoin Integration: {__blockchain_version__}")
        
        # Quick status check
        reqs = check_blockchain_requirements()
        if all(reqs.values()):
            print("✅ Blockchain features: Ready")
        elif reqs["web3_installed"]:
            print("⚠️ Blockchain features: Partially configured")
        else:
            print("❌ Blockchain features: Not available (missing web3)")


# Run initialization
_init_message()