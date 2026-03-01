import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { apiClient } from '../api/client'
import { login as apiLogin, logout as apiLogout } from '../api/auth'
import { User } from '../types'

interface AuthContextValue {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  refreshCurrentUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const refreshCurrentUser = async () => {
    try {
      const { data } = await apiClient.get<User>('/auth/me')
      setUser(data)
    } catch {
      setUser(null)
    }
  }

  const login = async (email: string, password: string) => {
    await apiLogin(email, password)
    await refreshCurrentUser()
  }

  const logout = async () => {
    await apiLogout()
    setUser(null)
  }

  useEffect(() => {
    refreshCurrentUser().finally(() => setLoading(false))
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, refreshCurrentUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used inside AuthProvider')
  }
  return ctx
}
