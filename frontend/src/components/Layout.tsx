import { Link, useLocation } from 'react-router-dom'
import { DarkModeToggle } from './DarkModeToggle'
import { useAuth } from '../hooks/useAuth'

export function Layout({
  dark,
  onToggleDark,
  children
}: {
  dark: boolean
  onToggleDark: () => void
  children: React.ReactNode
}) {
  const location = useLocation()
  const { user, logout } = useAuth()

  return (
    <div className="min-h-screen">
      <header className="flex items-center justify-between border-b border-slate-200 px-6 py-4 dark:border-slate-700">
        <div className="flex items-center gap-4">
          <h1 className="font-semibold">DevOps IPAM</h1>
          <nav className="flex gap-2 text-sm">
            <Link className={location.pathname === '/' ? 'font-semibold' : ''} to="/">Dashboard</Link>
            <Link className={location.pathname === '/ips' ? 'font-semibold' : ''} to="/ips">IPs</Link>
            <Link className={location.pathname === '/sites' ? 'font-semibold' : ''} to="/sites">Sites/Subnets</Link>
            <Link className={location.pathname === '/account' ? 'font-semibold' : ''} to="/account">Mon compte</Link>
            {user?.role === 'ADMIN' && (
              <Link className={location.pathname === '/users' ? 'font-semibold' : ''} to="/users">Users</Link>
            )}
          </nav>
        </div>
        <div className="flex items-center gap-3 text-sm">
          <span>{user?.email} ({user?.role})</span>
          <DarkModeToggle dark={dark} onToggle={onToggleDark} />
          <button onClick={logout} className="rounded-md border border-slate-300 px-3 py-1 dark:border-slate-700">
            Logout
          </button>
        </div>
      </header>
      <main className="p-6">{children}</main>
    </div>
  )
}
