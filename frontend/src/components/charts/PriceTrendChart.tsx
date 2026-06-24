'use client'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import { MarketSnapshot } from '@/types'

interface Props {
  data: MarketSnapshot[]
  title?: string
}

const fmt = (v: number) => v >= 1_000_000 ? `${(v / 1_000_000).toFixed(1)}M` : `${(v / 1_000).toFixed(0)}K`

export default function PriceTrendChart({ data, title }: Props) {
  const formatted = data.map(d => ({
    date: new Date(d.date).toLocaleDateString('en-EG', { month: 'short', day: 'numeric' }),
    avg: Math.round(parseFloat(d.avg_price)),
    median: Math.round(parseFloat(d.median_price)),
    psm: Math.round(parseFloat(d.avg_price_per_sqm)),
  }))

  return (
    <div>
      {title && <p className="text-sm font-medium text-gray-700 mb-3">{title}</p>}
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={formatted} margin={{ top: 5, right: 10, bottom: 5, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} tickLine={false} />
          <YAxis tickFormatter={fmt} tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
          <Tooltip formatter={(v: number) => v.toLocaleString() + ' EGP'} />
          <Legend />
          <Line type="monotone" dataKey="avg" name="Avg Price" stroke="#1a56db" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="median" name="Median" stroke="#10b981" strokeWidth={2} dot={false} strokeDasharray="4 4" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
