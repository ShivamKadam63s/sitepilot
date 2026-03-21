import { useDeploymentStore } from '@/store/deploymentStore'
import type { DeploymentStatus } from '@/types'

const STATUS_LABELS: Record<DeploymentStatus, string> = {
  pending:     'Queued',
  building:    'Building image...',
  testing:     'Running tests...',
  deploying:   'Deploying to Kubernetes...',
  live:        'Live',
  failed:      'Failed',
  rolled_back: 'Rolled back',
}

const STATUS_COLORS: Record<DeploymentStatus, string> = {
  pending:     'text-gray-500',
  building:    'text-blue-600',
  testing:     'text-yellow-600',
  deploying:   'text-purple-600',
  live:        'text-green-600',
  failed:      'text-red-600',
  rolled_back: 'text-orange-500',
}

export function useDeployment(siteId?: string) {
  const store = useDeploymentStore()

  const statusLabel = store.current
    ? STATUS_LABELS[store.current.status]
    : null

  const statusColor = store.current
    ? STATUS_COLORS[store.current.status]
    : 'text-gray-500'

  const isTerminal =
    store.current?.status === 'live' ||
    store.current?.status === 'failed' ||
    store.current?.status === 'rolled_back'

  function deploy(commitHash?: string) {
    if (!siteId) return
    return store.deploy(siteId, commitHash)
  }

  function rollback(deploymentId: string) {
    return store.rollback(deploymentId)
  }

  return {
    current:     store.current,
    history:     store.history,
    logs:        store.logs,
    isDeploying: store.isDeploying,
    isTerminal,
    statusLabel,
    statusColor,
    error:       store.error,
    deploy,
    rollback,
    loadHistory: () => siteId ? store.loadHistory(siteId) : undefined,
    clearCurrent: store.clearCurrent,
  }
}
