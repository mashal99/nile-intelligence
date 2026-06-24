'use client'
import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, ExternalLink, BedDouble, Bath, Maximize, Calendar, MapPin, Building } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import { PropertyListingDetail } from '@/types'
import Header from '@/components/layout/Header'
import { Card, CardHeader, CardTitle } from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'
import { formatPrice, formatPSM, formatDate, propertyTypeLabel, purposeLabel } from '@/lib/utils'

export default function PropertyDetailPage() {
  const params = useParams()
  const [listing, setListing] = useState<PropertyListingDetail | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get<PropertyListingDetail>(`/properties/${params.id}/`)
      .then(r => setListing(r.data))
      .catch(() => toast.error('Failed to load listing'))
      .finally(() => setLoading(false))
  }, [params.id])

  if (loading) return (
    <div className="flex flex-col flex-1">
      <Header title="Property Detail" />
      <div className="p-6 space-y-4">
        {Array(4).fill(0).map((_, i) => <div key={i} className="h-32 animate-pulse bg-white rounded-xl border" />)}
      </div>
    </div>
  )

  if (!listing) return null

  return (
    <div className="flex flex-col flex-1">
      <Header title="Property Detail" subtitle={listing.compound_name || listing.area?.name} />
      <div className="p-6 space-y-6">
        <Link href="/properties" className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
          <ArrowLeft className="w-4 h-4" /> Back to listings
        </Link>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Info */}
          <div className="lg:col-span-2 space-y-6">
            {/* Images */}
            {listing.images?.length > 0 && (
              <div className="grid grid-cols-3 gap-2 rounded-xl overflow-hidden h-64">
                <img src={listing.images[0]} alt="" className="col-span-2 w-full h-full object-cover" />
                {listing.images[1] && <img src={listing.images[1]} alt="" className="w-full h-full object-cover" />}
              </div>
            )}
            {!listing.images?.length && (
              <div className="h-48 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-xl flex items-center justify-center text-5xl">🏢</div>
            )}

            {/* Title & Badges */}
            <Card>
              <div className="flex flex-wrap gap-2 mb-3">
                <Badge variant="info">{propertyTypeLabel(listing.property_type)}</Badge>
                <Badge variant="success">{purposeLabel(listing.purpose)}</Badge>
                {listing.finishing && <Badge>{listing.finishing.replace(/_/g, ' ')}</Badge>}
              </div>
              <h2 className="text-xl font-bold text-gray-900 mb-2">{listing.title}</h2>
              {listing.description && <p className="text-gray-600 text-sm leading-relaxed">{listing.description}</p>}
            </Card>

            {/* Specs */}
            <Card>
              <CardHeader><CardTitle>Property Specs</CardTitle></CardHeader>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                {listing.bedrooms != null && (
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <BedDouble className="w-5 h-5 text-brand-600 mx-auto mb-1" />
                    <p className="text-xl font-bold text-gray-900">{listing.bedrooms}</p>
                    <p className="text-xs text-gray-500">Bedrooms</p>
                  </div>
                )}
                {listing.bathrooms != null && (
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <Bath className="w-5 h-5 text-brand-600 mx-auto mb-1" />
                    <p className="text-xl font-bold text-gray-900">{listing.bathrooms}</p>
                    <p className="text-xs text-gray-500">Bathrooms</p>
                  </div>
                )}
                {listing.area_sqm && (
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <Maximize className="w-5 h-5 text-brand-600 mx-auto mb-1" />
                    <p className="text-xl font-bold text-gray-900">{listing.area_sqm}</p>
                    <p className="text-xs text-gray-500">m²</p>
                  </div>
                )}
                {listing.floor != null && (
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <Building className="w-5 h-5 text-brand-600 mx-auto mb-1" />
                    <p className="text-xl font-bold text-gray-900">{listing.floor}</p>
                    <p className="text-xs text-gray-500">Floor {listing.total_floors ? `of ${listing.total_floors}` : ''}</p>
                  </div>
                )}
              </div>
            </Card>

            {/* Price History */}
            {listing.price_history?.length > 0 && (
              <Card>
                <CardHeader><CardTitle>Price History</CardTitle></CardHeader>
                <div className="space-y-2">
                  {listing.price_history.map((h, i) => (
                    <div key={i} className="flex items-center justify-between text-sm py-2 border-b border-gray-50 last:border-0">
                      <span className="text-gray-500">{formatDate(h.recorded_at)}</span>
                      <div className="flex items-center gap-3">
                        <span className="text-gray-400 line-through">{formatPrice(h.old_price)}</span>
                        <span className="text-gray-700 font-medium">{formatPrice(h.new_price)}</span>
                        <span className={`text-xs font-semibold ${parseFloat(h.change_percent) > 0 ? 'text-red-600' : 'text-green-600'}`}>
                          {parseFloat(h.change_percent) > 0 ? '+' : ''}{parseFloat(h.change_percent).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-4">
            <Card>
              <p className="text-3xl font-bold text-brand-700 mb-1">{formatPrice(listing.price)}</p>
              {listing.price_per_sqm && <p className="text-gray-500 text-sm">{formatPSM(listing.price_per_sqm)}</p>}
              {listing.down_payment && (
                <div className="mt-3 pt-3 border-t border-gray-100 space-y-1.5">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Down Payment</span>
                    <span className="font-medium">{formatPrice(listing.down_payment)}</span>
                  </div>
                  {listing.monthly_installment && (
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Monthly</span>
                      <span className="font-medium">{formatPrice(listing.monthly_installment)}</span>
                    </div>
                  )}
                  {listing.installment_years && (
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Duration</span>
                      <span className="font-medium">{listing.installment_years} years</span>
                    </div>
                  )}
                </div>
              )}
              <a
                href={listing.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-4 flex items-center justify-center gap-2 w-full py-2 text-sm font-medium text-brand-600 border border-brand-200 rounded-lg hover:bg-brand-50 transition-colors"
              >
                <ExternalLink className="w-4 h-4" /> View on {listing.source_portal}
              </a>
            </Card>

            {/* Location */}
            <Card>
              <CardTitle className="mb-3 text-sm">Location</CardTitle>
              <div className="space-y-2 text-sm">
                {listing.area && (
                  <div className="flex items-center gap-2 text-gray-600">
                    <MapPin className="w-4 h-4 text-gray-400" />{listing.area.name}
                  </div>
                )}
                {listing.compound?.developer && (
                  <div className="flex items-center gap-2 text-gray-600">
                    <Building className="w-4 h-4 text-gray-400" />{listing.compound.developer.name}
                  </div>
                )}
                {listing.compound && (
                  <div className="flex items-center gap-2 text-gray-600">
                    <span className="text-gray-400 w-4 h-4 flex items-center justify-center">🏘</span>
                    {listing.compound.name}
                  </div>
                )}
              </div>
            </Card>

            {/* Dates */}
            <Card>
              <CardTitle className="mb-3 text-sm">Dates</CardTitle>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Scraped</span>
                  <span className="text-gray-700">{formatDate(listing.scraped_at)}</span>
                </div>
                {listing.listed_at && (
                  <div className="flex justify-between">
                    <span className="text-gray-500">Listed</span>
                    <span className="text-gray-700">{formatDate(listing.listed_at)}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-gray-500">Source</span>
                  <span className="text-gray-700 capitalize">{listing.source_portal}</span>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
