'use client'

import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Users, FileText } from 'lucide-react'
import Link from 'next/link'

export default function ExpertsPage() {
  return (
    <div className="container max-w-4xl py-12 mx-auto">
      <h1 className="text-4xl font-bold mb-8">Expert Portal</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Apply as Expert
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground mb-4">Share your knowledge and get matched with users who need your expertise to solve critical problems.</p>
            <Link href="/experts/apply">
              <Button>Apply Now</Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Manage Requests
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground mb-4">View incoming expert assistance requests from users and manage your private advisory rooms.</p>
            <Button onClick={() => window.location.href = "/experts/requests"}>
              View Requests
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
