export interface User {
  id: number
  email: string
  full_name: string
  phone: string
  role: 'admin' | 'broker' | 'developer' | 'investor' | 'analyst'
  company_name: string
  avatar: string | null
  is_email_verified: boolean
  plan: 'free' | 'professional' | 'enterprise'
  date_joined: string
}

export interface Area {
  id: number
  name: string
  slug: string
  parent: number | null
}

export interface Developer {
  id: number
  name: string
  slug: string
  logo: string | null
  website: string
  total_projects: number
  founded_year: number | null
}

export interface Compound {
  id: number
  name: string
  slug: string
  developer: Developer
  area: Area
  launch_date: string | null
  delivery_date: string | null
  total_units: number | null
  land_area: string | null
  amenities: string[]
  images: string[]
  latitude: string | null
  longitude: string | null
}

export interface PropertyListing {
  id: number
  title: string
  property_type: string
  purpose: 'sale' | 'rent' | 'new_launch'
  status: 'active' | 'sold' | 'rented' | 'unavailable' | 'price_changed'
  finishing: string
  bedrooms: number | null
  bathrooms: number | null
  area_sqm: string | null
  floor: number | null
  total_floors: number | null
  price: string | null
  price_per_sqm: string | null
  down_payment: string | null
  monthly_installment: string | null
  installment_years: number | null
  area: Area
  developer: Developer
  compound_name: string | null
  source_url: string
  source_portal: string
  images: string[]
  scraped_at: string
  updated_at: string
}

export interface PropertyListingDetail extends PropertyListing {
  compound: Compound | null
  description: string
  price_history: PriceHistory[]
  listed_at: string | null
}

export interface PriceHistory {
  old_price: string
  new_price: string
  change_percent: string
  recorded_at: string
}

export interface MarketSnapshot {
  date: string
  avg_price: string
  median_price: string
  avg_price_per_sqm: string
  active_listings: number
}

export interface AreaHeatmap {
  name: string
  slug: string
  latitude: string | null
  longitude: string | null
  avg_psm: number
  total_listings: number
}

export interface DeveloperRanking {
  name: string
  slug: string
  active_count: number
  avg_psm: number | null
  total_projects: number
}

export interface InventorySummary {
  total_active: number
  new_last_7d: number
  by_type: { property_type: string; count: number }[]
  by_purpose: { purpose: string; count: number }[]
}

export interface MarketInsight {
  id: number
  insight_type: string
  title: string
  summary: string
  area_name: string | null
  tags: string[]
  generated_at: string
  valid_until: string | null
}

export interface Alert {
  id: number
  rule_name: string
  title: string
  message: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  metadata: Record<string, string>
  is_read: boolean
  created_at: string
}

export interface MonitoringRule {
  id: number
  name: string
  rule_type: string
  area: number | null
  developer: number | null
  compound: number | null
  property_type: string
  min_price: string | null
  max_price: string | null
  price_change_threshold_pct: string
  notification_channels: string[]
  webhook_url: string
  is_active: boolean
  created_at: string
  last_triggered_at: string | null
}

export interface Report {
  id: number
  title: string
  report_type: string
  status: 'queued' | 'generating' | 'completed' | 'failed'
  export_format: 'pdf' | 'excel' | 'json'
  file_url: string
  file_size_kb: number | null
  error_message: string
  generated_at: string | null
  created_at: string
}

export interface Subscription {
  plan: 'free' | 'professional' | 'enterprise'
  billing_cycle: 'monthly' | 'yearly' | null
  expires_at: string | null
  auto_renew: boolean
  limits: SubscriptionLimits
}

export interface SubscriptionLimits {
  name: string
  price_monthly: number
  price_yearly: number
  listings_per_day: number
  reports_per_month: number
  ai_queries_per_month: number
  competitor_alerts: boolean
  api_access: boolean
}

export interface PaginatedResponse<T> {
  count: number
  total_pages: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface DashboardData {
  inventory: InventorySummary
  top_developers: DeveloperRanking[]
  area_heatmap: AreaHeatmap[]
  latest_insights: MarketInsight[]
}

export interface AuthTokens {
  access: string
  refresh: string
}
