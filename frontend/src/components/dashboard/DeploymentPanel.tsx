import { useState, useRef } from 'react'
import { useDeployment } from '@/hooks/useDeployment'
import { Button } from '@/components/common/Button'
import { DeploymentBadge } from '@/components/common/Badge'
import { Spinner } from '@/components/common/Spinner'
import type { Site } from '@/types'

interface DeploymentPanelProps {
  site: Site
}

export function DeploymentPanel({ site }: DeploymentPanelProps) {
  const { current, logs, isDeploying, statusLabel, error, deploy } =
    useDeployment(site.id)

  const [commitMsg, setCommitMsg] = useState('')
  const logsEndRef = useRef<HTMLDivElement>(null)

  async function handleDeploy() {
    await deploy()
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Deploy controls */}
      <div className="rounded-xl border border-gray-200 bg-white p-5">
        <h2 className="mb-3 text-sm font-medium text-gray-900">
          Deploy <span className="text-brand-600">{site.name}</span>
        </h2>

        <div className="flex items-end gap-3">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Commit message (optional)"
              value={commitMsg}
              onChange={(e) => setCommitMsg(e.target.value)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm
                         focus:outline-none focus:ring-2 focus:ring-brand-400"
            />
          </div>
          <Button
            onClick={handleDeploy}
            isLoading={isDeploying}
            disabled={isDeploying}
          >
            {isDeploying ? 'Deploying…' : 'Deploy'}
          </Button>
        </div>

        {error && (
          <p className="mt-2 text-sm text-red-600">{error}</p>
        )}
      </div>

      {/* Status + live URL */}
      {current && (
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {isDeploying && <Spinner size="sm" />}
              <span className="text-sm text-gray-700">{statusLabel}</span>
              <DeploymentBadge status={current.status} />
            </div>
            {current.liveUrl && (
              <a
                href={current.liveUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm font-medium text-brand-600 hover:underline"
              >
                {current.liveUrl}
              </a>
            )}
          </div>
        </div>
      )}

      {/* Build logs */}
      {logs.length > 0 && (
        <div className="rounded-xl border border-gray-200 bg-gray-900 p-4">
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-gray-400">
            Build logs
          </p>
          <div className="max-h-64 overflow-y-auto font-mono text-xs text-green-400">
            {logs.map((line, i) => (
              <div key={i} className="leading-5">{line}</div>
            ))}
            <div ref={logsEndRef} />
          </div>
        </div>
      )}
    </div>
  )
}
