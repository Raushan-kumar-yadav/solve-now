'use client'

import { useState, useEffect } from 'react'
import { Search, Book, HelpCircle, Filter } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Checkbox } from '@/components/ui/checkbox'
import { api } from '@/lib/api'
import Link from 'next/link'
import { formatDistanceToNow } from 'date-fns'

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [activeTab, setActiveTab] = useState('knowledge')
  const [results, setResults] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [verifiedOnly, setVerifiedOnly] = useState(false)

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    try {
      if (activeTab === 'knowledge') {
        const res = await api.get('/knowledge/search', {
          params: { q: query, verified_only: verifiedOnly }
        })
        setResults(res.data)
      } else {
        const res = await api.get('/problems/search', {
          params: { q: query }
        })
        setResults(res.data.items || [])
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (query) {
      handleSearch()
    } else {
      setResults([])
    }
  }, [activeTab, verifiedOnly])

  return (
    <div className="container mx-auto py-8">
      <div className="flex flex-col items-center mb-10">
        <h1 className="text-4xl font-bold mb-6 tracking-tight">SolveNow Search</h1>
        <form onSubmit={handleSearch} className="w-full max-w-3xl flex items-center space-x-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-3 h-5 w-5 text-muted-foreground" />
            <Input 
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="Search for verified solutions, recurring problems, or technical guides..." 
              className="pl-10 py-6 text-lg rounded-full border-2 shadow-sm"
            />
          </div>
          <Button type="submit" size="lg" className="rounded-full px-8 py-6" disabled={loading}>
            {loading ? 'Searching...' : 'Search'}
          </Button>
        </form>
      </div>

      <div className="flex gap-8">
        <div className="w-64 flex-shrink-0 space-y-6">
          <div>
            <h3 className="font-semibold text-lg mb-4 flex items-center">
              <Filter className="w-4 h-4 mr-2" />
              Filters
            </h3>
            
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Category</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="All Categories" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Categories</SelectItem>
                    <SelectItem value="infrastructure">Infrastructure</SelectItem>
                    <SelectItem value="frontend">Frontend</SelectItem>
                    <SelectItem value="backend">Backend</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {activeTab === 'knowledge' && (
                <div className="flex items-center space-x-2">
                  <Checkbox 
                    id="verified" 
                    checked={verifiedOnly}
                    onCheckedChange={(c) => setVerifiedOnly(c === true)}
                  />
                  <Label htmlFor="verified" className="cursor-pointer">Verified Knowledge Only</Label>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="flex-1">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="mb-6 border-b rounded-none w-full justify-start h-auto p-0 bg-transparent">
              <TabsTrigger 
                value="knowledge" 
                className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-6 py-3"
              >
                <Book className="w-4 h-4 mr-2" />
                Knowledge Base
              </TabsTrigger>
              <TabsTrigger 
                value="problems"
                className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-6 py-3"
              >
                <HelpCircle className="w-4 h-4 mr-2" />
                Community Problems
              </TabsTrigger>
            </TabsList>

            <TabsContent value="knowledge" className="mt-0 space-y-4">
              {loading ? (
                <div className="space-y-4">
                  {[1,2,3].map(i => (
                    <Card key={i} className="animate-pulse h-32" />
                  ))}
                </div>
              ) : results.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  {query ? 'No knowledge documents matched your query.' : 'Enter a search term above.'}
                </div>
              ) : (
                results.map((r: any) => (
                  <Card key={r.id} className="hover:border-primary/50 transition-colors">
                    <CardContent className="p-6">
                      <div className="flex justify-between items-start mb-2">
                        <Link href={`/knowledge/${r.id}`} className="text-xl font-semibold text-primary hover:underline">
                          {r.title}
                        </Link>
                        <div className="flex space-x-2">
                          <span className="bg-green-100 text-green-800 text-xs font-semibold px-2.5 py-0.5 rounded border border-green-200">
                            Quality: {r.quality_score}/100
                          </span>
                          {r.verification_count > 0 && (
                            <span className="bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded border border-blue-200">
                              {r.verification_count} Verifications
                            </span>
                          )}
                        </div>
                      </div>
                      <p className="text-muted-foreground text-sm mb-4 line-clamp-2">{r.content_snippet}</p>
                      <div className="flex items-center text-xs text-muted-foreground space-x-4">
                        {r.category && <span>Category: {r.category}</span>}
                        <span>•</span>
                        <span>Added {formatDistanceToNow(new Date(r.created_at))} ago</span>
                        <span>•</span>
                        <span>Relevance: {Math.round(r.relevance * 100)}%</span>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </TabsContent>

            <TabsContent value="problems" className="mt-0 space-y-4">
              {loading ? (
                <div className="space-y-4">
                  {[1,2,3].map(i => (
                    <Card key={i} className="animate-pulse h-32" />
                  ))}
                </div>
              ) : results.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  {query ? 'No problems matched your query.' : 'Enter a search term above.'}
                </div>
              ) : (
                results.map((r: any) => (
                  <Card key={r.id} className="hover:border-primary/50 transition-colors">
                    <CardContent className="p-6">
                      <div className="flex justify-between items-start mb-2">
                        <Link href={`/problems/${r.public_id}`} className="text-xl font-semibold text-primary hover:underline">
                          {r.title}
                        </Link>
                        <span className={`px-2.5 py-0.5 rounded text-xs font-semibold ${
                          r.status === 'SOLVED' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {r.status}
                        </span>
                      </div>
                      <p className="text-muted-foreground text-sm mb-4 line-clamp-2">{r.description}</p>
                      <div className="flex items-center text-xs text-muted-foreground space-x-4">
                        <span>Urgency: <span className="capitalize">{r.urgency}</span></span>
                        <span>•</span>
                        <span>Created {formatDistanceToNow(new Date(r.created_at))} ago</span>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}
