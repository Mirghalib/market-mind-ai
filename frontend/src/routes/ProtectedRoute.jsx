import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'

/**
 * Guards private routes. Requires a valid token; optionally restricts
 * by role (`allow`). Redirects to the login page when unauthenticated,
 * or to the user's home when authenticated but unauthorized.
 */
export default function ProtectedRoute({ allow }) {
  const { isAuthenticated, role } = useAuth()
  const location = useLocation()

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />
  }

  if (allow && !allow.includes(role)) {
    return <Navigate to={role === 'admin' ? '/admin/dashboard' : '/dashboard'} replace />
  }

  return <Outlet />
}
