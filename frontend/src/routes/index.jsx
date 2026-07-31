import { Routes, Route, Navigate } from 'react-router-dom'
import DashboardLayout from '@/layouts/DashboardLayout'
import ProtectedRoute from './ProtectedRoute'
import Landing from '@/pages/Landing/Landing'
import Login from '@/pages/Login/Login'
import Register from '@/pages/Register/Register'
import Dashboard from '@/pages/Dashboard/Dashboard'
import History from '@/pages/History/History'
import Settings from '@/pages/Settings/Settings'
import AdminDashboard from '@/pages/Admin/AdminDashboard'

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Authenticated user routes */}
      <Route element={<ProtectedRoute />}>
        <Route element={<DashboardLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/history" element={<History />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Route>

      {/* Admin-only routes */}
      <Route element={<ProtectedRoute allow={['admin']} />}>
        <Route element={<DashboardLayout />}>
          <Route path="/admin/dashboard" element={<AdminDashboard />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
