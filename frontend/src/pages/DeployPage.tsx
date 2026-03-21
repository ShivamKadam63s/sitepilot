import { useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useSiteStore } from '@/store/siteStore'
import { useAuthStore } from '@/store/authStore'
import { DeploymentPanel } from '@/components/dashboard/DeploymentPanel'
import { CommitHistoryPanel } from '@/components/dashboard/CommitHistoryPanel'
import { Spinner } from '@/components/common/Spinner'

export function DeployPage() {
  const [params, setParams] = useSearchParams()
  const { tenant }          = useAuthStore()
  const { sites, activeSite, isLoading, loadSites, setActiveSite } = useSiteStore()

  // Load sites on mount
  useEffect(() => {
    if (tenant) loadSites(tenant.id)
  }, [tenant, loadSites])

  // Sync ?site= param → activeSite
  useEffect(() => {
    const siteId = params.get('site')
    if (siteId && sites.length > 0) {
      const found = sites.find((s) => s.id === siteId)
      if (found) setActiveSite(found)
    } else if (!siteId && sites.length > 0 && !activeSite) {
      setActiveSite(sites[0])
    }
  }, [params, sites, activeSite, setActiveSite])

  function handleSiteChange(id: string) {
    const site = sites.find((s) => s.id === id)
    if (site) {
      setActiveSite(site)
      setParams({ site: id })
    }
  }

  if (isLoading) {
    return <div className="flex justify-center py-16"><Spinner size="lg" /></div>
  }

  if (sites.length === 0) {
    return (
      <div className="py-16 text-center text-gray-400">
        No sites found. Create one first.
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Site picker */}
      <div className="flex items-center gap-4">
        <label className="text-sm font-medium text-gray-700">Site</label>
        <select
          value={activeSite?.id ?? ''}
          onChange={(e) => handleSiteChange(e.target.value)}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm
                     focus:outline-none focus:ring-2 focus:ring-brand-400"
        >
          {sites.map((s) => (
            <option key={s.id} value={s.id}>{s.name}</option>
          ))}
        </select>
      </div>

      {activeSite && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Deploy panel takes 2/3 */}
          <div className="lg:col-span-2">
            <DeploymentPanel site={activeSite} />
          </div>
          {/* Commit history takes 1/3 */}
          <div>
            <CommitHistoryPanel siteId={activeSite.id} />
          </div>
        </div>
      )}
    </div>
  )
}
