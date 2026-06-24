'use client'
import { useEffect, useState } from 'react'
import { FileText, Plus, Download, Loader2, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import { Report } from '@/types'
import Header from '@/components/layout/Header'
import { Card, CardHeader, CardTitle } from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'
import { formatDate } from '@/lib/utils'

const REPORT_TYPES = [
  { value: 'weekly_market', label: 'Weekly Market Report' },
  { value: 'monthly_market', label: 'Monthly Market Report' },
  { value: 'area_analysis', label: 'Area Analysis' },
  { value: 'developer_profile', label: 'Developer Profile' },
  { value: 'compound_comparison', label: 'Compound Comparison' },
  { value: 'investment_brief', label: 'Investment Brief' },
]

const STATUS_BADGE: Record<string, 'info' | 'warning' | 'success' | 'danger'> = {
  queued: 'info', generating: 'warning', completed: 'success', failed: 'danger',
}

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [creating, setCreating] = useState(false)
  const [form, setForm] = useState({ title: '', report_type: 'weekly_market', export_format: 'pdf' })

  const fetchReports = () => {
    api.get<{ results: Report[] }>('/reports/')
      .then(r => setReports(r.data.results))
      .catch(() => toast.error('Failed to load reports'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchReports()
    const interval = setInterval(() => {
      const hasGenerating = reports.some(r => r.status === 'generating' || r.status === 'queued')
      if (hasGenerating) fetchReports()
    }, 10000)
    return () => clearInterval(interval)
  }, [reports.length])

  const createReport = async () => {
    if (!form.title) { toast.error('Report title is required'); return }
    setCreating(true)
    try {
      const { data } = await api.post<Report>('/reports/', form)
      setReports(prev => [data, ...prev])
      setShowForm(false)
      setForm({ title: '', report_type: 'weekly_market', export_format: 'pdf' })
      toast.success('Report queued! It will be ready in a few minutes.')
    } catch { toast.error('Failed to create report') }
    finally { setCreating(false) }
  }

  const downloadReport = async (id: number) => {
    try {
      const { data } = await api.get<{ download_url: string }>(`/reports/${id}/download/`)
      window.open(data.download_url, '_blank')
    } catch { toast.error('Download not available yet') }
  }

  return (
    <div className="flex flex-col flex-1">
      <Header title="Reports" subtitle="Generate market intelligence reports in PDF, Excel, or JSON" />

      <div className="p-6 space-y-6">
        <div className="flex justify-end">
          <Button onClick={() => setShowForm(true)}>
            <Plus className="w-4 h-4 mr-1.5" /> Generate Report
          </Button>
        </div>

        {showForm && (
          <Card className="border-brand-200 bg-blue-50">
            <CardTitle className="mb-4">New Report</CardTitle>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="sm:col-span-3">
                <label className="text-sm font-medium text-gray-700 mb-1 block">Report Title</label>
                <input
                  value={form.title}
                  onChange={e => setForm(p => ({ ...p, title: e.target.value }))}
                  placeholder="e.g. New Cairo Apartment Market - Q3 2024"
                  className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700 mb-1 block">Report Type</label>
                <select
                  value={form.report_type}
                  onChange={e => setForm(p => ({ ...p, report_type: e.target.value }))}
                  className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none"
                >
                  {REPORT_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700 mb-1 block">Export Format</label>
                <select
                  value={form.export_format}
                  onChange={e => setForm(p => ({ ...p, export_format: e.target.value }))}
                  className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none"
                >
                  <option value="pdf">PDF</option>
                  <option value="excel">Excel (.xlsx)</option>
                  <option value="json">JSON</option>
                </select>
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <Button onClick={createReport} loading={creating}>Generate Report</Button>
              <Button variant="outline" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Report History</CardTitle>
          </CardHeader>

          {loading ? (
            <div className="space-y-3">
              {Array(4).fill(0).map((_, i) => <div key={i} className="h-16 animate-pulse bg-gray-100 rounded-lg" />)}
            </div>
          ) : reports.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="w-10 h-10 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500 font-medium">No reports yet</p>
              <p className="text-gray-400 text-sm mt-1">Generate your first market intelligence report.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {reports.map(report => (
                <div key={report.id} className="flex items-center gap-4 p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                  <div className="w-10 h-10 rounded-lg bg-white border border-gray-200 flex items-center justify-center flex-shrink-0">
                    <FileText className="w-5 h-5 text-brand-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 text-sm truncate">{report.title}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant={STATUS_BADGE[report.status] || 'default'} className="text-xs">
                        {report.status === 'generating' && <Loader2 className="w-3 h-3 mr-1 animate-spin" />}
                        {report.status}
                      </Badge>
                      <span className="text-xs text-gray-400">{report.export_format.toUpperCase()}</span>
                      <span className="text-xs text-gray-400">•</span>
                      <span className="text-xs text-gray-400">{formatDate(report.created_at)}</span>
                    </div>
                    {report.status === 'failed' && report.error_message && (
                      <p className="text-xs text-red-500 mt-1 flex items-center gap-1">
                        <AlertCircle className="w-3 h-3" />{report.error_message.slice(0, 80)}
                      </p>
                    )}
                  </div>
                  {report.status === 'completed' && (
                    <Button variant="outline" size="sm" onClick={() => downloadReport(report.id)}>
                      <Download className="w-4 h-4 mr-1" /> Download
                    </Button>
                  )}
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}
