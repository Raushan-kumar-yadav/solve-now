'use client'

import { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import { api } from '@/lib/api'
import {
  LayoutDashboard,
  Users,
  AlertCircle,
  Shield,
  Activity,
  FileText
} from 'lucide-react'

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const pathname = usePathname()
  const [isAdmin, setIsAdmin] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const checkAdmin = async () => {
      try {
        const res = await api.get('/auth/me')
        if (res.data.role === 'ADMIN') {
          setIsAdmin(true)
        } else {
          router.push('/')
        }
      } catch {
        router.push('/')
      } finally {
        setLoading(false)
      }
    }
    checkAdmin()
  }, [router])

  if (loading) return <div className="p-8">Loading admin application...</div>
  if (!isAdmin) return null

  const navItems = [
    { href: '/admin', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/admin/users', label: 'Users', icon: Users },
    { href: '/admin/problems', label: 'Problems', icon: FileText },
    { href: '/admin/moderation', label: 'Moderation', icon: Shield },
    { href: '/admin/ai', label: 'AI Monitoring', icon: Activity },
  ]

  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      {/* Sidebar */}
      <div className="w-64 border-r bg-muted/20 flex flex-col">
        <div className="p-4 border-b">
          <h2 className="font-semibold text-lg">Admin Control Panel</h2>
        </div>
        <nav className="flex-1 p-4 space-y-1">
          {navItems.map(item => {
            const Icon = item.icon
            const isActive = pathname === item.href
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                  isActive ? 'bg-primary text-primary-foreground font-medium' : 'hover:bg-muted text-muted-foreground'
                }`}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            )
          })}
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto bg-background p-8">
        {children}
      </div>
    </div>
  )
}

