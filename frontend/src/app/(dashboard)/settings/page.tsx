'use client'
import { useEffect, useState } from 'react'
import { User, Lock, CreditCard, Check } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import { Subscription } from '@/types'
import { useAuthStore } from '@/store/auth'
import Header from '@/components/layout/Header'
import { Card, CardHeader, CardTitle } from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'

export default function SettingsPage() {
  const { user, fetchMe } = useAuthStore()
  const [tab, setTab] = useState<'profile' | 'security' | 'billing'>('profile')
  const [subscription, setSubscription] = useState<Subscription | null>(null)
  const [profileLoading, setProfileLoading] = useState(false)
  const [passLoading, setPassLoading] = useState(false)
  const [upgradeLoading, setUpgradeLoading] = useState(false)

  const [profile, setProfile] = useState({ full_name: '', phone: '', company_name: '' })
  const [passwords, setPasswords] = useState({ current_password: '', new_password: '', new_password_confirm: '' })

  useEffect(() => {
    if (user) setProfile({ full_name: user.full_name, phone: user.phone, company_name: user.company_name })
  }, [user])

  useEffect(() => {
    api.get<Subscription>('/subscriptions/')
      .then(r => setSubscription(r.data))
      .catch(() => {})
  }, [])

  const updateProfile = async () => {
    setProfileLoading(true)
    try {
      await api.patch('/auth/me/', profile)
      await fetchMe()
      toast.success('Profile updated!')
    } catch { toast.error('Failed to update profile') }
    finally { setProfileLoading(false) }
  }

  const changePassword = async () => {
    if (passwords.new_password !== passwords.new_password_confirm) {
      toast.error('Passwords do not match')
      return
    }
    setPassLoading(true)
    try {
      await api.post('/auth/change-password/', passwords)
      setPasswords({ current_password: '', new_password: '', new_password_confirm: '' })
      toast.success('Password changed!')
    } catch (err: any) {
      toast.error(err?.response?.data?.current_password || 'Failed to change password')
    } finally { setPassLoading(false) }
  }

  const upgradePlan = async (plan: string) => {
    setUpgradeLoading(true)
    try {
      await api.post('/subscriptions/upgrade/', { plan, billing_cycle: 'monthly' })
      const { data } = await api.get<Subscription>('/subscriptions/')
      setSubscription(data)
      await fetchMe()
      toast.success(`Upgraded to ${plan} plan!`)
    } catch { toast.error('Failed to upgrade plan') }
    finally { setUpgradeLoading(false) }
  }

  const PLANS = [
    {
      id: 'free', name: 'Free', price: 0, color: 'gray',
      features: ['50 listings/day', '2 reports/month', '10 AI queries', 'Basic search'],
    },
    {
      id: 'professional', name: 'Professional', price: 299, color: 'blue',
      features: ['500 listings/day', '20 reports/month', '100 AI queries', 'Competitor alerts', 'Priority support'],
    },
    {
      id: 'enterprise', name: 'Enterprise', price: 999, color: 'purple',
      features: ['Unlimited listings', 'Unlimited reports', 'Unlimited AI', 'API access', 'Custom integrations', 'Dedicated support'],
    },
  ]

  return (
    <div className="flex flex-col flex-1">
      <Header title="Settings" subtitle="Manage your account and subscription" />

      <div className="p-6 space-y-6 max-w-3xl">
        {/* Tabs */}
        <div className="flex gap-2">
          {[
            { id: 'profile', label: 'Profile', icon: User },
            { id: 'security', label: 'Security', icon: Lock },
            { id: 'billing', label: 'Billing', icon: CreditCard },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setTab(id as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${tab === id ? 'bg-brand-600 text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'}`}
            >
              <Icon className="w-4 h-4" /> {label}
            </button>
          ))}
        </div>

        {/* Profile Tab */}
        {tab === 'profile' && (
          <Card>
            <CardHeader><CardTitle>Profile Information</CardTitle></CardHeader>
            <div className="space-y-4">
              <div className="flex items-center gap-4 mb-6 p-4 bg-gray-50 rounded-xl">
                <div className="w-16 h-16 rounded-full bg-brand-600 flex items-center justify-center text-2xl font-bold text-white">
                  {user?.full_name?.charAt(0).toUpperCase() || 'U'}
                </div>
                <div>
                  <p className="font-semibold text-gray-900">{user?.full_name}</p>
                  <p className="text-sm text-gray-500">{user?.email}</p>
                  <p className="text-xs text-gray-400 capitalize">{user?.role} · {user?.plan} plan</p>
                </div>
              </div>
              <Input label="Full Name" value={profile.full_name} onChange={e => setProfile(p => ({ ...p, full_name: e.target.value }))} />
              <Input label="Phone" value={profile.phone} onChange={e => setProfile(p => ({ ...p, phone: e.target.value }))} />
              <Input label="Company Name" value={profile.company_name} onChange={e => setProfile(p => ({ ...p, company_name: e.target.value }))} />
              <Input label="Email" value={user?.email || ''} disabled helperText="Email cannot be changed" />
              <Button onClick={updateProfile} loading={profileLoading}>Save Changes</Button>
            </div>
          </Card>
        )}

        {/* Security Tab */}
        {tab === 'security' && (
          <Card>
            <CardHeader><CardTitle>Change Password</CardTitle></CardHeader>
            <div className="space-y-4">
              <Input label="Current Password" type="password" value={passwords.current_password} onChange={e => setPasswords(p => ({ ...p, current_password: e.target.value }))} />
              <Input label="New Password" type="password" value={passwords.new_password} onChange={e => setPasswords(p => ({ ...p, new_password: e.target.value }))} helperText="Minimum 8 characters" />
              <Input label="Confirm New Password" type="password" value={passwords.new_password_confirm} onChange={e => setPasswords(p => ({ ...p, new_password_confirm: e.target.value }))} />
              <Button onClick={changePassword} loading={passLoading}>Update Password</Button>
            </div>
          </Card>
        )}

        {/* Billing Tab */}
        {tab === 'billing' && (
          <div className="space-y-4">
            {subscription && (
              <Card className="bg-gradient-to-r from-brand-600 to-brand-800 text-white border-0">
                <p className="text-sm opacity-80 mb-1">Current Plan</p>
                <p className="text-3xl font-bold capitalize mb-1">{subscription.plan}</p>
                {subscription.expires_at && (
                  <p className="text-sm opacity-70">Renews {new Date(subscription.expires_at).toLocaleDateString()}</p>
                )}
              </Card>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {PLANS.map(plan => {
                const isCurrent = user?.plan === plan.id
                return (
                  <div key={plan.id} className={`rounded-xl border-2 p-5 transition-all ${isCurrent ? 'border-brand-500 bg-blue-50' : 'border-gray-200 bg-white hover:border-gray-300'}`}>
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <p className="font-bold text-gray-900">{plan.name}</p>
                        <p className="text-2xl font-bold text-gray-900 mt-1">
                          {plan.price === 0 ? 'Free' : `$${plan.price}`}
                          {plan.price > 0 && <span className="text-sm font-normal text-gray-400">/mo</span>}
                        </p>
                      </div>
                      {isCurrent && (
                        <span className="text-xs px-2 py-1 bg-brand-100 text-brand-700 rounded-full font-medium">Current</span>
                      )}
                    </div>
                    <ul className="space-y-2 mb-4">
                      {plan.features.map(f => (
                        <li key={f} className="flex items-center gap-2 text-sm text-gray-600">
                          <Check className="w-3.5 h-3.5 text-green-500 flex-shrink-0" />{f}
                        </li>
                      ))}
                    </ul>
                    {!isCurrent && (
                      <Button
                        variant={plan.id === 'enterprise' ? 'primary' : 'outline'}
                        size="sm"
                        className="w-full"
                        loading={upgradeLoading}
                        onClick={() => upgradePlan(plan.id)}
                      >
                        {plan.price > (user?.plan === 'enterprise' ? 999 : 0) ? 'Upgrade' : 'Downgrade'} to {plan.name}
                      </Button>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
