import { NavLink } from 'react-router-dom'
import { clsx } from 'clsx'
import { useAuthStore } from '@/store/authStore'

const NAV_ITEMS = [
  { to: '/dashboard/sites',   label: 'Sites',      icon: '◫' },
  { to: '/dashboard/deploy',  label: 'Deploy',     icon: '⬆' },
  { to: '/dashboard/monitor', label: 'Monitoring', icon: '◉' },
  { to: '/dashboard/settings',label: 'Settings',   icon: '⚙' },
]

export function Sidebar() {
  const { tenant, user } = useAuthStore()

  return (
    <aside className="flex h-screen w-56 flex-col border-r border-gray-200 bg-white px-3 py-4">
      {/* Logo */}
      <div className="mb-6 px-3">
        <span className="text-xl font-semibold text-brand-800">SitePilot</span>
        {tenant && (
          <p className="mt-0.5 truncate text-xs text-gray-500">{tenant.name}</p>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-1">
        {NAV_ITEMS.map(({ to, label, icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              clsx(
                'sidebar-link',
                isActive && 'active'
              )
            }
          >
            <span className="text-base">{icon}</span>
            {label}
          </NavLink>
        ))}
      </nav>

      {/* User info at bottom */}
      <div className="mt-auto border-t border-gray-100 pt-3 px-2">
        <p className="truncate text-xs font-medium text-gray-700">{user?.email}</p>
        <p className="text-xs text-gray-400 capitalize">{user?.role}</p>
      </div>
    </aside>
  )
}
