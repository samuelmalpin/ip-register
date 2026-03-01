export type Role = 'ADMIN' | 'VIEWER'

export interface User {
  id: number
  email: string
  role: Role
  is_active: boolean
  must_change_credentials: boolean
}

export interface Site {
  id: number
  name: string
  location: string
}

export interface Subnet {
  id: number
  cidr: string
  site_id: number
  dhcp_start?: string | null
  dhcp_end?: string | null
}

export type IPStatus = 'FREE' | 'RESERVED' | 'STATIC' | 'DHCP' | 'CONFLICT' | 'UNKNOWN'

export interface IPAddress {
  id: number
  address: string
  status: IPStatus
  hostname?: string | null
  mac_address?: string | null
  site_id: number
  subnet_id: number
}

export interface DashboardStats {
  total_ips: number
  used_ips: number
  free_ips: number
  free_percentage: number
  by_site: Record<string, number>
  by_subnet: Record<string, number>
}
