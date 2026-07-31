import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import { LayoutDashboard, History, Settings, LogOut, Sparkles, X, Menu } from 'lucide-react'
import { APP_NAME, DASHBOARD_LINKS } from '@/constants'
import { removeToken } from '@/utils/token'
import { cn } from '@/utils/cn'

const ICONS = {
  LayoutDashboard,
  History,
  Settings,
}

export default function Sidebar() {
  const [open, setOpen] = useState(false)
  const navigate = useNavigate()

  const handleLogout = () => {
    removeToken()
    navigate('/login')
  }

  return (
    <>
      {/* Mobile top bar */}
      <header className="flex h-16 shrink-0 items-center justify-between border-b border-zinc-800 bg-zinc-900/50 px-4 lg:hidden">
        <div className="flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-purple-500">
            <Sparkles size={15} className="text-white" />
          </span>
          <span className="text-sm font-semibold text-white">{APP_NAME}</span>
        </div>
        <button
          type="button"
          onClick={() => setOpen(true)}
          aria-label="Open navigation"
          className="flex h-10 w-10 items-center justify-center rounded-lg text-zinc-300 transition-colors hover:bg-zinc-800 hover:text-white"
        >
          <Menu size={20} />
        </button>
      </header>

      {/* Desktop sidebar */}
      <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col border-r border-zinc-800 bg-zinc-900/50 lg:flex">
        <div className="flex h-16 items-center gap-2 border-b border-zinc-800 px-6">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-purple-500">
            <Sparkles size={15} className="text-white" />
          </span>
          <span className="text-sm font-semibold text-white">{APP_NAME}</span>
        </div>

        <nav aria-label="Dashboard navigation" className="flex-1 space-y-1 p-4">
          {DASHBOARD_LINKS.map((link) => {
            const Icon = ICONS[link.icon] ?? LayoutDashboard
            return (
              <NavLink
                key={link.href}
                to={link.href}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-indigo-500/10 text-indigo-400'
                      : 'text-zinc-400 hover:bg-zinc-800 hover:text-white'
                  )
                }
              >
                <Icon size={17} />
                {link.label}
              </NavLink>
            )
          })}
        </nav>

        <div className="border-t border-zinc-800 p-4">
          <button
            type="button"
            onClick={handleLogout}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-zinc-400 transition-colors hover:bg-zinc-800 hover:text-white"
          >
            <LogOut size={17} />
            Log out
          </button>
        </div>
      </aside>

      {/* Mobile drawer */}
      <AnimatePresence>
        {open && (
          <div className="fixed inset-0 z-50 lg:hidden">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setOpen(false)}
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            />
            <motion.aside
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ duration: 0.25, ease: 'easeInOut' }}
              className="absolute inset-y-0 left-0 flex w-72 flex-col border-r border-zinc-800 bg-zinc-950"
            >
              <div className="flex h-16 items-center justify-between border-b border-zinc-800 px-6">
                <div className="flex items-center gap-2">
                  <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-purple-500">
                    <Sparkles size={15} className="text-white" />
                  </span>
                  <span className="text-sm font-semibold text-white">{APP_NAME}</span>
                </div>
                <button
                  type="button"
                  onClick={() => setOpen(false)}
                  aria-label="Close navigation"
                  className="flex h-10 w-10 items-center justify-center rounded-lg text-zinc-300 transition-colors hover:bg-zinc-800 hover:text-white"
                >
                  <X size={20} />
                </button>
              </div>

              <nav aria-label="Dashboard navigation" className="flex-1 space-y-1 p-4">
                {DASHBOARD_LINKS.map((link) => {
                  const Icon = ICONS[link.icon] ?? LayoutDashboard
                  return (
                    <NavLink
                      key={link.href}
                      to={link.href}
                      onClick={() => setOpen(false)}
                      className={({ isActive }) =>
                        cn(
                          'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                          isActive
                            ? 'bg-indigo-500/10 text-indigo-400'
                            : 'text-zinc-400 hover:bg-zinc-800 hover:text-white'
                        )
                      }
                    >
                      <Icon size={17} />
                      {link.label}
                    </NavLink>
                  )
                })}
              </nav>

              <div className="border-t border-zinc-800 p-4">
                <button
                  type="button"
                  onClick={() => {
                    setOpen(false)
                    handleLogout()
                  }}
                  className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-zinc-400 transition-colors hover:bg-zinc-800 hover:text-white"
                >
                  <LogOut size={17} />
                  Log out
                </button>
              </div>
            </motion.aside>
          </div>
        )}
      </AnimatePresence>
    </>
  )
}
