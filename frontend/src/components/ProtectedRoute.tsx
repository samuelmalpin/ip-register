import { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return <div className="p-8">Loading...</div>
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (user.must_change_credentials && location.pathname !== '/first-login-setup') {
    return <Navigate to="/first-login-setup" replace />
  }

  if (!user.must_change_credentials && location.pathname === '/first-login-setup') {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}
