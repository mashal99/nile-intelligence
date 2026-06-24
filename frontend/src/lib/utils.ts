import { clsx, type ClassValue } from 'clsx'

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs)
}

export function formatPrice(price: string | number | null | undefined): string {
  if (!price) return 'N/A'
  const num = typeof price === 'string' ? parseFloat(price) : price
  if (isNaN(num)) return 'N/A'
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M EGP`
  if (num >= 1_000) return `${(num / 1_000).toFixed(0)}K EGP`
  return `${num.toLocaleString()} EGP`
}

export function formatPSM(psm: string | number | null | undefined): string {
  if (!psm) return 'N/A'
  const num = typeof psm === 'string' ? parseFloat(psm) : psm
  if (isNaN(num)) return 'N/A'
  return `${num.toLocaleString('en-EG', { maximumFractionDigits: 0 })} EGP/m²`
}

export function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString('en-EG', {
    year: 'numeric', month: 'short', day: 'numeric',
  })
}

export function formatRelativeDate(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days}d ago`
  return formatDate(dateStr)
}

export function propertyTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    apartment: 'Apartment', villa: 'Villa', townhouse: 'Townhouse',
    twin_house: 'Twin House', duplex: 'Duplex', penthouse: 'Penthouse',
    studio: 'Studio', office: 'Office', retail: 'Retail', chalet: 'Chalet',
  }
  return labels[type] || type
}

export function purposeLabel(purpose: string): string {
  return { sale: 'For Sale', rent: 'For Rent', new_launch: 'New Launch' }[purpose] || purpose
}

export function planBadgeColor(plan: string): string {
  return { free: 'bg-gray-100 text-gray-700', professional: 'bg-blue-100 text-blue-700', enterprise: 'bg-purple-100 text-purple-700' }[plan] || 'bg-gray-100 text-gray-700'
}

export function severityColor(severity: string): string {
  return {
    low: 'bg-green-100 text-green-700',
    medium: 'bg-yellow-100 text-yellow-700',
    high: 'bg-orange-100 text-orange-700',
    critical: 'bg-red-100 text-red-700',
  }[severity] || 'bg-gray-100 text-gray-700'
}
