# 🛡️ Filecoin-Enhanced GitHub Protection Agent 

A revolutionary intellectual property protection system that combines AI-powered repository analysis with Filecoin blockchain technology to provide immutable, decentralized protection for your GitHub repositories.

## 🌟 New Blockchain Features

### ⛓️ **Filecoin Integration**
- Smart contract repository registration on Filecoin Calibration testnet
- Immutable proof of ownership and creation dates
- Decentralized evidence storage via IPFS

### 📄 **Automated DMCA System**
- AI-powered infringement detection
- Automatic DMCA notice generation with legal templates
- Blockchain-backed evidence storage
- PDF generation with C2PA metadata support

### 💰 **Bounty System**
- Earn rewards for reporting infringements
- Community-driven IP protection network
- Automated verification and payment system

### 🔒 **Enhanced Security**
- Cryptographic repository fingerprinting
- Extensive commit history analysis
- Secret detection across entire project history
- Blockchain evidence preservation

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub Repo   │────│  Analysis Agent  │────│  Filecoin Chain │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                         │
                       ┌──────────────────┐    ┌─────────────────┐
                       │  IPFS Storage    │────│  Smart Contracts│
                       └──────────────────┘    └─────────────────┘
```

## 📋 Smart Contracts

| Contract | Address | Purpose |
|----------|---------|---------|
| `GitHubRepoProtection` | `0x19054030669efBFc413bA3729b63eCfD3Bdc22B5` | Main repository registration and violation tracking |
| `LinkRegistry` | `0x5fa19b4a48C20202055c8a6fdf16688633617D50` | License and DMCA document registry |
| `LinkRegistryWithDeals` | `0x25bc04a49997e25B7482eEcbeB2Ec67740AEd5a6` | Enhanced registry with Filecoin deal support |
| `InfringementBounty` | `0xA2cD4CC41b8DCE00D002Aa4B29050f2d53705400` | Bounty system for community reporting |
| `DealClient` | `0x592eC554ec3Af631d76981a680f699F9618B5687` | Filecoin storage deal management |

## 🚀 Quick Start

### 1. Installation

```bash
git clone <repository-url>
cd github-protection-agent
pip install -r requirements.txt
```

### 2. Environment Setup

Copy the example configuration:
```bash
cp .env.example .env
```

Configure your environment variables:
```bash
# Required: Filecoin wallet private key
PRIVATE_KEY=your_private_key_here

# Required: IPFS storage (Pinata recommended)
PINATA_API_KEY=your_pinata_key
PINATA_API_SECRET=your_pinata_secret

# Required: AI model (OpenAI or local)
OPENAI_API_KEY=your_openai_key
# OR
USE_LOCAL_MODEL=true

# Optional: GitHub integration
GITHUB_TOKEN=your_github_token
```

### 3. Get Testnet Tokens

Visit the [Filecoin Calibration Faucet](https://faucet.calibration.fildev.network/) to get free tFIL tokens for testing.

### 4. Run the Agent

```bash
python -m github_protection_agent.main_blockchain
```

## 🎯 Core Commands

### 🔗 Blockchain Operations

```bash
# Check blockchain status and account balance
blockchain-status

# Register repository on Filecoin with immutable proof
register-blockchain https://github.com/user/repo MIT

# Run complete protection workflow
workflow-blockchain https://github.com/user/repo

# Query registered repositories from blockchain
query-repos 1 10
```

### 🔍 Analysis & Detection

```bash
# Compare repositories with blockchain verification
analyze https://github.com/user/repo1 https://github.com/user/repo2

# Security audit with blockchain evidence storage
audit https://github.com/user/repo --extensive

