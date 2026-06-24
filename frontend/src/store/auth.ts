import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { User } from '@/types'
import api, { setTokens, clearTokens } from '@/lib/api'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => Promise<void>
  fetchMe: () => Promise<void>
  updateUser: (user: User) => void
}

interface RegisterData {
  email: string
  password: string
  password_confirm: string
  full_name: string
  role: string
  company_name?: string
  phone?: string
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email, password) => {
        set({ isLoading: true })
        try {
          const { data } = await api.post('/auth/login/', { email, password })
          setTokens(data.access, data.refresh)
          await get().fetchMe()
          set({ isAuthenticated: true })
        } finally {
          set({ isLoading: false })
        }
      },

      register: async (registerData) => {
        set({ isLoading: true })
        try {
          const { data } = await api.post('/auth/register/', registerData)
          setTokens(data.tokens.access, data.tokens.refresh)
          set({ user: data.user, isAuthenticated: true })
        } finally {
          set({ isLoading: false })
        }
      },

      logout: async () => {
        try {
          const Cookies = (await import('js-cookie')).default
          const refresh = Cookies.get('refresh_token')
          if (refresh) await api.post('/auth/logout/', { refresh })
        } catch {}
        clearTokens()
        set({ user: null, isAuthenticated: false })
      },

      fetchMe: async () => {
        const { data } = await api.get<User>('/auth/me/')
        set({ user: data, isAuthenticated: true })
      },

      updateUser: (user) => set({ user }),
    }),
    {
      name: 'nile-auth',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
)
