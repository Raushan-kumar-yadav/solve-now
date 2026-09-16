'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { api } from '@/lib/api'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Loader2 } from 'lucide-react'

const WS_MAX_RETRIES = 8
const WS_BASE_DELAY_MS = 1000  // 1s → 2s → 4s → 8s … max ~128s + jitter

export function RoomChat({ publicId, currentUser }: { publicId: string, currentUser: any }) {
  const [room, setRoom] = useState<any>(null)
  const [messages, setMessages] = useState<any[]>([])
  const [inputValue, setInputValue] = useState('')
  const [typingUsers, setTypingUsers] = useState<Set<string>>(new Set())
  const [onlineUsers, setOnlineUsers] = useState<Set<string>>(new Set())
  const [connected, setConnected] = useState(false)

  const ws = useRef<WebSocket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const typingTimeout = useRef<NodeJS.Timeout | null>(null)
  const retryCount = useRef(0)
  const retryTimer = useRef<NodeJS.Timeout | null>(null)
  const intentionalClose = useRef(false)

  const connectWsRef = useRef<((roomId: string) => void) | null>(null)

  const connectWs = useCallback((roomId: string) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) return

    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
    const socket = new WebSocket(`${wsUrl}/api/v1/ws/rooms/${roomId}`)

    socket.onopen = () => {
      setConnected(true)
      retryCount.current = 0  // Reset backoff on successful connect
    }

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)

        switch (data.type) {
          case 'message.created':
            setMessages(prev => [...prev, data.payload])
            break
          case 'presence.updated':
            setOnlineUsers(prev => {
              const next = new Set(prev)
              if (data.payload.status === 'online') next.add(data.payload.user_id)
              else next.delete(data.payload.user_id)
              return next
            })
            break
          case 'typing.started':
            if (data.payload.user_id !== currentUser?.id) {
              setTypingUsers(prev => {
                const next = new Set(prev)
                next.add(data.payload.name || data.payload.user_id)
                return next
              })
            }
            break
          case 'typing.stopped':
            if (data.payload.user_id !== currentUser?.id) {
              setTypingUsers(prev => {
                const next = new Set(prev)
                next.delete(data.payload.name || data.payload.user_id)
                return next
              })
            }
            break
        }
      } catch {
        // Ignore malformed messages
      }
    }

    socket.onclose = (event) => {
      setConnected(false)

      if (intentionalClose.current) return  // User navigated away — don't reconnect

      if (retryCount.current >= WS_MAX_RETRIES) {
        if (process.env.NODE_ENV === 'development') {
          console.warn(`[RoomChat] Max WS retries (${WS_MAX_RETRIES}) reached. Giving up.`)
        }
        return
      }

      // Exponential backoff with jitter: 2^n * baseDelay ± 20% jitter
      const delay = Math.min(
        WS_BASE_DELAY_MS * Math.pow(2, retryCount.current),
        120_000  // Cap at 2 minutes
      ) * (0.8 + Math.random() * 0.4)  // ±20% jitter

      retryCount.current += 1
      retryTimer.current = setTimeout(() => {
        if (connectWsRef.current) connectWsRef.current(roomId)
      }, delay)
    }

    socket.onerror = () => {
      // onclose will fire after onerror — backoff handled there
      setConnected(false)
    }

    ws.current = socket
  }, [currentUser])

  useEffect(() => {
    connectWsRef.current = connectWs
  }, [connectWs])

  useEffect(() => {
    api.get(`/problems/${publicId}/room`).then(res => {
      const r = res.data
      setRoom(r)
      api.get(`/rooms/${r.id}/messages`).then(mRes => {
        setMessages(mRes.data)
      })
      connectWs(r.id)
    }).catch(err => {
      if (process.env.NODE_ENV === 'development') console.error('[RoomChat]', err)
    })

    return () => {
      intentionalClose.current = true
      if (retryTimer.current) clearTimeout(retryTimer.current)
      if (ws.current) ws.current.close()
    }
  }, [publicId, connectWs])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])


  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value)
    
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type: 'typing.started' }))
      
      if (typingTimeout.current) clearTimeout(typingTimeout.current)
      
      typingTimeout.current = setTimeout(() => {
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
          ws.current.send(JSON.stringify({ type: 'typing.stopped' }))
        }
      }, 2000)
    }
  }

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputValue.trim() || !room) return
    
    // We send message via REST to ensure persistence
    try {
      const val = inputValue
      setInputValue('')
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
         ws.current.send(JSON.stringify({ type: 'typing.stopped' }))
      }
      // Note: backend broadcasts via WS upon creation
      await api.post(`/rooms/${room.id}/messages`, { content: val })
    } catch (err) {
      console.error(err)
    }
  }

  if (!room) return <div className="flex justify-center p-4"><Loader2 className="animate-spin text-primary" /></div>

  return (
    <Card className="flex flex-col h-full border-0 shadow-none sm:border sm:shadow-sm">
      <CardHeader className="border-b py-3">
        <CardTitle className="text-lg flex items-center justify-between">
          <span>Problem Room</span>
          <div className="flex items-center space-x-2 text-sm font-normal">
            <span className={`w-2.5 h-2.5 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-muted-foreground">{onlineUsers.size} Online</span>
          </div>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="flex-1 overflow-y-auto p-4 space-y-4 bg-muted/20">
        {messages.length === 0 ? (
          <div className="text-center text-muted-foreground text-sm mt-4">
            Welcome to the problem room. Be the first to say hi!
          </div>
        ) : (
          messages.map(msg => {
            const isMe = msg.author_id === currentUser?.id
            return (
              <div key={msg.id} className={`flex flex-col ${isMe ? 'items-end' : 'items-start'}`}>
                <div className={`px-3 py-2 rounded-lg max-w-[80%] ${isMe ? 'bg-primary text-primary-foreground' : 'bg-white border text-foreground'}`}>
                  {!isMe && <div className="text-xs font-bold mb-1 opacity-75">{msg.author_email || 'User'}</div>}
                  <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
                </div>
              </div>
            )
          })
        )}
        <div ref={messagesEndRef} />
      </CardContent>
      
      <CardFooter className="border-t p-3 flex-col items-start gap-2">
        {typingUsers.size > 0 && (
          <div className="text-xs text-muted-foreground italic h-4">
            {Array.from(typingUsers).join(', ')} {typingUsers.size > 1 ? 'are' : 'is'} typing...
          </div>
        )}
        <form onSubmit={handleSendMessage} className="flex w-full space-x-2">
          <Input 
            value={inputValue} 
            onChange={handleInputChange} 
            placeholder="Type a message..." 
            className="flex-1"
            disabled={!connected}
          />
          <Button type="submit" disabled={!connected || !inputValue.trim()}>Send</Button>
        </form>
      </CardFooter>
    </Card>
  )
}

