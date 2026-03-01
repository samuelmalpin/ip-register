import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { AuthProvider } from './hooks/useAuth'
import { LoginPage } from './pages/LoginPage'
import { DashboardPage } from './pages/DashboardPage'
import { IPsPage } from './pages/IPsPage'
import { SitesPage } from './pages/SitesPage'
import { UsersPage } from './pages/UsersPage'
import { AccountPage } from './pages/AccountPage'
import { FirstLoginSetupPage } from './pages/FirstLoginSetupPage'
import { ProtectedRoute } from './components/ProtectedRoute'
import { Layout } from './components/Layout'

function AppRoutes() {
  const [dark, setDark] = useState(false)

  useEffect(() => {
    const stored = localStorage.getItem('theme') === 'dark'
    setDark(stored)
  }, [])

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    localStorage.setItem('theme', dark ? 'dark' : 'light')
  }, [dark])

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="*"
        element={
          <ProtectedRoute>
            <Layout dark={dark} onToggleDark={() => setDark((prev) => !prev)}>
              <Routes>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/ips" element={<IPsPage />} />
                <Route path="/sites" element={<SitesPage />} />
                <Route path="/users" element={<UsersPage />} />
                <Route path="/account" element={<AccountPage />} />
                <Route path="/first-login-setup" element={<FirstLoginSetupPage />} />
              </Routes>
            </Layout>
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}
