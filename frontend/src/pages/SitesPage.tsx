import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSiteStore } from '@/store/siteStore'
import { useAuthStore } from '@/store/authStore'
import { Button } from '@/components/common/Button'
import { SiteBadge } from '@/components/common/Badge'
import { Modal } from '@/components/common/Modal'
import { Input } from '@/components/common/Input'
import { Spinner } from '@/components/common/Spinner'
import type { CreateSitePayload } from '@/types'

export function SitesPage() {
  const navigate      = useNavigate()
  const { tenant }    = useAuthStore()
  const { sites, isLoading, loadSites, createSite, deleteSite } = useSiteStore()

  const [showCreate, setShowCreate] = useState(false)
  const [newName, setNewName]       = useState('')
  const [newSlug, setNewSlug]       = useState('')
  const [repoUrl, setRepoUrl]       = useState('')
  const [creating, setCreating]     = useState(false)
  const [error, setError]           = useState('')

  useEffect(() => {
    if (tenant) loadSites(tenant.id)
  }, [tenant, loadSites])

  function slugify(name: string) {
    return name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
  }

  async function handleCreate() {
    setError('')
    setCreating(true)
    try {
      const payload: CreateSitePayload = {
        name: newName,
        slug: newSlug,
        sourceType: repoUrl ? 'git' : 'upload',
        repoUrl: repoUrl || undefined,
      }
      const site = await createSite(payload)
      setShowCreate(false)
      setNewName('')
      setNewSlug('')
      setRepoUrl('')
      navigate(`/dashboard/deploy?site=${site.id}`)
    } catch (err) {
      setError(String(err))
    } finally {
      setCreating(false)
    }
  }

  async function handleDelete(siteId: string, siteName: string) {
    if (!confirm(`Delete "${siteName}"? This cannot be undone.`)) return
    try {
      await deleteSite(siteId)
      if (tenant) loadSites(tenant.id) // Refresh list
    } catch (err) {
      alert(`Failed to delete site: ${err}`)
    }
  }

  if (isLoading) {
    return (
      <div className="flex justify-center py-16">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div>
      {/* Header row */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-medium text-gray-900">Your sites</h2>
          <p className="text-sm text-gray-500">
            {sites.length} / {tenant?.sitesAllowed ?? '—'} sites used
          </p>
        </div>
        <Button onClick={() => setShowCreate(true)}>New site</Button>
      </div>

      {/* Sites grid */}
      {sites.length === 0 ? (
        <div className="rounded-xl border-2 border-dashed border-gray-200 py-16 text-center">
          <p className="text-gray-400">No sites yet.</p>
          <Button
            variant="secondary"
            className="mt-4"
            onClick={() => setShowCreate(true)}
          >
            Create your first site
          </Button>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {sites.map((site) => (
            <div
              key={site.id}
              className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
            >
              <div className="mb-3 flex items-start justify-between">
                <div>
                  <p className="font-medium text-gray-900">{site.name}</p>
                  <p className="text-xs text-gray-400">{site.slug}</p>
                </div>
                <SiteBadge status={site.status} />
              </div>

              <p className="mb-1 text-xs text-gray-500 capitalize">
                Framework: {site.framework}
              </p>

              {site.liveUrl && (
                <a
                  href={site.liveUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mb-3 block truncate text-xs text-brand-600 hover:underline"
                >
                  {site.liveUrl}
                </a>
              )}

              <div className="flex gap-2 pt-3 border-t border-gray-100">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => navigate(`/dashboard/deploy?site=${site.id}`)}
                >
                  Deploy
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate(`/dashboard/monitor?site=${site.id}`)}
                >
                  Monitor
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="ml-auto text-red-500 hover:bg-red-50"
                  onClick={() => handleDelete(site.id, site.name)}
                >
                  Delete
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create site modal */}
      <Modal
        isOpen={showCreate}
        onClose={() => setShowCreate(false)}
        title="Create new site"
      >
        <div className="flex flex-col gap-4">
          <Input
            label="Site name"
            value={newName}
            onChange={(e) => {
              setNewName(e.target.value)
              setNewSlug(slugify(e.target.value))
            }}
            placeholder="My Awesome Site"
            autoFocus
          />
          <Input
            label="Slug (URL path)"
            value={newSlug}
            onChange={(e) => setNewSlug(slugify(e.target.value))}
            placeholder="my-awesome-site"
            helperText="Will be used in your deployment URL"
          />
          <Input
            label="GitHub / GitLab URL (optional)"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="https://github.com/you/repo"
            helperText="Leave blank to upload a ZIP after creation"
          />

          {error && (
            <p className="text-sm text-red-600">{error}</p>
          )}

          <div className="flex justify-end gap-3 pt-2">
            <Button variant="secondary" onClick={() => setShowCreate(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleCreate}
              isLoading={creating}
              disabled={!newName || !newSlug}
            >
              Create site
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
