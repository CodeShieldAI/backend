# 🛡️ Filecoin-Enhanced GitHub Protection Agent 

A revolutionary intellectual property protection system that combines AI-powered repository analysis with Filecoin blockchain technology to provide immutable, decentralized protection for your GitHub repositories.

# 🌟 New Blockchain Features

## ⛓️ **Filecoin Integration**
- Smart contract repository registration on Filecoin Calibration testnet
- Immutable proof of ownership and creation dates
- Decentralized evidence storage via IPFS

## 📄 **Automated DMCA System**
- AI-powered infringement detection
- Automatic DMCA notice generation with legal templates
- Blockchain-backed evidence storage
- PDF generation with C2PA metadata support

## 💰 **Bounty System**
- Earn rewards for reporting infringements
- Community-driven IP protection network
- Automated verification and payment system

## 🔒 **Enhanced Security**
- Cryptographic repository fingerprinting
- Extensive commit history analysis
- Secret detection across entire project history
- Blockchain evidence preservation

# 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub Repo   │────│  Analysis Agent  │────│  Filecoin Chain │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                         │
                       ┌──────────────────┐    ┌─────────────────┐
                       │  IPFS Storage    │────│  Smart Contracts│
                       └──────────────────┘    └─────────────────┘
```

# 📋 Smart Contracts

| Contract | Address | Purpose |
|----------|---------|---------|
| `GitHubRepoProtection` | `0x19054030669efBFc413bA3729b63eCfD3Bdc22B5` | Main repository registration and violation tracking |
| `LinkRegistry` | `0x5fa19b4a48C20202055c8a6fdf16688633617D50` | License and DMCA document registry |
| `LinkRegistryWithDeals` | `0x25bc04a49997e25B7482eEcbeB2Ec67740AEd5a6` | Enhanced registry with Filecoin deal support |
| `InfringementBounty` | `0xA2cD4CC41b8DCE00D002Aa4B29050f2d53705400` | Bounty system for community reporting |
| `DealClient` | `0x592eC554ec3Af631d76981a680f699F9618B5687` | Filecoin storage deal management |

# 🚀 Getting Started

Follow these steps to set up and run the CodeShield AI GitHub Protection Agent locally.

---

## 1. Clone the Repository

First, clone the project from GitHub and navigate into the newly created directory.

```bash
git clone [https://github.com/CodeShieldAI/backend.git](https://github.com/CodeShieldAI/backend.git)
cd backend
```

---

## 2. Set Up Environment Variables

The agent requires API keys and a wallet private key to function. These are managed through a `.env` file in the project's root directory.

1.  **Create the `.env` file** by copying the example template:
    ```bash
    cp .env.example .env
    ```

2.  **Edit the `.env` file** with your favorite editor (e.g., `nano .env` or `code .env`) and add your credentials.

    ```ini
    # REQUIRED: Your Filecoin wallet private key for transactions.
    # This wallet must be funded with tFIL tokens. See step 3.
    PRIVATE_KEY="0xyour_filecoin_wallet_private_key"

    # REQUIRED: Your OpenAI API Key for AI-powered analysis.
    # Get one from [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
    OPENAI_API_KEY="sk-your_openai_api_key"

    # RECOMMENDED: Your GitHub API token for higher API rate limits.
    # Generate one at [https://github.com/settings/tokens](https://github.com/settings/tokens) (with 'repo' scope).
    GITHUB_TOKEN="ghp_your_github_token"

    # OPTIONAL: Credentials for a dedicated IPFS pinning service like Pinata.
    # Get these from [https://www.pinata.cloud/](https://www.pinata.cloud/)
    PINATA_API_KEY="your_pinata_api_key"
    PINATA_API_SECRET="your_pinata_api_secret"
    ```

---

## 3. Get Testnet Tokens

To pay for transactions on the Filecoin network (like registering a repository), your wallet needs testnet tokens (`tFIL`).

Visit the **[Filecoin Calibration Faucet](https://faucet.calibration.fildev.network/)** to get free `tFIL` tokens sent to the wallet address associated with your `PRIVATE_KEY`.

---

## 4. Install Backend Dependencies

The backend is built with Python. Install the required packages using `pip`.

```bash
pip install -r requirements.txt
```

---

## 5. Validate Your Setup

Before running the agent, use the built-in validator to ensure your environment is configured correctly. This script checks everything from API keys and network connectivity to your wallet balance.

```bash
python github_protection_agent/setup_validator.py
```

If all checks pass, you are ready to proceed. The validator will provide clear instructions for fixing any issues it finds.

---

## 6. Run the Backend Agent

You can run the backend as an interactive shell or by passing commands directly via the command line.

### Option A: Interactive Mode

This mode starts an interactive shell where you can run commands one by one.

1.  **Start the agent from the root directory**:
    ```bash
    python github_protection_agent/main.py
    ```
2.  Once initialized, you will see a welcome banner and a command prompt `🛡️ FilecoinAgent>`.
3.  Type `help` to see a full list of commands.

### Option B: Command-Line Interface (CLI)

You can also execute commands directly. The script `run_agent.py` is a convenient wrapper for this.

**Usage:**

```bash
python run_agent.py <command> [arguments...]
```

**Example:**

```bash
# Register a repository from the command line
python run_agent.py register [https://github.com/your-username/your-repo](https://github.com/your-username/your-repo) MIT

# Run a security audit
python run_agent.py audit [https://github.com/your-username/your-repo](https://github.com/your-username/your-repo)
```

### Available Commands

Here is a list of the primary commands available in both modes:

#### 🔧 SYSTEM COMMANDS:

* **validate**
    * Run complete system validation (blockchain, IPFS, AI).
    * *Example: `validate`*
* **status**
    * Check blockchain connection, account balance, and IPFS services.
    * *Example: `status`*

#### 🔗 BLOCKCHAIN COMMANDS:

* **register `<url>` `[license_type]`**
    * Register a repository on Filecoin with license generation.
    * License types: MIT, Apache-2.0, GPL-3.0, BSD-3-Clause, Custom-AI.
    * *Example: `register https://github.com/user/repo MIT`*
* **query `[start_id]` `[limit]`**
    * Query repositories from the blockchain.
    * *Example: `query 1 10`*
* **workflow `<url>`**
    * Run the complete protection workflow (register + audit + scan).
    * *Example: `workflow https://github.com/user/repo`*

#### 🔍 ANALYSIS COMMANDS:

* **analyze `<url1>` `<url2>`**
    * Compare two repositories for similarity.
    * *Example: `analyze github.com/user1/repo1 github.com/user2/repo2`*
* **audit `<url>` `[--extensive]`**
    * Run a security audit with blockchain evidence storage.
    * *Example: `audit github.com/user/repo --extensive`*
* **scan `[repo_id]`**
    * Scan for violations and file DMCA notices.
    * *Example: `scan 1`*

#### 💰 BOUNTY COMMANDS:

* **bounty `<infringing_url>` `[original_repo_id]`**
    * Report an infringement to earn bounty rewards.
    * *Example: `bounty github.com/bad/repo 1`*

#### ℹ️ UTILITY COMMANDS:

* **help** - Show the complete command reference.
* **quit/exit** - Exit the interactive agent.

---

## 7. Install and Run the Frontend

The frontend provides a user-friendly web interface for the agent.

1.  **Navigate into the frontend directory**:
    ```bash
    cd frontend
    ```
2.  **Install the necessary NPM packages**:
    ```bash
    npm install
    ```
3.  **Start the frontend development server**:
    ```bash
    npm run dev
    ```
4.  Open your web browser and go to **`http://localhost:3000`** (or the URL shown in your terminal) to access the application.

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

- **Valid Infringement Report**
- **DMCA Takedown Success**
- **Community Verification**

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


## 🙏 Acknowledgments

- [Filecoin](https://filecoin.io/) for decentralized storage infrastructure

---
