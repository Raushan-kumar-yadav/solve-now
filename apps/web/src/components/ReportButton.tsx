'use client'

import { useState } from 'react'
import { Button } from './ui/button'
import { Flag } from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter
} from '@/components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { api } from '@/lib/api'

interface ReportButtonProps {
  entityType: 'problem' | 'solution' | 'comment' | 'user'
  entityId: string
  className?: string
}

export function ReportButton({ entityType, entityId, className }: ReportButtonProps) {
  const [open, setOpen] = useState(false)
  const [reason, setReason] = useState<string>('')
  const [details, setDetails] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    if (!reason) return
    setLoading(true)
    try {
      await api.post('/moderation/reports', {
        entity_type: entityType,
        entity_id: entityId,
        reason,
        details
      })
      alert('Report submitted for review. Thank you.')
      setOpen(false)
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Failed to submit report')
    }
    setLoading(false)
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button variant="ghost" size="sm" className={`text-muted-foreground hover:text-red-600 ${className}`} />}>
        <Flag className="h-4 w-4 mr-2" /> Report
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Report Content</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Reason</label>
            <Select value={reason} onValueChange={(val) => setReason(val || '')}>
              <SelectTrigger>
                <SelectValue placeholder="Select a reason" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="spam">Spam</SelectItem>
                <SelectItem value="harassment">Harassment</SelectItem>
                <SelectItem value="misinformation">Misinformation</SelectItem>
                <SelectItem value="dangerous content">Dangerous Content</SelectItem>
                <SelectItem value="privacy violation">Privacy Violation</SelectItem>
                <SelectItem value="other">Other</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Additional Details (Optional)</label>
            <Textarea 
              value={details} 
              onChange={e => setDetails(e.target.value)}
              placeholder="Provide more context..."
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
          <Button disabled={!reason || loading} onClick={handleSubmit}>Submit Report</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

