import { create } from 'zustand'
import { deploymentsApi } from '@/api/deployments'
import type { Deployment } from '@/types'

interface DeploymentState {
  current: Deployment | null
  history: Deployment[]
  logs: string[]
  isDeploying: boolean
  pollingIntervalId: ReturnType<typeof setInterval> | null
  error: string | null
}

interface DeploymentActions {
  deploy: (siteId: string, commitHash?: string) => Promise<void>
  pollStatus: (deploymentId: string) => void
  stopPolling: () => void
  loadHistory: (siteId: string) => Promise<void>
  rollback: (deploymentId: string) => Promise<void>
  clearCurrent: () => void
  clearError: () => void
}

export const useDeploymentStore = create<DeploymentState & DeploymentActions>(
  (set, get) => ({
    // ── State ────────────────────────────────────────────────────────────────
    current: null,
    history: [],
    logs: [],
    isDeploying: false,
    pollingIntervalId: null,
    error: null,

    // ── Actions ──────────────────────────────────────────────────────────────
    deploy: async (siteId, commitHash) => {
      set({ isDeploying: true, error: null, logs: [], current: null })
      try {
        const deployment = await deploymentsApi.create({ siteId, commitHash })
        set({ current: deployment })
        get().pollStatus(deployment.id)
      } catch (err) {
        set({ isDeploying: false, error: String(err) })
        throw err
      }
    },

    pollStatus: (deploymentId) => {
      const id = setInterval(async () => {
        try {
          const [deployment, logs] = await Promise.all([
            deploymentsApi.get(deploymentId),
            deploymentsApi.getLogs(deploymentId),
          ])
          set({ current: deployment, logs })

          const terminal = ['live', 'failed', 'rolled_back']
          if (terminal.includes(deployment.status)) {
            get().stopPolling()
            set({ isDeploying: false })
          }
        } catch {
          get().stopPolling()
          set({ isDeploying: false, error: 'Lost connection to deployment' })
        }
      }, 3000)

      set({ pollingIntervalId: id })
    },

    stopPolling: () => {
      const { pollingIntervalId } = get()
      if (pollingIntervalId) clearInterval(pollingIntervalId)
      set({ pollingIntervalId: null })
    },

    loadHistory: async (siteId) => {
      const history = await deploymentsApi.list(siteId)
      set({ history })
    },

    rollback: async (deploymentId) => {
      set({ isDeploying: true, error: null })
      const deployment = await deploymentsApi.rollback(deploymentId)
      set({ current: deployment })
      get().pollStatus(deployment.id)
    },

    clearCurrent: () => {
      get().stopPolling()
      set({ current: null, logs: [], isDeploying: false })
    },

    clearError: () => set({ error: null }),
  })
)
