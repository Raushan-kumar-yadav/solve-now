'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { formatDistanceToNow } from 'date-fns'
import { MoreHorizontal, EyeOff, Eye, Lock } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import Link from 'next/link'

export default function AdminProblems() {
  const [problems, setProblems] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const fetchProblems = async () => {
    try {
      const res = await api.get('/admin/problems')
      setProblems(res.data)
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  useEffect(() => {
    fetchProblems()
  }, [])

  const handleAction = async (problemId: string, action: string) => {
    try {
      await api.post('/moderation/actions', {
        entity_type: 'problem',
        entity_id: problemId,
        action,
        reason: 'Admin panel action'
      })
      fetchProblems()
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Action failed')
    }
  }

  if (loading) return <div>Loading problems...</div>

  return (
    <div className="space-y-6 max-w-6xl">
      <h1 className="text-3xl font-bold tracking-tight">Problem Management</h1>
      
      <div className="border rounded-md overflow-hidden bg-white">
        <table className="w-full text-sm text-left">
          <thead className="text-xs text-muted-foreground uppercase bg-muted/50 border-b">
            <tr>
              <th className="px-6 py-3">Title</th>
              <th className="px-6 py-3">Author</th>
              <th className="px-6 py-3">Status</th>
              <th className="px-6 py-3">Visibility</th>
              <th className="px-6 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {problems.map(p => (
              <tr key={p.id} className="border-b last:border-0 hover:bg-muted/30">
                <td className="px-6 py-4 font-medium">
                  <Link href={`/problems/${p.public_id}`} className="hover:underline">
                    {p.title}
                  </Link>
                  <div className="text-xs text-muted-foreground mt-1">
                    Created {formatDistanceToNow(new Date(p.created_at))} ago
                  </div>
                </td>
                <td className="px-6 py-4 text-muted-foreground">{p.author}</td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 rounded text-xs bg-secondary">{p.status}</span>
                </td>
                <td className="px-6 py-4">
                  <div className="flex gap-2">
                    {p.is_hidden && <span className="text-red-600 font-medium text-xs border border-red-200 px-1 rounded">Hidden</span>}
                    {p.is_locked && <span className="text-amber-600 font-medium text-xs border border-amber-200 px-1 rounded">Locked</span>}
                    {!p.is_hidden && !p.is_locked && <span className="text-green-600 font-medium text-xs border border-green-200 px-1 rounded">Normal</span>}
                  </div>
                </td>
                <td className="px-6 py-4 text-right">
                  <DropdownMenu>
                    <DropdownMenuTrigger render={<Button variant="ghost" className="h-8 w-8 p-0" />}>
                      <MoreHorizontal className="h-4 w-4" />
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      {p.is_hidden ? (
                        <DropdownMenuItem onClick={() => handleAction(p.id, 'RESTORE')}>
                          <Eye className="mr-2 h-4 w-4" /> Restore Visibility
                        </DropdownMenuItem>
                      ) : (
                        <DropdownMenuItem onClick={() => handleAction(p.id, 'HIDE')} className="text-red-600">
                          <EyeOff className="mr-2 h-4 w-4" /> Hide
                        </DropdownMenuItem>
                      )}
                      {!p.is_locked && (
                        <DropdownMenuItem onClick={() => handleAction(p.id, 'LOCK')} className="text-amber-600">
                          <Lock className="mr-2 h-4 w-4" /> Lock Thread
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

