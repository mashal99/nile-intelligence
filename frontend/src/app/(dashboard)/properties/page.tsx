'use client'
import { useEffect, useState, useCallback } from 'react'
import { Search, Filter, ExternalLink, BedDouble, Bath, Maximize } from 'lucide-react'
import toast from 'react-hot-toast'
import Link from 'next/link'
import api from '@/lib/api'
import { PropertyListing, PaginatedResponse } from '@/types'
import Header from '@/components/layout/Header'
import { Card } from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'
import { formatPrice, formatPSM, propertyTypeLabel, purposeLabel, formatRelativeDate } from '@/lib/utils'

const PROPERTY_TYPES = [
  { value: '', label: 'All Types' },
  { value: 'apartment', label: 'Apartment' },
  { value: 'villa', label: 'Villa' },
  { value: 'townhouse', label: 'Townhouse' },
  { value: 'twin_house', label: 'Twin House' },
  { value: 'duplex', label: 'Duplex' },
  { value: 'penthouse', label: 'Penthouse' },
  { value: 'studio', label: 'Studio' },
  { value: 'chalet', label: 'Chalet' },
]

const PURPOSES = [
  { value: '', label: 'Any Purpose' },
  { value: 'sale', label: 'For Sale' },
  { value: 'rent', label: 'For Rent' },
  { value: 'new_launch', label: 'New Launch' },
]

const STATUS_BADGE: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'default'> = {
  active: 'success', price_changed: 'warning', sold: 'danger', rented: 'info', unavailable: 'default',
}

export default function PropertiesPage() {
  const [listings, setListings] = useState<PropertyListing[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [total, setTotal] = useState(0)

  const [filters, setFilters] = useState({
    q: '', property_type: '', purpose: '', order_by: '-scraped_at',
  })

  const fetchListings = useCallback(() => {
    setLoading(true)
    const params = new URLSearchParams({ page: String(page) })
    if (filters.q) params.set('q', filters.q)
    if (filters.property_type) params.set('property_type', filters.property_type)
    if (filters.purpose) params.set('purpose', filters.purpose)
    params.set('order_by', filters.order_by)

    api.get<PaginatedResponse<PropertyListing>>(`/properties/?${params}`)
      .then(r => {
        setListings(r.data.results)
        setTotalPages(r.data.total_pages)
        setTotal(r.data.count)
      })
      .catch(() => toast.error('Failed to load listings'))
      .finally(() => setLoading(false))
  }, [page, filters])

  useEffect(() => { fetchListings() }, [fetchListings])

  return (
    <div className="flex flex-col flex-1">
      <Header title="Property Listings" subtitle={`${total.toLocaleString()} active listings`} />

      <div className="p-6 space-y-4">
        {/* Filters */}
        <Card padding="sm">
          <div className="flex flex-wrap gap-3 items-end">
            <div className="flex-1 min-w-48 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search compounds, areas, developers..."
                value={filters.q}
                onChange={e => { setFilters(f => ({ ...f, q: e.target.value })); setPage(1) }}
                className="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
            </div>
            <select
              value={filters.property_type}
              onChange={e => { setFilters(f => ({ ...f, property_type: e.target.value })); setPage(1) }}
              className="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              {PROPERTY_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>
            <select
              value={filters.purpose}
              onChange={e => { setFilters(f => ({ ...f, purpose: e.target.value })); setPage(1) }}
              className="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              {PURPOSES.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
            </select>
            <select
              value={filters.order_by}
              onChange={e => { setFilters(f => ({ ...f, order_by: e.target.value })); setPage(1) }}
              className="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              <option value="-scraped_at">Newest First</option>
              <option value="price">Price: Low to High</option>
              <option value="-price">Price: High to Low</option>
              <option value="price_per_sqm">PSM: Low to High</option>
            </select>
          </div>
        </Card>

        {/* Listings Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {Array(9).fill(0).map((_, i) => (
              <div key={i} className="h-64 animate-pulse bg-white rounded-xl border border-gray-200" />
            ))}
          </div>
        ) : listings.length === 0 ? (
          <div className="text-center py-16">
            <p className="text-gray-400 text-lg">No listings found</p>
            <p className="text-gray-400 text-sm mt-1">Try adjusting your filters</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {listings.map(listing => (
              <Link key={listing.id} href={`/properties/${listing.id}`}>
                <div className="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow cursor-pointer overflow-hidden group">
                  {/* Image */}
                  <div className="h-40 bg-gradient-to-br from-blue-100 to-indigo-100 relative overflow-hidden">
                    {listing.images?.[0] ? (
                      <img src={listing.images[0]} alt={listing.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform" />
                    ) : (
                      <div className="flex items-center justify-center h-full">
                        <span className="text-4xl">🏢</span>
                      </div>
                    )}
                    <div className="absolute top-2 left-2 flex gap-1.5">
                      <Badge variant={STATUS_BADGE[listing.status] || 'default'} className="text-xs">
                        {purposeLabel(listing.purpose)}
                      </Badge>
                      {listing.source_portal && (
                        <Badge variant="info" className="text-xs">{listing.source_portal}</Badge>
                      )}
                    </div>
                  </div>

                  {/* Content */}
                  <div className="p-4">
                    <p className="font-semibold text-gray-900 text-sm mb-1 line-clamp-2">{listing.title}</p>
                    <p className="text-xs text-gray-500 mb-3">
                      {listing.compound_name && `${listing.compound_name} · `}
                      {listing.area?.name}
                    </p>

                    <div className="flex items-center gap-4 text-xs text-gray-500 mb-3">
                      {listing.bedrooms != null && (
                        <span className="flex items-center gap-1"><BedDouble className="w-3.5 h-3.5" />{listing.bedrooms} bed</span>
                      )}
                      {listing.bathrooms != null && (
                        <span className="flex items-center gap-1"><Bath className="w-3.5 h-3.5" />{listing.bathrooms} bath</span>
                      )}
                      {listing.area_sqm && (
                        <span className="flex items-center gap-1"><Maximize className="w-3.5 h-3.5" />{listing.area_sqm}m²</span>
                      )}
                    </div>

                    <div className="flex items-end justify-between">
                      <div>
                        <p className="text-lg font-bold text-brand-700">{formatPrice(listing.price)}</p>
                        {listing.price_per_sqm && (
                          <p className="text-xs text-gray-400">{formatPSM(listing.price_per_sqm)}</p>
                        )}
                      </div>
                      <span className="text-xs text-gray-400">{formatRelativeDate(listing.scraped_at)}</span>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-2 pt-2">
            <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(p => p - 1)}>
              Previous
            </Button>
            <span className="text-sm text-gray-600">Page {page} of {totalPages}</span>
            <Button variant="outline" size="sm" disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>
              Next
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
