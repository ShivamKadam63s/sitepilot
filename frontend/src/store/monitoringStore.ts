import { create } from 'zustand'
import { monitoringApi } from '@/api/monitoring'
import type { SiteMetrics, LogEntry, TimeRange } from '@/types'

interface MonitoringState {
  metrics: SiteMetrics | null
  logs: LogEntry[]
  selectedSiteId: string | null
  timeRange: TimeRange
  isLoadingMetrics: boolean
  isLoadingLogs: boolean
  refreshIntervalId: ReturnType<typeof setInterval> | null
}

interface MonitoringActions {
  selectSite: (siteId: string) => void
  setTimeRange: (range: TimeRange) => void
  fetchMetrics: () => Promise<void>
  fetchLogs: (filters?: { level?: string; search?: string }) => Promise<void>
  startAutoRefresh: () => void
  stopAutoRefresh: () => void
}

export const useMonitoringStore = create<MonitoringState & MonitoringActions>(
  (set, get) => ({
    // ── State ────────────────────────────────────────────────────────────────
    metrics: null,
    logs: [],
    selectedSiteId: null,
    timeRange: '1h',
    isLoadingMetrics: false,
    isLoadingLogs: false,
    refreshIntervalId: null,

    // ── Actions ──────────────────────────────────────────────────────────────
    selectSite: (siteId) => {
      set({ selectedSiteId: siteId, metrics: null, logs: [] })
      get().fetchMetrics()
      get().fetchLogs()
    },

    setTimeRange: (range) => {
      set({ timeRange: range })
      get().fetchMetrics()
    },

    fetchMetrics: async () => {
      const { selectedSiteId, timeRange } = get()
      if (!selectedSiteId) return
      set({ isLoadingMetrics: true })
      try {
        const metrics = await monitoringApi.getMetrics(selectedSiteId, timeRange)
        set({ metrics, isLoadingMetrics: false })
      } catch {
        set({ isLoadingMetrics: false })
      }
    },

    fetchLogs: async (filters) => {
      const { selectedSiteId } = get()
      if (!selectedSiteId) return
      set({ isLoadingLogs: true })
      try {
        const logs = await monitoringApi.getLogs(selectedSiteId, filters)
        set({ logs, isLoadingLogs: false })
      } catch {
        set({ isLoadingLogs: false })
      }
    },

    startAutoRefresh: () => {
      get().stopAutoRefresh()
      const id = setInterval(() => get().fetchMetrics(), 15_000)
      set({ refreshIntervalId: id })
    },

    stopAutoRefresh: () => {
      const { refreshIntervalId } = get()
      if (refreshIntervalId) clearInterval(refreshIntervalId)
      set({ refreshIntervalId: null })
    },
  })
)
