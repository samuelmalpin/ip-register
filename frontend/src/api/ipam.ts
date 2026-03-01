import { apiClient } from './client'
import { DashboardStats, IPAddress, Site, Subnet } from '../types'

export async function getSites(): Promise<Site[]> {
  const { data } = await apiClient.get<Site[]>('/sites')
  return data
}

export async function createSite(payload: { name: string; location: string }): Promise<Site> {
  const { data } = await apiClient.post<Site>('/sites', payload)
  return data
}

export async function deleteSite(siteId: number): Promise<void> {
  await apiClient.delete(`/sites/${siteId}`)
}

export async function getSubnets(): Promise<Subnet[]> {
  const { data } = await apiClient.get<Subnet[]>('/subnets')
  return data
}

export async function createSubnet(payload: {
  cidr: string
  site_id: number
  dhcp_start?: string | null
  dhcp_end?: string | null
}): Promise<Subnet> {
  const { data } = await apiClient.post<Subnet>('/subnets', payload)
  return data
}

export async function deleteSubnet(subnetId: number): Promise<void> {
  await apiClient.delete(`/subnets/${subnetId}`)
}

export async function getIPs(): Promise<IPAddress[]> {
  const { data } = await apiClient.get<IPAddress[]>('/ips')
  return data
}

export async function createIP(payload: Omit<IPAddress, 'id'>): Promise<IPAddress> {
  const { data } = await apiClient.post<IPAddress>('/ips', payload)
  return data
}

export async function getDashboardStats(): Promise<DashboardStats> {
  const { data } = await apiClient.get<DashboardStats>('/dashboard/stats')
  return data
}

export async function suggestIP(subnetId: number): Promise<string> {
  const { data } = await apiClient.get<{ suggested_ip: string }>(`/ips/suggest/${subnetId}`)
  return data.suggested_ip
}

export async function importCSV(file: File): Promise<{ created: number; errors: unknown[] }> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await apiClient.post('/ips/import', form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return data
}

export function exportCSVUrl(): string {
  return `${apiClient.defaults.baseURL}/ips/export`
}

export async function scanSubnet(subnetId: number): Promise<{
  subnet: string
  results: Array<{ address: string; status: string }>
  persisted: { created: number; updated: number; total_detected: number }
}> {
  const { data } = await apiClient.post(`/scan/${subnetId}`)
  return data
}
