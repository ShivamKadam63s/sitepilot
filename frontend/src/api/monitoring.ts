import { client } from './client'
import type { SiteMetrics, LogEntry, TimeRange } from '@/types'

const toCamelMetrics = (metrics: Record<string, unknown>): SiteMetrics => ({
  requestRate: metrics.request_rate,
  errorRate: metrics.error_rate,
  p95LatencyMs: metrics.p95_latency_ms,
  activeConnections: metrics.active_connections,
  timestamps: metrics.timestamps,
  requestHistory: metrics.request_history,
  errorHistory: metrics.error_history,
})

export const monitoringApi = {
  getMetrics: async (siteId: string, range: TimeRange): Promise<SiteMetrics> => {
    const { data } = await client.get<SiteMetrics>(
      `/api/monitoring/metrics/${siteId}`,
      { params: { range } }
    )
    return toCamelMetrics(data)
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
