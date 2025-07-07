import React, { useState } from 'react'
import { DollarSign, ExternalLink, Loader2, Trophy, AlertTriangle } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/Card'
import { Button } from './ui/Button'
import { Input } from './ui/Input'
import { Badge } from './ui/Badge'
import { useInfringementBounty, useContractReads } from '../hooks/useContracts'
import { useBackendApi } from '../hooks/useBackendApi'
import { formatFilecoin, isValidGitHubUrl } from '../lib/utils'
import toast from 'react-hot-toast'
import { useAccount } from 'wagmi'

export function ClaimBounties() {
  const [reportUrl, setReportUrl] = useState('')
  const [licenseCID, setLicenseCID] = useState('')
  const [dmcaCID, setDmcaCID] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<any>(null)

  const { address } = useAccount()
  const { reportInfringement, withdrawRewards, isPending, isConfirming } = useInfringementBounty()
  const { getRewards } = useContractReads()
  const { performSecurityAudit } = useBackendApi()

  const { data: userRewards } = getRewards(address!)

  const handleAnalyzeUrl = async () => {
    if (!isValidGitHubUrl(reportUrl)) {
      toast.error('Please enter a valid GitHub repository URL')
      return
    }

    setIsAnalyzing(true)
    try {
      const result = await performSecurityAudit(reportUrl)
      setAnalysisResult(result)
      
      if (result.success && result.total_findings > 0) {
        toast.success(`Analysis complete! Found ${result.total_findings} security findings`)
      } else if (result.success) {
        toast.success('Analysis complete - no major security issues found')
      }
    } catch (error) {
      toast.error('Failed to analyze repository')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleReportInfringement = async () => {
    if (!reportUrl || !licenseCID || !dmcaCID) {
      toast.error('Please fill in all required fields')
      return
    }

    try {
      await reportInfringement(reportUrl, licenseCID, dmcaCID)
      
      // Reset form
      setReportUrl('')
      setLicenseCID('')
      setDmcaCID('')
      setAnalysisResult(null)
      
      toast.success('Infringement reported! Bounty will be credited to your account.')
    } catch (error) {
      toast.error('Failed to report infringement')
    }
  }

  const handleWithdraw = async () => {
    try {
      await withdrawRewards()
      toast.success('Withdrawal initiated!')
    } catch (error) {
      toast.error('Withdrawal failed')
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Claim Bounties</h1>
        <p className="text-gray-600">
          Report new infringing repositories and earn rewards for protecting intellectual property.
        </p>
      </div>

      {/* Rewards Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Trophy className="h-5 w-5 text-yellow-500" />
            <span>Your Rewards</span>
          </CardTitle>
          <CardDescription>
            Accumulated bounty rewards from reporting violations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-3xl font-bold text-gray-900">
                {userRewards ? formatFilecoin(userRewards) : '0 tFIL'}
              </p>
              <p className="text-sm text-gray-600">Available for withdrawal</p>
            </div>
            <Button 
              onClick={handleWithdraw}
              disabled={!userRewards || userRewards === 0n || isPending || isConfirming}
              size="lg"
            >
              {isPending || isConfirming ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <DollarSign className="h-4 w-4 mr-2" />
                  Withdraw Rewards
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Report New Infringement */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <AlertTriangle className="h-5 w-5 text-orange-500" />
            <span>Report New Infringement</span>
          </CardTitle>
          <CardDescription>
            Submit a new infringing repository to earn a bounty reward
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* URL Input and Analysis */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Repository URL
              </label>
              <div className="flex space-x-2">
                <Input
                  placeholder="https://github.com/username/infringing-repository"
                  value={reportUrl}
                  onChange={(e) => setReportUrl(e.target.value)}
                  className="flex-1"
                />
                <Button 
                  onClick={handleAnalyzeUrl}
                  disabled={!reportUrl || !isValidGitHubUrl(reportUrl) || isAnalyzing}
                  variant="outline"
                >
                  {isAnalyzing ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    'Analyze'
                  )}
                </Button>
              </div>
              {reportUrl && !isValidGitHubUrl(reportUrl) && (
                <p className="text-sm text-red-600 mt-1">Please enter a valid GitHub repository URL</p>
              )}
            </div>

            {/* Analysis Results */}
            {analysisResult && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">Security Analysis Results</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                  <div>
                    <p className="text-sm text-gray-600">Total Findings</p>
                    <p className="text-lg font-semibold">{analysisResult.total_findings || 0}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Critical</p>
                    <p className="text-lg font-semibold text-red-600">{analysisResult.critical_findings || 0}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">High</p>
                    <p className="text-lg font-semibold text-orange-600">{analysisResult.high_findings || 0}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Files Scanned</p>
                    <p className="text-lg font-semibold">{analysisResult.files_scanned || 0}</p>
                  </div>
                </div>
                
                {analysisResult.total_findings > 0 ? (
                  <Badge variant="error">High probability of infringement detected</Badge>
                ) : (
                  <Badge variant="success">No obvious infringement detected</Badge>
                )}
              </div>
            )}
          </div>

          {/* IPFS References */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                License IPFS CID
              </label>
              <Input
                placeholder="QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
                value={licenseCID}
                onChange={(e) => setLicenseCID(e.target.value)}
              />
              <p className="text-xs text-gray-500 mt-1">
                IPFS hash of the original license document
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                DMCA Notice IPFS CID
              </label>
              <Input
                placeholder="QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
                value={dmcaCID}
                onChange={(e) => setDmcaCID(e.target.value)}
              />
              <p className="text-xs text-gray-500 mt-1">
                IPFS hash of the DMCA takedown notice
              </p>
            </div>
          </div>

          {/* Submit Button */}
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="flex items-start space-x-3">
              <DollarSign className="h-5 w-5 text-blue-600 mt-0.5" />
              <div>
                <h4 className="font-medium text-blue-900">Bounty Reward</h4>
                <p className="text-sm text-blue-700">
                  Earn 1 tFIL for each verified infringement report. Reports are automatically 
                  verified through smart contract checks.
                </p>
              </div>
            </div>
          </div>

          <Button 
            onClick={handleReportInfringement}
            disabled={!reportUrl || !licenseCID || !dmcaCID || isPending || isConfirming}
            className="w-full"
            size="lg"
          >
            {isPending || isConfirming ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Submitting Report...
              </>
            ) : (
              <>
                <Trophy className="h-4 w-4 mr-2" />
                Submit Infringement Report
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* How It Works */}
      <Card>
        <CardHeader>
          <CardTitle>How Bounty Claims Work</CardTitle>
          <CardDescription>
            Understanding the infringement reporting and reward process
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-xl font-bold text-blue-600">1</span>
              </div>
              <h4 className="font-medium text-gray-900 mb-2">Discover Infringement</h4>
              <p className="text-sm text-gray-600">
                Find repositories that infringe on protected intellectual property
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-xl font-bold text-blue-600">2</span>
              </div>
              <h4 className="font-medium text-gray-900 mb-2">Submit Evidence</h4>
              <p className="text-sm text-gray-600">
                Provide IPFS links to license documents and DMCA notices
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-xl font-bold text-blue-600">3</span>
              </div>
              <h4 className="font-medium text-gray-900 mb-2">Earn Rewards</h4>
              <p className="text-sm text-gray-600">
                Receive bounty payments for verified infringement reports
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}