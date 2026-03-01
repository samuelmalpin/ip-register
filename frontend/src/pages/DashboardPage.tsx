import { useEffect, useState } from 'react'
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { getDashboardStats } from '../api/ipam'
import { DashboardStats } from '../types'

export function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)

  useEffect(() => {
    getDashboardStats().then(setStats).catch(() => setStats(null))
  }, [])

  if (!stats) {
    return <p>Loading dashboard...</p>
  }

  const siteData = Object.entries(stats.by_site).map(([name, value]) => ({ name, value }))
  const subnetData = Object.entries(stats.by_subnet).map(([name, value]) => ({ name, value }))
  const isDark = document.documentElement.classList.contains('dark')

  const barColor = isDark ? '#60a5fa' : '#2563eb'
  const axisColor = isDark ? '#cbd5e1' : '#475569'
  const gridColor = isDark ? '#334155' : '#cbd5e1'
  const tooltipStyle = {
    backgroundColor: isDark ? '#0f172a' : '#ffffff',
    border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`,
    color: isDark ? '#f8fafc' : '#0f172a',
  }
  const piePalette = isDark
    ? ['#60a5fa', '#34d399', '#f59e0b', '#f472b6', '#a78bfa', '#22d3ee']
    : ['#2563eb', '#059669', '#d97706', '#db2777', '#7c3aed', '#0891b2']

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        <Card title="Total IPs" value={stats.total_ips} />
        <Card title="Used IPs" value={stats.used_ips} />
        <Card title="Free IPs" value={stats.free_ips} />
        <Card title="Free %" value={`${stats.free_percentage.toFixed(1)}%`} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-lg border border-slate-200 p-4 text-slate-500 dark:border-slate-700 dark:text-slate-300">
          <h3 className="mb-3 font-medium">IPs by site</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={siteData}>
                <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
                <XAxis dataKey="name" stroke={axisColor} tick={{ fill: axisColor }} />
                <YAxis stroke={axisColor} tick={{ fill: axisColor }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="value" fill={barColor} radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="rounded-lg border border-slate-200 p-4 text-slate-700 dark:border-slate-700 dark:text-slate-100">
          <h3 className="mb-3 font-medium">IPs by subnet</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={subnetData} dataKey="value" nameKey="name" outerRadius={100}>
                  {subnetData.map((entry, index) => (
                    <Cell key={`${entry.name}-${index}`} fill={piePalette[index % piePalette.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={tooltipStyle} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}

function Card({ title, value }: { title: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-slate-200 p-4 dark:border-slate-700">
      <p className="text-sm text-slate-500 dark:text-slate-400">{title}</p>
      <p className="text-2xl font-semibold">{value}</p>
    </div>
  )
}
