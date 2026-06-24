import { cn } from '@/lib/utils'
import { LucideIcon } from 'lucide-react'

interface StatCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: LucideIcon
  trend?: number
  iconColor?: string
  iconBg?: string
  className?: string
}

export default function StatCard({ title, value, subtitle, icon: Icon, trend, iconColor = 'text-brand-600', iconBg = 'bg-brand-50', className }: StatCardProps) {
  return (
    <div className={cn('bg-white rounded-xl border border-gray-200 shadow-sm p-6', className)}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
          {trend !== undefined && (
            <div className={cn('flex items-center gap-1 mt-2 text-sm font-medium', trend >= 0 ? 'text-green-600' : 'text-red-600')}>
              <span>{trend >= 0 ? '↑' : '↓'} {Math.abs(trend).toFixed(1)}%</span>
              <span className="text-gray-400 font-normal">vs last week</span>
            </div>
          )}
        </div>
        <div className={cn('w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0', iconBg)}>
          <Icon className={cn('w-6 h-6', iconColor)} />
        </div>
      </div>
    </div>
  )
}