# Scan for violations with automatic DMCA filing
scan 1
```

### 💰 Bounty System

```bash
# Report infringement and earn bounty
report-bounty https://github.com/bad/repo QmLicense123 QmDMCA456
```

## 🔧 Advanced Features

### Submission Types

The system supports three types of blockchain submissions:

1. **Register** (`SubmissionType.Register = 0`)
   - Register new repository with license
   - Generate and store license PDF on IPFS
   - Create immutable ownership record

2. **ReportViolation** (`SubmissionType.ReportViolation = 1`)
   - Report copyright infringement
   - Generate DMCA notice automatically
   - Store evidence on blockchain

3. **UpdateLicense** (`SubmissionType.UpdateLicense = 2`)
   - Update repository license
   - Maintain license history
   - Ensure compliance tracking

### IPFS Integration

All documents are stored on IPFS for decentralized access:

- **License PDFs**: Generated with legal templates
- **DMCA Notices**: Professional takedown requests
- **Security Reports**: Comprehensive audit results
- **Evidence Files**: Cryptographic proof of violations

### AI-Powered Analysis

- **Repository Fingerprinting**: Unique cryptographic signatures
- **Code Similarity Detection**: Advanced ML algorithms
- **Security Scanning**: 50+ vulnerability patterns
- **Commit History Analysis**: Full project lifecycle review

## 🏦 Economic Model

### Gas Costs (Estimated)

| Operation | Gas | Cost (tFIL) |
|-----------|-----|-------------|
| Register Repository | ~200,000 | ~0.002 |
| Report Violation | ~150,000 | ~0.0015 |
| File DMCA | ~100,000 | ~0.001 |
| Add Link | ~100,000 | ~0.001 |

### Bounty Rewards

- **Valid Infringement Report**: 1.0 tFIL
- **DMCA Takedown Success**: 2.0 tFIL
- **Community Verification**: 0.5 tFIL

## 🔐 Security Features

### Multi-Layer Protection

1. **Blockchain Immutability**: Records cannot be altered
2. **IPFS Persistence**: Documents remain accessible
3. **Cryptographic Signatures**: Tamper-proof evidence
4. **C2PA Metadata**: Content authenticity verification

### Privacy & Compliance

- **GDPR Compliant**: Right to erasure supported
- **DMCA Compliant**: Legal framework adherence
- **Open Source**: Transparent and auditable
- **Decentralized**: No single point of failure

## 🌐 Network Information

### Filecoin Calibration Testnet

- **Chain ID**: 314159 (0x4cb2f)
- **Currency**: tFIL
- **Block Time**: ~30 seconds
- **Explorer**: https://calibration.filscan.io
- **Faucet**: https://faucet.calibration.fildev.network/

### RPC Endpoints

```bash
# Primary (Ankr)
https://rpc.ankr.com/filecoin_testnet

# Alternative endpoints
https://api.calibration.node.glif.io/rpc/v1
https://filecoin-calibration.chainup.net/rpc/v1
```

## 📊 Usage Examples

### Complete Protection Workflow

```python
from github_protection_agent import BlockchainEnhancedGitHubProtectionAgent

# Initialize agent with blockchain support
config = {
    'PRIVATE_KEY': 'your_private_key',
    'PINATA_API_KEY': 'your_pinata_key',
    'PINATA_API_SECRET': 'your_pinata_secret',
    'OPENAI_API_KEY': 'your_openai_key'
}

agent = BlockchainEnhancedGitHubProtectionAgent(config)

# Run complete protection workflow
result = agent.run_protection_workflow_blockchain('https://github.com/user/repo')

print(f"Repository registered with ID: {result['summary']['repo_id']}")
print(f"Blockchain transactions: {result['summary']['total_blockchain_transactions']}")
print(f"DMCA notices filed: {result['summary']['dmca_notices_filed']}")
```

### Query Blockchain Data

```python
# Get repository from blockchain
repo_data = agent.contract_interface.get_repository_from_chain(1)
print(f"Repository: {repo_data['repository']['github_url']}")
print(f"Owner: {repo_data['repository']['owner']}")
print(f"License: {repo_data['repository']['license_type']}")

# Check account balance
balance = agent.contract_interface.get_account_balance()
print(f"Account balance: {balance:.6f} tFIL")
```

## 🐛 Troubleshooting

### Common Issues

1. **"Failed to connect to Filecoin network"**
   - Check your RPC URL and internet connection
   - Try alternative RPC endpoints
   - Verify network isn't under maintenance

2. **"Insufficient funds for gas"**
   - Get more tFIL from the faucet
   - Check account balance with `blockchain-status`
   - Wait for faucet cooldown period

3. **"IPFS upload failed"**
   - Verify Pinata API credentials
   - Check IPFS service status
   - Try alternative IPFS providers

4. **"Contract call failed"**
   - Check contract addresses are correct
   - Verify ABI matches deployed contract
   - Ensure account has permissions

### Debug Mode

Enable detailed logging:
```bash
export LOG_LEVEL=DEBUG
export DEVELOPMENT_MODE=true
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone repository
git clone https://github.com/CodeShieldAI/backend
cd github-protection-agent

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Run tests
pytest tests/
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Filecoin](https://filecoin.io/) for decentralized storage infrastructure

---
