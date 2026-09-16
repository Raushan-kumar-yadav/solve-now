'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { api } from '@/lib/api'

export default function ExpertRequestsPage() {
  const [requests, setRequests] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    // In a real app we would have a specific endpoint to list incoming requests
    // Let's create a stub /experts/requests GET endpoint.
    api.get('/experts/requests')
      .then(res => setRequests(res.data))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const handleAccept = async (reqId: string) => {
    try {
      await api.post(`/experts/requests/${reqId}/accept`)
      // Refresh
      const res = await api.get('/experts/requests')
      setRequests(res.data)
      alert('Request accepted! A private room has been created.')
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to accept')
    }
  }

  if (loading) return <div className="p-8">Loading requests...</div>

  return (
    <div className="container mx-auto py-12 max-w-4xl">
      <h1 className="text-3xl font-bold mb-8">Expert Requests</h1>
      
      {requests.length === 0 ? (
        <p className="text-muted-foreground">You have no pending requests.</p>
      ) : (
        <div className="space-y-4">
          {requests.map(req => (
            <Card key={req.id}>
              <CardContent className="pt-6 flex justify-between items-center">
                <div>
                  <h3 className="font-semibold text-lg">{req.problem.title}</h3>
                  <p className="text-sm text-muted-foreground mb-2">Requested by {req.requester.username}</p>
                  {req.message && (
                    <div className="bg-muted p-3 rounded-md text-sm italic mb-2">
                      "{req.message}"
                    </div>
                  )}
                  <span className={`px-2 py-1 rounded text-xs font-bold ${
                    req.status === 'ACCEPTED' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'
                  }`}>
                    {req.status}
                  </span>
                </div>
                
                <div className="flex flex-col space-y-2 ml-4 min-w-[120px]">
                  {req.status === 'PENDING' ? (
                    <>
                      <Button onClick={() => handleAccept(req.id)} className="w-full bg-green-600 hover:bg-green-700 text-white">Accept</Button>
                      <Button variant="outline" className="w-full">Decline</Button>
                    </>
                  ) : req.status === 'ACCEPTED' ? (
                    <Button onClick={() => router.push(`/problems/${req.problem.public_id}`)} className="w-full">Go to Room</Button>
                  ) : null}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

