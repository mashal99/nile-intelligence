'use client'
import { Suspense, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'

function ResetPasswordContent() {
  const params = useSearchParams()
  const token = params.get('token')
  const [sent, setSent] = useState(false)
  const [loading, setLoading] = useState(false)

  const emailForm = useForm<{ email: string }>()
  const resetForm = useForm<{ new_password: string; new_password_confirm: string }>()

  const onRequestReset = async (data: { email: string }) => {
    setLoading(true)
    try {
      await api.post('/auth/password-reset/', data)
      setSent(true)
      toast.success('Reset link sent if email exists.')
    } catch { toast.error('Something went wrong.') }
    finally { setLoading(false) }
  }

  const onConfirmReset = async (data: { new_password: string; new_password_confirm: string }) => {
    if (data.new_password !== data.new_password_confirm) {
      resetForm.setError('new_password_confirm', { message: 'Passwords do not match' })
      return
    }
    setLoading(true)
    try {
      await api.post('/auth/password-reset/confirm/', { token, ...data })
      toast.success('Password reset successfully!')
    } catch { toast.error('Invalid or expired link.') }
    finally { setLoading(false) }
  }

  if (token) {
    return (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-1">Set new password</h2>
        <p className="text-gray-500 text-sm mb-6">Choose a strong new password.</p>
        <form onSubmit={resetForm.handleSubmit(onConfirmReset)} className="space-y-4">
          <Input label="New password" type="password" {...resetForm.register('new_password')} error={resetForm.formState.errors.new_password?.message} />
          <Input label="Confirm password" type="password" {...resetForm.register('new_password_confirm')} error={resetForm.formState.errors.new_password_confirm?.message} />
          <Button type="submit" className="w-full" loading={loading}>Reset Password</Button>
        </form>
      </div>
    )
  }

  if (sent) {
    return (
      <div className="text-center">
        <h2 className="text-xl font-bold text-gray-900 mb-2">Check your email</h2>
        <p className="text-gray-500 mb-6">We sent a password reset link to your email address.</p>
        <Link href="/login"><Button variant="outline" className="w-full">Back to Login</Button></Link>
      </div>
    )
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-1">Forgot password?</h2>
      <p className="text-gray-500 text-sm mb-6">Enter your email to receive a reset link.</p>
      <form onSubmit={emailForm.handleSubmit(onRequestReset)} className="space-y-4">
        <Input label="Email address" type="email" {...emailForm.register('email', { required: true })} error={emailForm.formState.errors.email?.message} />
        <Button type="submit" className="w-full" loading={loading}>Send reset link</Button>
      </form>
      <p className="text-center text-sm text-gray-500 mt-4">
        <Link href="/login" className="text-brand-600 hover:underline">Back to login</Link>
      </p>
    </div>
  )
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<div className="text-center text-gray-500 text-sm">Loading...</div>}>
      <ResetPasswordContent />
    </Suspense>
  )
}
