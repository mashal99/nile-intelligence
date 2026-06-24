'use client'
import { useEffect, useState } from 'react'
import { TrendingUp, Building2, MapPin } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import { AreaHeatmap, DeveloperRanking, MarketSnapshot, InventorySummary } from '@/types'
import Header from '@/components/layout/Header'
import { Card, CardHeader, CardTitle } from '@/components/ui/Card'
import PriceTrendChart from '@/components/charts/PriceTrendChart'
import { formatPSM } from '@/lib/utils'

const AREAS = [
  { value: 'new-cairo', label: 'New Cairo' },
  { value: 'sheikh-zayed', label: 'Sheikh Zayed' },
  { value: '6th-of-october', label: '6th of October' },
  { value: 'new-administrative-capital', label: 'New Capital' },
  { value: 'maadi', label: 'Maadi' },
  { value: 'north-coast', label: 'North Coast' },
]

const TYPES = [
  { value: 'apartment', label: 'Apartments' },
  { value: 'villa', label: 'Villas' },
  { value: 'townhouse', label: 'Townhouses' },
  { value: 'chalet', label: 'Chalets' },
]

export default function MarketPage() {
  const [heatmap, setHeatmap] = useState<AreaHeatmap[]>([])
  const [rankings, setRankings] = useState<DeveloperRanking[]>([])
  const [trend, setTrend] = useState<MarketSnapshot[]>([])
  const [inventory, setInventory] = useState<InventorySummary | null>(null)
  const [selectedArea, setSelectedArea] = useState('new-cairo')
  const [selectedType, setSelectedType] = useState('apartment')
  const [trendDays, setTrendDays] = useState(90)
  const [loading, setLoading] = useState(true)
  const [trendLoading, setTrendLoading] = useState(false)

  useEffect(() => {
    Promise.all([
      api.get<AreaHeatmap[]>('/market/heatmap/'),
      api.get<DeveloperRanking[]>('/market/developer-rankings/?limit=20'),
      api.get<InventorySummary>('/market/inventory/'),
    ])
      .then(([h, r, i]) => {
        setHeatmap(h.data)
        setRankings(r.data)
        setInventory(i.data)
      })
      .catch(() => toast.error('Failed to load market data'))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    setTrendLoading(true)
    api.get<MarketSnapshot[]>(`/market/trends/${selectedArea}/?type=${selectedType}&days=${trendDays}`)
      .then(r => setTrend(r.data))
      .catch(() => toast.error('Failed to load trend data'))
      .finally(() => setTrendLoading(false))
  }, [selectedArea, selectedType, trendDays])

  return (
    <div className="flex flex-col flex-1">
      <Header title="Market Intelligence" subtitle="Egyptian real estate market data and trends" />

      <div className="p-6 space-y-6">
        {/* Stats Row */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Card>
            <p className="text-sm text-gray-500">Total Active Listings</p>
            <p className="text-3xl font-bold text-gray-900 mt-1">
              {loading ? '...' : inventory?.total_active.toLocaleString()}
            </p>
            <p className="text-xs text-green-600 mt-1">↑ {inventory?.new_last_7d} new this week</p>
          </Card>
          <Card>
            <p className="text-sm text-gray-500">Active Developers</p>
            <p className="text-3xl font-bold text-gray-900 mt-1">
              {loading ? '...' : rankings.length}
            </p>
          </Card>
          <Card>
            <p className="text-sm text-gray-500">Areas Tracked</p>
            <p className="text-3xl font-bold text-gray-900 mt-1">{loading ? '...' : heatmap.length}</p>
          </Card>
        </div>

        {/* Price Trend */}
        <Card>
          <CardHeader>
            <CardTitle>Price Trends</CardTitle>
            <div className="flex gap-2 flex-wrap">
              <select
                value={selectedArea}
                onChange={e => setSelectedArea(e.target.value)}
                className="text-sm border border-gray-300 rounded-lg px-2 py-1.5 focus:outline-none"
              >
                {AREAS.map(a => <option key={a.value} value={a.value}>{a.label}</option>)}
              </select>
              <select
                value={selectedType}
                onChange={e => setSelectedType(e.target.value)}
                className="text-sm border border-gray-300 rounded-lg px-2 py-1.5 focus:outline-none"
              >
                {TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
              </select>
              <select
                value={trendDays}
                onChange={e => setTrendDays(Number(e.target.value))}
                className="text-sm border border-gray-300 rounded-lg px-2 py-1.5 focus:outline-none"
              >
                <option value={30}>30 days</option>
                <option value={90}>90 days</option>
                <option value={180}>180 days</option>
                <option value={365}>1 year</option>
              </select>
            </div>
          </CardHeader>
          {trendLoading ? (
            <div className="h-72 animate-pulse bg-gray-100 rounded-lg" />
          ) : trend.length === 0 ? (
            <div className="h-72 flex items-center justify-center text-gray-400">
              <div className="text-center">
                <TrendingUp className="w-10 h-10 mx-auto mb-2 opacity-30" />
                <p>No price trend data yet for this area/type.</p>
                <p className="text-sm mt-1">Data accumulates as the scraper runs daily.</p>
              </div>
            </div>
          ) : (
            <PriceTrendChart data={trend} />
          )}
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Heatmap Table */}
          <Card>
            <CardHeader>
              <CardTitle>Area Price Comparison (EGP/m²)</CardTitle>
            </CardHeader>
            {loading ? (
              <div className="space-y-2">
                {Array(8).fill(0).map((_, i) => <div key={i} className="h-8 animate-pulse bg-gray-100 rounded" />)}
              </div>
            ) : (
              <div className="space-y-2">
                {heatmap.slice(0, 12).map((area, i) => {
                  const max = heatmap[0]?.avg_psm || 1
                  const pct = Math.round((area.avg_psm / max) * 100)
                  return (
                    <div key={area.slug}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="font-medium text-gray-700">{area.name}</span>
                        <span className="text-brand-700 font-semibold">
                          {Number(area.avg_psm).toLocaleString('en-EG', { maximumFractionDigits: 0 })} EGP/m²
                        </span>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-brand-500 to-brand-700 rounded-full"
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </Card>

          {/* Developer Rankings */}
          <Card>
            <CardHeader>
              <CardTitle>Developer Rankings</CardTitle>
            </CardHeader>
            {loading ? (
              <div className="space-y-3">
                {Array(8).fill(0).map((_, i) => <div key={i} className="h-10 animate-pulse bg-gray-100 rounded-lg" />)}
              </div>
            ) : (
              <div className="space-y-3 overflow-y-auto max-h-96">
                {rankings.map((dev, i) => (
                  <div key={dev.slug} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold
                        ${i === 0 ? 'bg-yellow-100 text-yellow-700' :
                          i === 1 ? 'bg-gray-200 text-gray-600' :
                          i === 2 ? 'bg-orange-100 text-orange-700' :
                          'bg-gray-100 text-gray-500'}`}>
                        {i + 1}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{dev.name}</p>
                        <p className="text-xs text-gray-400">{dev.total_projects} projects</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-brand-700">{dev.active_count.toLocaleString()}</p>
                      <p className="text-xs text-gray-400">listings</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  )
}
