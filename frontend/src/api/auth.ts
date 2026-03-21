import { client } from './client'
import type { AuthResponse, User, Tenant } from '@/types'

export interface LoginPayload {
  email: string
  password: string
}

export interface MeResponse {
  user: User
  tenant: Tenant
}

export const authApi = {
  login: async (payload: LoginPayload): Promise<AuthResponse> => {
    const { data } = await client.post<AuthResponse>('/api/auth/login', payload)
    return data
  },

  logout: async (): Promise<void> => {
    await client.post('/api/auth/logout')
  },

  getMe: async (): Promise<MeResponse> => {
    const { data } = await client.get<MeResponse>('/api/auth/me')
    return data
  },
}
