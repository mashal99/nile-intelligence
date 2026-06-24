'use client'
import { useEffect, useState } from 'react'
import { Bell, Plus, Eye, Trash2, Check, CheckCheck } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import { Alert, MonitoringRule } from '@/types'
import Header from '@/components/layout/Header'
import { Card, CardHeader, CardTitle } from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'
import { severityColor, formatRelativeDate } from '@/lib/utils'

const RULE_TYPES = [
  { value: 'new_listing', label: 'New Listing' },
  { value: 'price_drop', label: 'Price Drop' },
  { value: 'price_increase', label: 'Price Increase' },
  { value: 'new_launch', label: 'New Launch' },
  { value: 'developer_activity', label: 'Developer Activity' },
]

export default function MonitoringPage() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [rules, setRules] = useState<MonitoringRule[]>([])
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState<'alerts' | 'rules'>('alerts')
  const [showRuleForm, setShowRuleForm] = useState(false)
  const [unreadOnly, setUnreadOnly] = useState(false)
  const [newRule, setNewRule] = useState({ name: '', rule_type: 'new_listing', price_change_threshold_pct: '5.0' })
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    setLoading(true)
    const alertsUrl = unreadOnly ? '/monitoring/alerts/?unread=true' : '/monitoring/alerts/'
    Promise.all([
      api.get<Alert[]>(alertsUrl),
      api.get<MonitoringRule[]>('/monitoring/rules/'),
    ])
      .then(([a, r]) => { setAlerts(a.data); setRules(r.data) })
      .catch(() => toast.error('Failed to load monitoring data'))
      .finally(() => setLoading(false))
  }, [unreadOnly])

  const markRead = async (id: number) => {
    await api.patch(`/monitoring/alerts/${id}/read/`)
    setAlerts(prev => prev.map(a => a.id === id ? { ...a, is_read: true } : a))
  }

  const markAllRead = async () => {
    await api.post('/monitoring/alerts/read-all/')
    setAlerts(prev => prev.map(a => ({ ...a, is_read: true })))
    toast.success('All alerts marked as read')
  }

  const deleteRule = async (id: number) => {
    await api.delete(`/monitoring/rules/${id}/`)
    setRules(prev => prev.filter(r => r.id !== id))
    toast.success('Rule deleted')
  }

  const createRule = async () => {
    if (!newRule.name) { toast.error('Rule name is required'); return }
    setCreating(true)
    try {
      const { data } = await api.post<MonitoringRule>('/monitoring/rules/', {
        ...newRule,
        notification_channels: ['in_app', 'email'],
      })
      setRules(prev => [data, ...prev])
      setShowRuleForm(false)
      setNewRule({ name: '', rule_type: 'new_listing', price_change_threshold_pct: '5.0' })
      toast.success('Monitoring rule created!')
    } catch { toast.error('Failed to create rule') }
    finally { setCreating(false) }
  }

  const unreadCount = alerts.filter(a => !a.is_read).length

  return (
    <div className="flex flex-col flex-1">
      <Header title="Competitor Monitoring" subtitle="Alerts and automated market watches" />

      <div className="p-6 space-y-6">
        {/* Tabs */}
        <div className="flex gap-2">
          <button
            onClick={() => setTab('alerts')}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${tab === 'alerts' ? 'bg-brand-600 text-white' : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'}`}
          >
            Alerts {unreadCount > 0 && <span className="ml-1.5 px-1.5 py-0.5 bg-red-500 text-white text-xs rounded-full">{unreadCount}</span>}
          </button>
          <button
            onClick={() => setTab('rules')}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${tab === 'rules' ? 'bg-brand-600 text-white' : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'}`}
          >
            Rules ({rules.length})
          </button>
        </div>

        {tab === 'alerts' && (
          <Card>
            <CardHeader>
              <CardTitle>
                {unreadOnly ? 'Unread Alerts' : 'All Alerts'}
                {unreadCount > 0 && <span className="ml-2 text-sm font-normal text-red-500">{unreadCount} unread</span>}
              </CardTitle>
              <div className="flex gap-2">
                <button
                  onClick={() => setUnreadOnly(!unreadOnly)}
                  className="text-sm text-gray-500 hover:text-gray-700"
                >
                  {unreadOnly ? 'Show all' : 'Unread only'}
                </button>
                {unreadCount > 0 && (
                  <Button variant="ghost" size="sm" onClick={markAllRead}>
                    <CheckCheck className="w-4 h-4 mr-1" /> Mark all read
                  </Button>
                )}
              </div>
            </CardHeader>

            {loading ? (
              <div className="space-y-3">
                {Array(5).fill(0).map((_, i) => <div key={i} className="h-16 animate-pulse bg-gray-100 rounded-lg" />)}
              </div>
            ) : alerts.length === 0 ? (
              <div className="text-center py-12">
                <Bell className="w-10 h-10 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500 font-medium">No alerts yet</p>
                <p className="text-gray-400 text-sm mt-1">Create monitoring rules to get notified about market changes</p>
              </div>
            ) : (
              <div className="space-y-2">
                {alerts.map(alert => (
                  <div key={alert.id} className={`flex items-start gap-4 p-4 rounded-xl border transition-colors ${alert.is_read ? 'bg-white border-gray-100' : 'bg-blue-50 border-blue-200'}`}>
                    <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${alert.is_read ? 'bg-gray-300' : 'bg-brand-600'}`} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${severityColor(alert.severity)}`}>
                          {alert.severity}
                        </span>
                        <span className="text-xs text-gray-400">{alert.rule_name}</span>
                      </div>
                      <p className="text-sm font-medium text-gray-900">{alert.title}</p>
                      <p className="text-xs text-gray-500 mt-0.5">{alert.message}</p>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <span className="text-xs text-gray-400">{formatRelativeDate(alert.created_at)}</span>
                      {!alert.is_read && (
                        <button onClick={() => markRead(alert.id)} className="p-1 text-gray-400 hover:text-brand-600 transition-colors" title="Mark as read">
                          <Check className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        )}

        {tab === 'rules' && (
          <div className="space-y-4">
            <div className="flex justify-end">
              <Button onClick={() => setShowRuleForm(true)} size="sm">
                <Plus className="w-4 h-4 mr-1" /> New Rule
              </Button>
            </div>

            {showRuleForm && (
              <Card className="border-brand-200 bg-blue-50">
                <CardTitle className="mb-4">Create Monitoring Rule</CardTitle>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="sm:col-span-2">
                    <label className="text-sm font-medium text-gray-700 mb-1 block">Rule Name</label>
                    <input
                      value={newRule.name}
                      onChange={e => setNewRule(p => ({ ...p, name: e.target.value }))}
                      placeholder="e.g. New villa listings in New Cairo"
                      className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-1 block">Alert Type</label>
                    <select
                      value={newRule.rule_type}
                      onChange={e => setNewRule(p => ({ ...p, rule_type: e.target.value }))}
                      className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none"
                    >
                      {RULE_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                    </select>
                  </div>
                </div>
                {['price_drop', 'price_increase'].includes(newRule.rule_type) && (
                  <div className="mt-3">
                    <label className="text-sm font-medium text-gray-700 mb-1 block">Threshold (%)</label>
                    <input
                      type="number"
                      value={newRule.price_change_threshold_pct}
                      onChange={e => setNewRule(p => ({ ...p, price_change_threshold_pct: e.target.value }))}
                      className="w-32 text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none"
                    />
                  </div>
                )}
                <div className="flex gap-2 mt-4">
                  <Button onClick={createRule} loading={creating}>Create Rule</Button>
                  <Button variant="outline" onClick={() => setShowRuleForm(false)}>Cancel</Button>
                </div>
              </Card>
            )}

            {rules.length === 0 ? (
              <Card>
                <div className="text-center py-12">
                  <Eye className="w-10 h-10 text-gray-300 mx-auto mb-3" />
                  <p className="text-gray-500 font-medium">No monitoring rules</p>
                  <p className="text-gray-400 text-sm mt-1">Create rules to get alerted about price changes, new listings, and more.</p>
                </div>
              </Card>
            ) : (
              <div className="space-y-3">
                {rules.map(rule => (
                  <Card key={rule.id} padding="sm">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-2.5 h-2.5 rounded-full ${rule.is_active ? 'bg-green-500' : 'bg-gray-300'}`} />
                        <div>
                          <p className="font-medium text-gray-900 text-sm">{rule.name}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge variant="info" className="text-xs">{rule.rule_type.replace(/_/g, ' ')}</Badge>
                            {rule.last_triggered_at && (
                              <span className="text-xs text-gray-400">Last triggered {formatRelativeDate(rule.last_triggered_at)}</span>
                            )}
                          </div>
                        </div>
                      </div>
                      <button onClick={() => deleteRule(rule.id)} className="p-2 text-gray-400 hover:text-red-500 transition-colors">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
