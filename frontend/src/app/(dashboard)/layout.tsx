'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Sidebar from '@/components/layout/Sidebar'
import { useAuthStore } from '@/store/auth'
import Cookies from 'js-cookie'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const { isAuthenticated, fetchMe } = useAuthStore()

  useEffect(() => {
    const token = Cookies.get('access_token')
    if (!token) { router.replace('/login'); return }
    if (!isAuthenticated) {
      fetchMe().catch(() => router.replace('/login'))
    }
  }, [isAuthenticated, fetchMe, router])

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 lg:ml-64 flex flex-col min-h-screen">
        {children}
      </main>
    </div>
  )
}
