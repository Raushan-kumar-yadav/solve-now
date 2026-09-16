'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Search, Mic, Paperclip, Activity, CheckCircle, Users, BookOpen } from 'lucide-react'
import Link from 'next/link'
import { formatDistanceToNow } from 'date-fns'

function SkeletonCard() {
  return (
    <div className="border rounded-xl p-5 space-y-3 animate-pulse bg-card">
      <div className="h-5 bg-muted rounded w-3/4"></div>
      <div className="h-4 bg-muted rounded w-full"></div>
      <div className="h-4 bg-muted rounded w-5/6"></div>
      <div className="flex gap-2 pt-2">
        <div className="h-6 w-16 bg-muted rounded-full"></div>
        <div className="h-6 w-16 bg-muted rounded-full"></div>
      </div>
    </div>
  )
}

export default function HomePage() {
  const router = useRouter()
  const [problemQuery, setProblemQuery] = useState('')
  const [trending, setTrending] = useState<any[]>([])
  const [solved, setSolved] = useState<any[]>([])
  const [knowledge, setKnowledge] = useState<any[]>([])
  const [experts, setExperts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchFeeds = async () => {
      try {
        const [pRes, eRes, kRes] = await Promise.all([
          api.get('/problems?limit=6'),
          api.get('/experts/search?limit=4'),
          api.get('/knowledge/search?limit=3').catch(() => ({ data: { results: [] } })),
        ])
        const problems = pRes.data?.items ?? pRes.data ?? []
        setTrending(problems.filter((p: any) => p.status === 'OPEN').slice(0, 3))
        setSolved(problems.filter((p: any) => p.status === 'SOLVED').slice(0, 3))
        setExperts(eRes.data?.experts ?? eRes.data ?? [])
        // Knowledge search returns { results: [...] } — handle gracefully if empty
        setKnowledge(kRes.data?.results ?? kRes.data ?? [])
      } catch (e) {
        // Log in development only — never expose stack traces in production UI
        if (process.env.NODE_ENV === 'development') {
          console.error('[HomePage] Feed fetch error:', e)
        }
      } finally {
        setLoading(false)
      }
    }
    fetchFeeds()
  }, [])


  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault()
    if (!problemQuery.trim()) return
    router.push(`/problems/new?initialTitle=${encodeURIComponent(problemQuery)}`)
  }

  return (
    <div className="min-h-screen bg-muted/20">
      {/* Hero Section */}
      <div className="bg-background border-b pt-16 pb-20 px-4">
        <div className="max-w-3xl mx-auto text-center space-y-8">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-foreground">
            What problem are you trying to solve?
          </h1>
          
          <form onSubmit={handleCreate} className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-primary/20 to-primary/20 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"></div>
            <div className="relative bg-background border shadow-sm rounded-2xl p-2 flex flex-col sm:flex-row focus-within:ring-2 ring-primary/20 transition-all">
              <Textarea
                placeholder="Describe your issue, paste an error log, or ask a question..."
                className="border-0 shadow-none focus-visible:ring-0 resize-none min-h-[80px] sm:min-h-[60px] text-base p-3"
                value={problemQuery}
                onChange={(e) => setProblemQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleCreate(e)
                  }
                }}
              />
              <div className="flex sm:flex-col justify-between sm:justify-end gap-2 p-2 sm:p-0 sm:pl-2 border-t sm:border-t-0 sm:border-l mt-2 sm:mt-0">
                <div className="flex gap-1">
                  <Button type="button" variant="ghost" size="icon" className="h-9 w-9 rounded-full text-muted-foreground hover:text-foreground" aria-label="Upload file">
                    <Paperclip className="h-4 w-4" />
                  </Button>
                  <Button type="button" variant="ghost" size="icon" className="h-9 w-9 rounded-full text-muted-foreground hover:text-foreground" aria-label="Voice input">
                    <Mic className="h-4 w-4" />
                  </Button>
                </div>
                <Button type="submit" className="h-9 rounded-full px-6 font-semibold" disabled={!problemQuery.trim()}>
                  Start Investigation
                </Button>
              </div>
            </div>
          </form>
        </div>
      </div>

      {/* Live Feeds */}
      <div className="max-w-7xl mx-auto px-4 py-12 space-y-16">
        
        {/* Trending & Solved */}
        <div className="grid md:grid-cols-2 gap-12">
          {/* Trending */}
          <section className="space-y-6">
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-blue-500" />
              <h2 className="text-xl font-bold tracking-tight">Trending Investigations</h2>
            </div>
            <div className="space-y-4">
              {loading ? (
                Array(3).fill(0).map((_, i) => <SkeletonCard key={i} />)
              ) : trending.length > 0 ? (
                trending.map(problem => (
                  <Link href={`/problems/${problem.public_id}`} key={problem.id} className="block group">
                    <div className="border bg-card rounded-xl p-5 hover:border-primary/50 transition-colors shadow-sm">
                      <h3 className="font-semibold text-lg group-hover:text-primary transition-colors">{problem.title}</h3>
                      <p className="text-sm text-muted-foreground mt-2 line-clamp-2">{problem.description}</p>
                      <div className="flex items-center gap-4 mt-4 text-xs text-muted-foreground font-medium">
                        <span className="bg-secondary px-2 py-1 rounded-md">{problem.category?.name || 'General'}</span>
                        <span>{formatDistanceToNow(new Date(problem.created_at))} ago</span>
                        <span>{problem.author}</span>
                      </div>
                    </div>
                  </Link>
                ))
              ) : (
                <div className="text-center p-8 border border-dashed rounded-xl text-muted-foreground">
                  No active investigations right now. <button onClick={() => router.push('/problems/new')} className="text-primary hover:underline font-medium">Start one.</button>
                </div>
              )}
            </div>
            <Button variant="outline" className="w-full" render={<Link href="/explore?status=OPEN" />}>
              View All Open Problems
            </Button>
          </section>

          {/* Solved */}
          <section className="space-y-6">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <h2 className="text-xl font-bold tracking-tight">Recently Solved</h2>
            </div>
            <div className="space-y-4">
              {loading ? (
                Array(3).fill(0).map((_, i) => <SkeletonCard key={i} />)
              ) : solved.length > 0 ? (
                solved.map(problem => (
                  <Link href={`/problems/${problem.public_id}`} key={problem.id} className="block group">
                    <div className="border bg-card rounded-xl p-5 hover:border-green-500/50 transition-colors shadow-sm">
                      <h3 className="font-semibold text-lg group-hover:text-green-600 transition-colors">{problem.title}</h3>
                      <p className="text-sm text-muted-foreground mt-2 line-clamp-2">{problem.description}</p>
                      <div className="flex items-center gap-4 mt-4 text-xs text-muted-foreground font-medium">
                        <span className="bg-green-100 text-green-800 px-2 py-1 rounded-md">Solved</span>
                        <span>{formatDistanceToNow(new Date(problem.created_at))} ago</span>
                      </div>
                    </div>
                  </Link>
                ))
              ) : (
                <div className="text-center p-8 border border-dashed rounded-xl text-muted-foreground">
                  No solutions verified yet today.
                </div>
              )}
            </div>
          </section>
        </div>

        {/* Experts */}
        <section className="space-y-6">
          <div className="flex items-center gap-2">
            <Users className="h-5 w-5 text-purple-500" />
            <h2 className="text-xl font-bold tracking-tight">Top Experts</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
            {loading ? (
              Array(4).fill(0).map((_, i) => (
                <div key={i} className="border rounded-xl p-4 animate-pulse bg-card">
                  <div className="h-10 w-10 bg-muted rounded-full mb-3"></div>
                  <div className="h-4 bg-muted rounded w-1/2 mb-2"></div>
                  <div className="h-3 bg-muted rounded w-3/4"></div>
                </div>
              ))
            ) : experts.length > 0 ? (
              experts.map(expert => (
                <div key={expert.id} className="border bg-card rounded-xl p-5 shadow-sm text-center">
                  <div className="h-12 w-12 bg-primary/10 text-primary rounded-full flex items-center justify-center mx-auto mb-3 font-bold text-lg">
                    {expert.username.charAt(0).toUpperCase()}
                  </div>
                  <h3 className="font-semibold truncate">{expert.username}</h3>
                  <p className="text-xs text-muted-foreground mt-1">{expert.success_rate}% Success Rate</p>
                  <Button variant="secondary" size="sm" className="w-full mt-4" render={<Link href={`/profile/${expert.user_id}`} />}>
                    View Profile
                  </Button>
                </div>
              ))
            ) : (
              <div className="col-span-full text-center p-8 border border-dashed rounded-xl text-muted-foreground">
                No experts available right now.
              </div>
            )}
          </div>
        </section>

      </div>
    </div>
  )
}
