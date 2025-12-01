'use client'

import { useState } from 'react'
import { MessageSquare, Menu, BookOpen, Users, Star, GitBranch, LogOut } from 'lucide-react'

export type MenuOption = 'chat' | 'knowledge-base' | 'favorites' | 'graph-info'

interface SidebarProps {
  activeOption: MenuOption
  onOptionChange: (option: MenuOption) => void
  loggedInUser: string | null
  onLogout: () => void
}

export default function Sidebar({
  activeOption,
  onOptionChange,
  loggedInUser,
  onLogout,
}: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false)

  const menuOptions = [
    { id: 'chat' as MenuOption, label: 'Chat', icon: MessageSquare },
    { id: 'knowledge-base' as MenuOption, label: 'Knowledge Base', icon: BookOpen },
    { id: 'favorites' as MenuOption, label: 'Favorites', icon: Star },
    { id: 'graph-info' as MenuOption, label: 'Graph Info', icon: GitBranch },
  ]

  return (
    <div className={`bg-gray-800 text-white transition-all duration-300 ${
      isCollapsed ? 'w-16' : 'w-64'
    } flex flex-col h-screen border-r border-gray-700 flex-shrink-0`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-700 flex items-center justify-between">
        {!isCollapsed && (
          <h2 className="text-lg font-semibold">GraphRAG</h2>
        )}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-2 hover:bg-gray-700 rounded transition-colors"
          aria-label="Toggle sidebar"
        >
          <Menu size={20} />
        </button>
      </div>

      {/* Menu Options */}
      <nav className="flex-1 p-4 space-y-2">
        {menuOptions.map((option) => {
          const Icon = option.icon
          const isActive = activeOption === option.id
          
          return (
            <button
              key={option.id}
              onClick={() => onOptionChange(option.id)}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'
              }`}
            >
              <Icon size={20} />
              {!isCollapsed && <span>{option.label}</span>}
            </button>
          )
        })}
      </nav>

      {/* Footer/User Info */}
      <div className="p-4 border-t border-gray-700 text-xs text-gray-400 space-y-3">
        {!isCollapsed ? (
          <>
            <div className="flex items-center gap-2 text-gray-300">
              <Users size={16} />
              <span className="font-medium text-sm">Logged in as</span>
            </div>
            {loggedInUser && (
              <div className="bg-gray-900 rounded-md px-3 py-2 text-sm text-white">
                {loggedInUser.charAt(0).toUpperCase() + loggedInUser.slice(1)}
              </div>
            )}
            <button
              onClick={onLogout}
              className="w-full flex items-center justify-center gap-2 bg-gray-700 hover:bg-gray-600 text-white py-2 px-3 rounded-md text-sm font-medium transition-colors"
            >
              <LogOut size={16} />
              <span>Logout</span>
            </button>
            <p className="text-[11px] leading-snug text-gray-500">
              GraphRAG v1.0.0
            </p>
          </>
        ) : (
          <div className="flex flex-col items-center gap-2 text-[10px] text-gray-500">
            <Users size={18} />
            <span>Expand for user info</span>
          </div>
        )}
      </div>
    </div>
  )
}

