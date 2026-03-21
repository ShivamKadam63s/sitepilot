import { client } from './client'
import type { Site, CreateSitePayload, CommitRecord, PaginatedResponse } from '@/types'

export const sitesApi = {
  list: async (tenantId: string): Promise<Site[]> => {
    const { data } = await client.get<PaginatedResponse<Site>>('/api/sites', {
      params: { tenant_id: tenantId },
    })
    return data.items
  },

  get: async (siteId: string): Promise<Site> => {
    const { data } = await client.get<Site>(`/api/sites/${siteId}`)
    return data
  },

  create: async (payload: CreateSitePayload): Promise<Site> => {
    const { data } = await client.post<Site>('/api/sites', payload)
    return data
  },

  update: async (siteId: string, patch: Partial<Site>): Promise<Site> => {
    const { data } = await client.patch<Site>(`/api/sites/${siteId}`, patch)
    return data
  },

  delete: async (siteId: string): Promise<void> => {
    await client.delete(`/api/sites/${siteId}`)
  },

  commit: async (siteId: string, message: string): Promise<CommitRecord> => {
    const { data } = await client.post<CommitRecord>(
      `/api/sites/${siteId}/commit`,
      { message }
    )
    return data
  },

  getHistory: async (siteId: string): Promise<CommitRecord[]> => {
    const { data } = await client.get<CommitRecord[]>(
      `/api/sites/${siteId}/history`
    )
    return data
  },

  uploadZip: async (
    siteId: string,
    file: File,
    onProgress?: (pct: number) => void
  ): Promise<void> => {
    const form = new FormData()
    form.append('file', file)
    await client.post(`/api/sites/${siteId}/upload`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (onProgress && e.total) {
          onProgress(Math.round((e.loaded / e.total) * 100))
        }
      },
    })
  },
}
