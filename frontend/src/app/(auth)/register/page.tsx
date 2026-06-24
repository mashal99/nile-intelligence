'use client'
import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import { useAuthStore } from '@/store/auth'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Select from '@/components/ui/Select'

const schema = z.object({
  full_name: z.string().min(2, 'Full name is required'),
  email: z.string().email('Enter a valid email'),
  company_name: z.string().optional(),
  role: z.enum(['broker', 'developer', 'investor', 'analyst']),
  password: z.string().min(8, 'Minimum 8 characters'),
  password_confirm: z.string(),
}).refine(d => d.password === d.password_confirm, {
  message: 'Passwords do not match',
  path: ['password_confirm'],
})
type FormData = z.infer<typeof schema>

const ROLE_OPTIONS = [
  { value: 'broker', label: 'Broker / Agent' },
  { value: 'developer', label: 'Real Estate Developer' },
  { value: 'investor', label: 'Investor' },
  { value: 'analyst', label: 'Market Analyst' },
]

export default function RegisterPage() {
  const router = useRouter()
  const { register: registerUser, isLoading } = useAuthStore()
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { role: 'broker' },
  })

  const onSubmit = async (data: FormData) => {
    try {
      await registerUser(data)
      toast.success('Account created! Please verify your email.')
      router.replace('/dashboard')
    } catch (err: any) {
      const detail = err?.response?.data?.detail || err?.response?.data?.email?.[0] || 'Registration failed'
      toast.error(detail)
    }
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-1">Create account</h2>
      <p className="text-gray-500 text-sm mb-6">Start your free plan — no credit card required</p>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Input label="Full name" error={errors.full_name?.message} {...register('full_name')} />
        <Input label="Email address" type="email" error={errors.email?.message} {...register('email')} />
        <Input label="Company name (optional)" error={errors.company_name?.message} {...register('company_name')} />
        <Select label="Your role" options={ROLE_OPTIONS} error={errors.role?.message} {...register('role')} />
        <Input label="Password" type="password" error={errors.password?.message} {...register('password')} />
        <Input label="Confirm password" type="password" error={errors.password_confirm?.message} {...register('password_confirm')} />

        <Button type="submit" className="w-full" loading={isLoading}>
          Create account
        </Button>
      </form>

      <p className="text-center text-sm text-gray-500 mt-6">
        Already have an account?{' '}
        <Link href="/login" className="text-brand-600 font-medium hover:underline">Sign in</Link>
      </p>
    </div>
  )
}
