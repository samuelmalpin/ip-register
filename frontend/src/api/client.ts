import axios from 'axios'
import type { InternalAxiosRequestConfig } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
})

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const csrf = document.cookie
    .split('; ')
    .find((cookie) => cookie.startsWith('csrf_token='))
    ?.split('=')[1]

  if (csrf && config.method && ['post', 'patch', 'put', 'delete'].includes(config.method)) {
    config.headers['X-CSRF-Token'] = csrf
  }
  return config
})
