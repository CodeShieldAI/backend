import React from 'react'
import { Shield, Github, AlertTriangle, DollarSign } from 'lucide-react'
import { useAccount } from 'wagmi'
import { Button } from './ui/Button'
import { cn } from '../lib/utils'

interface LayoutProps {
  children: React.ReactNode
  activeTab: 'dashboard' | 'register' | 'violations' | 'bounties'
  onTabChange: (tab: 'dashboard' | 'register' | 'violations' | 'bounties') => void
}

export function Layout({ children, activeTab, onTabChange }: LayoutProps) {
  const { isConnected } = useAccount()

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: Shield },
    { id: 'register', label: 'Register Repo', icon: Github },
    { id: 'violations', label: 'Report Violations', icon: AlertTriangle },
    { id: 'bounties', label: 'Claim Bounties', icon: DollarSign }
  ] as const

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-600 rounded-lg">
                <Shield className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">GitHub Protection</h1>
                <p className="text-sm text-gray-600">Filecoin Network</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="hidden md:flex items-center space-x-2 px-3 py-1 bg-green-100 rounded-full">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-green-800">Calibration Testnet</span>
              </div>
              <w3m-button />
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      {isConnected && (
        <nav className="border-b bg-white/60 backdrop-blur-sm">
          <div className="container mx-auto px-4">
            <div className="flex space-x-1">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => onTabChange(tab.id)}
                    className={cn(
                      'flex items-center space-x-2 px-4 py-3 text-sm font-medium transition-colors border-b-2',
                      activeTab === tab.id
                        ? 'border-blue-600 text-blue-600 bg-blue-50'
                        : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{tab.label}</span>
                  </button>
                )
              })}
            </div>
          </div>
        </nav>
      )}

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {isConnected ? (
          children
        ) : (
          <div className="flex flex-col items-center justify-center min-h-[500px] text-center">
            <div className="p-6 bg-white rounded-2xl shadow-lg border max-w-md">
              <Shield className="h-16 w-16 text-blue-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Connect Your Wallet</h2>
              <p className="text-gray-600 mb-6">
                Connect your wallet to start protecting your GitHub repositories on the Filecoin network.
              </p>
              <w3m-button size="md" />
            </div>
          </div>
        )}
      </main>
    </div>
  )
}