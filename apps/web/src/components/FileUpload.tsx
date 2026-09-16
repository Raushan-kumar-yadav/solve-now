'use client'

import { useState, useRef, useCallback } from 'react'
import { api } from '@/lib/api'
import { UploadCloud, X, File as FileIcon, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'

interface FileUploadProps {
  publicId: string
  onUploadComplete: () => void
}

export function FileUpload({ publicId, onUploadComplete }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  // To allow canceling
  const abortControllerRef = useRef<AbortController | null>(null)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const uploadFile = async (file: File) => {
    setError(null)
    setUploading(true)
    setProgress(0)
    
    // Quick frontend check (though backend is the source of truth)
    if (file.size > 10 * 1024 * 1024) {
      setError('File must be smaller than 10MB')
      setUploading(false)
      return
    }

    const formData = new FormData()
    formData.append('file', file)

    const controller = new AbortController()
    abortControllerRef.current = controller

    try {
      await api.post(`/problems/${publicId}/files`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        signal: controller.signal,
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            setProgress(percentCompleted)
          }
        }
      })
      
      setUploading(false)
      setProgress(0)
      onUploadComplete() // notify parent to refresh file list
      
    } catch (err: any) {
      if (err.name === 'CanceledError' || err.code === 'ERR_CANCELED') {
        setError('Upload cancelled')
      } else {
        setError(err.response?.data?.detail || 'Upload failed')
      }
      setUploading(false)
      setProgress(0)
    }
  }

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      uploadFile(e.dataTransfer.files[0])
    }
  }, [publicId, onUploadComplete])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      uploadFile(e.target.files[0])
    }
  }

  const cancelUpload = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
  }

  return (
    <div className="w-full">
      {!uploading ? (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-lg p-6 flex flex-col items-center justify-center cursor-pointer transition-colors ${
            isDragging ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'
          }`}
        >
          <input
            type="file"
            className="hidden"
            ref={fileInputRef}
            onChange={handleFileSelect}
            accept=".jpg,.jpeg,.png,.pdf,.txt"
          />
          <UploadCloud className="w-10 h-10 text-muted-foreground mb-4" />
          <p className="font-medium text-sm">Click or drag file to upload</p>
          <p className="text-xs text-muted-foreground mt-1">PNG, JPG, PDF up to 10MB</p>
          {error && <p className="text-destructive text-sm mt-2 font-medium">{error}</p>}
        </div>
      ) : (
        <div className="border rounded-lg p-4 bg-muted/20">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <Loader2 className="w-4 h-4 animate-spin text-primary" />
              <span className="text-sm font-medium">Uploading...</span>
            </div>
            <Button variant="ghost" size="sm" onClick={cancelUpload} className="h-8 px-2 text-muted-foreground">
              <X className="w-4 h-4 mr-1" /> Cancel
            </Button>
          </div>
          <Progress value={progress} className="h-2" />
        </div>
      )}
    </div>
  )
}

