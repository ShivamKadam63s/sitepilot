import { useEffect } from 'react'
import { useSiteStore } from '@/store/siteStore'
import { useDeployment } from '@/hooks/useDeployment'
import { Button } from '@/components/common/Button'

interface CommitHistoryPanelProps {
  siteId: string
}

export function CommitHistoryPanel({ siteId }: CommitHistoryPanelProps) {
  const { commitHistory, loadHistory } = useSiteStore()
  const { rollback, isDeploying } = useDeployment(siteId)

  useEffect(() => {
    loadHistory(siteId)
  }, [siteId, loadHistory])

  if (commitHistory.length === 0) {
    return (
      <div className="rounded-xl border border-gray-200 bg-white px-4 py-8 text-center">
        <p className="text-sm text-gray-400">No commits yet</p>
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-gray-200 bg-white">
      <div className="border-b border-gray-100 px-4 py-3">
        <p className="text-sm font-medium text-gray-700">Commit history</p>
      </div>
      <div className="divide-y divide-gray-50">
        {commitHistory.map((commit, i) => (
          <div key={commit.hash} className="flex items-center justify-between px-4 py-3">
            <div className="flex items-start gap-3">
              <code className="rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-600">
                {commit.shortHash}
              </code>
              <div>
                <p className="text-sm text-gray-800">{commit.message}</p>
                <p className="text-xs text-gray-400">
                  {new Date(commit.timestamp).toLocaleString()}
                </p>
              </div>
            </div>
            {i > 0 && commit.deploymentId && (
              <Button
                variant="secondary"
                size="sm"
                disabled={isDeploying}
                onClick={() => commit.deploymentId && rollback(commit.deploymentId)}
              >
                Restore
              </Button>
            )}
            {i === 0 && (
              <span className="rounded bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">
                current
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
