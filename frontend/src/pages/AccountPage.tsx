import { FormEvent, useState } from 'react'
import { changeMyPassword, logout } from '../api/auth'

export function AccountPage() {
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [message, setMessage] = useState('')

  const getErrorMessage = (error: unknown): string => {
    const detail = (error as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
    if (typeof detail === 'string') {
      return detail
    }
    return 'Impossible de changer le mot de passe'
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (newPassword.length < 12) {
      setMessage('Le nouveau mot de passe doit contenir au moins 12 caractères')
      return
    }

    try {
      await changeMyPassword({ current_password: currentPassword, new_password: newPassword })
      setCurrentPassword('')
      setNewPassword('')
      setMessage('Mot de passe changé. Reconnexion requise...')
      await logout()
      window.location.href = '/login'
    } catch (error) {
      setMessage(getErrorMessage(error))
    }
  }

  return (
    <div className="max-w-xl space-y-4 rounded-lg border border-slate-200 p-4 dark:border-slate-700">
      <h2 className="text-xl font-semibold">Mon compte</h2>
      <p className="text-sm text-slate-500 dark:text-slate-400">Changer mon mot de passe</p>

      {message && <p className="text-sm">{message}</p>}

      <form onSubmit={handleSubmit} className="space-y-3">
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
        <button className="rounded bg-slate-900 px-3 py-1 text-white dark:bg-slate-100 dark:text-slate-900">Mettre à jour le mot de passe</button>
      </form>
    </div>
  )
}
