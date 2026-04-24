import { client } from './client'
import type { Site, CreateSitePayload, CommitRecord, PaginatedResponse } from '@/types'

const toCamelSite = (site: Record<string, unknown>): Site => ({
  id: site.id,
  tenantId: site.tenant_id,
  name: site.name,
  slug: site.slug,
  framework: site.framework,
  status: site.status,
  liveUrl: site.live_url,
  repoPath: site.repo_path,
  sourceType: site.source_type,
  repoUrl: site.repo_url,
  createdAt: site.created_at,
  updatedAt: site.updated_at,
})

const toSnakeCreateSitePayload = (payload: CreateSitePayload) => ({
  name: payload.name,
  slug: payload.slug,
  source_type: payload.sourceType,
  repo_url: payload.repoUrl,
})

export const sitesApi = {
  list: async (tenantId: string): Promise<Site[]> => {
    const { data } = await client.get<PaginatedResponse<Site>>('/api/sites', {
      params: { tenant_id: tenantId },
    })
    return data.items.map(toCamelSite)
  },

  get: async (siteId: string): Promise<Site> => {
    const { data } = await client.get<Site>(`/api/sites/${siteId}`)
    return toCamelSite(data)
  },

  create: async (payload: CreateSitePayload): Promise<Site> => {
    const { data } = await client.post<Site>('/api/sites', toSnakeCreateSitePayload(payload))
    return toCamelSite(data)
  },

  update: async (siteId: string, patch: Partial<Site>): Promise<Site> => {
    const body: Record<string, unknown> = {}
    if (patch.name !== undefined) body.name = patch.name
    if (patch.slug !== undefined) body.slug = patch.slug
    if (patch.status !== undefined) body.status = patch.status
    if (patch.liveUrl !== undefined) body.live_url = patch.liveUrl
    if (patch.repoUrl !== undefined) body.repo_url = patch.repoUrl

    const { data } = await client.patch<Site>(`/api/sites/${siteId}`, body)
    return toCamelSite(data)
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
