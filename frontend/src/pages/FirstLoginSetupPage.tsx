import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { firstLoginSetup } from '../api/auth'
import { useAuth } from '../hooks/useAuth'

export function FirstLoginSetupPage() {
  const navigate = useNavigate()
  const { user, refreshCurrentUser } = useAuth()

  const [newEmail, setNewEmail] = useState(user?.email ?? '')
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  const getErrorMessage = (error: unknown): string => {
    const detail = (error as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
    if (typeof detail === 'string') {
      return detail
    }
    return 'Impossible de finaliser la première connexion'
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setMessage('')

    if (newPassword.length < 12) {
      setMessage('Le nouveau mot de passe doit contenir au moins 12 caractères')
      return
    }

    setLoading(true)
    try {
      await firstLoginSetup({
        new_email: newEmail,
        current_password: currentPassword,
        new_password: newPassword,
      })
      await refreshCurrentUser()
      navigate('/')
    } catch (error) {
      setMessage(getErrorMessage(error))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-xl space-y-4 rounded-lg border border-slate-200 p-4 dark:border-slate-700">
      <h2 className="text-xl font-semibold">Première connexion administrateur</h2>
      <p className="text-sm text-slate-500 dark:text-slate-400">
        Pour sécuriser le panel, vous devez changer l&apos;email admin et le mot de passe par défaut avant de continuer.
      </p>

      {message && <p className="text-sm">{message}</p>}

      <form onSubmit={handleSubmit} className="space-y-3">
        <input
          className="w-full rounded border border-slate-300 px-3 py-2 dark:border-slate-700 dark:bg-slate-900"
          type="email"
          placeholder="Nouvel email admin"
          value={newEmail}
          onChange={(e) => setNewEmail(e.target.value)}
          required
        />
        <input
          className="w-full rounded border border-slate-300 px-3 py-2 dark:border-slate-700 dark:bg-slate-900"
          type="password"
          placeholder="Mot de passe actuel"
          value={currentPassword}
          onChange={(e) => setCurrentPassword(e.target.value)}
          required
        />
        <input
          className="w-full rounded border border-slate-300 px-3 py-2 dark:border-slate-700 dark:bg-slate-900"
          type="password"
          placeholder="Nouveau mot de passe"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          required
          minLength={12}
        />
        <button
          disabled={loading}
          className="rounded bg-slate-900 px-3 py-1 text-white disabled:opacity-50 dark:bg-slate-100 dark:text-slate-900"
        >
          {loading ? 'Validation...' : 'Valider les nouveaux identifiants'}
        </button>
      </form>
    </div>
  )
}
