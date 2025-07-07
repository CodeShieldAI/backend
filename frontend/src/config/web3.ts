import { defaultWagmiConfig } from '@web3modal/wagmi/react/config'
import { filecoinCalibration } from 'wagmi/chains'
import { createWeb3Modal } from '@web3modal/wagmi/react'

// Get projectId from https://cloud.walletconnect.com
const projectId = 'your-project-id-here' // You'll need to get this from WalletConnect

const metadata = {
  name: 'GitHub Repository Protection',
  description: 'Protect your GitHub repositories on Filecoin',
  url: 'https://github-protection.app',
  icons: ['https://avatars.githubusercontent.com/u/37784886']
}

const chains = [filecoinCalibration] as const

export const config = defaultWagmiConfig({
  chains,
  projectId,
  metadata,
})

createWeb3Modal({
  wagmiConfig: config,
  projectId,
  enableAnalytics: true,
  themeMode: 'light',
  themeVariables: {
    '--w3m-color-mix': '#2563eb',
    '--w3m-color-mix-strength': 20
  }
})

// Contract addresses
export const CONTRACT_ADDRESSES = {
  GitHubRepoProtection: '0x19054030669efBFc413bA3729b63eCfD3Bdc22B5',
  DealClient: '0x592eC554ec3Af631d76981a680f699F9618B5687',
  LinkRegistry: '0x5fa19b4a48C20202055c8a6fdf16688633617D50',
  LinkRegistryWithDeals: '0x25bc04a49997e25B7482eEcbeB2Ec67740AEd5a6',
  InfringementBounty: '0xA2cD4CC41b8DCE00D002Aa4B29050f2d53705400'
} as const

// Backend API URL
export const BACKEND_API = 'http://localhost:8000'