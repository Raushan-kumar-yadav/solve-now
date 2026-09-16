'use client'

import { useState } from 'react'
import { api } from '@/lib/api'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Bot, Send, User } from 'lucide-react'

interface AIChatModalProps {
  problemContext: string;
}

export function AIChatModal({ problemContext }: AIChatModalProps) {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<{role: 'user' | 'ai', content: string}[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSend = async (actionType: string = 'chat', overrideMessage?: string) => {
    const text = overrideMessage || input
    if (!text.trim() && actionType === 'chat') return

    const newMsgs = [...messages]
    if (text) {
      newMsgs.push({ role: 'user', content: text })
    }
    setMessages(newMsgs)
    setInput('')
    setLoading(true)

    try {
      const res = await api.post('/ai/chat', {
        message: text,
        problem_context: problemContext,
        action_type: actionType
      })
      setMessages([...newMsgs, { role: 'ai', content: res.data.response }])
    } catch (err: any) {
      setMessages([...newMsgs, { role: 'ai', content: `Error: ${err.response?.data?.detail || 'Failed to connect to AI provider.'}` }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Button variant="outline" onClick={() => setOpen(true)} className="gap-2 bg-primary/5 hover:bg-primary/10 border-primary/20">
        <Bot className="h-4 w-4" /> Ask AI
      </Button>
      
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="sm:max-w-[500px] h-[600px] flex flex-col">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2"><Bot className="h-5 w-5 text-primary" /> SolveNow AI Assistant</DialogTitle>
          </DialogHeader>
          
          <div className="flex flex-wrap gap-2 py-2 border-b">
            <Button variant="secondary" size="sm" onClick={() => handleSend('hint', 'Please give me a hint.')} disabled={loading}>Hint</Button>
            <Button variant="secondary" size="sm" onClick={() => handleSend('explain', 'Please explain this problem.')} disabled={loading}>Explain</Button>
            <Button variant="secondary" size="sm" onClick={() => handleSend('debug', 'Can you help me debug?')} disabled={loading}>Debug</Button>
            <Button variant="secondary" size="sm" onClick={() => handleSend('review', 'Please review my approach.')} disabled={loading}>Review</Button>
          </div>

          <div className="flex-1 p-4 bg-muted/30 rounded-md my-2 overflow-y-auto">
            {messages.length === 0 ? (
              <div className="text-center text-muted-foreground text-sm mt-10">
                Ask a question or select an action above. Context from this problem will automatically be included.
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((m, i) => (
                  <div key={i} className={`flex gap-3 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    {m.role === 'ai' && <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0"><Bot className="h-4 w-4 text-primary" /></div>}
                    <div className={`p-3 rounded-lg max-w-[80%] text-sm ${m.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-background border'}`}>
                      <div className="whitespace-pre-wrap">{m.content}</div>
                    </div>
                    {m.role === 'user' && <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center shrink-0"><User className="h-4 w-4" /></div>}
                  </div>
                ))}
                {loading && (
                  <div className="flex gap-3 justify-start">
                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0"><Bot className="h-4 w-4 text-primary" /></div>
                    <div className="p-3 rounded-lg bg-background border text-sm text-muted-foreground animate-pulse">Thinking...</div>
                  </div>
                )}
              </div>
            )}
          </div>

          <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="flex gap-2 pt-2">
            <Input 
              value={input} 
              onChange={e => setInput(e.target.value)} 
              placeholder="Type your message..." 
              disabled={loading}
            />
            <Button type="submit" disabled={loading || !input.trim()} size="icon">
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </DialogContent>
      </Dialog>
    </>
  )
}
