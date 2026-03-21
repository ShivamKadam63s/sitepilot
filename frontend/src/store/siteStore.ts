import { create } from 'zustand'
import { sitesApi } from '@/api/sites'
import type { Site, CommitRecord, CreateSitePayload } from '@/types'

interface SiteState {
  sites: Site[]
  activeSite: Site | null
  commitHistory: CommitRecord[]
  isDirty: boolean
  isLoading: boolean
  error: string | null
}

interface SiteActions {
  loadSites: (tenantId: string) => Promise<void>
  setActiveSite: (site: Site) => void
  createSite: (payload: CreateSitePayload) => Promise<Site>
  deleteSite: (siteId: string) => Promise<void>
  markDirty: () => void
  commitChanges: (message: string) => Promise<void>
  loadHistory: (siteId: string) => Promise<void>
  clearError: () => void
}

export const useSiteStore = create<SiteState & SiteActions>((set, get) => ({
  // ── State ──────────────────────────────────────────────────────────────────
  sites: [],
  activeSite: null,
  commitHistory: [],
  isDirty: false,
  isLoading: false,
  error: null,

  // ── Actions ────────────────────────────────────────────────────────────────
  loadSites: async (tenantId) => {
    set({ isLoading: true, error: null })
    try {
      const sites = await sitesApi.list(tenantId)
      set({ sites, isLoading: false })
    } catch (err) {
      set({ error: String(err), isLoading: false })
    }
  },

  setActiveSite: (site) => {
    set({ activeSite: site, isDirty: false, commitHistory: [] })
  },

  createSite: async (payload) => {
    const site = await sitesApi.create(payload)
    set((s) => ({ sites: [...s.sites, site] }))
    return site
  },

  deleteSite: async (siteId) => {
    await sitesApi.delete(siteId)
    set((s) => ({
      sites: s.sites.filter((x) => x.id !== siteId),
      activeSite: s.activeSite?.id === siteId ? null : s.activeSite,
    }))
  },

  markDirty: () => set({ isDirty: true }),

  commitChanges: async (message) => {
    const { activeSite } = get()
    if (!activeSite) return
    const record = await sitesApi.commit(activeSite.id, message)
    set((s) => ({
      isDirty: false,
      commitHistory: [record, ...s.commitHistory],
    }))
  },

  loadHistory: async (siteId) => {
    const history = await sitesApi.getHistory(siteId)
    set({ commitHistory: history })
  },

  clearError: () => set({ error: null }),
}))
