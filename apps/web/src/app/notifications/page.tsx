'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { Bell, CheckCircle } from 'lucide-react'

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchNotifications()
  }, [])

  const fetchNotifications = async () => {
    try {
      const res = await api.get('/notifications')
      setNotifications(res.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const markAsRead = async (id: string) => {
    try {
      await api.post(`/notifications/${id}/read`)
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, read_at: new Date().toISOString() } : n))
    } catch (err) {}
  }

  const markAllRead = async () => {
    try {
      await api.post('/notifications/read-all')
      fetchNotifications()
    } catch (err) {}
  }

  return (
    <div className="container max-w-3xl py-10 mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Bell className="h-6 w-6" /> Notifications
        </h1>
        <Button variant="outline" onClick={markAllRead}>Mark All as Read</Button>
      </div>

      {loading ? (
        <div className="text-center py-10">Loading...</div>
      ) : notifications.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12 text-muted-foreground">
            No notifications yet.
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {notifications.map(n => (
            <Card key={n.id} className={!n.read_at ? 'bg-primary/5 border-primary/20' : ''}>
              <CardContent className="p-4 flex items-start justify-between">
                <div>
                  <h3 className="font-semibold mb-1">{n.title}</h3>
                  <p className="text-sm text-muted-foreground mb-2">{n.body}</p>
                  <div className="flex items-center gap-4">
                    <span className="text-xs text-muted-foreground">{new Date(n.created_at).toLocaleString()}</span>
                    {n.action_url && (
                      <Link href={n.action_url} className="text-xs text-primary hover:underline">View Details</Link>
                    )}
                  </div>
                </div>
                {!n.read_at && (
                  <Button variant="ghost" size="sm" onClick={() => markAsRead(n.id)}>
                    <CheckCircle className="h-4 w-4 mr-2" /> Mark Read
                  </Button>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
