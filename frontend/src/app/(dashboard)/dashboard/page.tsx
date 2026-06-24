'use client'
import { useEffect, useState } from 'react'
import { Building2, TrendingUp, Bell, Sparkles, ArrowUpRight } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import { DashboardData } from '@/types'
import Header from '@/components/layout/Header'
import StatCard from '@/components/ui/StatCard'
import { Card, CardHeader, CardTitle } from '@/components/ui/Card'
import InventoryChart from '@/components/charts/InventoryChart'
import { formatPSM, formatDate } from '@/lib/utils'
import Link from 'next/link'

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get<DashboardData>('/market/dashboard/')
      .then(r => setData(r.data))
      .catch(() => toast.error('Failed to load dashboard data'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="flex flex-col flex-1">
      <Header title="Dashboard" subtitle="Egyptian Real Estate Market Overview" />

      <div className="p-6 space-y-6">
        {/* Stats Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Active Listings"
            value={loading ? '...' : (data?.inventory.total_active.toLocaleString() || '0')}
            subtitle="Across all portals"
            icon={Building2}
          />
          <StatCard
            title="New This Week"
            value={loading ? '...' : (data?.inventory.new_last_7d.toLocaleString() || '0')}
            subtitle="New listings (7 days)"
            icon={TrendingUp}
            iconColor="text-green-600"
            iconBg="bg-green-50"
          />
          <StatCard
            title="Developers Tracked"
            value={loading ? '...' : (data?.top_developers.length?.toString() || '0')}
            subtitle="Active developers"
            icon={Building2}
            iconColor="text-purple-600"
            iconBg="bg-purple-50"
          />
          <StatCard
            title="Market Insights"
            value={loading ? '...' : (data?.latest_insights.length?.toString() || '0')}
            subtitle="AI-generated reports"
            icon={Sparkles}
            iconColor="text-amber-600"
            iconBg="bg-amber-50"
          />
        </div>

        {/* Middle Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Inventory by Type */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Inventory by Property Type</CardTitle>
              <Link href="/properties" className="text-sm text-brand-600 hover:underline flex items-center gap-1">
                View all <ArrowUpRight className="w-3.5 h-3.5" />
              </Link>
            </CardHeader>
            {loading ? (
              <div className="h-48 animate-pulse bg-gray-100 rounded-lg" />
            ) : (
              <InventoryChart data={data?.inventory.by_type || []} />
            )}
          </Card>

          {/* Top Developers */}
          <Card>
            <CardHeader>
              <CardTitle>Top Developers</CardTitle>
              <Link href="/market" className="text-sm text-brand-600 hover:underline flex items-center gap-1">
                Full rankings <ArrowUpRight className="w-3.5 h-3.5" />
              </Link>
            </CardHeader>
            <div className="space-y-3">
              {loading ? (
                Array(5).fill(0).map((_, i) => (
                  <div key={i} className="h-10 animate-pulse bg-gray-100 rounded-lg" />
                ))
              ) : (
                data?.top_developers.slice(0, 6).map((dev, i) => (
                  <div key={dev.slug} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="w-6 h-6 rounded-full bg-gray-100 text-gray-600 text-xs flex items-center justify-center font-bold">
                        {i + 1}
                      </span>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{dev.name}</p>
                        <p className="text-xs text-gray-400">{dev.active_count.toLocaleString()} listings</p>
                      </div>
                    </div>
                    <span className="text-xs text-gray-500">{dev.avg_psm ? formatPSM(dev.avg_psm) : '—'}</span>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>

        {/* Area Heatmap Table */}
        <Card>
          <CardHeader>
            <CardTitle>Area Price Heat Map</CardTitle>
            <Link href="/market" className="text-sm text-brand-600 hover:underline flex items-center gap-1">
              Detailed view <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </CardHeader>
          {loading ? (
            <div className="h-40 animate-pulse bg-gray-100 rounded-lg" />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-100">
                    <th className="text-left font-medium text-gray-500 pb-2">Area</th>
                    <th className="text-right font-medium text-gray-500 pb-2">Avg EGP/m²</th>
                    <th className="text-right font-medium text-gray-500 pb-2">Listings</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {data?.area_heatmap.slice(0, 8).map((area) => (
                    <tr key={area.slug} className="hover:bg-gray-50 transition-colors">
                      <td className="py-2.5 font-medium text-gray-900">{area.name}</td>
                      <td className="py-2.5 text-right text-brand-700 font-semibold">
                        {area.avg_psm ? Number(area.avg_psm).toLocaleString('en-EG', { maximumFractionDigits: 0 }) : '—'}
                      </td>
                      <td className="py-2.5 text-right text-gray-500">{Number(area.total_listings).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        {/* Latest AI Insights */}
        <Card>
          <CardHeader>
            <CardTitle>Latest Market Insights</CardTitle>
            <Link href="/ai-insights" className="text-sm text-brand-600 hover:underline flex items-center gap-1">
              View all <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </CardHeader>
          <div className="space-y-4">
            {loading ? (
              Array(3).fill(0).map((_, i) => <div key={i} className="h-16 animate-pulse bg-gray-100 rounded-lg" />)
            ) : data?.latest_insights.length === 0 ? (
              <div className="text-center py-8">
                <Sparkles className="w-8 h-8 text-gray-300 mx-auto mb-2" />
                <p className="text-gray-500 text-sm">No insights yet. Generate your first AI market analysis.</p>
                <Link href="/ai-insights">
                  <button className="mt-3 text-sm text-brand-600 hover:underline">Generate Insight →</button>
                </Link>
              </div>
            ) : (
              data?.latest_insights.map((insight) => (
                <div key={insight.id} className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-100">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-gray-900 text-sm mb-1">{insight.title}</p>
                      <p className="text-gray-600 text-xs line-clamp-2">{insight.summary}</p>
                    </div>
                    <div className="text-xs text-gray-400 whitespace-nowrap">{formatDate(insight.generated_at)}</div>
                  </div>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>
    </div>
  )
}
