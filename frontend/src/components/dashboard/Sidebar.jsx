import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import {
  History,
  LayoutDashboard,
  LogOut,
  PanelLeft,
  Settings,
  Sparkles,
  X,
} from 'lucide-react'
import { APP_NAME, DASHBOARD_LINKS } from '@/constants'
import { removeToken } from '@/utils/token'
import { cn } from '@/utils/cn'

const ICONS = {
  LayoutDashboard,
  History,
  Settings,
}

const EXPANDED_WIDTH = 272
const COLLAPSED_WIDTH = 72

export default function Sidebar({ mobileOpen, onOpenChange }) {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()

  const closeMobile = () => onOpenChange?.(false)

  const handleLogout = () => {
    removeToken()
    navigate('/login')
  }

  return (
    <>
      {/* Desktop sidebar */}
      <aside
        aria-label="Dashboard navigation"
        className={cn(
          'sticky top-0 hidden h-screen shrink-0 flex-col border-r transition-colors lg:flex',
          'border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900'
        )}
        style={{ width: collapsed ? COLLAPSED_WIDTH : EXPANDED_WIDTH }}
      >
        {/* Brand header */}
        <div className="flex h-16 shrink-0 items-center border-b border-zinc-200 px-4 transition-colors dark:border-zinc-800">
          {collapsed ? (
            <span className="mx-auto flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 shadow-lg shadow-indigo-500/25">
              <Sparkles size={17} className="text-white" />
            </span>
          ) : (
            <div className="flex flex-1 items-center gap-2.5 overflow-hidden">
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 shadow-lg shadow-indigo-500/25">
                <Sparkles size={17} className="text-white" />
              </span>
              <span className="truncate text-sm font-semibold tracking-tight text-zinc-900 dark:text-white">
                {APP_NAME}
              </span>
            </div>
          )}
        </div>

        {/* Collapse toggle */}
        <div
          className={cn(
            'flex shrink-0 items-center border-b border-zinc-200 transition-colors dark:border-zinc-800',
            collapsed ? 'justify-center py-2' : 'justify-end px-3 py-2'
          )}
        >
          <button
            type="button"
            onClick={() => setCollapsed((v) => !v)}
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            className="flex h-8 w-8 items-center justify-center rounded-lg text-zinc-500 transition-colors hover:bg-zinc-100 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-white"
          >
            <motion.span
              animate={{ rotate: collapsed ? 180 : 0 }}
              transition={{ duration: 0.25, ease: 'easeInOut' }}
              className="flex"
            >
              <PanelLeft size={17} />
            </motion.span>
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 overflow-y-auto overflow-x-hidden p-3">
          {DASHBOARD_LINKS.map((link) => {
            const Icon = ICONS[link.icon] ?? LayoutDashboard
            return (
              <NavLink
                key={link.href}
                to={link.href}
                title={collapsed ? link.label : undefined}
                className={({ isActive }) =>
                  cn(
                    'group relative flex items-center gap-3 rounded-xl py-2.5 text-sm font-medium transition-colors',
                    collapsed ? 'justify-center px-0' : 'px-3',
                    isActive
                      ? 'text-indigo-600 dark:text-indigo-300'
                      : 'text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white'
                  )
                }
              >
                {({ isActive }) => (
                  <>
                    {isActive && (
                      <motion.span
                        layoutId="sidebar-active"
                        transition={{ type: 'spring', stiffness: 350, damping: 32 }}
                        className="absolute inset-0 rounded-xl bg-indigo-500/10 ring-1 ring-indigo-500/20 dark:bg-indigo-500/15 dark:ring-indigo-400/20"
                      />
                    )}
                    <span
                      className={cn(
                        'relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg transition-colors',
                        !isActive &&
                          'group-hover:bg-zinc-100 group-hover:text-zinc-900 dark:group-hover:bg-zinc-800 dark:group-hover:text-white'
                      )}
                    >
                      <Icon size={18} strokeWidth={1.75} />
                    </span>
                    {!collapsed && (
                      <span className="relative z-10 truncate">{link.label}</span>
                    )}
                  </>
                )}
              </NavLink>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="shrink-0 border-t border-zinc-200 p-3 transition-colors dark:border-zinc-800">
          <button
            type="button"
            onClick={handleLogout}
            title={collapsed ? 'Log out' : undefined}
            className={cn(
              'group flex w-full items-center gap-3 rounded-xl py-2.5 text-sm font-medium text-zinc-600 transition-colors hover:bg-zinc-100 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-white',
              collapsed ? 'justify-center px-0' : 'px-3'
            )}
          >
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg">
              <LogOut size={18} strokeWidth={1.75} />
            </span>
            {!collapsed && <span className="truncate">Log out</span>}
          </button>
        </div>
      </aside>

      {/* Mobile drawer */}
      <AnimatePresence>
        {mobileOpen && (
          <div className="fixed inset-0 z-50 lg:hidden">
            <motion.button
              type="button"
              aria-label="Close navigation"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={closeMobile}
              className="absolute inset-0 w-full cursor-default bg-black/60 backdrop-blur-sm"
            />
            <motion.aside
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', stiffness: 300, damping: 32 }}
              className="absolute inset-y-0 left-0 flex w-72 max-w-[85vw] flex-col border-r border-zinc-200 bg-white shadow-2xl transition-colors dark:border-zinc-800 dark:bg-zinc-900"
            >
              <div className="flex h-16 shrink-0 items-center justify-between border-b border-zinc-200 px-4 transition-colors dark:border-zinc-800">
                <div className="flex items-center gap-2.5">
                  <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 shadow-lg shadow-indigo-500/25">
                    <Sparkles size={17} className="text-white" />
                  </span>
                  <span className="text-sm font-semibold tracking-tight text-zinc-900 dark:text-white">
                    {APP_NAME}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={closeMobile}
                  aria-label="Close navigation"
                  className="flex h-10 w-10 items-center justify-center rounded-lg text-zinc-600 transition-colors hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800"
                >
                  <X size={20} />
                </button>
              </div>

              <nav className="flex-1 space-y-1 overflow-y-auto p-3">
                {DASHBOARD_LINKS.map((link) => {
                  const Icon = ICONS[link.icon] ?? LayoutDashboard
                  return (
                    <NavLink
                      key={link.href}
                      to={link.href}
                      onClick={closeMobile}
                      className={({ isActive }) =>
                        cn(
                          'group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors',
                          isActive
                            ? 'bg-indigo-500/10 text-indigo-600 ring-1 ring-indigo-500/20 dark:text-indigo-300 dark:ring-indigo-400/20'
                            : 'text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-white'
                        )
                      }
                    >
                      <span className="flex h-8 w-8 items-center justify-center rounded-lg">
                        <Icon size={18} strokeWidth={1.75} />
                      </span>
                      {link.label}
                    </NavLink>
                  )
                })}
              </nav>

              <div className="shrink-0 border-t border-zinc-200 p-3 transition-colors dark:border-zinc-800">
                <button
                  type="button"
                  onClick={() => {
                    closeMobile()
                    handleLogout()
                  }}
                  className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-zinc-600 transition-colors hover:bg-zinc-100 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-white"
                >
                  <span className="flex h-8 w-8 items-center justify-center rounded-lg">
                    <LogOut size={18} strokeWidth={1.75} />
                  </span>
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
