'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Trophy, CheckCircle2, ThumbsUp, Medal, Activity } from 'lucide-react'
import { api } from '@/lib/api'

export default function ProfilePage() {
  const { id } = useParams()
  const [profile, setProfile] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get(`/users/${id}/profile`)
      .then(res => setProfile(res.data))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [id])

  if (loading) {
    return <div className="p-8">Loading profile...</div>
  }

  if (!profile) {
    return <div className="p-8">Profile not found.</div>
  }

  return (
    <div className="container mx-auto py-12 max-w-5xl">
      <div className="flex items-center space-x-6 mb-12">
        <div className="h-24 w-24 rounded-full bg-primary/10 flex items-center justify-center border-4 border-primary/20">
          <span className="text-4xl font-bold text-primary">{profile.username.charAt(0).toUpperCase()}</span>
        </div>
        <div>
          <h1 className="text-4xl font-bold">{profile.username}</h1>
          <div className="flex items-center mt-2 text-muted-foreground font-semibold">
            <Trophy className="w-5 h-5 mr-2 text-amber-500" />
            <span className="text-xl">Solver Score: {profile.reputation_score.toLocaleString()}</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
        <Card>
          <CardContent className="pt-6 flex flex-col items-center justify-center text-center">
            <CheckCircle2 className="w-8 h-8 mb-2 text-green-500" />
            <span className="text-3xl font-bold">{profile.problems_solved}</span>
            <span className="text-sm text-muted-foreground mt-1">Accepted Solutions</span>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 flex flex-col items-center justify-center text-center">
            <Medal className="w-8 h-8 mb-2 text-blue-500" />
            <span className="text-3xl font-bold">{profile.solutions_verified}</span>
            <span className="text-sm text-muted-foreground mt-1">Community Verifications</span>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 flex flex-col items-center justify-center text-center">
            <Activity className="w-8 h-8 mb-2 text-purple-500" />
            <span className="text-3xl font-bold">{profile.success_rate}%</span>
            <span className="text-sm text-muted-foreground mt-1">Success Rate</span>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 flex flex-col items-center justify-center text-center">
            <ThumbsUp className="w-8 h-8 mb-2 text-pink-500" />
            <span className="text-3xl font-bold">{profile.helpful_votes}</span>
            <span className="text-sm text-muted-foreground mt-1">Helpful Votes</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-2xl flex items-center">
            <Trophy className="w-6 h-6 mr-2" />
            Area of Expertise
          </CardTitle>
        </CardHeader>
        <CardContent>
          {profile.expertise.length === 0 ? (
            <p className="text-muted-foreground">No expertise data available yet.</p>
          ) : (
            <div className="space-y-6 mt-4">
              {profile.expertise.map((exp: any, i: number) => (
                <div key={i}>
                  <div className="flex justify-between mb-1">
                    <span className="font-semibold">{exp.category_name}</span>
                    <span className="text-sm text-muted-foreground font-mono">{exp.score} pts</span>
                  </div>
                  <div className="w-full bg-secondary rounded-full h-2.5">
                    <div 
                      className="bg-primary h-2.5 rounded-full" 
                      style={{ width: `${Math.min((exp.score / (profile.expertise[0].score || 1)) * 100, 100)}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

