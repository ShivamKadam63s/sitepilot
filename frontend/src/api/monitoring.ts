import { client } from './client'
import type { SiteMetrics, LogEntry, TimeRange } from '@/types'

export const monitoringApi = {
  getMetrics: async (siteId: string, range: TimeRange): Promise<SiteMetrics> => {
    const { data } = await client.get<SiteMetrics>(
      `/api/monitoring/metrics/${siteId}`,
      { params: { range } }
    )
    return data
  },

  getLogs: async (
    siteId: string,
    filters?: { level?: string; search?: string }
  ): Promise<LogEntry[]> => {
    const { data } = await client.get<LogEntry[]>(
      `/api/monitoring/logs/${siteId}`,
      { params: filters }
    )
    return data
  },
}
