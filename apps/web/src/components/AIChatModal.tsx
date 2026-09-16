'use client'

import { useState } from 'react'
import { api } from '@/lib/api'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Bot, Send, User, Code, Wrench, Search, Calculator, GraduationCap, CheckCircle2, ChevronDown, ChevronUp } from 'lucide-react'

interface AIChatModalProps {
  problemContext: string;
}

interface MessageItem {
  role: 'user' | 'ai';
  content: string;
  agent_role?: string;
  activity_steps?: Array<{ step: string; description: string; data?: any }>;
}

export function AIChatModal({ problemContext }: AIChatModalProps) {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<MessageItem[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [selectedAgent, setSelectedAgent] = useState<string>('auto')
  const [expandedSteps, setExpandedSteps] = useState<{ [key: number]: boolean }>({})

  const toggleStep = (idx: number) => {
    setExpandedSteps(prev => ({ ...prev, [idx]: !prev[idx] }))
  }

  const handleSend = async (actionType: string = 'chat', overrideMessage?: string, agentOverride?: string) => {
    const text = overrideMessage || input
    if (!text.trim() && actionType === 'chat') return

    const newMsgs: MessageItem[] = [...messages]
    if (text) {
      newMsgs.push({ role: 'user', content: text })
    }
    setMessages(newMsgs)
    setInput('')
    setLoading(true)

    const targetAgent = agentOverride || selectedAgent

    try {
      const res = await api.post('/ai/chat', {
        message: text,
        problem_context: problemContext,
        action_type: actionType,
        agent_type: targetAgent
      })
      setMessages([
        ...newMsgs,
        {
          role: 'ai',
          content: res.data.response,
          agent_role: res.data.agent_role,
          activity_steps: res.data.activity_steps
        }
      ])
    } catch (err: any) {
      setMessages([
        ...newMsgs,
        {
          role: 'ai',
          content: `Error: ${err.response?.data?.detail || 'Failed to connect to AI engine.'}`
        }
      ])
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
        <DialogContent className="sm:max-w-[600px] h-[680px] flex flex-col">
          <DialogHeader className="pb-2 border-b">
            <DialogTitle className="flex items-center justify-between">
              <span className="flex items-center gap-2"><Bot className="h-5 w-5 text-primary" /> SolveNow Multi-Agent Assistant</span>
            </DialogTitle>
          </DialogHeader>

          {/* Specialized Agent Chips */}
          <div className="flex items-center gap-1.5 overflow-x-auto py-2 border-b text-xs">
            <span className="text-muted-foreground font-medium pl-1 mr-1">Agent:</span>
            {[
              { id: 'auto', label: 'Auto (Orchestrator)', icon: Bot },
              { id: 'coding', label: 'Coding', icon: Code },
              { id: 'debugging', label: 'Debugger', icon: Wrench },
              { id: 'research', label: 'Research', icon: Search },
              { id: 'math', label: 'Math', icon: Calculator },
              { id: 'tutor', label: 'Tutor', icon: GraduationCap },
              { id: 'verifier', label: 'Verifier', icon: CheckCircle2 },
            ].map(agent => {
              const Icon = agent.icon
              const isSelected = selectedAgent === agent.id
              return (
                <button
                  key={agent.id}
                  onClick={() => setSelectedAgent(agent.id)}
                  className={`flex items-center gap-1 px-2.5 py-1 rounded-full whitespace-nowrap transition-colors ${
                    isSelected ? 'bg-primary text-primary-foreground font-semibold shadow-xs' : 'bg-muted hover:bg-muted/80 text-muted-foreground'
                  }`}
                >
                  <Icon className="h-3 w-3" />
                  {agent.label}
                </button>
              )
            })}
          </div>
          
          {/* Quick Actions */}
          <div className="flex flex-wrap gap-2 py-2 border-b">
            <Button variant="secondary" size="sm" className="h-7 text-xs" onClick={() => handleSend('hint', 'Please give me a hint.', 'tutor')} disabled={loading}>Hint</Button>
            <Button variant="secondary" size="sm" className="h-7 text-xs" onClick={() => handleSend('explain', 'Please explain this problem in detail.', 'tutor')} disabled={loading}>Explain</Button>
            <Button variant="secondary" size="sm" className="h-7 text-xs" onClick={() => handleSend('debug', 'Can you help diagnose and debug the error?', 'debugging')} disabled={loading}>Debug</Button>
            <Button variant="secondary" size="sm" className="h-7 text-xs" onClick={() => handleSend('review', 'Please audit and review this solution.', 'verifier')} disabled={loading}>Review</Button>
          </div>

          <div className="flex-1 p-4 bg-muted/30 rounded-md my-2 overflow-y-auto space-y-4">
            {messages.length === 0 ? (
              <div className="text-center text-muted-foreground text-sm mt-12 space-y-2">
                <Bot className="h-10 w-10 mx-auto text-primary/40 mb-3" />
                <p className="font-semibold text-foreground">SolveNow Multi-Agent Orchestrator Ready</p>
                <p className="text-xs max-w-sm mx-auto">
                  Ask a question or select a specialized agent above. Code execution, research search, and solution verification are active.
                </p>
              </div>
            ) : (
              messages.map((m, i) => (
                <div key={i} className={`flex flex-col gap-1 ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
                  {m.role === 'ai' && m.agent_role && (
                    <span className="text-[10px] font-semibold text-primary px-2 py-0.5 rounded bg-primary/10 mb-1">
                      {m.agent_role}
                    </span>
                  )}
                  
                  {/* Activity Trace Accordion */}
                  {m.activity_steps && m.activity_steps.length > 0 && (
                    <div className="w-full max-w-[85%] mb-2 bg-background border rounded-lg p-2 text-xs">
                      <button
                        onClick={() => toggleStep(i)}
                        className="flex items-center justify-between w-full font-medium text-muted-foreground hover:text-foreground"
                      >
                        <span className="flex items-center gap-1.5 text-primary">
                          <CheckCircle2 className="h-3.5 w-3.5 text-green-500" />
                          AI Activity Trace ({m.activity_steps.length} steps)
                        </span>
                        {expandedSteps[i] ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
                      </button>
                      
                      {expandedSteps[i] && (
                        <div className="mt-2 pt-2 border-t space-y-1.5">
                          {m.activity_steps.map((step, sIdx) => (
                            <div key={sIdx} className="flex items-start gap-1.5 text-[11px]">
                              <span className="text-muted-foreground font-mono">[{step.step}]</span>
                              <span className="text-foreground">{step.description}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  <div className={`flex gap-2 max-w-[85%] ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    {m.role === 'ai' && <div className="h-7 w-7 rounded-full bg-primary/10 flex items-center justify-center shrink-0 mt-0.5"><Bot className="h-4 w-4 text-primary" /></div>}
                    <div className={`p-3 rounded-xl text-sm ${m.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-background border shadow-xs'}`}>
                      <div className="whitespace-pre-wrap leading-relaxed">{m.content}</div>
                    </div>
                    {m.role === 'user' && <div className="h-7 w-7 rounded-full bg-muted flex items-center justify-center shrink-0 mt-0.5"><User className="h-4 w-4" /></div>}
                  </div>
                </div>
              ))
            )}
            {loading && (
              <div className="flex gap-2 items-center text-muted-foreground text-xs p-2 bg-muted/40 rounded-lg animate-pulse w-fit">
                <Bot className="h-4 w-4 text-primary animate-spin" />
                <span>Orchestrating agents and executing tools...</span>
              </div>
            )}
          </div>

          <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="flex gap-2 pt-2">
            <Input 
              value={input} 
              onChange={e => setInput(e.target.value)} 
              placeholder={`Ask ${selectedAgent === 'auto' ? 'AI assistant' : selectedAgent + ' agent'}...`}
              disabled={loading}
              className="text-sm"
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
