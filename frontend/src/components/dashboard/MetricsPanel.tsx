import { useEffect } from 'react'
import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid,
} from 'recharts'
import { useMonitoringStore } from '@/store/monitoringStore'
import { LogLevelBadge } from '@/components/common/Badge'
import { Spinner } from '@/components/common/Spinner'
import type { TimeRange } from '@/types'

const TIME_RANGES: TimeRange[] = ['1h', '6h', '24h', '7d']

interface MetricsPanelProps {
  siteId: string
}

export function MetricsPanel({ siteId }: MetricsPanelProps) {
  const store = useMonitoringStore()

  useEffect(() => {
    store.selectSite(siteId)
    store.startAutoRefresh()
    return () => store.stopAutoRefresh()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [siteId])

  const chartData = store.metrics
    ? store.metrics.timestamps.map((t, i) => ({
        time: new Date(t).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        requests: store.metrics!.requestHistory[i] ?? 0,
        errors:   store.metrics!.errorHistory[i] ?? 0,
      }))
    : []

  return (
    <div className="flex flex-col gap-4">
      {/* Time range selector */}
      <div className="flex gap-2">
        {TIME_RANGES.map((r) => (
          <button
            key={r}
            onClick={() => store.setTimeRange(r)}
            className={`rounded px-3 py-1 text-sm font-medium transition-colors ${
              store.timeRange === r
                ? 'bg-brand-600 text-white'
                : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
            }`}
          >
            {r}
          </button>
        ))}
      </div>

      {/* Stat cards */}
      {store.metrics && (
        <div className="grid grid-cols-3 gap-4">
          <StatCard
            label="Request rate"
            value={`${store.metrics.requestRate.toFixed(1)}/s`}
          />
          <StatCard
            label="Error rate"
            value={`${(store.metrics.errorRate * 100).toFixed(1)}%`}
            alert={store.metrics.errorRate > 0.05}
          />
          <StatCard
            label="p95 latency"
            value={`${store.metrics.p95LatencyMs}ms`}
            alert={store.metrics.p95LatencyMs > 500}
          />
        </div>
      )}

      {/* Request chart */}
      {store.isLoadingMetrics && (
        <div className="flex justify-center py-8"><Spinner /></div>
      )}
      {!store.isLoadingMetrics && chartData.length > 0 && (
        <div className="rounded-xl border border-gray-200 bg-white p-4">
          <p className="mb-3 text-sm font-medium text-gray-700">Request rate</p>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="time" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line
                type="monotone" dataKey="requests"
                stroke="#534ab7" strokeWidth={2} dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Logs */}
      <div className="rounded-xl border border-gray-200 bg-white">
        <div className="border-b border-gray-100 px-4 py-3">
          <p className="text-sm font-medium text-gray-700">Recent logs</p>
        </div>
        {store.isLoadingLogs ? (
          <div className="flex justify-center py-6"><Spinner /></div>
        ) : (
          <div className="divide-y divide-gray-50 font-mono text-xs">
            {store.logs.slice(0, 50).map((log, i) => (
              <div key={i} className="flex items-start gap-3 px-4 py-2">
                <span className="w-14 shrink-0 text-gray-400">
                  {new Date(log.timestamp).toLocaleTimeString([], {
                    hour: '2-digit', minute: '2-digit', second: '2-digit',
                  })}
                </span>
                <LogLevelBadge level={log.level} />
                <span className="text-gray-700">{log.message}</span>
              </div>
            ))}
            {store.logs.length === 0 && (
              <p className="px-4 py-6 text-center text-gray-400">
                No logs yet
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

function StatCard({
  label, value, alert = false,
}: { label: string; value: string; alert?: boolean }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4">
      <p className="text-xs text-gray-500">{label}</p>
      <p className={`mt-1 text-2xl font-semibold ${alert ? 'text-red-600' : 'text-gray-900'}`}>
        {value}
      </p>
    </div>
  )
}
