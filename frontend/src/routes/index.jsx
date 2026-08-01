import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import DashboardLayout from '@/layouts/DashboardLayout'
import ProtectedRoute from './ProtectedRoute'
import Loader from '@/components/ui/Loader'

// Code-split every page so the initial bundle stays lean.
const Landing = lazy(() => import('@/pages/Landing/Landing'))
const Login = lazy(() => import('@/pages/Login/Login'))
const Register = lazy(() => import('@/pages/Register/Register'))
const AcceptInvite = lazy(() => import('@/pages/AcceptInvite/AcceptInvite'))
const Dashboard = lazy(() => import('@/pages/Dashboard/Dashboard'))
const History = lazy(() => import('@/pages/History/History'))
const Settings = lazy(() => import('@/pages/Settings/Settings'))
const AdminDashboard = lazy(() => import('@/pages/Admin/AdminDashboard'))

function PageLoader() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background text-foreground">
      <Loader size="lg" />
    </div>
  )
}

export default function AppRoutes() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/accept-invite" element={<AcceptInvite />} />

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
    </Suspense>
  )
}
