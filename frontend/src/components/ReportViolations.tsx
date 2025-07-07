import React, { useState } from 'react'
import { AlertTriangle, Search, ExternalLink, Loader2 } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/Card'
import { Button } from './ui/Button'
import { Input } from './ui/Input'
import { Badge } from './ui/Badge'
import { useRepoProtection, useContractReads } from '../hooks/useContracts'
import { useBackendApi } from '../hooks/useBackendApi'
import { isValidGitHubUrl } from '../lib/utils'
import toast from 'react-hot-toast'
import { useAccount } from 'wagmi'

export function ReportViolations() {
  const [originalRepoId, setOriginalRepoId] = useState('')
  const [violatingUrl, setViolatingUrl] = useState('')
  const [violations, setViolations] = useState<any[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [selectedRepo, setSelectedRepo] = useState<any>(null)

  const { address } = useAccount()
  const { reportViolation, isPending, isConfirming, isConfirmed } = useRepoProtection()
  const { getUserRepos, getRepository } = useContractReads()
  const { searchViolations, performSecurityAudit } = useBackendApi()

  const { data: userRepos } = getUserRepos(address!)

  const handleSearchViolations = async () => {
    if (!originalRepoId) {
      toast.error('Please select a repository')
      return
    }

    setIsSearching(true)
    try {
      const foundViolations = await searchViolations(parseInt(originalRepoId))
      setViolations(foundViolations)
      
      if (foundViolations.length === 0) {
        toast.success('No violations found - your repository appears safe!')
      } else {
        toast.success(`Found ${foundViolations.length} potential violations`)
      }
    } catch (error) {
      toast.error('Failed to search for violations')
    } finally {
      setIsSearching(false)
    }
  }

  const handleReportViolation = async (violation: any) => {
    try {
      // Generate evidence hash
      const evidenceData = {
        original_repo_id: originalRepoId,
        violating_url: violation.repo_url,
        similarity_score: violation.similarity,
        timestamp: Date.now()
      }
      const evidenceHash = btoa(JSON.stringify(evidenceData))

      await reportViolation(
        parseInt(originalRepoId),
        violation.repo_url,
        evidenceHash,
        Math.floor(violation.similarity * 100)
      )

      toast.success('Violation reported successfully!')
    } catch (error) {
      toast.error('Failed to report violation')
    }
  }

  const handleManualReport = async () => {
    if (!originalRepoId || !violatingUrl) {
      toast.error('Please fill in all fields')
      return
    }

    if (!isValidGitHubUrl(violatingUrl)) {
      toast.error('Please enter a valid GitHub URL')
      return
    }

    try {
      // Perform security audit to get similarity score
      const auditResult = await performSecurityAudit(violatingUrl)
      const similarityScore = 85 // Placeholder - would be calculated by backend

      const evidenceData = {
        original_repo_id: originalRepoId,
        violating_url: violatingUrl,
        similarity_score: similarityScore,
        timestamp: Date.now(),
        audit_findings: auditResult.total_findings || 0
      }
      const evidenceHash = btoa(JSON.stringify(evidenceData))

      await reportViolation(
        parseInt(originalRepoId),
        violatingUrl,
        evidenceHash,
        similarityScore
      )

      toast.success('Manual violation report submitted!')
      setViolatingUrl('')
    } catch (error) {
      toast.error('Failed to submit manual report')
    }
  }

  // Get repository details when repo ID changes
  React.useEffect(() => {
    if (originalRepoId) {
      const { data: repo } = getRepository(parseInt(originalRepoId))
      setSelectedRepo(repo)
    }
  }, [originalRepoId])

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Report Violations</h1>
        <p className="text-gray-600">
          Search for potential code violations and report them to earn bounties.
        </p>
      </div>

      {/* Repository Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Search className="h-5 w-5" />
            <span>Select Repository</span>
          </CardTitle>
          <CardDescription>
            Choose one of your registered repositories to search for violations
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Your Repositories
            </label>
            <select
              value={originalRepoId}
              onChange={(e) => setOriginalRepoId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select a repository...</option>
              {userRepos?.map((repoId) => (
                <option key={repoId.toString()} value={repoId.toString()}>
                  Repository #{repoId.toString()}
                </option>
              ))}
            </select>
          </div>

          {selectedRepo && (
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-medium text-blue-900 mb-2">Selected Repository</h4>
              <p className="text-sm text-blue-700">{selectedRepo.githubUrl}</p>
              <p className="text-xs text-blue-600 mt-1">
                License: {selectedRepo.licenseType} • 
                Registered: {new Date(Number(selectedRepo.registeredAt) * 1000).toLocaleDateString()}
              </p>
            </div>
          )}

          <Button 
            onClick={handleSearchViolations}
            disabled={!originalRepoId || isSearching}
            className="w-full"
          >
            {isSearching ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Searching for Violations...
              </>
            ) : (
              <>
                <Search className="h-4 w-4 mr-2" />
                Search for Violations
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Search Results */}
      {violations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-orange-500" />
              <span>Potential Violations Found</span>
            </CardTitle>
            <CardDescription>
              Review and report suspected code violations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {violations.map((violation, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 mb-1">{violation.name}</h4>
                      <p className="text-sm text-gray-600 mb-2">{violation.description}</p>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span>Language: {violation.language || 'Unknown'}</span>
                        <span>Created: {violation.created_at ? new Date(violation.created_at).toLocaleDateString() : 'Unknown'}</span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge 
                        variant={violation.similarity > 0.8 ? 'error' : violation.similarity > 0.6 ? 'warning' : 'secondary'}
                      >
                        {Math.round(violation.similarity * 100)}% match
                      </Badge>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <a
                      href={violation.repo_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 text-sm flex items-center space-x-1"
                    >
                      <span>{violation.repo_url}</span>
                      <ExternalLink className="h-3 w-3" />
                    </a>
                    <Button
                      size="sm"
                      onClick={() => handleReportViolation(violation)}
                      disabled={isPending || isConfirming || violation.similarity < 0.7}
                    >
                      Report Violation
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Manual Report */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <AlertTriangle className="h-5 w-5" />
            <span>Manual Violation Report</span>
          </CardTitle>
          <CardDescription>
            Report a specific repository that you believe violates your code
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Violating Repository URL
            </label>
            <Input
              placeholder="https://github.com/username/violating-repository"
              value={violatingUrl}
              onChange={(e) => setViolatingUrl(e.target.value)}
            />
            {violatingUrl && !isValidGitHubUrl(violatingUrl) && (
              <p className="text-sm text-red-600 mt-1">Please enter a valid GitHub repository URL</p>
            )}
          </div>

          <Button 
            onClick={handleManualReport}
            disabled={!originalRepoId || !violatingUrl || !isValidGitHubUrl(violatingUrl) || isPending || isConfirming}
            className="w-full"
          >
            {isPending || isConfirming ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Submitting Report...
              </>
            ) : (
              'Submit Manual Report'
            )}
          </Button>
        </CardContent>
      </Card>

      {/* No repositories message */}
      {userRepos && userRepos.length === 0 && (
        <Card>
          <CardContent className="pt-6 text-center">
            <AlertTriangle className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Repositories Found</h3>
            <p className="text-gray-600 mb-6">
              You need to register at least one repository before you can report violations.
            </p>
            <Button variant="outline">
              Register Your First Repository
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}