import React from 'react'
import { useAccount } from 'wagmi'
import { Github, Shield, AlertTriangle, DollarSign, ExternalLink } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/Card'
import { Badge } from './ui/Badge'
import { Button } from './ui/Button'
import { useContractReads } from '../hooks/useContracts'
import { formatAddress, formatFilecoin } from '../lib/utils'

export function Dashboard() {
  const { address } = useAccount()
  const { totalRepos, totalViolations, getUserRepos, getRewards } = useContractReads()
  
  const { data: userRepos } = getUserRepos(address!)
  const { data: userRewards } = getRewards(address!)

  const stats = [
    {
      title: 'Total Repositories',
      value: totalRepos.toLocaleString(),
      description: 'Registered on network',
      icon: Github,
      color: 'bg-blue-500'
    },
    {
      title: 'Total Violations',
      value: totalViolations.toLocaleString(),
      description: 'Reported violations',
      icon: AlertTriangle,
      color: 'bg-orange-500'
    },
    {
      title: 'Your Repositories',
      value: userRepos ? userRepos.length.toString() : '0',
      description: 'Your protected repos',
      icon: Shield,
      color: 'bg-green-500'
    },
    {
      title: 'Available Rewards',
      value: userRewards ? formatFilecoin(userRewards) : '0 tFIL',
      description: 'Ready to withdraw',
      icon: DollarSign,
      color: 'bg-purple-500'
    }
  ]

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">
          Welcome back! Here's an overview of your repository protection status.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <Card key={stat.title} className="overflow-hidden">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">{stat.title}</p>
                    <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                    <p className="text-xs text-gray-500 mt-1">{stat.description}</p>
                  </div>
                  <div className={`p-3 rounded-full ${stat.color}`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Github className="h-5 w-5" />
              <span>Your Protected Repositories</span>
            </CardTitle>
            <CardDescription>
              Repositories you've registered for protection
            </CardDescription>
          </CardHeader>
          <CardContent>
            {userRepos && userRepos.length > 0 ? (
              <div className="space-y-3">
                {userRepos.slice(0, 5).map((repoId) => (
                  <RepositoryItem key={repoId.toString()} repoId={Number(repoId)} />
                ))}
                {userRepos.length > 5 && (
                  <p className="text-sm text-gray-500 text-center pt-2">
                    +{userRepos.length - 5} more repositories
                  </p>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <Github className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">No repositories registered yet</p>
                <p className="text-sm text-gray-400">Start by registering your first repository</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5" />
              <span>Recent Network Activity</span>
            </CardTitle>
            <CardDescription>
              Latest violations and reports across the network
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                <div>
                  <p className="text-sm font-medium text-red-900">High similarity violation</p>
                  <p className="text-xs text-red-600">github.com/user/suspicious-repo</p>
                </div>
                <Badge variant="error">95% match</Badge>
              </div>
              <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                <div>
                  <p className="text-sm font-medium text-yellow-900">Medium similarity violation</p>
                  <p className="text-xs text-yellow-600">github.com/user/similar-project</p>
                </div>
                <Badge variant="warning">78% match</Badge>
              </div>
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <div>
                  <p className="text-sm font-medium text-green-900">New repository registered</p>
                  <p className="text-xs text-green-600">github.com/user/awesome-project</p>
                </div>
                <Badge variant="success">Protected</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Account Info */}
      <Card>
        <CardHeader>
          <CardTitle>Account Information</CardTitle>
          <CardDescription>Your wallet and network details</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Wallet Address</p>
              <p className="text-sm font-mono text-gray-900">{formatAddress(address!)}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Network</p>
              <p className="text-sm text-gray-900">Filecoin Calibration Testnet</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Chain ID</p>
              <p className="text-sm text-gray-900">314159</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function RepositoryItem({ repoId }: { repoId: number }) {
  const { getRepository } = useContractReads()
  const { data: repo } = getRepository(repoId)

  if (!repo) {
    return (
      <div className="animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
        <div className="h-3 bg-gray-200 rounded w-1/2"></div>
      </div>
    )
  }

  return (
    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
      <div>
        <p className="text-sm font-medium text-gray-900">Repository #{repoId}</p>
        <p className="text-xs text-gray-600">{repo.githubUrl}</p>
      </div>
      <div className="flex items-center space-x-2">
        <Badge variant={repo.isActive ? 'success' : 'secondary'}>
          {repo.isActive ? 'Active' : 'Inactive'}
        </Badge>
        <Button size="sm" variant="ghost" asChild>
          <a href={repo.githubUrl} target="_blank" rel="noopener noreferrer">
            <ExternalLink className="h-3 w-3" />
          </a>
        </Button>
      </div>
    </div>
  )
}