import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import { Shield, Eye, EyeOff, Lock, Zap } from 'lucide-react'
import API from '../api'

const DEMO_USERS = [
  { email: 'admin@vaultrag.ai',      password: 'admin123', role: 'Admin',             icon: 'ADM', color: '#9333ea' },
  { email: 'engineer@vaultrag.ai',   password: 'eng123',   role: 'Engineer',          icon: 'ENG', color: '#10b981' },
  { email: 'finance@vaultrag.ai',    password: 'fin123',   role: 'Finance Analyst',   icon: 'FIN', color: '#f59e0b' },
  { email: 'hr@vaultrag.ai',         password: 'hr123',    role: 'HR Manager',        icon: 'HR', color: '#0ea5e9' },
  { email: 'compliance@vaultrag.ai', password: 'comp123',  role: 'Compliance Officer',icon: 'GRC', color: '#ef4444' },
]

export default function Login({ onLogin }) {
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [showPwd, setShowPwd]   = useState(false)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true); setError('')
    try {
      const res = await axios.post(`${API}/login`, { email, password })
      onLogin(res.data.user)
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid credentials')
    } finally { setLoading(false) }
  }

  const quickLogin = (u) => { setEmail(u.email); setPassword(u.password) }

  return (
    <div className="min-h-screen grid-bg flex items-center justify-center p-4 relative overflow-hidden">
      {/* Animated background orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-cyan-500/8 rounded-full blur-3xl animate-pulse" style={{animationDelay:'1s'}} />

      <motion.div initial={{opacity:0,y:24}} animate={{opacity:1,y:0}} transition={{duration:0.5}}
        className="w-full max-w-md">

        {/* Logo */}
        <div className="text-center mb-8">
          <motion.div initial={{scale:0.8}} animate={{scale:1}} transition={{duration:0.4, delay:0.1}}
            className="inline-flex items-center justify-center w-20 h-20 rounded-2xl mb-4 glow-border"
            style={{background:'linear-gradient(135deg,#6366f1,#9333ea)'}}>
            <Shield className="w-10 h-10 text-white" />
          </motion.div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
            VaultRAG AI
          </h1>
          <p className="text-slate-400 text-sm mt-1">Enterprise Secure Intelligence Platform</p>
          <div className="flex items-center justify-center gap-2 mt-2">
            <span className="pulse-dot w-2 h-2 rounded-full bg-green-400 inline-block" />
            <span className="text-green-400 text-xs mono">SYSTEM ONLINE</span>
          </div>
        </div>

        {/* Login card */}
        <div className="glass p-8 glow-border">
          <div className="flex items-center gap-2 mb-6 pb-4 border-b border-vault-border">
            <Lock className="w-4 h-4 text-indigo-400" />
            <span className="text-slate-300 text-sm font-medium">ENTERPRISE SSO AUTHENTICATION</span>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1.5 uppercase tracking-wider">
                Corporate Email
              </label>
              <input type="email" value={email} onChange={e=>setEmail(e.target.value)} required
                placeholder="user@vaultrag.ai"
                className="w-full bg-vault-bg border border-vault-border rounded-lg px-4 py-2.5 text-slate-200 text-sm placeholder-slate-600 transition-all" />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1.5 uppercase tracking-wider">
                Password
              </label>
              <div className="relative">
                <input type={showPwd ? 'text' : 'password'} value={password} onChange={e=>setPassword(e.target.value)} required
                  placeholder="Password"
                  className="w-full bg-vault-bg border border-vault-border rounded-lg px-4 py-2.5 text-slate-200 text-sm placeholder-slate-600 transition-all" />
                <button type="button" onClick={()=>setShowPwd(!showPwd)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300">
                  {showPwd ? <EyeOff className="w-4 h-4"/> : <Eye className="w-4 h-4"/>}
                </button>
              </div>
            </div>

            <AnimatePresence>
              {error && (
                <motion.div initial={{opacity:0,height:0}} animate={{opacity:1,height:'auto'}} exit={{opacity:0,height:0}}
                  className="bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-2.5 text-red-400 text-sm flex items-center gap-2">
                  <span>!</span> {error}
                </motion.div>
              )}
            </AnimatePresence>

            <motion.button type="submit" disabled={loading} whileHover={{scale:1.02}} whileTap={{scale:0.98}}
              className="w-full py-3 rounded-lg font-semibold text-white text-sm transition-all disabled:opacity-50"
              style={{background:'linear-gradient(135deg,#6366f1,#9333ea)'}}>
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"/>
                  Authenticating...
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  <Zap className="w-4 h-4"/> Secure Login
                </span>
              )}
            </motion.button>
          </form>
        </div>

        {/* Quick login demo cards */}
        <div className="mt-6">
          <p className="text-center text-xs text-slate-500 mb-3 uppercase tracking-wider">Demo Accounts</p>
          <div className="grid grid-cols-5 gap-2">
            {DEMO_USERS.map(u => (
              <motion.button key={u.email} whileHover={{scale:1.05,y:-2}} whileTap={{scale:0.95}}
                onClick={() => quickLogin(u)}
                className="glass p-2 text-center rounded-lg cursor-pointer transition-all hover:border-indigo-500/40"
                title={`${u.role}\n${u.email}`}>
                <div className="text-xl mb-1">{u.icon}</div>
                <div className="text-[10px] text-slate-400 leading-tight">{u.role.split(' ')[0]}</div>
              </motion.button>
            ))}
          </div>
          <p className="text-center text-[11px] text-slate-600 mt-2">Click to auto-fill credentials</p>
        </div>
      </motion.div>
    </div>
  )
}
