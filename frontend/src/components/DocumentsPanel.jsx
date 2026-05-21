import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import { FileText, Lock, Unlock, Filter } from 'lucide-react'
import API from '../api'

const TYPE_COLOR = { pdf:'#6366f1', csv:'#10b981', json:'#f59e0b', sql:'#06b6d4' }
const TYPE_ICON  = { pdf:'PDF', csv:'CSV', json:'{}', sql:'DB' }
const DEPT_COLOR = { HR:'#0ea5e9', Finance:'#f59e0b', Engineering:'#10b981', Compliance:'#ef4444', System:'#6366f1' }

export default function DocumentsPanel({ user }) {
  const [docs, setDocs]     = useState([])
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    axios.get(`${API}/documents`, { params: { role: user.role } })
      .then(r => setDocs(r.data.documents || []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [user.role])

  const filtered = filter === 'all' ? docs
    : filter === 'accessible' ? docs.filter(d => d.accessible)
    : docs.filter(d => d.type === filter)

  const stats = {
    total: docs.length,
    accessible: docs.filter(d => d.accessible).length,
    denied: docs.filter(d => !d.accessible).length,
  }

  return (
    <div className="page-enter">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-bold text-white">Enterprise Data Sources</h2>
          <p className="text-xs text-slate-500">Documents indexed in the knowledge base</p>
        </div>
        <div className="flex gap-2">
          {['all','accessible','pdf','csv','json'].map(f => (
            <button key={f} onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all
                ${filter === f
                  ? 'bg-indigo-600/30 text-indigo-300 border border-indigo-500/40'
                  : 'text-slate-500 hover:text-slate-300 border border-vault-border hover:border-slate-600'}`}>
              {f.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {[
          { label:'Total Sources', value: stats.total, color:'#6366f1' },
          { label:'Accessible',    value: stats.accessible, color:'#10b981' },
          { label:'RBAC Denied',   value: stats.denied, color:'#ef4444' },
        ].map((s,i) => (
          <motion.div key={i} initial={{opacity:0,y:12}} animate={{opacity:1,y:0}} transition={{delay:i*0.08}}
            className="glass border border-vault-border rounded-xl p-4">
            <div className="text-2xl font-bold" style={{color: s.color}}>{s.value}</div>
            <div className="text-xs text-slate-500 mt-0.5">{s.label}</div>
          </motion.div>
        ))}
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-16 text-slate-600">Loading sources...</div>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          {filtered.map((doc, i) => (
            <motion.div key={doc.source} initial={{opacity:0,y:8}} animate={{opacity:1,y:0}} transition={{delay:i*0.04}}
              className={`glass border rounded-xl p-4 transition-all ${doc.accessible
                ? 'border-vault-border hover:border-indigo-500/30'
                : 'border-red-500/20 opacity-60'}`}>
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center text-base"
                    style={{background: (TYPE_COLOR[doc.type]||'#6366f1')+'15'}}>
                    {TYPE_ICON[doc.type]||'SRC'}
                  </div>
                  <div>
                    <div className="text-sm font-medium text-slate-200 mono">{doc.filename}</div>
                    <div className="flex items-center gap-1.5 mt-0.5">
                      <span className="badge text-[9px]" style={{
                        background: (DEPT_COLOR[doc.department]||'#6366f1')+'15',
                        color: DEPT_COLOR[doc.department]||'#6366f1',
                        border: `1px solid ${DEPT_COLOR[doc.department]||'#6366f1'}30`
                      }}>{doc.department}</span>
                      <span className="badge text-[9px]" style={{
                        background: (TYPE_COLOR[doc.type])+'15',
                        color: TYPE_COLOR[doc.type],
                        border: `1px solid ${TYPE_COLOR[doc.type]}30`
                      }}>{doc.type.toUpperCase()}</span>
                    </div>
                  </div>
                </div>
                {doc.accessible
                  ? <Unlock className="w-4 h-4 text-green-400 flex-shrink-0"/>
                  : <Lock className="w-4 h-4 text-red-400 flex-shrink-0"/>}
              </div>
              {!doc.accessible && (
                <div className="text-[11px] text-red-400 flex items-center gap-1.5 mt-1">
                  <span>!</span> Access restricted by RBAC ({user.role})
                </div>
              )}
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}
