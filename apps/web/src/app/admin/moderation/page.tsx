'use client'

import { useEffect, useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { api } from '@/lib/api'
import { formatDistanceToNow } from 'date-fns'

export default function ModerationDashboard() {
  const [reports, setReports] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const fetchReports = async () => {
    try {
      const res = await api.get('/moderation/reports')
      setReports(res.data)
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  useEffect(() => {
    fetchReports()
  }, [])

  const handleAction = async (entityType: string, entityId: string, action: string, reason: string) => {
    try {
      await api.post('/moderation/actions', {
        entity_type: entityType,
        entity_id: entityId,
        action,
        reason
      })
      alert(`Action ${action} executed.`)
      fetchReports() // refresh
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Failed action')
    }
  }

  if (loading) return <div className="p-8">Loading...</div>

  return (
    <div className="space-y-6 max-w-6xl">
      <h1 className="text-3xl font-bold mb-8">Moderation Queue</h1>

      {reports.length === 0 ? (
        <p className="text-muted-foreground">No reports pending.</p>
      ) : (
        <div className="space-y-4">
          {reports.map(report => (
            <Card key={report.id}>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex justify-between">
                  <span>Report on {report.entity_type}</span>
                  <span className={`text-sm px-2 py-1 rounded ${report.status === 'PENDING' ? 'bg-amber-100 text-amber-800' : 'bg-gray-100'}`}>
                    {report.status}
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-semibold">Reason: <span className="font-normal">{report.reason}</span></p>
                    <p className="text-sm font-semibold mt-2">Details:</p>
                    <p className="text-sm bg-muted p-2 rounded mt-1">{report.details || 'None provided'}</p>
                    <p className="text-xs text-muted-foreground mt-2">Reported {formatDistanceToNow(new Date(report.created_at))} ago by {report.reporter_id}</p>
                    <p className="text-xs text-muted-foreground mt-1">Entity ID: {report.entity_id}</p>
                  </div>
                  <div className="flex flex-col gap-2 justify-end">
                    <Button onClick={() => handleAction(report.entity_type, report.entity_id, 'HIDE', 'Violation of terms')} variant="destructive">
                      Hide Content
                    </Button>
                    <Button onClick={() => handleAction(report.entity_type, report.entity_id, 'WARN', 'Warning issued')} variant="outline">
                      Warn User
                    </Button>
                    <Button onClick={() => handleAction(report.entity_type, report.entity_id, 'SUSPEND', 'Suspended account')} variant="outline" className="border-red-200 text-red-600 hover:bg-red-50">
                      Suspend User
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

