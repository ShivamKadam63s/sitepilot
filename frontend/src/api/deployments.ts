import { client } from './client'
import type { Deployment, PaginatedResponse } from '@/types'

export interface CreateDeploymentPayload {
  siteId: string
  commitHash?: string  // if omitted, deploys latest commit
}

export const deploymentsApi = {
  create: async (payload: CreateDeploymentPayload): Promise<Deployment> => {
    const { data } = await client.post<Deployment>('/api/deployments', {
      site_id: payload.siteId,
      commit_hash: payload.commitHash,
    })
    return data
  },

  get: async (deploymentId: string): Promise<Deployment> => {
    const { data } = await client.get<Deployment>(
      `/api/deployments/${deploymentId}`
    )
    return data
  },

  list: async (siteId: string): Promise<Deployment[]> => {
    const { data } = await client.get<PaginatedResponse<Deployment>>(
      '/api/deployments',
      { params: { site_id: siteId } }
    )
    return data.items
  },

  getLogs: async (deploymentId: string): Promise<string[]> => {
    const { data } = await client.get<{ logs: string[] }>(
      `/api/deployments/${deploymentId}/logs`
    )
    return data.logs
  },

  rollback: async (deploymentId: string): Promise<Deployment> => {
    const { data } = await client.post<Deployment>(
      `/api/deployments/${deploymentId}/rollback`
    )
    return data
  },
}
