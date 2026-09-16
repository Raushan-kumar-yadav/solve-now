'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { NotificationProvider } from './NotificationProvider'
import { NotificationBell } from './NotificationBell'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { Button } from './ui/button'
import { Search, PlusCircle, User, LogOut, LayoutDashboard, Compass, Lightbulb, Users, BookOpen } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu'

export function Navbar() {
  const [user, setUser] = useState<any>(null)
  const pathname = usePathname()
  const router = useRouter()
  
  useEffect(() => {
    api.get('/auth/me').then(res => setUser(res.data)).catch(() => {})
  }, [])

  const handleLogout = async () => {
    try {
      await api.post('/auth/logout')
      window.location.href = '/'
    } catch {}
  }

  const navLinks = [
    { href: '/explore', label: 'Explore', icon: Compass },
    
    { href: '/experts', label: 'Experts', icon: Users },
    { href: '/knowledge', label: 'Knowledge', icon: BookOpen },
  ]

  return (
    <NotificationProvider user={user}>
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="max-w-7xl mx-auto px-4 flex h-16 items-center justify-between">
          
          {/* Left: Logo & Search */}
          <div className="flex items-center gap-6">
            <Link className="flex items-center space-x-2" href="/">
              <div className="bg-primary text-primary-foreground p-1 rounded-md">
                <Lightbulb className="h-5 w-5" />
              </div>
              <span className="font-bold text-lg hidden sm:inline-block tracking-tight">SolveNow</span>
            </Link>
          </div>

          {/* Center: Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            {navLinks.map(link => {
              const isActive = pathname.startsWith(link.href)
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`text-sm font-medium transition-colors hover:text-primary ${
                    isActive ? 'text-primary' : 'text-muted-foreground'
                  }`}
                >
                  {link.label}
                </Link>
              )
            })}
          </nav>

          {/* Right: Actions */}
          <div className="flex items-center justify-end space-x-2 sm:space-x-4">
            <Button variant="ghost" size="icon" onClick={() => router.push('/search')} aria-label="Search">
              <Search className="h-5 w-5 text-muted-foreground" />
            </Button>
            
            {user ? (
              <>
                <NotificationBell />
                <Button className="hidden sm:flex gap-2" size="sm" onClick={() => router.push('/problems/new')}>
                  <PlusCircle className="h-4 w-4" /> Create Problem
                </Button>
                
                <DropdownMenu>
                  <DropdownMenuTrigger render={<Button variant="ghost" size="icon" className="rounded-full bg-muted" />}>
                    <User className="h-4 w-4 text-muted-foreground" />
                    <span className="sr-only">Toggle user menu</span>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-56">
                    <div className="px-2 py-2">
                      <p className="text-sm font-medium">{user.username}</p>
                      <p className="text-xs text-muted-foreground truncate">{user.email}</p>
                    </div>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem render={<Link href={`/profile/${user.id}`} className="cursor-pointer" />}>
                      <User className="mr-2 h-4 w-4" /> Profile
                    </DropdownMenuItem>
                    {user.role === 'ADMIN' && (
                      <DropdownMenuItem render={<Link href="/admin" className="cursor-pointer" />}>
                        <LayoutDashboard className="mr-2 h-4 w-4" /> Admin Panel
                      </DropdownMenuItem>
                    )}
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={handleLogout} className="cursor-pointer text-red-600 focus:text-red-600">
                      <LogOut className="mr-2 h-4 w-4" /> Log out
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </>
            ) : (
              <Button size="sm" onClick={() => router.push('/login')}>Log in</Button>
            )}
          </div>
        </div>
      </header>
    </NotificationProvider>
  )
}
