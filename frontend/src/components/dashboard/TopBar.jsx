import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import {
  Bell,
  ChevronDown,
  HelpCircle,
  LogOut,
  Menu,
  Search,
  Settings,
  User,
} from 'lucide-react'
import ThemeSwitcher from '@/components/common/ThemeSwitcher'
import { useAuth } from '@/context/AuthContext'
import { cn } from '@/utils/cn'

const notifications = [
  {
    id: 1,
    title: 'Strategy ready',
    message: 'Your Q3 email campaign is ready to review.',
    time: '2m ago',
  },
  {
    id: 2,
    title: 'New insight',
    message: 'Competitor pricing shift detected in your market.',
    time: '1h ago',
  },
  {
    id: 3,
    title: 'Weekly report',
    message: 'Your weekly performance report is available.',
    time: '1d ago',
  },
]

/**
 * App-shell top bar: search, notifications, theme toggle, profile menu.
 * `onMenuClick` opens the mobile sidebar drawer; `onSearch` is debounced by
 * the parent. Reusable and self-contained — no backend.
 */
export default function TopBar({
  onMenuClick,
  onSearch,
  userName,
  userRole,
  className,
}) {
  const { userName: authName, userRole: authRole, logout } = useAuth()
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [openMenu, setOpenMenu] = useState(null) // 'notifications' | 'profile' | null
  const shellRef = useRef(null)

  const displayName = userName ?? authName ?? 'User'
  const displayRole = userRole ?? authRole ?? 'Member'

  // Close menus on outside click / Escape
  useEffect(() => {
    if (!openMenu) return

    const onPointerDown = (event) => {
      if (shellRef.current && !shellRef.current.contains(event.target)) {
        setOpenMenu(null)
      }
    }
    const onKeyDown = (event) => {
      if (event.key === 'Escape') setOpenMenu(null)
    }

    document.addEventListener('pointerdown', onPointerDown)
    document.addEventListener('keydown', onKeyDown)
    return () => {
      document.removeEventListener('pointerdown', onPointerDown)
      document.removeEventListener('keydown', onKeyDown)
    }
  }, [openMenu])

  const handleSearchChange = (event) => {
    const value = event.target.value
    setQuery(value)
    onSearch?.(value)
  }

  const handleLogout = () => {
    setOpenMenu(null)
    logout()
    navigate('/login')
  }

  const iconButton =
    'relative flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-muted-foreground transition-colors hover:bg-muted hover:text-foreground dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-white'

  return (
    <header
      className={cn('sticky top-0 z-40 flex h-16 shrink-0 items-center gap-3 border-b bg-subtle px-4 backdrop-blur transition-colors sm:px-6 dark:border-zinc-800 dark:bg-zinc-900/80' ,
        className
      )}
    >
      {/* Mobile menu button */}
      <button
        type="button"
        onClick={onMenuClick}
        aria-label="Open navigation"
        className={cn(iconButton, 'lg:hidden')}
      >
        <Menu size={20} />
      </button>

      {/* Search */}
      <div className="relative w-full max-w-md">
        <Search
          size={16}
          className="pointer-events-none absolute top-1/2 left-3.5 -translate-y-1/2 text-muted-foreground dark:text-zinc-500"
        />
        <input
          type="search"
          value={query}
          onChange={handleSearchChange}
          placeholder="Search strategies, campaigns…"
          aria-label="Search"
          className="h-10 w-full rounded-xl border border-border bg-card pr-4 pl-10 text-sm text-foreground placeholder-zinc-400 shadow-sm transition-all duration-200 hover:border-zinc-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/30 focus:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100 dark:placeholder-zinc-500 dark:hover:border-zinc-600"
        />
      </div>

      <div ref={shellRef} className="ml-auto flex shrink-0 items-center gap-2">
        {/* Theme switcher */}
        <ThemeSwitcher />

        {/* Notifications */}
        <div className="relative">
          <button
            type="button"
            onClick={() =>
              setOpenMenu((current) => (current === 'notifications' ? null : 'notifications'))
            }
            aria-label="Notifications"
            aria-expanded={openMenu === 'notifications'}
            className={iconButton}
          >
            <Bell size={19} />
            <span className="absolute top-2 right-2.5 flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-indigo-400 opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-indigo-500" />
            </span>
          </button>

          <AnimatePresence>
            {openMenu === 'notifications' && (
              <motion.div
                initial={{ opacity: 0, y: 8, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 8, scale: 0.98 }}
                transition={{ duration: 0.18, ease: 'easeOut' }}
                className="absolute right-0 mt-2 w-80 max-w-[calc(100vw-2rem)] origin-top-right overflow-hidden rounded-2xl border border-border bg-card shadow-xl shadow-black/10 dark:border-zinc-700 dark:bg-zinc-900 dark:shadow-black/40"
              >
                <div className="flex items-center justify-between border-b border-border px-5 py-3.5 dark:border-zinc-800">
                  <p className="text-sm font-semibold text-foreground dark:text-white">
                    Notifications
                  </p>
                  <span className="rounded-full bg-indigo-500/15 px-2 py-0.5 text-xs font-semibold text-indigo-600 dark:text-indigo-300">
                    {notifications.length} new
                  </span>
                </div>
                <ul className="max-h-72 overflow-y-auto">
                  {notifications.map((notification) => (
                    <li key={notification.id}>
                      <button
                        type="button"
                        onClick={() => setOpenMenu(null)}
                        className="flex w-full flex-col gap-0.5 px-5 py-3.5 text-left transition-colors hover:bg-zinc-50 dark:hover:bg-zinc-800/60"
                      >
                        <span className="text-sm font-medium text-foreground dark:text-white">
                          {notification.title}
                        </span>
                        <span className="text-sm text-muted-foreground dark:text-zinc-400">
                          {notification.message}
                        </span>
                        <span className="mt-0.5 text-xs text-muted-foreground dark:text-zinc-500">
                          {notification.time}
                        </span>
                      </button>
                    </li>
                  ))}
                </ul>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Profile */}
        <div className="relative">
          <button
            type="button"
            onClick={() =>
              setOpenMenu((current) => (current === 'profile' ? null : 'profile'))
            }
            aria-label="Account menu"
            aria-expanded={openMenu === 'profile'}
            className={cn('flex items-center gap-2.5 rounded-xl p-1.5 pr-2 transition-colors hover:bg-zinc-100 dark:hover:bg-zinc-800' )}
          >
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-purple-500 text-xs font-semibold text-white">
              {displayName
                .split(' ')
                .map((part) => part[0])
                .slice(0, 2)
                .join('')
                .toUpperCase()}
            </span>
            <span className="hidden text-left sm:block">
              <span className="block max-w-32 truncate text-sm font-medium text-foreground dark:text-white">
                {displayName}
              </span>
              <span className="block max-w-32 truncate text-xs capitalize text-muted-foreground dark:text-zinc-400">
                {displayRole}
              </span>
            </span>
            <ChevronDown
              size={15}
              className={cn('hidden text-muted-foreground transition-transform duration-200 sm:block dark:text-zinc-500' ,
                openMenu === 'profile' && 'rotate-180'
              )}
            />
          </button>

          <AnimatePresence>
            {openMenu === 'profile' && (
              <motion.div
                initial={{ opacity: 0, y: 8, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 8, scale: 0.98 }}
                transition={{ duration: 0.18, ease: 'easeOut' }}
                className="absolute right-0 mt-2 w-56 origin-top-right overflow-hidden rounded-2xl border border-border bg-card py-1.5 shadow-xl shadow-black/10 dark:border-zinc-700 dark:bg-zinc-900 dark:shadow-black/40"
              >
                <div className="border-b border-border px-4 py-3 dark:border-zinc-800">
                  <p className="text-sm font-semibold text-foreground dark:text-white">
                    {displayName}
                  </p>
                  <p className="text-xs capitalize text-muted-foreground dark:text-zinc-400">
                    {displayRole}
                  </p>
                </div>
                <div className="py-1">
                  {[
                    { label: 'Profile', icon: User, to: '/settings' },
                    { label: 'Account settings', icon: Settings, to: '/settings' },
                    { label: 'Help & support', icon: HelpCircle, to: '/settings' },
                  ].map(({ label, icon: Icon, to }) => (
                    <button
                      key={label}
                      type="button"
                      onClick={() => {
                        setOpenMenu(null)
                        navigate(to)
                      }}
                      className="flex w-full items-center gap-2.5 px-4 py-2.5 text-sm text-muted-foreground transition-colors hover:bg-zinc-50 hover:text-zinc-900 dark:text-zinc-300 dark:hover:bg-zinc-800/60 dark:hover:text-white"
                    >
                      <Icon size={16} strokeWidth={1.75} className="text-muted-foreground dark:text-zinc-500" />
                      {label}
                    </button>
                  ))}
                </div>
                <div className="border-t border-border py-1 dark:border-zinc-800">
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="flex w-full items-center gap-2.5 px-4 py-2.5 text-sm text-red-500 transition-colors hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-500/10"
                  >
                    <LogOut size={16} strokeWidth={1.75} />
                    Log out
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </header>
  )
}
