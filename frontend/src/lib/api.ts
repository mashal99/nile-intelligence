import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import Cookies from 'js-cookie'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = Cookies.get('access_token')
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

let isRefreshing = false
let refreshQueue: ((token: string) => void)[] = []

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    if (error.response?.status === 401 && !original._retry) {
      original._retry = true

      const refreshToken = Cookies.get('refresh_token')
      if (!refreshToken) {
        clearTokens()
        if (typeof window !== 'undefined') window.location.href = '/login'
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise((resolve) => {
          refreshQueue.push((token) => {
            original.headers.Authorization = `Bearer ${token}`
            resolve(api(original))
          })
        })
      }

      isRefreshing = true
      try {
        const { data } = await axios.post(`${API_URL}/auth/token/refresh/`, { refresh: refreshToken })
        const newAccess = data.access
        Cookies.set('access_token', newAccess, { expires: 1, sameSite: 'strict' })
        refreshQueue.forEach((cb) => cb(newAccess))
        refreshQueue = []
        original.headers.Authorization = `Bearer ${newAccess}`
        return api(original)
      } catch {
        clearTokens()
        if (typeof window !== 'undefined') window.location.href = '/login'
        return Promise.reject(error)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export function setTokens(access: string, refresh: string) {
  Cookies.set('access_token', access, { expires: 1, sameSite: 'strict' })
  Cookies.set('refresh_token', refresh, { expires: 7, sameSite: 'strict' })
}

export function clearTokens() {
  Cookies.remove('access_token')
  Cookies.remove('refresh_token')
}

export default api
