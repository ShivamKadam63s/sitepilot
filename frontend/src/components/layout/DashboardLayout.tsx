import { Outlet, useLocation } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { Header } from './Header'

const TITLES: Record<string, string> = {
  '/dashboard/sites':    'Sites',
  '/dashboard/deploy':   'Deploy',
  '/dashboard/monitor':  'Monitoring',
  '/dashboard/settings': 'Settings',
}

export function DashboardLayout() {
  const { pathname } = useLocation()
  const title = TITLES[pathname] ?? 'Dashboard'

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header title={title} />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
