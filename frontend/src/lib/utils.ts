import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatAddress(address: string) {
  return `${address.slice(0, 6)}...${address.slice(-4)}`
}

export function formatHash(hash: string) {
  return `${hash.slice(0, 8)}...${hash.slice(-8)}`
}

export function formatDate(timestamp: number) {
  return new Date(timestamp * 1000).toLocaleDateString()
}

export function formatFilecoin(amount: bigint) {
  return `${Number(amount) / 1e18} tFIL`
}

export function isValidGitHubUrl(url: string): boolean {
  const githubRegex = /^https:\/\/github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+\/?$/
  return githubRegex.test(url)
}

export function extractRepoFromUrl(url: string): { owner: string; repo: string } | null {
  const match = url.match(/github\.com\/([^\/]+)\/([^\/]+)/)
  if (!match) return null
  return { owner: match[1], repo: match[2] }
}