'use client'
import { Bell, Search } from 'lucide-react'
import { useAuthStore } from '@/store/auth'
import { planBadgeColor } from '@/lib/utils'

interface HeaderProps {
  title: string
  subtitle?: string
}

export default function Header({ title, subtitle }: HeaderProps) {
  const { user } = useAuthStore()

  return (
    <header className="sticky top-0 z-20 bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{title}</h1>
          {subtitle && <p className="text-sm text-gray-500 mt-0.5">{subtitle}</p>}
        </div>
        <div className="flex items-center gap-4">
          <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors relative">
            <Bell className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-brand-600 flex items-center justify-center text-xs font-bold text-white">
              {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
            </div>
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${planBadgeColor(user?.plan || 'free')}`}>
              {user?.plan || 'free'}
            </span>
          </div>
        </div>
      </div>
    </header>
  )
}
