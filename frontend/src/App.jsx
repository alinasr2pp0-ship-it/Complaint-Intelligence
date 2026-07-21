import React, { useEffect, useRef, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function StampBadge({ ready }) {
  return (
    <div
      className={`inline-flex items-center gap-2 border-2 rounded-sm px-2.5 py-1 rotate-[-2deg] font-mono text-[11px] tracking-widest uppercase
        ${ready ? 'border-teal text-teal' : 'border-stamp text-stamp'}`}
      style={{ opacity: 0.85 }}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${ready ? 'bg-teal' : 'bg-stamp'}`} />
      {ready ? 'Index Ready' : 'Index Offline'}
    </div>
  )
}

function ExhibitCard({ index, source }) {
  return (
    <div className="border border-line bg-[#F7F4EC] rounded-sm p-3 relative">
      <div className="absolute -top-2.5 left-3 bg-[#F7F4EC] px-1.5 font-mono text-[10px] tracking-widest text-teal-dark uppercase">
        Exhibit {String(index + 1).padStart(2, '0')}
      </div>
      <div className="flex items-baseline justify-between mb-1.5 pt-1">
        <span className="font-display font-semibold text-ink text-sm">{source.company}</span>
        <span className="font-mono text-[11px] text-ink/50">#{source.complaint_id}</span>
      </div>
      <p className="text-[13px] leading-relaxed text-ink/75 font-body">{source.snippet}</p>
    </div>
  )
}

function Message({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[72ch] ${isUser ? '' : 'w-full'}`}>
        {!isUser && (
          <div className="font-mono text-[10px] tracking-widest uppercase text-teal-dark mb-1.5">
            Analyst Response
          </div>
        )}
        <div
          className={`px-4 py-3 rounded-sm border font-body text-[14.5px] leading-relaxed whitespace-pre-wrap
            ${isUser
              ? 'bg-ink text-paper border-ink'
              : 'bg-[#F7F4EC] text-ink border-line'}`}
        >
          {msg.content}
        </div>
        {msg.sources && msg.sources.length > 0 && (
          <div className="mt-3 grid gap-2.5 sm:grid-cols-2">
            {msg.sources.map((s, i) => (
              <ExhibitCard key={i} index={i} source={s} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default function App() {
  const [health, setHealth] = useState(null)
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content:
        "This is the Complaint Intelligence desk. Ask about any pattern in the consumer-complaints file — a company, an issue type, or a specific case — and I'll pull the relevant records before answering.",
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const scrollRef = useRef(null)

  useEffect(() => {
    fetch(`${API_BASE}/api/v1/health`)
      .then((r) => r.json())
      .then(setHealth)
      .catch(() => setHealth({ status: 'unreachable', vector_store_ready: false }))
  }, [])

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, loading])

  async function submitQuestion(e) {
    e.preventDefault()
    const question = input.trim()
    if (!question || loading) return

    setMessages((m) => [...m, { role: 'user', content: question }])
    setInput('')
    setLoading(true)
    setError(null)

    try {
      const res = await fetch(`${API_BASE}/api/v1/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      })
      if (!res.ok) throw new Error(`Request failed (${res.status})`)
      const data = await res.json()
      setMessages((m) => [...m, { role: 'assistant', content: data.answer, sources: data.sources }])
    } catch (err) {
      setError(err.message || 'Something went wrong reaching the API.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b-2 border-ink/80 bg-paper/60 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <div className="font-mono text-[10px] tracking-[0.25em] text-teal-dark uppercase mb-1">
              Case File · Consumer Complaints
            </div>
            <h1 className="font-display text-2xl font-semibold text-ink tracking-tight">
              Complaint Intelligence
            </h1>
          </div>
          {health && <StampBadge ready={health.vector_store_ready} />}
        </div>
      </header>

      {/* Chat surface */}
      <main className="flex-1 max-w-5xl w-full mx-auto px-6 py-8 flex flex-col">
        <div
          ref={scrollRef}
          className="flex-1 overflow-y-auto scrollbar-thin space-y-6 pb-6"
          style={{ maxHeight: 'calc(100vh - 230px)' }}
        >
          {messages.map((msg, i) => (
            <Message key={i} msg={msg} />
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="px-4 py-3 rounded-sm border border-line bg-[#F7F4EC] font-mono text-[12px] text-ink/50 tracking-wide">
                Pulling records…
              </div>
            </div>
          )}
        </div>

        {error && (
          <div className="mb-3 px-3 py-2 border border-stamp/50 bg-stamp/5 text-stamp text-[13px] font-mono rounded-sm">
            {error}
          </div>
        )}

        {/* Composer */}
        <form onSubmit={submitQuestion} className="border-t-2 border-line pt-4">
          <div className="flex items-end gap-3">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  submitQuestion(e)
                }
              }}
              placeholder="e.g. What do complaints against Wells Fargo about credit card reporting usually involve?"
              rows={2}
              className="flex-1 resize-none bg-[#F7F4EC] border border-line rounded-sm px-3.5 py-2.5 font-body text-[14px] text-ink placeholder:text-ink/35 focus:outline-none focus:ring-2 focus:ring-teal/40 focus:border-teal"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="font-mono text-[12px] tracking-widest uppercase bg-ink text-paper px-4 py-2.5 rounded-sm hover:bg-teal-dark transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            >
              File
            </button>
          </div>
          <div className="mt-2 font-mono text-[10px] text-ink/35 tracking-wide">
            Enter to send · Shift+Enter for a new line · {API_BASE.replace(/^https?:\/\//, '')}
          </div>
        </form>
      </main>
    </div>
  )
}
