'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

export default function SettingsPage() {
  const [user, setUser] = useState<any>(null)
  
  useEffect(() => {
    api.get('/auth/me').then(res => setUser(res.data)).catch(() => {})
  }, [])

  if (!user) return <div className="p-8 text-center text-muted-foreground">Loading settings...</div>

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold">Settings</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>Account Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Email</Label>
            <Input value={user.email} disabled />
            <p className="text-xs text-muted-foreground">Email cannot be changed.</p>
          </div>
          <div className="space-y-2">
            <Label>Username</Label>
            <Input value={user.username || ''} disabled />
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle>AI Preferences</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">AI features are currently managed by workspace admins.</p>
          <Button disabled>Save Preferences</Button>
        </CardContent>
      </Card>
    </div>
  )
}
