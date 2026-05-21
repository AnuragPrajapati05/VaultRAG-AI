import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import { Send, Zap, Shield, AlertTriangle, ChevronDown, ChevronUp, FileText, Database, Activity } from 'lucide-react'
import API from '../api'

const DEMO_QUERIES = [
  'Why did payroll processing fail last Friday?',
  'Show security anomalies from engineering logs.',
  'Summarize GDPR compliance policies.',
  'List unresolved enterprise incidents.',
  'What is the current engineering budget status?',
]

function ConfidenceMeter({ value }) {
  const color = value >= 80 ? '#10b981' : value >= 60 ? '#f59e0b' : '#ef4444'
  const label = value >= 80 ? 'HIGH' : value >= 60 ? 'MEDIUM' : 'LOW'
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 bg-vault-bg rounded-full h-2 overflow-hidden">
        <motion.div initial={{width:0}} animate={{width:`${value}%`}} transition={{duration:1,delay:0.3}}
          className="h-full rounded-full" style={{background:`linear-gradient(90deg,#6366f1,${color})`}} />
      </div>
      <span className="mono text-sm font-bold" style={{color}}>{value}%</span>
      <span className="badge text-[10px]" style={{background:color+'15',color,border:`1px solid ${color}30`}}>{label}</span>
    </div>
  )
}

function SourceTag({ source }) {
  const ext = source.includes('.pdf') ? 'PDF' : source.includes('.csv') ? 'CSV'
    : source.includes('.json') ? 'JSON' : source.includes('.db') ? 'DB' : 'SRC'
  return <span className="source-tag">{ext} {source}</span>
}

