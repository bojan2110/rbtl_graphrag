'use client'

import { useEffect, useState } from 'react'
import ChatInterface from '@/components/ChatInterface'
import KnowledgeBase from '@/components/KnowledgeBase'
import FavoritesView from '@/components/FavoritesView'
import GraphInfo from '@/components/GraphInfo'
import Sidebar, { MenuOption } from '@/components/Sidebar'
import Login from '@/components/Login'

const AUTH_STORAGE_KEY = 'graphrag_authenticated_user'
const SESSION_DURATION_MS = 24 * 60 * 60 * 1000 // 24 hours in milliseconds

interface AuthData {
  username: string
  loginTimestamp: number
}

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false)
  const [authenticatedUser, setAuthenticatedUser] = useState<string | null>(null)
  const [activeOption, setActiveOption] = useState<MenuOption>('chat')
  const [isChatProcessing, setIsChatProcessing] = useState(false)

  // Check for existing authentication on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const storedAuth = localStorage.getItem(AUTH_STORAGE_KEY)
      if (storedAuth) {
        try {
          const authData: AuthData = JSON.parse(storedAuth)
          const now = Date.now()
          const timeSinceLogin = now - authData.loginTimestamp

          // Check if session is still valid (less than 24 hours old)
          if (timeSinceLogin < SESSION_DURATION_MS) {
            setAuthenticatedUser(authData.username)
            setIsAuthenticated(true)
          } else {
            // Session expired, clear it
            localStorage.removeItem(AUTH_STORAGE_KEY)
          }
        } catch (error) {
          // Invalid stored data, clear it
          localStorage.removeItem(AUTH_STORAGE_KEY)
        }
      }
    }
  }, [])

  const handleLogin = (username: string) => {
    if (typeof window !== 'undefined') {
      const authData: AuthData = {
        username,
        loginTimestamp: Date.now(),
      }
      localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(authData))
    }
    setAuthenticatedUser(username)
    setIsAuthenticated(true)
  }

  const handleLogout = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(AUTH_STORAGE_KEY)
    }
    setAuthenticatedUser(null)
    setIsAuthenticated(false)
  }

  // Show login screen if not authenticated
  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />
  }

  return (
    <main className="flex h-screen bg-gray-50 overflow-hidden">
      {/* Sidebar (1/4 of screen) */}
      <Sidebar
        activeOption={activeOption}
        onOptionChange={setActiveOption}
        loggedInUser={authenticatedUser}
        onLogout={handleLogout}
      />
      
      {/* Main Content Area (3/4 of screen) */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {activeOption === 'chat' && (
          <div className="flex-1 flex flex-col p-6 min-h-0 overflow-hidden">
            <div className="flex-1 min-h-0 overflow-hidden">
              <ChatInterface
                selectedUser={authenticatedUser}
                isUserSelectionReady={!!authenticatedUser}
                userLoadError={null}
                onProcessingChange={setIsChatProcessing}
              />
            </div>
          </div>
        )}
        
        {activeOption === 'knowledge-base' && (
          <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
            <KnowledgeBase selectedTester={authenticatedUser} />
          </div>
        )}

        {activeOption === 'favorites' && (
          <div className="flex-1 flex flex-col p-6 min-h-0 overflow-hidden">
            <FavoritesView
              selectedUser={authenticatedUser}
              isUserSelectionReady={!!authenticatedUser}
            />
          </div>
        )}

        {activeOption === 'graph-info' && (
          <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
            <GraphInfo />
          </div>
        )}
        
        {/* Future: Add other views here based on activeOption */}
        {activeOption !== 'chat' &&
          activeOption !== 'knowledge-base' &&
          activeOption !== 'favorites' &&
          activeOption !== 'graph-info' && (
          <div className="flex-1 flex items-center justify-center">
            <p className="text-gray-500">Coming soon...</p>
          </div>
        )}
      </div>
    </main>
  )
}

