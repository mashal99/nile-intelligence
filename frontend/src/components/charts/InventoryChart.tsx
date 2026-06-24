'use client'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

interface Props {
  data: { property_type: string; count: number }[]
}

const COLORS = ['#1a56db', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
const TYPE_LABEL: Record<string, string> = {
  apartment: 'Apt', villa: 'Villa', townhouse: 'Town', twin_house: 'Twin',
  duplex: 'Duplex', penthouse: 'PH', studio: 'Studio', chalet: 'Chalet',
}

export default function InventoryChart({ data }: Props) {
  const formatted = data.map(d => ({ name: TYPE_LABEL[d.property_type] || d.property_type, count: d.count }))

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={formatted} margin={{ top: 5, right: 10, bottom: 5, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="name" tick={{ fontSize: 11 }} tickLine={false} />
        <YAxis tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
        <Tooltip />
        <Bar dataKey="count" name="Listings" radius={[4, 4, 0, 0]}>
          {formatted.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
