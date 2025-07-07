// GitHub Repository Protection Contract ABI
export const GITHUB_REPO_PROTECTION_ABI = [
  {
    "inputs": [],
    "name": "getTotalRepositories",
    "outputs": [{"type": "uint256"}],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "getTotalViolations", 
    "outputs": [{"type": "uint256"}],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [{"type": "uint256", "name": "repoId"}],
    "name": "getRepository",
    "outputs": [{
      "components": [
        {"type": "uint256", "name": "id"},
        {"type": "address", "name": "owner"},
        {"type": "string", "name": "githubUrl"},
        {"type": "string", "name": "repoHash"},
        {"type": "string", "name": "codeFingerprint"},
        {"type": "string[]", "name": "keyFeatures"},
        {"type": "string", "name": "licenseType"},
        {"type": "uint256", "name": "registeredAt"},
        {"type": "bool", "name": "isActive"},
        {"type": "string", "name": "ipfsMetadata"}
      ],
      "type": "tuple"
    }],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [{"type": "address", "name": "user"}],
    "name": "getUserRepositories",
    "outputs": [{"type": "uint256[]"}],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {"type": "string", "name": "githubUrl"},
      {"type": "string", "name": "repoHash"}, 
      {"type": "string", "name": "codeFingerprint"},
      {"type": "string[]", "name": "keyFeatures"},
      {"type": "string", "name": "licenseType"},
      {"type": "string", "name": "ipfsMetadata"}
    ],
    "name": "registerRepository",
    "outputs": [{"type": "uint256"}],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {"type": "uint256", "name": "originalRepoId"},
      {"type": "string", "name": "violatingUrl"},
      {"type": "string", "name": "evidenceHash"},
      {"type": "uint256", "name": "similarityScore"}
    ],
    "name": "reportViolation",
    "outputs": [{"type": "uint256"}],
    "stateMutability": "nonpayable", 
    "type": "function"
  },
  {
    "anonymous": false,
    "inputs": [
      {"indexed": true, "type": "uint256", "name": "repoId"},
      {"indexed": true, "type": "address", "name": "owner"},
      {"indexed": false, "type": "string", "name": "githubUrl"},
      {"indexed": false, "type": "string", "name": "repoHash"}
    ],
    "name": "RepositoryRegistered",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {"indexed": true, "type": "uint256", "name": "violationId"},
      {"indexed": true, "type": "uint256", "name": "originalRepoId"},
      {"indexed": true, "type": "address", "name": "reporter"},
      {"indexed": false, "type": "string", "name": "violatingUrl"},
      {"indexed": false, "type": "uint256", "name": "similarityScore"}
    ],
    "name": "ViolationReported",
    "type": "event"
  }
] as const

// Infringement Bounty Contract ABI
export const INFRINGEMENT_BOUNTY_ABI = [
  {
    "inputs": [
      {"type": "string", "name": "url"},
      {"type": "string", "name": "licenseCID"},
      {"type": "string", "name": "dmcaCID"}
    ],
    "name": "reportInfringement",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "withdraw",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [{"type": "address", "name": ""}],
    "name": "rewards",
    "outputs": [{"type": "uint256"}],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "anonymous": false,
    "inputs": [
      {"indexed": true, "type": "address", "name": "reporter"},
      {"indexed": false, "type": "string", "name": "url"},
      {"indexed": false, "type": "uint256", "name": "amount"}
    ],
    "name": "BountyPaid",
    "type": "event"
  }
] as const

// Link Registry ABI
export const LINK_REGISTRY_ABI = [
  {
    "inputs": [{"type": "string", "name": ""}],
    "name": "linkRecords",
    "outputs": [
      {"type": "string", "name": "url"},
      {"type": "string", "name": "licenseCID"},
      {"type": "string", "name": "dmcaCID"},
      {"type": "uint8", "name": "status"},
      {"type": "uint256", "name": "timestamp"},
      {"type": "bool", "name": "exists"}
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "getLinkCount",
    "outputs": [{"type": "uint256"}],
    "stateMutability": "view",
    "type": "function"
  }
] as const