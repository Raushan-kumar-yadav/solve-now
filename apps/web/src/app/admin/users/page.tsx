'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { formatDistanceToNow } from 'date-fns'
import { MoreHorizontal, Ban, RefreshCcw } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

export default function AdminUsers() {
  const [users, setUsers] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const fetchUsers = async () => {
    try {
      const res = await api.get('/admin/users')
      setUsers(res.data)
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  useEffect(() => {
    fetchUsers()
  }, [])

  const handleSuspend = async (userId: string) => {
    try {
      await api.post(`/admin/users/${userId}/suspend`)
      fetchUsers()
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Failed to suspend user')
    }
  }

  const handleRestore = async (userId: string) => {
    try {
      await api.post(`/admin/users/${userId}/restore`)
      fetchUsers()
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Failed to restore user')
    }
  }

  if (loading) return <div>Loading users...</div>

  return (
    <div className="space-y-6 max-w-6xl">
      <h1 className="text-3xl font-bold tracking-tight">User Management</h1>
      
      <div className="border rounded-md overflow-hidden bg-white">
        <table className="w-full text-sm text-left">
          <thead className="text-xs text-muted-foreground uppercase bg-muted/50 border-b">
            <tr>
              <th className="px-6 py-3">User</th>
              <th className="px-6 py-3">Role</th>
              <th className="px-6 py-3">Status</th>
              <th className="px-6 py-3">Joined</th>
              <th className="px-6 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id} className="border-b last:border-0 hover:bg-muted/30">
                <td className="px-6 py-4 font-medium">
                  {user.username}
                  <div className="text-xs text-muted-foreground">{user.email}</div>
                </td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${user.role === 'ADMIN' ? 'bg-primary/10 text-primary' : 'bg-secondary'}`}>
                    {user.role}
                  </span>
                </td>
                <td className="px-6 py-4">
                  {user.is_active ? (
                    <span className="text-green-600 font-medium">Active</span>
                  ) : (
                    <span className="text-red-600 font-medium">Suspended</span>
                  )}
                </td>
                <td className="px-6 py-4 text-muted-foreground">
                  {formatDistanceToNow(new Date(user.created_at))} ago
                </td>
                <td className="px-6 py-4 text-right">
                  <DropdownMenu>
                    <DropdownMenuTrigger render={<Button variant="ghost" className="h-8 w-8 p-0" />}>
                      <MoreHorizontal className="h-4 w-4" />
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      {user.is_active ? (
                        <DropdownMenuItem onClick={() => handleSuspend(user.id)} className="text-red-600">
                          <Ban className="mr-2 h-4 w-4" /> Suspend
                        </DropdownMenuItem>
                      ) : (
                        <DropdownMenuItem onClick={() => handleRestore(user.id)}>
                          <RefreshCcw className="mr-2 h-4 w-4" /> Restore
                        </DropdownMenuItem>
                      )}
                    </DropdownMenuContent>
                  </DropdownMenu>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

