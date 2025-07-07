import { useReadContract, useWriteContract, useWaitForTransactionReceipt } from 'wagmi'
import { parseEther } from 'viem'
import toast from 'react-hot-toast'
import { CONTRACT_ADDRESSES } from '../config/web3'
import { 
  GITHUB_REPO_PROTECTION_ABI, 
  INFRINGEMENT_BOUNTY_ABI,
  LINK_REGISTRY_ABI 
} from '../contracts/abis'

export function useRepoProtection() {
  const { writeContract, data: hash, isPending, error } = useWriteContract()
  
  const { isLoading: isConfirming, isSuccess: isConfirmed } = 
    useWaitForTransactionReceipt({ hash })

  const registerRepository = async (
    githubUrl: string,
    repoHash: string,
    codeFingerprint: string,
    keyFeatures: string[],
    licenseType: string = 'MIT',
    ipfsMetadata: string = ''
  ) => {
    try {
      await writeContract({
        address: CONTRACT_ADDRESSES.GitHubRepoProtection,
        abi: GITHUB_REPO_PROTECTION_ABI,
        functionName: 'registerRepository',
        args: [githubUrl, repoHash, codeFingerprint, keyFeatures, licenseType, ipfsMetadata]
      })
      
      toast.success('Repository registration initiated!')
    } catch (error) {
      console.error('Registration failed:', error)
      toast.error('Registration failed')
      throw error
    }
  }

  const reportViolation = async (
    originalRepoId: number,
    violatingUrl: string,
    evidenceHash: string,
    similarityScore: number
  ) => {
    try {
      await writeContract({
        address: CONTRACT_ADDRESSES.GitHubRepoProtection,
        abi: GITHUB_REPO_PROTECTION_ABI,
        functionName: 'reportViolation',
        args: [BigInt(originalRepoId), violatingUrl, evidenceHash, BigInt(similarityScore)]
      })
      
      toast.success('Violation report submitted!')
    } catch (error) {
      console.error('Violation report failed:', error)
      toast.error('Violation report failed')
      throw error
    }
  }

  return {
    registerRepository,
    reportViolation,
    hash,
    isPending,
    isConfirming,
    isConfirmed,
    error
  }
}

export function useInfringementBounty() {
  const { writeContract, data: hash, isPending } = useWriteContract()
  const { isLoading: isConfirming, isSuccess: isConfirmed } = 
    useWaitForTransactionReceipt({ hash })

  const reportInfringement = async (
    url: string,
    licenseCID: string,
    dmcaCID: string
  ) => {
    try {
      await writeContract({
        address: CONTRACT_ADDRESSES.InfringementBounty,
        abi: INFRINGEMENT_BOUNTY_ABI,
        functionName: 'reportInfringement',
        args: [url, licenseCID, dmcaCID]
      })
      
      toast.success('Infringement report submitted!')
    } catch (error) {
      console.error('Infringement report failed:', error)
      toast.error('Infringement report failed')
      throw error
    }
  }

  const withdrawRewards = async () => {
    try {
      await writeContract({
        address: CONTRACT_ADDRESSES.InfringementBounty,
        abi: INFRINGEMENT_BOUNTY_ABI,
        functionName: 'withdraw'
      })
      
      toast.success('Withdrawal initiated!')
    } catch (error) {
      console.error('Withdrawal failed:', error)
      toast.error('Withdrawal failed')
      throw error
    }
  }

  return {
    reportInfringement,
    withdrawRewards,
    hash,
    isPending,
    isConfirming,
    isConfirmed
  }
}

export function useContractReads() {
  const { data: totalRepos } = useReadContract({
    address: CONTRACT_ADDRESSES.GitHubRepoProtection,
    abi: GITHUB_REPO_PROTECTION_ABI,
    functionName: 'getTotalRepositories'
  })

  const { data: totalViolations } = useReadContract({
    address: CONTRACT_ADDRESSES.GitHubRepoProtection,
    abi: GITHUB_REPO_PROTECTION_ABI,
    functionName: 'getTotalViolations'
  })

  const getUserRepos = (address: string) => {
    return useReadContract({
      address: CONTRACT_ADDRESSES.GitHubRepoProtection,
      abi: GITHUB_REPO_PROTECTION_ABI,
      functionName: 'getUserRepositories',
      args: [address as `0x${string}`]
    })
  }

  const getRewards = (address: string) => {
    return useReadContract({
      address: CONTRACT_ADDRESSES.InfringementBounty,
      abi: INFRINGEMENT_BOUNTY_ABI,
      functionName: 'rewards',
      args: [address as `0x${string}`]
    })
  }

  const getRepository = (repoId: number) => {
    return useReadContract({
      address: CONTRACT_ADDRESSES.GitHubRepoProtection,
      abi: GITHUB_REPO_PROTECTION_ABI,
      functionName: 'getRepository',
      args: [BigInt(repoId)]
    })
  }

  return {
    totalRepos: totalRepos ? Number(totalRepos) : 0,
    totalViolations: totalViolations ? Number(totalViolations) : 0,
    getUserRepos,
    getRewards,
    getRepository
  }
}