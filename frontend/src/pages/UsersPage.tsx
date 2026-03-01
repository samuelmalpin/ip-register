import { FormEvent, useEffect, useState } from 'react'
import { createUser, deleteUser, fetchUsers, resetUserPassword, updateUser } from '../api/auth'
import { Role, User } from '../types'
import { useAuth } from '../hooks/useAuth'

export function UsersPage() {
  const { user: currentUser } = useAuth()
  const [users, setUsers] = useState<User[]>([])
  const [message, setMessage] = useState<string>('')
  const [createForm, setCreateForm] = useState({ email: '', password: '', role: 'VIEWER' as Role })
  const [passwordDrafts, setPasswordDrafts] = useState<Record<number, string>>({})

  const isAdmin = currentUser?.role === 'ADMIN'

  const load = async () => {
    const data = await fetchUsers()
    setUsers(data)
  }

  const getErrorMessage = (error: unknown): string => {
    const detail = (error as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
    if (typeof detail === 'string') {
      return detail
    }
    if (Array.isArray(detail) && detail.length > 0) {
      return String(detail[0])
    }
    return 'Une erreur est survenue'
  }

  useEffect(() => {
    if (isAdmin) {
      load().catch(() => setMessage('Impossible de charger les utilisateurs'))
    }
  }, [isAdmin])

  if (!isAdmin) {
    return <p>Accès refusé (admin uniquement).</p>
  }

  const handleRoleChange = async (userId: number, role: Role) => {
    try {
      await updateUser(userId, { role })
      await load()
      setMessage('Rôle mis à jour')
    } catch (error) {
      setMessage(getErrorMessage(error))
    }
  }

  const handleActiveChange = async (userId: number, isActive: boolean) => {
    try {
      await updateUser(userId, { is_active: isActive })
      await load()
      setMessage('Statut mis à jour')
    } catch (error) {
      setMessage(getErrorMessage(error))
    }
  }

  const handleDelete = async (userId: number) => {
    if (currentUser?.id === userId) {
      setMessage('Tu ne peux pas supprimer ton propre compte')
      return
    }
    try {
      await deleteUser(userId)
      await load()
      setMessage('Utilisateur supprimé')
    } catch (error) {
      setMessage(getErrorMessage(error))
    }
  }

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault()
    try {
      await createUser(createForm)
      setCreateForm({ email: '', password: '', role: 'VIEWER' })
      await load()
      setMessage('Utilisateur créé')
    } catch (error) {
      setMessage(getErrorMessage(error))
    }
  }

  const handleResetPassword = async (userId: number) => {
    const newPassword = passwordDrafts[userId] || ''
    if (newPassword.length < 12) {
        setMessage('Le nouveau mot de passe doit contenir au moins 12 caractères')
        return
    }
    try {
      await resetUserPassword(userId, newPassword)
      setPasswordDrafts((prev) => ({ ...prev, [userId]: '' }))
      setMessage('Mot de passe utilisateur mis à jour')
    } catch (error) {
      setMessage(getErrorMessage(error))
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-semibold">Gestion des utilisateurs</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">Modifier les accès au panel (rôle et activation).</p>
      </div>

      {message && <p className="text-sm">{message}</p>}

      <form onSubmit={handleCreate} className="grid grid-cols-1 gap-3 rounded-lg border border-slate-200 p-4 md:grid-cols-4 dark:border-slate-700">
        <input
          className="rounded border border-slate-300 px-2 py-1 dark:border-slate-700 dark:bg-slate-900"
          type="email"
          placeholder="Email"
          value={createForm.email}
          onChange={(e) => setCreateForm((prev) => ({ ...prev, email: e.target.value }))}
          required
        />
        <input
          className="rounded border border-slate-300 px-2 py-1 dark:border-slate-700 dark:bg-slate-900"
          type="password"
          placeholder="Mot de passe (12+ chars)"
          value={createForm.password}
          onChange={(e) => setCreateForm((prev) => ({ ...prev, password: e.target.value }))}
          required
          minLength={12}
        />
        <select
          className="rounded border border-slate-300 px-2 py-1 dark:border-slate-700 dark:bg-slate-900"
          value={createForm.role}
          onChange={(e) => setCreateForm((prev) => ({ ...prev, role: e.target.value as Role }))}
        >
          <option value="VIEWER">VIEWER</option>
          <option value="ADMIN">ADMIN</option>
        </select>
        <button className="rounded bg-slate-900 px-3 py-1 text-white dark:bg-slate-100 dark:text-slate-900">Ajouter utilisateur</button>
      </form>

      <div className="rounded-lg border border-slate-200 p-4 dark:border-slate-700">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left">
              <th>Email</th>
              <th>Rôle</th>
              <th>Actif</th>
              <th>Nouveau MDP</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} className="border-t border-slate-200 dark:border-slate-700">
                <td>{user.email}</td>
                <td>
                  <select
                    className="rounded border border-slate-300 px-2 py-1 dark:border-slate-700 dark:bg-slate-900"
                    value={user.role}
                    disabled={user.role === 'ADMIN'}
                    onChange={(e) => handleRoleChange(user.id, e.target.value as Role)}
                  >
                    <option value="ADMIN">ADMIN</option>
                    <option value="VIEWER">VIEWER</option>
                  </select>
                </td>
                <td>
                  <label className="inline-flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={user.is_active}
                      disabled={user.role === 'ADMIN'}
                      onChange={(e) => handleActiveChange(user.id, e.target.checked)}
                    />
                    {user.is_active ? 'Oui' : 'Non'}
                  </label>
                </td>
                <td>
                  <input
                    className="rounded border border-slate-300 px-2 py-1 dark:border-slate-700 dark:bg-slate-900"
                    type="password"
                    value={passwordDrafts[user.id] || ''}
                    placeholder="12+ chars"
                    onChange={(e) => setPasswordDrafts((prev) => ({ ...prev, [user.id]: e.target.value }))}
                  />
                </td>
                <td>
                  <button
                    onClick={() => handleResetPassword(user.id)}
                    className="mr-2 rounded border border-slate-300 px-3 py-1 dark:border-slate-700"
                  >
                    MDP
                  </button>
                  <button
                    onClick={() => handleDelete(user.id)}
                    disabled={user.role === 'ADMIN'}
                    className="rounded border border-slate-300 px-3 py-1 dark:border-slate-700"
                  >
                    Supprimer
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
