import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from '@/api/queryClient'
import { ProtectedRoute } from '@/components/common/ProtectedRoute'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { LoginPage }      from '@/pages/LoginPage'
import { SitesPage }      from '@/pages/SitesPage'
import { DeployPage }     from '@/pages/DeployPage'
import { MonitoringPage } from '@/pages/MonitoringPage'
import { SettingsPage }   from '@/pages/SettingsPage'

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Public */}
          <Route path="/login" element={<LoginPage />} />

          {/* Protected dashboard */}
          <Route element={<ProtectedRoute />}>
            <Route element={<DashboardLayout />}>
              <Route path="/dashboard/sites"    element={<SitesPage />} />
              <Route path="/dashboard/deploy"   element={<DeployPage />} />
              <Route path="/dashboard/monitor"  element={<MonitoringPage />} />
              <Route path="/dashboard/settings" element={<SettingsPage />} />
            </Route>
          </Route>

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/dashboard/sites" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
