import { useState } from 'react'
import { Routes, Route, NavLink, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Shield, MessageSquare, FileText, Activity, Lock, LogOut, ChevronRight, Database, Cpu } from 'lucide-react'
import ChatConsole from '../components/ChatConsole'
import DocumentsPanel from '../components/DocumentsPanel'
import AccessLogsPanel from '../components/AccessLogsPanel'
import StatsPanel from '../components/StatsPanel'

export default function Dashboard({ user, onLogout }) {
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const navItems = [
    { to: '/dashboard',          icon: Cpu,           label: 'Overview',      end: true },
    { to: '/dashboard/chat',     icon: MessageSquare, label: 'AI Console'            },
    { to: '/dashboard/sources',  icon: FileText,      label: 'Data Sources'          },
    { to: '/dashboard/logs',     icon: Activity,      label: 'Access Logs'           },
  ]

  const handleLogout = () => { onLogout(); navigate('/login') }

  return (
    <div className="dashboard-shell flex h-screen overflow-hidden bg-vault-bg">
      {/* Sidebar */}
      <motion.aside initial={{x:-20,opacity:0}} animate={{x:0,opacity:1}}
        className="dashboard-sidebar w-64 flex-shrink-0 flex flex-col border-r border-vault-border glass rounded-none">

        {/* Logo */}
        <div className="p-5 border-b border-vault-border">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center"
              style={{background:'linear-gradient(135deg,#6366f1,#9333ea)'}}>
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="font-bold text-white text-sm">VaultRAG AI</div>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="pulse-dot w-1.5 h-1.5 rounded-full bg-green-400 inline-block" />
                <span className="text-green-400 text-[10px] mono">SECURE</span>
              </div>
            </div>
          </div>
        </div>

        {/* User badge */}
        <div className="mx-4 mt-4 p-3 rounded-xl border" style={{
          borderColor: user.badge_color + '40',
          background: user.badge_color + '10'
        }}>
          <div className="flex items-center gap-2.5">
            <span className="text-2xl">{user.icon}</span>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-semibold text-white truncate">{user.name}</div>
              <div className="text-[11px] font-medium" style={{color: user.badge_color}}>
                {user.display_role || user.role}
              </div>
              <div className="text-[10px] text-slate-500 mono">{user.employee_id}</div>
            </div>
            <Lock className="w-3.5 h-3.5 flex-shrink-0" style={{color: user.badge_color}} />
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 p-4 space-y-1 mt-2">
          {navItems.map(({ to, icon: Icon, label, end }) => (
            <NavLink key={to} to={to} end={end}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all group
                ${isActive
                  ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'}`
              }>
              {({ isActive }) => (
                <>
                  <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-400' : 'text-slate-500 group-hover:text-slate-300'}`} />
                  {label}
                  {isActive && <ChevronRight className="w-3 h-3 ml-auto text-indigo-400" />}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* RBAC indicator */}
        <div className="p-4 border-t border-vault-border">
          <div className="text-[10px] text-slate-600 uppercase tracking-wider mb-2">RBAC Policy Active</div>
          <div className="text-[11px] text-slate-400 mono truncate">{user.role}</div>
          <div className="text-[10px] text-slate-600 mt-1">
            {user.allowed_sources?.length || 0} sources accessible
          </div>
        </div>

        {/* Logout */}
        <div className="p-4 border-t border-vault-border">
          <button onClick={handleLogout}
            className="flex items-center gap-2 text-slate-500 hover:text-red-400 text-sm transition-colors w-full group">
            <LogOut className="w-4 h-4 group-hover:text-red-400" />
            Sign Out
          </button>
        </div>
      </motion.aside>

      {/* Main */}
      <main className="flex-1 overflow-hidden flex flex-col">
        {/* Top bar */}
        <div className="dashboard-topbar flex items-center justify-between px-6 py-3 border-b border-vault-border bg-vault-panel/50">
          <div className="flex items-center gap-2 text-xs text-slate-500 mono">
            <Database className="w-3.5 h-3.5" />
            <span>VaultCorp Enterprise / 8 PDF / 7 CSV / 3 JSON / 1 SQL</span>
          </div>
          <div className="flex items-center gap-4 text-xs text-slate-500">
            <span className="flex items-center gap-1.5">
              <span className="pulse-dot w-1.5 h-1.5 rounded-full bg-green-400 inline-block"/>
              API Connected
            </span>
            <span className="mono text-slate-600">{new Date().toLocaleTimeString()}</span>
          </div>
        </div>

        {/* Content */}
        <div className="dashboard-content flex-1 overflow-auto p-6">
          <Routes>
            <Route index element={<StatsPanel user={user} />} />
            <Route path="chat" element={<ChatConsole user={user} />} />
            <Route path="sources" element={<DocumentsPanel user={user} />} />
            <Route path="logs" element={<AccessLogsPanel user={user} />} />
          </Routes>
        </div>
      </main>
    </div>
  )
}
