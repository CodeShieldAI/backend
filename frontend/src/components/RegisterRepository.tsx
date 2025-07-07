import React, { useState } from 'react'
import { Github, Loader2, CheckCircle, AlertCircle } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/Card'
import { Button } from './ui/Button'
import { Input } from './ui/Input'
import { Badge } from './ui/Badge'
import { useRepoProtection } from '../hooks/useContracts'
import { useBackendApi } from '../hooks/useBackendApi'
import { isValidGitHubUrl } from '../lib/utils'
import toast from 'react-hot-toast'

export function RegisterRepository() {
  const [githubUrl, setGithubUrl] = useState('')
  const [licenseType, setLicenseType] = useState('MIT')
  const [analysisResult, setAnalysisResult] = useState<any>(null)
  const [step, setStep] = useState<'input' | 'analyzing' | 'analyzed' | 'registering' | 'completed'>('input')

  const { registerRepository, isPending, isConfirming, isConfirmed } = useRepoProtection()
  const { analyzeRepository, isLoading: isAnalyzing } = useBackendApi()

  const handleAnalyze = async () => {
    if (!isValidGitHubUrl(githubUrl)) {
      toast.error('Please enter a valid GitHub repository URL')
      return
    }

    setStep('analyzing')
    const result = await analyzeRepository(githubUrl)
    
    if (result.success) {
      setAnalysisResult(result)
      setStep('analyzed')
    } else {
      setStep('input')
      toast.error(result.error || 'Analysis failed')
    }
  }

  const handleRegister = async () => {
    if (!analysisResult) return

    setStep('registering')
    
    try {
      const keyFeatures = analysisResult.key_features
        ? analysisResult.key_features.split('\n').filter((f: string) => f.trim())
        : ['Repository analysis completed']

      await registerRepository(
        githubUrl,
        analysisResult.repo_hash,
        analysisResult.fingerprint,
        keyFeatures,
        licenseType,
        '' // IPFS metadata - can be added later
      )
    } catch (error) {
      setStep('analyzed')
    }
  }

  React.useEffect(() => {
    if (isConfirmed) {
      setStep('completed')
      toast.success('Repository registered successfully!')
    }
  }, [isConfirmed])

  const resetForm = () => {
    setGithubUrl('')
    setLicenseType('MIT')
    setAnalysisResult(null)
    setStep('input')
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Register Repository</h1>
        <p className="text-gray-600">
          Protect your GitHub repository by registering it on the Filecoin network.
        </p>
      </div>

      {/* Progress Indicator */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            {[
              { id: 'input', label: 'Repository URL', completed: ['analyzing', 'analyzed', 'registering', 'completed'].includes(step) },
              { id: 'analyzing', label: 'Analysis', completed: ['analyzed', 'registering', 'completed'].includes(step) },
              { id: 'registering', label: 'Registration', completed: ['completed'].includes(step) },
              { id: 'completed', label: 'Complete', completed: step === 'completed' }
            ].map((stepItem, index) => (
              <div key={stepItem.id} className="flex items-center">
                <div className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
                  stepItem.completed 
                    ? 'bg-green-500 border-green-500 text-white' 
                    : step === stepItem.id
                    ? 'border-blue-500 text-blue-500'
                    : 'border-gray-300 text-gray-300'
                }`}>
                  {stepItem.completed ? (
                    <CheckCircle className="h-5 w-5" />
                  ) : (
                    <span className="text-sm font-medium">{index + 1}</span>
                  )}
                </div>
                <span className={`ml-2 text-sm font-medium ${
                  stepItem.completed ? 'text-green-600' : 'text-gray-500'
                }`}>
                  {stepItem.label}
                </span>
                {index < 3 && (
                  <div className={`w-12 h-0.5 mx-4 ${
                    stepItem.completed ? 'bg-green-500' : 'bg-gray-300'
                  }`} />
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Repository Input */}
      {(step === 'input' || step === 'analyzing') && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Github className="h-5 w-5" />
              <span>Repository Information</span>
            </CardTitle>
            <CardDescription>
              Enter your GitHub repository URL to start the protection process
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                GitHub Repository URL
              </label>
              <Input
                placeholder="https://github.com/username/repository"
                value={githubUrl}
                onChange={(e) => setGithubUrl(e.target.value)}
                disabled={step === 'analyzing'}
              />
              {githubUrl && !isValidGitHubUrl(githubUrl) && (
                <p className="text-sm text-red-600 mt-1">Please enter a valid GitHub repository URL</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                License Type
              </label>
              <select
                value={licenseType}
                onChange={(e) => setLicenseType(e.target.value)}
                disabled={step === 'analyzing'}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="MIT">MIT License</option>
                <option value="Apache-2.0">Apache 2.0 License</option>
                <option value="GPL-3.0">GPL 3.0 License</option>
                <option value="BSD-3-Clause">BSD 3-Clause License</option>
                <option value="Proprietary">Proprietary</option>
              </select>
            </div>

            <Button 
              onClick={handleAnalyze} 
              disabled={!githubUrl || !isValidGitHubUrl(githubUrl) || step === 'analyzing'}
              className="w-full"
            >
              {step === 'analyzing' ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Analyzing Repository...
                </>
              ) : (
                'Analyze Repository'
              )}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Analysis Results */}
      {(step === 'analyzed' || step === 'registering') && analysisResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <span>Analysis Complete</span>
            </CardTitle>
            <CardDescription>
              Repository analysis completed successfully
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium text-gray-700 mb-1">Repository Hash</p>
                <p className="text-sm font-mono text-gray-600 bg-gray-50 p-2 rounded">
                  {analysisResult.repo_hash?.slice(0, 16)}...
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700 mb-1">Code Fingerprint</p>
                <p className="text-sm font-mono text-gray-600 bg-gray-50 p-2 rounded">
                  {analysisResult.fingerprint?.slice(0, 16)}...
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700 mb-1">Total Files</p>
                <p className="text-sm text-gray-900">{analysisResult.total_files}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700 mb-1">License</p>
                <Badge variant="secondary">{licenseType}</Badge>
              </div>
            </div>

            {analysisResult.key_features && (
              <div>
                <p className="text-sm font-medium text-gray-700 mb-2">Key Features</p>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">
                    {analysisResult.key_features}
                  </p>
                </div>
              </div>
            )}

            <Button 
              onClick={handleRegister}
              disabled={step === 'registering' || isPending || isConfirming}
              className="w-full"
            >
              {step === 'registering' || isPending || isConfirming ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  {isPending ? 'Confirming...' : isConfirming ? 'Processing...' : 'Registering...'}
                </>
              ) : (
                'Register Repository'
              )}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Completion */}
      {step === 'completed' && (
        <Card>
          <CardContent className="pt-6 text-center">
            <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-gray-900 mb-2">Repository Registered!</h3>
            <p className="text-gray-600 mb-6">
              Your repository has been successfully registered and is now protected on the Filecoin network.
            </p>
            <div className="flex justify-center space-x-4">
              <Button onClick={resetForm} variant="outline">
                Register Another Repository
              </Button>
              <Button onClick={() => window.open(githubUrl, '_blank')}>
                View Repository
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}