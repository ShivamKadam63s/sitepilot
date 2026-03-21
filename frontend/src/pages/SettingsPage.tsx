import { useAuthStore } from '@/store/authStore'
import { Button } from '@/components/common/Button'

export function SettingsPage() {
  const { user, tenant } = useAuthStore()

  if (!user || !tenant) return null

  const storagePercent = Math.round(
    (tenant.storageUsedMb / tenant.storageLimitMb) * 100
  )

  return (
    <div className="mx-auto max-w-2xl flex flex-col gap-6">
      {/* Account */}
      <Section title="Account">
        <Row label="Email"       value={user.email} />
        <Row label="Role"        value={user.role} capitalize />
        <Row label="Tenant"      value={tenant.name} />
      </Section>

      {/* Plan */}
      <Section title="Plan">
        <Row
          label="Current plan"
          value={tenant.plan}
          capitalize
          pill
        />
        <Row
          label="Sites"
          value={`${tenant.sitesUsed} / ${tenant.sitesAllowed}`}
        />
        <div className="flex flex-col gap-1">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Storage</span>
            <span className="text-gray-700">
              {tenant.storageUsedMb} MB / {tenant.storageLimitMb} MB
            </span>
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-gray-100">
            <div
              className="h-full rounded-full bg-brand-600 transition-all"
              style={{ width: `${Math.min(storagePercent, 100)}%` }}
            />
          </div>
          <p className="text-xs text-gray-400">{storagePercent}% used</p>
        </div>
      </Section>

      {/* Danger zone */}
      <Section title="Danger zone">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-800">Delete account</p>
            <p className="text-xs text-gray-400">
              Permanently delete your account and all sites
            </p>
          </div>
          <Button variant="danger" size="sm" disabled>
            Delete account
          </Button>
        </div>
      </Section>
    </div>
  )
}

// ── Sub-components ────────────────────────────────────────────────────────────

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white">
      <div className="border-b border-gray-100 px-5 py-3">
        <h3 className="text-sm font-medium text-gray-900">{title}</h3>
      </div>
      <div className="flex flex-col gap-4 px-5 py-4">{children}</div>
    </div>
  )
}

function Row({
  label, value, capitalize = false, pill = false,
}: {
  label: string
  value: string | number
  capitalize?: boolean
  pill?: boolean
}) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-gray-600">{label}</span>
      {pill ? (
        <span className="rounded-full bg-brand-100 px-3 py-0.5 text-xs font-medium
                         text-brand-800 capitalize">
          {value}
        </span>
      ) : (
        <span className={`text-sm font-medium text-gray-800 ${capitalize ? 'capitalize' : ''}`}>
          {value}
        </span>
      )}
    </div>
  )
}
