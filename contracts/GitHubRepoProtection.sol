// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title GitHubRepoProtection
 * @dev Smart contract for registering and protecting GitHub repositories.
 * @notice This contract is designed to be deployed on an EVM-compatible network like Filecoin's FEVM.
 */
contract GitHubRepoProtection is Ownable, ReentrancyGuard {
    using Counters for Counters.Counter;
    
    Counters.Counter private _repoIds;
    Counters.Counter private _violationIds;
    
    // --- Enums ---

    /**
     * @dev Describes the purpose of a submission to the contract.
     */
    enum SubmissionType {
        Register,
        ReportViolation,
        UpdateLicense
    }

    enum ViolationStatus {
        Pending,
        Verified,
        Disputed,
        Resolved,
        Rejected
    }

    // --- Structs ---
    
    struct Repository {
        uint256 id;
        address owner;
        string githubUrl;
        string repoHash; // A unique hash of the repository content
        string codeFingerprint; // A more detailed fingerprint for similarity checks
        string[] keyFeatures;
        string licenseType;
        uint256 registeredAt;
        bool isActive;
        string ipfsMetadata; // Link to metadata on IPFS
    }
    
    struct CodeViolation {
        uint256 id;
        uint256 originalRepoId;
        address reporter;
        string violatingUrl;
        string evidenceHash;
        uint256 similarityScore; // 0-100
        ViolationStatus status;
        uint256 reportedAt;
        string dmcaReference;
    }
    
    // --- Mappings ---

    mapping(uint256 => Repository) public repositories;
    mapping(uint256 => CodeViolation) public violations;
    mapping(address => uint256[]) public userRepositories;
    mapping(string => uint256) public repoHashToId;
    mapping(uint256 => uint256[]) public repoViolations;
    
    // --- Events ---
    
    event RepositoryRegistered(
        uint256 indexed repoId,
        address indexed owner,
        string githubUrl,
        string repoHash
    );
    
    event ViolationReported(
        uint256 indexed violationId,
        uint256 indexed originalRepoId,
        address indexed reporter,
        string violatingUrl,
        uint256 similarityScore
    );
    
    event ViolationStatusUpdated(
        uint256 indexed violationId,
        ViolationStatus newStatus,
        string dmcaReference
    );
    
    event LicenseUpdated(
        uint256 indexed repoId,
        string newLicense
    );

    /**
     * @dev Emitted when any submission is processed, indicating its purpose.
     * @notice This event is key for backend services to track on-chain actions.
     */
    event SubmissionProcessed(
        address indexed user,
        SubmissionType indexed submissionType,
        uint256 relevantId, // repoId for Register/UpdateLicense, violationId for ReportViolation
        string details
    );
    
    // --- Constructor ---

    /**
     * @dev Sets the initial owner of the contract to the deployer.
     * @notice This is required for OpenZeppelin Contracts v5.0+
     */
    constructor() Ownable(msg.sender) {}

    // --- Modifiers ---

    modifier onlyRepoOwner(uint256 repoId) {
        require(repositories[repoId].owner == msg.sender, "Not repository owner");
        _;
    }
    
    modifier validRepo(uint256 repoId) {
        require(repositories[repoId].id != 0, "Repository does not exist");
        require(repositories[repoId].isActive, "Repository is not active");
        _;
    }
    
    // --- Core Functions ---

    /**
     * @dev NEW: A unified function to handle different types of submissions.
     * @notice This is the primary function your frontend should call.
     * @param submissionType The purpose of this transaction (Register, ReportViolation, UpdateLicense).
     * @param repoId The ID of the repository (used for UpdateLicense and ReportViolation).
     * @param githubUrl The URL of the repository (used for Register and ReportViolation).
     * @param repoHash A unique hash of the repository content (used for Register).
     * @param codeFingerprint A detailed fingerprint of the code (used for Register).
     * @param keyFeatures An array of strings describing key features (used for Register).
     * @param licenseType The license of the repository (used for Register and UpdateLicense).
     * @param ipfsMetadata A link to IPFS metadata (used for Register).
     * @param evidenceHash A hash of evidence for a violation report (used for ReportViolation).
     * @param similarityScore A score from 0-100 indicating code similarity (used for ReportViolation).
     */
    function processSubmission(
        SubmissionType submissionType,
        uint256 repoId,
        string memory githubUrl,
        string memory repoHash,
        string memory codeFingerprint,
        string[] memory keyFeatures,
        string memory licenseType,
        string memory ipfsMetadata,
        string memory evidenceHash,
        uint256 similarityScore
    ) external nonReentrant {
        if (submissionType == SubmissionType.Register) {
            uint256 newRepoId = _registerRepository(githubUrl, repoHash, codeFingerprint, keyFeatures, licenseType, ipfsMetadata);
            emit SubmissionProcessed(msg.sender, submissionType, newRepoId, string.concat("Registered new repo: ", githubUrl));
        } else if (submissionType == SubmissionType.ReportViolation) {
            uint256 newViolationId = _reportViolation(repoId, githubUrl, evidenceHash, similarityScore);
            emit SubmissionProcessed(msg.sender, submissionType, newViolationId, string.concat("Reported violation for repoId ", _toString(repoId)));
        } else if (submissionType == SubmissionType.UpdateLicense) {
            _updateLicense(repoId, licenseType);
            emit SubmissionProcessed(msg.sender, submissionType, repoId, string.concat("Updated license for repoId ", _toString(repoId)));
        } else {
            revert("Invalid submission type");
        }
    }

    // --- Existing Functions (can be made internal if desired) ---
    
    /**
     * @dev Register a new GitHub repository for protection. Can be called directly or via processSubmission.
     */
    function registerRepository(
        string memory githubUrl,
        string memory repoHash,
        string memory codeFingerprint,
        string[] memory keyFeatures,
        string memory licenseType,
        string memory ipfsMetadata
    ) external nonReentrant returns (uint256) {
        uint256 newRepoId = _registerRepository(githubUrl, repoHash, codeFingerprint, keyFeatures, licenseType, ipfsMetadata);
        emit SubmissionProcessed(msg.sender, SubmissionType.Register, newRepoId, string.concat("Registered new repo: ", githubUrl));
        return newRepoId;
    }
    
    /**
     * @dev Report a code violation. Can be called directly or via processSubmission.
     */
    function reportViolation(
        uint256 originalRepoId,
        string memory violatingUrl,
        string memory evidenceHash,
        uint256 similarityScore
    ) external validRepo(originalRepoId) nonReentrant returns (uint256) {
        uint256 newViolationId = _reportViolation(originalRepoId, violatingUrl, evidenceHash, similarityScore);
        emit SubmissionProcessed(msg.sender, SubmissionType.ReportViolation, newViolationId, string.concat("Reported violation for repoId ", _toString(originalRepoId)));
        return newViolationId;
    }
    
    /**
     * @dev Update repository license. Can be called directly or via processSubmission.
     */
    function updateLicense(
        uint256 repoId,
        string memory newLicense
    ) external onlyRepoOwner(repoId) {
        _updateLicense(repoId, newLicense);
        emit SubmissionProcessed(msg.sender, SubmissionType.UpdateLicense, repoId, string.concat("Updated license for repoId ", _toString(repoId)));
    }

    /**
     * @dev Update violation status (owner or authorized agent)
     */
    function updateViolationStatus(
        uint256 violationId,
        ViolationStatus newStatus,
        string memory dmcaReference
    ) external {
        CodeViolation storage violation = violations[violationId];
        require(violation.id != 0, "Violation does not exist");
        
        Repository memory repo = repositories[violation.originalRepoId];
        require(
            msg.sender == repo.owner || msg.sender == owner(),
            "Not authorized"
        );
        
        violation.status = newStatus;
        if (bytes(dmcaReference).length > 0) {
            violation.dmcaReference = dmcaReference;
        }
        
        emit ViolationStatusUpdated(violationId, newStatus, dmcaReference);
    }
    
    /**
     * @dev Deactivate repository
     */
    function deactivateRepository(uint256 repoId) external onlyRepoOwner(repoId) {
        repositories[repoId].isActive = false;
    }
    
    // --- Internal Logic Functions ---

    function _registerRepository(
        string memory githubUrl,
        string memory repoHash,
        string memory codeFingerprint,
        string[] memory keyFeatures,
        string memory licenseType,
        string memory ipfsMetadata
    ) internal returns (uint256) {
        require(bytes(githubUrl).length > 0, "GitHub URL required");
        require(bytes(repoHash).length > 0, "Repository hash required");
        require(repoHashToId[repoHash] == 0, "Repository already registered");
        
        _repoIds.increment();
        uint256 newRepoId = _repoIds.current();
        
        repositories[newRepoId] = Repository({
            id: newRepoId,
            owner: msg.sender,
            githubUrl: githubUrl,
            repoHash: repoHash,
            codeFingerprint: codeFingerprint,
            keyFeatures: keyFeatures,
            licenseType: licenseType,
            registeredAt: block.timestamp,
            isActive: true,
            ipfsMetadata: ipfsMetadata
        });
        
        userRepositories[msg.sender].push(newRepoId);
        repoHashToId[repoHash] = newRepoId;
        
        emit RepositoryRegistered(newRepoId, msg.sender, githubUrl, repoHash);
        
        return newRepoId;
    }

    function _reportViolation(
        uint256 originalRepoId,
        string memory violatingUrl,
        string memory evidenceHash,
        uint256 similarityScore
    ) internal validRepo(originalRepoId) returns (uint256) {
        require(bytes(violatingUrl).length > 0, "Violating URL required");
        require(similarityScore <= 100, "Invalid similarity score");
        require(similarityScore >= 70, "Similarity score too low"); // Minimum threshold
        
        _violationIds.increment();
        uint256 newViolationId = _violationIds.current();
        
        violations[newViolationId] = CodeViolation({
            id: newViolationId,
            originalRepoId: originalRepoId,
            reporter: msg.sender,
            violatingUrl: violatingUrl,
            evidenceHash: evidenceHash,
            similarityScore: similarityScore,
            status: ViolationStatus.Pending,
            reportedAt: block.timestamp,
            dmcaReference: ""
        });
        
        repoViolations[originalRepoId].push(newViolationId);
        
        emit ViolationReported(
            newViolationId,
            originalRepoId,
            msg.sender,
            violatingUrl,
            similarityScore
        );
        
        return newViolationId;
    }

    function _updateLicense(uint256 repoId, string memory newLicense) internal onlyRepoOwner(repoId) {
        repositories[repoId].licenseType = newLicense;
        emit LicenseUpdated(repoId, newLicense);
    }

    // --- View Functions ---
    
    function getRepository(uint256 repoId) external view returns (Repository memory) {
        return repositories[repoId];
    }
    
    function getViolation(uint256 violationId) external view returns (CodeViolation memory) {
        return violations[violationId];
    }
    
    function getUserRepositories(address user) external view returns (uint256[] memory) {
        return userRepositories[user];
    }
    
    function getRepositoryViolations(uint256 repoId) external view returns (uint256[] memory) {
        return repoViolations[repoId];
    }
    
    function getRepositoryByHash(string memory repoHash) external view returns (Repository memory) {
        uint256 repoId = repoHashToId[repoHash];
        require(repoId != 0, "Repository not found");
        return repositories[repoId];
    }
    
    function getTotalRepositories() external view returns (uint256) {
        return _repoIds.current();
    }
    
    function getTotalViolations() external view returns (uint256) {
        return _violationIds.current();
    }

    // --- Helper Functions ---

    function _toString(uint256 value) internal pure returns (string memory) {
        if (value == 0) {
            return "0";
        }
        uint256 temp = value;
        uint256 digits;
        while (temp != 0) {
            digits++;
            temp /= 10;
        }
        bytes memory buffer = new bytes(digits);
        while (value != 0) {
            digits -= 1;
            buffer[digits] = bytes1(uint8(48 + uint256(value % 10)));
            value /= 10;
        }
        return string(buffer);
    }
}
