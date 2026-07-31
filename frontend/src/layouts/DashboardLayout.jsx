import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { LogOut } from 'lucide-react'
import { APP_NAME, DASHBOARD_LINKS } from '@/constants'
import { removeToken } from '@/utils/token'
import { cn } from '@/utils/cn'

export default function DashboardLayout() {
  const navigate = useNavigate()

  const handleLogout = () => {
    removeToken()
    navigate('/login')
  }

  return (
    <div className="flex min-h-screen bg-zinc-950 text-zinc-100">
      <aside className="flex w-64 flex-col border-r border-zinc-800 bg-zinc-900/50">
        <div className="flex h-16 items-center gap-2 border-b border-zinc-800 px-6">
          <span className="h-2.5 w-2.5 rounded-sm bg-indigo-500" />
          <span className="text-sm font-semibold text-white">{APP_NAME}</span>
        </div>

        <nav className="flex-1 space-y-1 p-4">
          {DASHBOARD_LINKS.map((link) => (
            <NavLink
              key={link.href}
              to={link.href}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
                  isActive
                    ? 'bg-indigo-500/10 text-indigo-400'
                    : 'text-zinc-400 hover:bg-zinc-800 hover:text-white'
                )
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-zinc-800 p-4">
          <button
            type="button"
            onClick={handleLogout}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-zinc-400 transition-colors hover:bg-zinc-800 hover:text-white"
          >
            <LogOut size={16} />
            Log out
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  )
}
