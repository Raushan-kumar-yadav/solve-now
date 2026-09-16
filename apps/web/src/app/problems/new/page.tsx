'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card'

export default function NewProblemPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const initialTitle = searchParams.get('initialTitle') || ''
  
  const [title, setTitle] = useState(initialTitle)
  const [description, setDescription] = useState('')
  const [urgency, setUrgency] = useState('normal')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const res = await api.post('/problems', {
        title,
        description,
        urgency,
        is_public: true
      })
      router.push(`/problems/${res.data.public_id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create problem. Please login.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container max-w-3xl py-10 mx-auto">
      <Card>
        <CardHeader>
          <CardTitle className="text-3xl">Create New Problem</CardTitle>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-6">
            {error && <div className="p-3 bg-red-100 text-red-800 rounded">{error}</div>}
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Title</label>
              <Input 
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Briefly summarize the issue..."
                required 
              />
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Description</label>
              <Textarea 
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Provide all the details, logs, or context needed..."
                required 
                className="min-h-[200px]"
              />
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Urgency</label>
              <select 
                value={urgency} 
                onChange={e => setUrgency(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
              >
                <option value="low">Low</option>
                <option value="normal">Normal</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
          </CardContent>
          <CardFooter className="flex justify-end space-x-4">
            <Button variant="outline" type="button" onClick={() => router.back()}>Cancel</Button>
            <Button type="submit" disabled={loading}>{loading ? 'Creating...' : 'Submit Problem'}</Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  )
}