function RetrievalTrace({ trace, routing }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="mt-3 border border-vault-border rounded-xl overflow-hidden">
      <button onClick={()=>setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-2.5 bg-vault-panel/50 text-xs text-slate-400 hover:text-slate-200 transition-colors">
        <span className="flex items-center gap-2">
          <Activity className="w-3.5 h-3.5 text-indigo-400"/>
          RETRIEVAL TRACE - {trace.length} sources queried
        </span>
        {open ? <ChevronUp className="w-3.5 h-3.5"/> : <ChevronDown className="w-3.5 h-3.5"/>}
      </button>
      <AnimatePresence>
        {open && (
          <motion.div initial={{height:0,opacity:0}} animate={{height:'auto',opacity:1}} exit={{height:0,opacity:0}}
            className="overflow-hidden">
            <div className="p-3 space-y-2 bg-vault-bg/50">
              {/* Routing info */}
              <div className="grid grid-cols-3 gap-2 mb-3">
                <div className="glass p-2 rounded-lg">
                  <div className="text-[10px] text-slate-500 mb-0.5">INTENTS</div>
                  <div className="text-xs text-indigo-300">{routing?.intents?.join(', ') || '-'}</div>
                </div>
                <div className="glass p-2 rounded-lg">
                  <div className="text-[10px] text-slate-500 mb-0.5">DEPARTMENT</div>
                  <div className="text-xs text-cyan-300">{routing?.department || '-'}</div>
                </div>
                <div className="glass p-2 rounded-lg">
                  <div className="text-[10px] text-slate-500 mb-0.5">POLICY</div>
                  <div className="text-xs text-purple-300 truncate">{routing?.policy_applied || '-'}</div>
                </div>
              </div>
              {/* Source chunks */}
              {trace.map((t, i) => (
                <div key={i} className="flex items-start gap-3 p-2.5 rounded-lg bg-vault-card border border-vault-border/50">
                  <div className="flex-shrink-0 w-6 h-6 rounded flex items-center justify-center text-xs"
                    style={{background:'rgba(99,102,241,0.15)'}}>
                    {t.type === 'pdf' ? 'PDF' : t.type === 'csv' ? 'CSV' : t.type === 'json' ? '{}' : 'DB'}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-medium text-slate-300 mono truncate">{t.source}</span>
                      <span className="text-[10px] text-slate-500 ml-2">score: {t.score?.toFixed(3)}</span>
                    </div>
                    <div className="text-[11px] text-slate-500 leading-relaxed line-clamp-2">{t.snippet}</div>
                  </div>
                </div>
              ))}
              {routing?.denied_sources?.length > 0 && (
                <div className="flex items-center gap-2 p-2 rounded-lg bg-red-500/5 border border-red-500/20">
                  <AlertTriangle className="w-3 h-3 text-red-400 flex-shrink-0" />
                  <span className="text-[11px] text-red-400">
                    Denied by RBAC: {routing.denied_sources.join(', ')}
                  </span>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

function Message({ msg }) {
  if (msg.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="max-w-lg bg-indigo-600/20 border border-indigo-500/30 rounded-2xl rounded-tr-sm px-4 py-3 text-sm text-slate-200">
          {msg.content}
        </div>
      </div>
    )
  }

  const data = msg.data
  if (!data) return null

  if (data.access_denied) {
    return (
      <motion.div initial={{opacity:0,scale:0.97}} animate={{opacity:1,scale:1}}
        className="access-denied border-2 border-red-500/50 rounded-2xl overflow-hidden"
        style={{background:'rgba(239,68,68,0.05)'}}>
        <div className="flex items-center gap-3 px-5 py-4 bg-red-500/10 border-b border-red-500/30">
          <AlertTriangle className="w-5 h-5 text-red-400" />
          <span className="text-red-300 font-bold text-sm tracking-wide">ACCESS DENIED</span>
          <span className="ml-auto badge" style={{background:'#ef444415',color:'#ef4444',border:'1px solid #ef444430'}}>
            RBAC ENFORCED
          </span>
        </div>
        <div className="px-5 py-4">
          <p className="text-red-300 text-sm font-medium mb-2">
            Insufficient privileges under enterprise RBAC policy.
          </p>
          <p className="text-slate-500 text-xs">Policy: {data.policy_applied}</p>
          {data.denied_sources?.length > 0 && (
            <div className="mt-2 text-xs text-red-400/70 mono">
              Restricted sources: {data.denied_sources.join(', ')}
            </div>
          )}
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div initial={{opacity:0,y:8}} animate={{opacity:1,y:0}}
      className="glass border border-vault-border rounded-2xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-3 px-5 py-3 border-b border-vault-border bg-vault-panel/50">
        <div className="w-6 h-6 rounded-lg flex items-center justify-center"
          style={{background:'linear-gradient(135deg,#6366f1,#9333ea)'}}>
          <Zap className="w-3.5 h-3.5 text-white"/>
        </div>
        <span className="text-slate-300 text-xs font-semibold tracking-wider">AI RESPONSE</span>
        <span className="ml-auto text-[11px] text-slate-600 mono">{data.elapsed_ms}ms / {data.model}</span>
      </div>

      {/* Answer */}
      <div className="px-5 py-4">
        <div className="text-sm text-slate-200 leading-relaxed whitespace-pre-wrap">{data.answer}</div>
      </div>

      {/* Confidence */}
      <div className="px-5 pb-4">
        <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-2">Confidence Score</div>
        <ConfidenceMeter value={data.confidence} />
      </div>

      {/* Citations */}
      {data.citations?.length > 0 && (
        <div className="px-5 pb-4">
          <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-2">Sources Used</div>
          <div className="flex flex-wrap gap-1.5">
            {data.citations.map((c,i) => <SourceTag key={i} source={c} />)}
          </div>
        </div>
      )}

      {/* Policy badge */}
      <div className="px-5 pb-4">
        <span className="badge text-[10px]" style={{background:'rgba(99,102,241,0.1)',color:'#818cf8',border:'1px solid rgba(99,102,241,0.2)'}}>
          <Shield className="w-3 h-3"/> {data.policy_applied}
        </span>
      </div>

      {/* Trace */}
      {data.retrieval_trace?.length > 0 && (
        <div className="px-5 pb-5">
          <RetrievalTrace trace={data.retrieval_trace} routing={data.routing} />
        </div>
      )}
    </motion.div>
  )
}

export default function ChatConsole({ user }) {
  const [messages, setMessages] = useState([])
  const [input, setInput]       = useState('')
  const [loading, setLoading]   = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => { bottomRef.current?.scrollIntoView({behavior:'smooth'}) }, [messages])

  const send = async (q = input) => {
    if (!q.trim() || loading) return
    const query = q.trim()
    setInput('')
    setMessages(prev => [...prev, {role:'user', content:query}])
    setLoading(true)

    try {
      const res = await axios.post(`${API}/query`, {
        query, email: user.email, role: user.role
      })
      setMessages(prev => [...prev, {role:'assistant', data: res.data}])
    } catch(err) {
      setMessages(prev => [...prev, {role:'assistant', data:{
        access_denied:false, answer:`Error: ${err.message}. Ensure the backend is running.`,
        confidence:0, citations:[], retrieval_trace:[], elapsed_ms:0, model:'-',
        policy_applied: user.role, routing:{}
      }}])
    } finally { setLoading(false) }
  }

  return (
    <div className="h-full flex gap-4 page-enter">
      {/* Chat area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold text-white">AI Intelligence Console</h2>
            <p className="text-xs text-slate-500">Multi-source RAG with RBAC enforcement</p>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg glass text-xs mono"
            style={{color: user.badge_color}}>
            {user.icon} {user.display_role || user.role}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 pr-1 min-h-0">
          {messages.length === 0 && (
            <motion.div initial={{opacity:0}} animate={{opacity:1}} className="text-center py-12">
              <div className="w-16 h-16 mx-auto rounded-2xl flex items-center justify-center mb-4"
                style={{background:'linear-gradient(135deg,rgba(99,102,241,0.15),rgba(147,51,234,0.15))'}}>
                <Database className="w-8 h-8 text-indigo-400"/>
              </div>
              <p className="text-slate-400 mb-1">Ask anything about enterprise data</p>
              <p className="text-slate-600 text-xs">RBAC policies are enforced on every query</p>
            </motion.div>
          )}
          {messages.map((m, i) => <Message key={i} msg={m} />)}
          {loading && (
            <motion.div initial={{opacity:0}} animate={{opacity:1}}
              className="glass border border-vault-border rounded-2xl p-4 flex items-center gap-3">
              <div className="flex gap-1.5">
                {[0,1,2].map(i => (
                  <motion.div key={i} className="w-2 h-2 rounded-full bg-indigo-400"
                    animate={{scale:[1,1.4,1],opacity:[0.5,1,0.5]}}
                    transition={{duration:1,delay:i*0.15,repeat:Infinity}} />
                ))}
              </div>
              <span className="text-slate-400 text-sm">Retrieving from enterprise sources...</span>
            </motion.div>
          )}
          <div ref={bottomRef}/>
        </div>

        {/* Input */}
        <div className="mt-4">
          <div className="glass border border-vault-border rounded-xl overflow-hidden">
            <textarea value={input} onChange={e=>setInput(e.target.value)}
              onKeyDown={e=>{ if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send()} }}
              placeholder="Ask about payroll failures, security anomalies, compliance policies..."
              rows={2}
              className="w-full bg-transparent px-4 pt-3 text-sm text-slate-200 placeholder-slate-600 resize-none" />
            <div className="flex items-center justify-between px-4 py-2 border-t border-vault-border">
              <span className="text-[11px] text-slate-600">Enter to send / Shift+Enter for newline</span>
              <motion.button onClick={()=>send()} disabled={!input.trim()||loading}
                whileHover={{scale:1.05}} whileTap={{scale:0.95}}
                className="flex items-center gap-2 px-4 py-1.5 rounded-lg text-sm font-medium text-white transition-all disabled:opacity-30"
                style={{background:'linear-gradient(135deg,#6366f1,#9333ea)'}}>
                <Send className="w-3.5 h-3.5"/> Send
              </motion.button>
            </div>
          </div>
        </div>
      </div>

      {/* Sidebar - Demo queries */}
      <div className="w-64 flex-shrink-0 space-y-4">
        <div className="glass border border-vault-border rounded-xl p-4">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Demo Queries</div>
          <div className="space-y-2">
            {DEMO_QUERIES.map((q,i) => (
              <motion.button key={i} onClick={()=>send(q)} disabled={loading}
                whileHover={{x:2}} whileTap={{scale:0.98}}
                className="w-full text-left text-xs text-slate-400 hover:text-slate-200 py-2 px-3 rounded-lg
                  hover:bg-indigo-500/10 border border-transparent hover:border-indigo-500/20 transition-all leading-relaxed">
                {q}
              </motion.button>
            ))}
          </div>
        </div>

        <div className="glass border border-vault-border rounded-xl p-4">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Access Policy</div>
          <div className="space-y-1.5">
            <div className="flex items-center gap-2 text-xs">
              <span className="w-2 h-2 rounded-full bg-green-400"/>
              <span className="text-slate-400">RBAC: Active</span>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <span className="w-2 h-2 rounded-full" style={{background: user.badge_color}}/>
              <span className="text-slate-400">{user.role}</span>
            </div>
            <div className="text-[11px] text-slate-600 mt-2 mono">
              {user.allowed_sources?.length || 0} sources permitted
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
