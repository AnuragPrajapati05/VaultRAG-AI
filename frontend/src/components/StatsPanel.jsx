import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import { Shield, Database, Activity, Key, AlertTriangle, Terminal, Lock } from 'lucide-react'
import API from '../api'

export default function StatsPanel({ user }) {
  const [incidents, setIncidents] = useState([])
  const [docs, setDocs] = useState([])
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const isCompliance = user.role === 'Compliance_Officer'
  const canViewLogs = user.role === 'Admin' || isCompliance
  const canViewIncidents = user.role === 'Admin' || user.role === 'Engineer' || isCompliance

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [docsRes, logsRes, incRes] = await Promise.all([
          axios.get(`${API}/documents`, { params: { role: user.role } }),
          canViewLogs
            ? axios.get(`${API}/logs`, { params: { role: user.role } }).catch(() => ({ data: { logs: [] } }))
            : Promise.resolve({ data: { logs: [] } }),
          canViewIncidents
            ? axios.get(`${API}/incidents`, { params: { role: user.role } }).catch(() => ({ data: { incidents: [] } }))
            : Promise.resolve({ data: { incidents: [] } })
        ])
        setDocs(docsRes.data.documents || [])
        setLogs(logsRes.data.logs || [])
        setIncidents(incRes.data.incidents || [])
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [user.role, canViewLogs, canViewIncidents])

  const isHighSeverity = (severity = '') => (
    severity.startsWith('P1') || severity.startsWith('P2') ||
    severity.toLowerCase().includes('critical') ||
    severity.toLowerCase().includes('high')
  )

  const stats = {
    totalDocs: docs.length,
    accessibleDocs: docs.filter(d => d.accessible).length,
    securityLevel: user.role === 'Admin' ? 'Level 5 (Superuser)' : isCompliance ? 'Level 4 (Compliance)' : 'Level 3 (Departmental)',
    recentAlerts: incidents.filter(i => isHighSeverity(i.severity)).length
  }

  return (
    <div className="overview-page space-y-6 page-enter">
      {/* Title */}
      <div className="overview-heading">
        <h1 className="text-2xl font-extrabold text-white tracking-tight">Security Command Center</h1>
        <p className="text-xs text-slate-500 mt-1">Real-time status overview of the VaultRAG secure gateway.</p>
      </div>

      {/* Hero card */}
      <div className="dashboard-hero glass p-6 border border-indigo-500/25 relative overflow-hidden bg-gradient-to-r from-indigo-950/20 via-vault-panel/50 to-vault-panel">
        <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 rounded-full blur-2xl pointer-events-none" />
        <div className="flex items-start justify-between">
          <div className="space-y-3">
            <span className="badge text-[10px]" style={{background:'rgba(99,102,241,0.15)',color:'#818cf8',border:'1px solid rgba(99,102,241,0.3)'}}>
              Active Security Session
            </span>
            <h2 className="text-xl font-bold text-white">Welcome back, {user.name}</h2>
            <p className="text-sm text-slate-400 max-w-xl">
              You are authenticated under the <strong className="text-indigo-400">{user.display_role}</strong> role. 
              The system has filtered your current session search indexes to match authorized document classes only.
            </p>
          </div>
          <Shield className="w-12 h-12 text-indigo-400 opacity-80" />
        </div>
      </div>

      {/* Grid Stats */}
      <div className="stats-grid grid grid-cols-4 gap-4">
        {[
          { label: 'Total Enterprise Docs', value: stats.totalDocs, icon: Database, color: '#6366f1' },
          { label: 'Authorized Index Chunks', value: `${stats.accessibleDocs} / ${stats.totalDocs}`, icon: Key, color: '#10b981' },
          { label: 'Gateway Security Clearance', value: stats.securityLevel, icon: Shield, color: '#9333ea' },
          { label: 'Unresolved Incidents', value: stats.recentAlerts, icon: AlertTriangle, color: '#ef4444' }
        ].map((s, i) => (
          <motion.div key={i} initial={{opacity:0,y:12}} animate={{opacity:1,y:0}} transition={{delay:i*0.05}}
            className="stat-card glass border border-vault-border rounded-xl p-4 flex items-start justify-between">
            <div>
              <div className="text-xs text-slate-500 font-medium">{s.label}</div>
              <div className="text-lg font-bold text-slate-200 mt-2">{s.value}</div>
            </div>
            <s.icon className="w-5 h-5 opacity-70" style={{color: s.color}} />
          </motion.div>
        ))}
      </div>

      {/* Row Split: Incidents & Logs */}
      <div className="overview-panels grid grid-cols-2 gap-6">
        {/* Active Incident INC-2045 Tracker */}
        <div className="dashboard-panel glass border border-vault-border rounded-xl p-5 flex flex-col">
          <div className="flex items-center justify-between pb-3 border-b border-vault-border mb-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-red-400" />
              Active Incident Database
            </h3>
            <span className="text-[10px] text-slate-500 mono">SECURE SQL QUERY</span>
          </div>

          {loading ? (
            <div className="flex-1 flex items-center justify-center text-xs text-slate-600">Executing DB query...</div>
          ) : incidents.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center py-10 border border-dashed border-vault-border rounded-lg bg-vault-bg/30">
              <Lock className="w-8 h-8 text-red-500/40 mb-2" />
              <p className="text-xs text-slate-500">Access Restricted</p>
              <p className="text-[10px] text-slate-600 mt-0.5">Require Engineer or Compliance permissions.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {incidents.slice(0, 3).map((inc) => (
                <div key={inc.id} className="p-3 rounded-lg bg-vault-card border border-vault-border/50 hover:border-indigo-500/20 transition-all">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-bold text-indigo-400 mono">{inc.id}</span>
                    <span className={`badge text-[9px]`} style={{
                      background: isHighSeverity(inc.severity) ? 'rgba(239,68,68,0.1)' : 'rgba(245,158,11,0.1)',
                      color: isHighSeverity(inc.severity) ? '#ef4444' : '#f59e0b',
                      border: isHighSeverity(inc.severity) ? '1px solid rgba(239,68,68,0.2)' : '1px solid rgba(245,158,11,0.2)'
                    }}>{inc.severity}</span>
                  </div>
                  <div className="text-xs text-slate-300 font-medium">{inc.title}</div>
                  <div className="grid grid-cols-2 gap-2 mt-2 pt-2 border-t border-vault-border/30 text-[10px] text-slate-500">
                    <div>Status: <span className="text-slate-400 font-medium">{inc.status}</span></div>
                    <div className="text-right">Owner: <span className="text-slate-400 font-medium">{inc.reporter}</span></div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Live Security Access Log snippet */}
        <div className="dashboard-panel glass border border-vault-border rounded-xl p-5 flex flex-col">
          <div className="flex items-center justify-between pb-3 border-b border-vault-border mb-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Activity className="w-4 h-4 text-indigo-400" />
              Live Security Gate Logs
            </h3>
            <span className="text-[10px] text-slate-500 mono">SESSION LOGS</span>
          </div>

          {loading ? (
            <div className="flex-1 flex items-center justify-center text-xs text-slate-600">Retrieving security logs...</div>
          ) : !canViewLogs ? (
            <div className="flex-1 flex flex-col items-center justify-center py-10 border border-dashed border-vault-border rounded-lg bg-vault-bg/30">
              <Lock className="w-8 h-8 text-red-500/40 mb-2" />
              <p className="text-xs text-slate-500">Audit Logs Restricted</p>
              <p className="text-[10px] text-slate-600 mt-0.5">Require Compliance Officer or Admin clearance.</p>
            </div>
          ) : logs.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center text-xs text-slate-600 py-10">
              <Terminal className="w-8 h-8 text-slate-700 mb-2"/>
              No access logs recorded in this session.
            </div>
          ) : (
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {logs.slice(0, 4).map((log, i) => (
                <div key={i} className="flex items-center gap-3 p-2 rounded-lg bg-vault-card/50 border border-vault-border/30 text-[11px]">
                  <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${log.result === 'SUCCESS' ? 'bg-green-500' : 'bg-red-500'}`} />
                  <span className="text-slate-500 mono">{log.timestamp?.slice(11,19)}</span>
                  <span className="text-slate-300 font-medium truncate max-w-[80px]">{log.email?.split('@')[0]}</span>
                  <span className="text-slate-400 truncate flex-1">{log.query}</span>
                  <span className={`font-semibold text-[10px] ${log.result === 'SUCCESS' ? 'text-green-400' : 'text-red-400'}`}>{log.result}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
