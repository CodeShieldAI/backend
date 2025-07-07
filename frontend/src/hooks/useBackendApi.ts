import { useState } from 'react'
import toast from 'react-hot-toast'
import { BACKEND_API } from '../config/web3'

interface AnalysisResult {
  success: boolean
  repo_hash?: string
  fingerprint?: string
  key_features?: string
  total_files?: number
  analysis?: any
  error?: string
}

interface SecurityAuditResult {
  success: boolean
  audit_id?: number
  findings?: any[]
  total_findings?: number
  critical_findings?: number
  high_findings?: number
  medium_findings?: number
  low_findings?: number
  error?: string
}

export function useBackendApi() {
  const [isLoading, setIsLoading] = useState(false)

  const analyzeRepository = async (githubUrl: string): Promise<AnalysisResult> => {
    setIsLoading(true)
    try {
      const response = await fetch(`${BACKEND_API}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ github_url: githubUrl })
      })
      
      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`)
      }
      
      const data = await response.json()
      
      if (data.success) {
        toast.success('Repository analyzed successfully!')
      } else {
        toast.error(data.error || 'Analysis failed')
      }
      
      return data
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Analysis failed'
      toast.error(errorMsg)
      return { success: false, error: errorMsg }
    } finally {
      setIsLoading(false)
    }
  }

  const performSecurityAudit = async (url: string): Promise<SecurityAuditResult> => {
    setIsLoading(true)
    try {
      const response = await fetch(`${BACKEND_API}/api/audit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input_url: url })
      })
      
      if (!response.ok) {
        throw new Error(`Security audit failed: ${response.statusText}`)
      }
      
      const data = await response.json()
      
      if (data.success) {
        toast.success(`Security audit completed! Found ${data.total_findings} findings`)
      } else {
        toast.error(data.error || 'Security audit failed')
      }
      
      return data
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Security audit failed'
      toast.error(errorMsg)
      return { success: false, error: errorMsg }
    } finally {
      setIsLoading(false)
    }
  }

  const searchViolations = async (repoId: number): Promise<any[]> => {
    setIsLoading(true)
    try {
      const response = await fetch(`${BACKEND_API}/api/search-violations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_id: repoId })
      })
      
      if (!response.ok) {
        throw new Error(`Violation search failed: ${response.statusText}`)
      }
      
      const data = await response.json()
      return data.violations || []
    } catch (error) {
      toast.error('Failed to search for violations')
      return []
    } finally {
      setIsLoading(false)
    }
  }

  const cleanUrls = async (text: string) => {
    setIsLoading(true)
    try {
      const response = await fetch(`${BACKEND_API}/api/clean-urls`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url_text: text })
      })
      
      if (!response.ok) {
        throw new Error(`URL cleaning failed: ${response.statusText}`)
      }
      
      return await response.json()
    } catch (error) {
      toast.error('Failed to clean URLs')
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' }
    } finally {
      setIsLoading(false)
    }
  }

  return {
    analyzeRepository,
    performSecurityAudit,
    searchViolations,
    cleanUrls,
    isLoading
  }
}