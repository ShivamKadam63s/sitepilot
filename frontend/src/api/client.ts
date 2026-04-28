import axios, { AxiosError } from 'axios'
import type { ApiError } from '@/types'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

export const client = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30_000,
})

// Inject auth token on every request
client.interceptors.request.use((config) => {
  const raw = sessionStorage.getItem('sitepilot_token')
  if (raw) {
    config.headers.Authorization = `Bearer ${raw}`
  }
  return config
})

// Handle 401 globally — clear session and redirect to login
client.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    if (error.response?.status === 401) {
      sessionStorage.removeItem('sitepilot_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Helper to extract a readable message from any API error
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as ApiError | undefined
    return data?.detail ?? error.message
  }
  if (error instanceof Error) return error.message
  return 'An unexpected error occurred'
}
