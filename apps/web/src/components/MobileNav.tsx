'use client'

import { usePathname, useRouter } from 'next/navigation'
import Link from 'next/link'
import { Home, Compass, PlusCircle, Bell, Menu, Users, BookOpen, UserCircle, Settings, LogOut } from 'lucide-react'
import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'

export function MobileNav() {
  const pathname = usePathname()
  const router = useRouter()
  const [user, setUser] = useState<any>(null)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    api.get('/auth/me').then(res => setUser(res.data)).catch(() => {})
  }, [])

  const handleLogout = async () => {
    try {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token')
      }
      await api.post('/auth/logout')
      window.location.href = '/'
    } catch (e) {
      window.location.href = '/'
    }
  }

  if (pathname.startsWith('/admin') || pathname.startsWith('/login') || pathname.startsWith('/register')) {
    return null
  }

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-background border-t pb-safe">
      <div className="flex items-center justify-around h-16 px-2">
        <Link href="/" className={`flex flex-col items-center justify-center w-full h-full space-y-1 ${pathname === '/' ? 'text-primary' : 'text-muted-foreground'}`}>
          <Home className="h-5 w-5" />
          <span className="text-[10px] font-medium">Home</span>
        </Link>
        
        <Link href="/explore" className={`flex flex-col items-center justify-center w-full h-full space-y-1 ${pathname.startsWith('/explore') ? 'text-primary' : 'text-muted-foreground'}`}>
          <Compass className="h-5 w-5" />
          <span className="text-[10px] font-medium">Explore</span>
        </Link>
        
        <div className="flex flex-col items-center justify-center w-full h-full relative -top-3">
          <button onClick={() => router.push(user ? '/problems/new' : '/login')} className="bg-primary text-primary-foreground p-3 rounded-full shadow-lg" aria-label="Create Problem">
            <PlusCircle className="h-6 w-6" />
          </button>
        </div>
        
        <Link href="/notifications" className={`flex flex-col items-center justify-center w-full h-full space-y-1 ${pathname.startsWith('/notifications') ? 'text-primary' : 'text-muted-foreground'}`}>
          <div className="relative"><Bell className="h-5 w-5" /></div>
          <span className="text-[10px] font-medium">Alerts</span>
        </Link>
        
        {/* Button must be OUTSIDE the Sheet since we aren't using SheetTrigger */}
        <button onClick={() => setOpen(true)} className="flex flex-col items-center justify-center w-full h-full space-y-1 text-muted-foreground">
          <Menu className="h-5 w-5" />
          <span className="text-[10px] font-medium">Menu</span>
        </button>
        
        <Sheet open={open} onOpenChange={setOpen}>
          <SheetContent side="right" className="w-[80vw] sm:w-[350px] flex flex-col">
            <SheetHeader>
              <SheetTitle className="text-left">Menu</SheetTitle>
            </SheetHeader>
            <div className="flex flex-col flex-1 gap-2 mt-4">
              <Link href="/explore" onClick={() => setOpen(false)} className="flex items-center gap-3 p-3 rounded-lg hover:bg-muted">
                <Compass className="h-5 w-5 text-muted-foreground" />
                <span className="font-medium">Explore</span>
              </Link>
              <Link href="/experts" onClick={() => setOpen(false)} className="flex items-center gap-3 p-3 rounded-lg hover:bg-muted">
                <Users className="h-5 w-5 text-muted-foreground" />
                <span className="font-medium">Experts</span>
              </Link>
              <Link href="/knowledge" onClick={() => setOpen(false)} className="flex items-center gap-3 p-3 rounded-lg hover:bg-muted">
                <BookOpen className="h-5 w-5 text-muted-foreground" />
                <span className="font-medium">Knowledge Base</span>
              </Link>
              
              <div className="my-4 border-t" />
              
              {user ? (
                <>
                  <Link href={`/profile/${user.id}`} onClick={() => setOpen(false)} className="flex items-center gap-3 p-3 rounded-lg hover:bg-muted">
                    <UserCircle className="h-5 w-5 text-muted-foreground" />
                    <span className="font-medium">Profile</span>
                  </Link>
                  <Link href="/settings" onClick={() => setOpen(false)} className="flex items-center gap-3 p-3 rounded-lg hover:bg-muted">
                    <Settings className="h-5 w-5 text-muted-foreground" />
                    <span className="font-medium">Settings</span>
                  </Link>
                  <button onClick={() => { setOpen(false); handleLogout(); }} className="flex items-center gap-3 p-3 rounded-lg hover:bg-muted text-red-500">
                    <LogOut className="h-5 w-5" />
                    <span className="font-medium">Sign Out</span>
                  </button>
                </>
              ) : (
                <div className="flex flex-col gap-3 mt-auto mb-4">
                  <Link href="/login" onClick={() => setOpen(false)} className="flex items-center justify-center p-3 rounded-lg bg-muted font-medium">Log In</Link>
                  <Link href="/register" onClick={() => setOpen(false)} className="flex items-center justify-center p-3 rounded-lg bg-primary text-primary-foreground font-medium">Sign Up</Link>
                </div>
              )}
            </div>
          </SheetContent>
        </Sheet>
      </div>
    </nav>
  )
}
