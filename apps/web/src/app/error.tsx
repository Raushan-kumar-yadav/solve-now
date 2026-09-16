'use client'
 
import { useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert'
import { AlertCircle } from 'lucide-react'
 
export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error(error)
  }, [error])
 
  return (
    <div className="flex items-center justify-center min-h-[50vh] p-4">
      <Alert variant="destructive" className="max-w-md">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Something went wrong!</AlertTitle>
        <AlertDescription className="mt-2 flex flex-col gap-4">
          <p>An unexpected error occurred. Please try again.</p>
          <Button variant="outline" onClick={() => reset()} className="w-fit">
            Try again
          </Button>
        </AlertDescription>
      </Alert>
    </div>
  )
}

