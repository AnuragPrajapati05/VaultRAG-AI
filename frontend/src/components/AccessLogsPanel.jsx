import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import { Activity, RefreshCw } from 'lucide-react'
import API from '../api'

const RESULT_COLOR = { SUCCESS:'#10b981', ACCESS_DENIED:'#ef4444', ERROR:'#f59e0b' }

export default function AccessLogsPanel({ user }) {
  const [logs, setLogs]     = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError]   = useState('')

  const fetchLogs = () => {
    setLoading(true)
    axios.get(`${API}/logs`, { params: { role: user.role } })
      .then(r => { setLogs(r.data.logs || []); setError('') })
      .catch(e => setError(e.response?.data?.detail || 'Failed to load logs'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchLogs() }, [user.role])

  return (
    <div className="page-enter">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-bold text-white">Access Audit Logs</h2>
          <p className="text-xs text-slate-500">Real-time access activity for this session</p>
        </div>
        <button onClick={fetchLogs} className="flex items-center gap-2 px-3 py-1.5 rounded-lg glass text-xs text-slate-400 hover:text-slate-200 border border-vault-border transition-all">
          <RefreshCw className="w-3.5 h-3.5"/> Refresh
        </button>
      </div>

      {error ? (
        <div className="glass border border-red-500/30 rounded-xl p-6 text-center">
          <p className="text-red-400 text-sm">! {error}</p>
          <p className="text-slate-600 text-xs mt-1">Access log viewing requires Compliance Officer or Admin role</p>
        </div>
      ) : loading ? (
        <div className="flex items-center justify-center py-16 text-slate-600">Loading logs...</div>
      ) : logs.length === 0 ? (
        <div className="text-center py-16">
          <Activity className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <p className="text-slate-500">No activity logged yet.</p>
          <p className="text-slate-600 text-xs mt-1">Run some queries in the AI Console to generate logs.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {logs.map((log, i) => (
            <motion.div key={i} initial={{opacity:0,x:-8}} animate={{opacity:1,x:0}} transition={{delay:i*0.03}}
              className="glass border border-vault-border rounded-xl px-4 py-3 flex items-center gap-4">
              <div className="w-2 h-2 rounded-full flex-shrink-0"
                style={{background: RESULT_COLOR[log.result] || '#6366f1'}}/>
              <div className="flex-1 min-w-0 grid grid-cols-5 gap-2 text-xs">
                <span className="mono text-slate-500 truncate">{log.timestamp?.slice(11,19)}</span>
                <span className="text-slate-300 truncate">{log.email?.split('@')[0]}</span>
                <span className="text-indigo-300 truncate">{log.role}</span>
                <span className="text-slate-400 truncate col-span-1">{log.query}</span>
                <span className="font-medium" style={{color: RESULT_COLOR[log.result]||'#818cf8'}}>
                  {log.result}
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}
