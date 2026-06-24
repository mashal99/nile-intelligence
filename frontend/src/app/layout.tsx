import type { Metadata } from 'next'
import './globals.css'
import { Toaster } from 'react-hot-toast'

export const metadata: Metadata = {
  title: 'Nile Intelligence — Egyptian Real Estate Market Intelligence',
  description: 'Comprehensive market data, competitor monitoring, pricing trends, and business intelligence for the Egyptian real estate market.',
  keywords: 'Egyptian real estate, property market, Cairo, New Cairo, market intelligence',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: { fontSize: '14px', maxWidth: '400px' },
          }}
        />
        {children}
      </body>
    </html>
  )
}
