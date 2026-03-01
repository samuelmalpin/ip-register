import { apiClient } from './client'
import { Role, User } from '../types'

export async function login(email: string, password: string) {
  await apiClient.post('/auth/login', { email, password })
}

export async function register(email: string, password: string, role: 'ADMIN' | 'VIEWER') {
  await apiClient.post('/auth/register', { email, password, role })
}

export async function refreshToken() {
  await apiClient.post('/auth/refresh')
}

export async function logout() {
  await apiClient.post('/auth/logout')
}

export async function changeMyPassword(payload: { current_password: string; new_password: string }) {
  await apiClient.post('/auth/change-password', payload)
}

export async function firstLoginSetup(payload: { new_email: string; current_password: string; new_password: string }) {
  await apiClient.post('/auth/first-login-setup', payload)
}

export async function fetchUsers(): Promise<User[]> {
  const { data } = await apiClient.get<User[]>('/users')
  return data
}

export async function createUser(payload: { email: string; password: string; role: Role }): Promise<User> {
  const { data } = await apiClient.post<User>('/users', payload)
  return data
}

export async function updateUser(userId: number, payload: { role?: Role; is_active?: boolean }): Promise<User> {
  const { data } = await apiClient.patch<User>(`/users/${userId}`, payload)
  return data
}

export async function deleteUser(userId: number): Promise<void> {
  await apiClient.delete(`/users/${userId}`)
}

export async function resetUserPassword(userId: number, newPassword: string): Promise<User> {
  const { data } = await apiClient.post<User>(`/users/${userId}/password`, { new_password: newPassword })
  return data
}
