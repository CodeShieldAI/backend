import React, { useState } from 'react'
import { WagmiProvider } from 'wagmi'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { config } from './config/web3'
import { Layout } from './components/Layout'
import { Dashboard } from './components/Dashboard'
import { RegisterRepository } from './components/RegisterRepository'
import { ReportViolations } from './components/ReportViolations'
import { ClaimBounties } from './components/ClaimBounties'

const queryClient = new QueryClient()

function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'register' | 'violations' | 'bounties'>('dashboard')

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />
      case 'register':
        return <RegisterRepository />
      case 'violations':
        return <ReportViolations />
      case 'bounties':
        return <ClaimBounties />
      default:
        return <Dashboard />
    }
  }

  return (
    <WagmiProvider config={config}>
      <QueryClientProvider client={queryClient}>
        <Layout activeTab={activeTab} onTabChange={setActiveTab}>
          {renderContent()}
        </Layout>
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#fff',
              color: '#333',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              fontSize: '14px'
            }
          }}
        />
      </QueryClientProvider>
    </WagmiProvider>
  )
}

export default App