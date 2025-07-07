"""
GitHub Protection Agent with Filecoin Integration
A comprehensive tool for protecting GitHub repositories using blockchain technology
"""

__version__ = "5.0.0"
__author__ = "KreonLabs"
__email__ = "legal@kreonlabs.com"

# Package metadata
PACKAGE_NAME = "github-protection-agent-filecoin"
DESCRIPTION = "AI-powered GitHub repository protection with Filecoin blockchain integration"

# Contract addresses on Filecoin Calibration Testnet
DEPLOYED_CONTRACTS = {
    'github_protection': '0x19054030669efBFc413bA3729b63eCfD3Bdc22B5',
    'link_registry': '0x5fa19b4a48C20202055c8a6fdf16688633617D50',
    'link_registry_deals': '0x25bc04a49997e25B7482eEcbeB2Ec67740AEd5a6',
    'infringement_bounty': '0xA2cD4CC41b8DCE00D002Aa4B29050f2d53705400',
    'deal_client': '0x592eC554ec3Af631d76981a680f699F9618B5687'
}

# Network configuration
FILECOIN_CALIBRATION = {
    'chain_id': 314159,
    'rpc_url': 'https://rpc.ankr.com/filecoin_testnet',
    'explorer': 'https://calibration.filscan.io',
    'faucet': 'https://faucet.calibration.fildev.network/',
    'currency': 'tFIL'
}

def get_version():
    """Get package version"""
    return __version__

def get_contracts():
    """Get deployed contract addresses"""
    return DEPLOYED_CONTRACTS.copy()

def get_network_info():
    """Get Filecoin network information"""
    return FILECOIN_CALIBRATION.copy()