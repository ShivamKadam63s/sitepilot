import { create } from 'zustand'
import { authApi } from '@/api/auth'
import type { User, Tenant } from '@/types'

interface AuthState {
  user: User | null
  tenant: Tenant | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

interface AuthActions {
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  loadMe: () => Promise<void>
  clearError: () => void
}

const TOKEN_KEY = 'sitepilot_token'

export const useAuthStore = create<AuthState & AuthActions>((set) => ({
  // ── State ──────────────────────────────────────────────────────────────────
  user: null,
  tenant: null,
  token: sessionStorage.getItem(TOKEN_KEY),
  isAuthenticated: !!sessionStorage.getItem(TOKEN_KEY),
  isLoading: false,
  error: null,

  // ── Actions ────────────────────────────────────────────────────────────────
  login: async (email, password) => {
    set({ isLoading: true, error: null })
    try {
      const res = await authApi.login({ email, password })
      sessionStorage.setItem(TOKEN_KEY, res.access_token)
      set({
        token: res.access_token,
        user: res.user,
        tenant: res.tenant,
        isAuthenticated: true,
        isLoading: false,
      })
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Login failed'
      set({ isLoading: false, error: msg, isAuthenticated: false })
      throw err
    }
  },

  logout: async () => {
    try {
      await authApi.logout()
    } finally {
      sessionStorage.removeItem(TOKEN_KEY)
      set({ user: null, tenant: null, token: null, isAuthenticated: false })
    }
  },

  loadMe: async () => {
    set({ isLoading: true })
    try {
      const { user, tenant } = await authApi.getMe()
      set({ user, tenant, isLoading: false })
    } catch {
      sessionStorage.removeItem(TOKEN_KEY)
      set({ isAuthenticated: false, isLoading: false })
    }
  },

  clearError: () => set({ error: null }),
}))
