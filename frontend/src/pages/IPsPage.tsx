import { FormEvent, useEffect, useState } from 'react'
import { createIP, exportCSVUrl, getIPs, getSubnets, importCSV, scanSubnet, suggestIP } from '../api/ipam'
import { IPAddress, IPStatus, Subnet } from '../types'
import { useAuth } from '../hooks/useAuth'

export function IPsPage() {
  const { user } = useAuth()
  const isAdmin = user?.role === 'ADMIN'
  const [ips, setIps] = useState<IPAddress[]>([])
  const [subnets, setSubnets] = useState<Subnet[]>([])
  const [form, setForm] = useState({ address: '', status: 'RESERVED' as IPStatus, hostname: '', mac_address: '', site_id: 1, subnet_id: 1 })
  const [suggested, setSuggested] = useState<string>('')
  const [scanMessage, setScanMessage] = useState<string>('')

  const load = async () => {
    const [ipsData, subnetData] = await Promise.all([getIPs(), getSubnets()])
    setIps(ipsData)
    setSubnets(subnetData)
  }

  useEffect(() => {
    load().catch(() => undefined)
  }, [])

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    await createIP(form)
    await load()
  }

  const onSuggest = async () => {
    const ip = await suggestIP(form.subnet_id)
    setSuggested(ip)
    setForm((prev) => ({ ...prev, address: ip }))
  }

  const onImport = async (file: File) => {
    await importCSV(file)
    await load()
  }

  const onScan = async () => {
    const result = await scanSubnet(form.subnet_id)
    setScanMessage(
      `Scan ${result.subnet}: ${result.results.length} hôtes détectés, ${result.persisted.created} créés, ${result.persisted.updated} mis à jour`
    )
    await load()
  }

  return (
    <div className="space-y-6">
      {isAdmin && (
        <div className="rounded-lg border border-slate-200 p-4 dark:border-slate-700">
          <h3 className="mb-3 font-medium">Ajouter une IP</h3>
          <form onSubmit={submit} className="grid grid-cols-1 gap-3 md:grid-cols-3">
            <input className="rounded border border-slate-300 px-2 py-1 dark:border-slate-700 dark:bg-slate-900" value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} placeholder="IP" required />
            <select className="rounded border border-slate-300 px-2 py-1 dark:border-slate-700 dark:bg-slate-900" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value as IPStatus })}>
              {['FREE', 'RESERVED', 'STATIC', 'DHCP', 'CONFLICT', 'UNKNOWN'].map((status) => <option key={status} value={status}>{status}</option>)}
            </select>
            <select className="rounded border border-slate-300 px-2 py-1 dark:border-slate-700 dark:bg-slate-900" value={form.subnet_id} onChange={(e) => setForm({ ...form, subnet_id: Number(e.target.value) })}>
              {subnets.map((subnet) => <option key={subnet.id} value={subnet.id}>{subnet.cidr}</option>)}
            </select>
            <input className="rounded border border-slate-300 px-2 py-1 dark:border-slate-700 dark:bg-slate-900" value={form.hostname} onChange={(e) => setForm({ ...form, hostname: e.target.value })} placeholder="Hostname" />
            <input className="rounded border border-slate-300 px-2 py-1 dark:border-slate-700 dark:bg-slate-900" value={form.mac_address} onChange={(e) => setForm({ ...form, mac_address: e.target.value })} placeholder="MAC" />
            <input className="rounded border border-slate-300 px-2 py-1 dark:border-slate-700 dark:bg-slate-900" value={form.site_id} onChange={(e) => setForm({ ...form, site_id: Number(e.target.value) })} placeholder="Site ID" type="number" />
            <div className="flex gap-2 md:col-span-3">
              <button type="button" onClick={onSuggest} className="rounded border border-slate-300 px-3 py-1 dark:border-slate-700">Suggest free IP</button>
              <button type="button" onClick={onScan} className="rounded border border-slate-300 px-3 py-1 dark:border-slate-700">Scan subnet</button>
              <button className="rounded bg-slate-900 px-3 py-1 text-white dark:bg-slate-100 dark:text-slate-900">Save</button>
              <label className="rounded border border-slate-300 px-3 py-1 dark:border-slate-700 cursor-pointer">
                Import CSV
                <input type="file" accept=".csv" className="hidden" onChange={(e) => e.target.files?.[0] && onImport(e.target.files[0])} />
              </label>
              <a href={exportCSVUrl()} className="rounded border border-slate-300 px-3 py-1 dark:border-slate-700">Export CSV</a>
            </div>
            {suggested && <p className="text-sm md:col-span-3">Suggested: {suggested}</p>}
            {scanMessage && <p className="text-sm md:col-span-3">{scanMessage}</p>}
          </form>
        </div>
      )}

      <div className="rounded-lg border border-slate-200 p-4 dark:border-slate-700">
        <h3 className="mb-3 font-medium">Liste des IPs</h3>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left">
              <th>Address</th>
              <th>Status</th>
              <th>Hostname</th>
              <th>MAC</th>
            </tr>
          </thead>
          <tbody>
            {ips.map((ip) => (
              <tr key={ip.id} className="border-t border-slate-200 dark:border-slate-700">
                <td>{ip.address}</td>
                <td>{ip.status}</td>
                <td>{ip.hostname}</td>
                <td>{ip.mac_address}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
