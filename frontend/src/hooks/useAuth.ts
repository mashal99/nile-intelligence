'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/auth'
import Cookies from 'js-cookie'

export function useRequireAuth() {
  const router = useRouter()
  const { isAuthenticated, fetchMe } = useAuthStore()

  useEffect(() => {
    const token = Cookies.get('access_token')
    if (!token) {
      router.replace('/login')
      return
    }
    if (!isAuthenticated) {
      fetchMe().catch(() => router.replace('/login'))
    }
  }, [isAuthenticated, fetchMe, router])

  return useAuthStore()
}

export function useRedirectIfAuth() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (isAuthenticated) router.replace('/dashboard')
  }, [isAuthenticated, router])
}
