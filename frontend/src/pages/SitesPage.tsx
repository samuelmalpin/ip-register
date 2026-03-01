import { FormEvent, useEffect, useState } from 'react'
import { createSite, createSubnet, deleteSite, deleteSubnet, getSites, getSubnets } from '../api/ipam'
import { Site, Subnet } from '../types'
import { useAuth } from '../hooks/useAuth'

export function SitesPage() {
  const { user } = useAuth()
  const isAdmin = user?.role === 'ADMIN'
  const [sites, setSites] = useState<Site[]>([])
  const [subnets, setSubnets] = useState<Subnet[]>([])
  const [siteForm, setSiteForm] = useState({ name: '', location: '' })
  const [subnetForm, setSubnetForm] = useState({ cidr: '', site_id: 1, dhcp_start: '', dhcp_end: '' })
  const [message, setMessage] = useState('')

  const getErrorMessage = (error: unknown): string => {
    const detail = (error as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
    if (typeof detail === 'string') {
      return detail
    }
    return 'Une erreur est survenue'
  }

  const load = async () => {
    const [siteData, subnetData] = await Promise.all([getSites(), getSubnets()])
    setSites(siteData)
    setSubnets(subnetData)
    if (siteData.length > 0 && subnetForm.site_id === 1) {
      setSubnetForm((prev) => ({ ...prev, site_id: siteData[0].id }))
    }
  }

  useEffect(() => {
    load().catch(() => undefined)
  }, [])

  const submitSite = async (e: FormEvent) => {
    e.preventDefault()
    try {
      await createSite(siteForm)
      setSiteForm({ name: '', location: '' })
      await load()
      setMessage('Site ajouté')
    } catch (error) {
      setMessage(getErrorMessage(error))
    }
  }

  const submitSubnet = async (e: FormEvent) => {
    e.preventDefault()
    try {
      await createSubnet({
        cidr: subnetForm.cidr,
        site_id: subnetForm.site_id,
        dhcp_start: subnetForm.dhcp_start || null,
        dhcp_end: subnetForm.dhcp_end || null,
      })
      setSubnetForm({ cidr: '', site_id: subnetForm.site_id, dhcp_start: '', dhcp_end: '' })
      await load()
      setMessage('Subnet ajouté')
    } catch (error) {
      setMessage(getErrorMessage(error))
    }
  }

  const handleDeleteSite = async (siteId: number) => {
    try {
      await deleteSite(siteId)
      await load()
      setMessage('Site supprimé')
    } catch (error) {
      setMessage(getErrorMessage(error))
    }
  }

  const handleDeleteSubnet = async (subnetId: number) => {
    try {
      await deleteSubnet(subnetId)
      await load()
      setMessage('Subnet supprimé')
    } catch (error) {
      setMessage(getErrorMessage(error))
    }
  }

  return (
    <div className="space-y-6">
      {message && <p className="text-sm">{message}</p>}
      {isAdmin && (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <form onSubmit={submitSite} className="space-y-2 rounded-lg border border-slate-200 p-4 dark:border-slate-700">
            <h3 className="font-medium">Créer un site</h3>
            <input className="w-full rounded border border-slate-300 px-2 py-1 dark:border-slate-700 dark:bg-slate-900" placeholder="Nom" value={siteForm.name} onChange={(e) => setSiteForm({ ...siteForm, name: e.target.value })} required />
            <input className="w-full rounded border border-slate-300 px-2 py-1 dark:border-slate-700 dark:bg-slate-900" placeholder="Location" value={siteForm.location} onChange={(e) => setSiteForm({ ...siteForm, location: e.target.value })} required />
            <button className="rounded bg-slate-900 px-3 py-1 text-white dark:bg-slate-100 dark:text-slate-900">Ajouter site</button>
          </form>

          <form onSubmit={submitSubnet} className="space-y-2 rounded-lg border border-slate-200 p-4 dark:border-slate-700">
            <h3 className="font-medium">Créer un subnet</h3>
            <input className="w-full rounded border border-slate-300 px-2 py-1 dark:border-slate-700 dark:bg-slate-900" placeholder="CIDR ex: 192.168.1.0/24" value={subnetForm.cidr} onChange={(e) => setSubnetForm({ ...subnetForm, cidr: e.target.value })} required />
            <input className="w-full rounded border border-slate-300 px-2 py-1 dark:border-slate-700 dark:bg-slate-900" placeholder="DHCP start (optionnel)" value={subnetForm.dhcp_start} onChange={(e) => setSubnetForm({ ...subnetForm, dhcp_start: e.target.value })} />
            <input className="w-full rounded border border-slate-300 px-2 py-1 dark:border-slate-700 dark:bg-slate-900" placeholder="DHCP end (optionnel)" value={subnetForm.dhcp_end} onChange={(e) => setSubnetForm({ ...subnetForm, dhcp_end: e.target.value })} />
            <select className="w-full rounded border border-slate-300 px-2 py-1 dark:border-slate-700 dark:bg-slate-900" value={subnetForm.site_id} onChange={(e) => setSubnetForm({ ...subnetForm, site_id: Number(e.target.value) })}>
              {sites.map((site) => <option key={site.id} value={site.id}>{site.name}</option>)}
            </select>
            <button className="rounded bg-slate-900 px-3 py-1 text-white dark:bg-slate-100 dark:text-slate-900">Ajouter subnet</button>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className="rounded-lg border border-slate-200 p-4 dark:border-slate-700">
          <h3 className="mb-2 font-medium">Sites</h3>
          <ul className="space-y-1 text-sm">
            {sites.map((site) => (
              <li key={site.id} className="flex items-center justify-between gap-2">
                <span>{site.id} - {site.name} ({site.location})</span>
                {isAdmin && (
                  <button className="rounded border border-slate-300 px-2 py-1 dark:border-slate-700" onClick={() => handleDeleteSite(site.id)}>
                    Supprimer
                  </button>
                )}
              </li>
            ))}
          </ul>
        </div>
        <div className="rounded-lg border border-slate-200 p-4 dark:border-slate-700">
          <h3 className="mb-2 font-medium">Subnets</h3>
          <ul className="space-y-1 text-sm">
            {subnets.map((subnet) => (
              <li key={subnet.id} className="flex items-center justify-between gap-2">
                <span>{subnet.id} - {subnet.cidr} (site {subnet.site_id}) {subnet.dhcp_start && subnet.dhcp_end ? `DHCP: ${subnet.dhcp_start} - ${subnet.dhcp_end}` : ''}</span>
                {isAdmin && (
                  <button className="rounded border border-slate-300 px-2 py-1 dark:border-slate-700" onClick={() => handleDeleteSubnet(subnet.id)}>
                    Supprimer
                  </button>
                )}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}
