import { Routes, Route, Navigate } from 'react-router-dom'
import { useState } from 'react'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'

export default function App() {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('vaultrag_user')) } catch { return null }
  })

  const handleLogin = (userData) => {
    localStorage.setItem('vaultrag_user', JSON.stringify(userData))
    setUser(userData)
  }

  const handleLogout = () => {
    localStorage.removeItem('vaultrag_user')
    setUser(null)
  }

  return (
    <Routes>
      <Route path="/login" element={
        user ? <Navigate to="/dashboard" replace /> : <Login onLogin={handleLogin} />
      } />
      <Route path="/dashboard/*" element={
        user ? <Dashboard user={user} onLogout={handleLogout} /> : <Navigate to="/login" replace />
      } />
      <Route path="*" element={<Navigate to={user ? "/dashboard" : "/login"} replace />} />
    </Routes>
  )
}
