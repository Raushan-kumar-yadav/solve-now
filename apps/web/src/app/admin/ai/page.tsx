'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { formatDistanceToNow } from 'date-fns'

export default function AdminAI() {
  const [investigations, setInvestigations] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const fetchAI = async () => {
    try {
      const res = await api.get('/admin/ai')
      setInvestigations(res.data)
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  useEffect(() => {
    fetchAI()
  }, [])

  if (loading) return <div>Loading AI metrics...</div>

  return (
    <div className="space-y-6 max-w-6xl">
      <h1 className="text-3xl font-bold tracking-tight">AI Investigations Log</h1>
      
      <div className="border rounded-md overflow-hidden bg-white">
        <table className="w-full text-sm text-left">
          <thead className="text-xs text-muted-foreground uppercase bg-muted/50 border-b">
            <tr>
              <th className="px-6 py-3">ID</th>
              <th className="px-6 py-3">Status</th>
              <th className="px-6 py-3">Model</th>
              <th className="px-6 py-3">Latency (ms)</th>
              <th className="px-6 py-3">Tokens Used</th>
              <th className="px-6 py-3">Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {investigations.map(inv => (
              <tr key={inv.id} className="border-b last:border-0 hover:bg-muted/30">
                <td className="px-6 py-4 font-medium font-mono text-xs">{inv.id.substring(0, 8)}...</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    inv.status === 'COMPLETED' ? 'bg-green-100 text-green-800' : 
                    inv.status === 'FAILED' ? 'bg-red-100 text-red-800' : 'bg-blue-100 text-blue-800'
                  }`}>
                    {inv.status}
                  </span>
                </td>
                <td className="px-6 py-4 text-muted-foreground">{inv.provider} / {inv.model}</td>
                <td className="px-6 py-4 font-mono">{inv.latency_ms} ms</td>
                <td className="px-6 py-4 font-mono">{inv.tokens_used}</td>
                <td className="px-6 py-4 text-muted-foreground">
                  {formatDistanceToNow(new Date(inv.created_at))} ago
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

