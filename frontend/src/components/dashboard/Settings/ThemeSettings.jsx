import { motion } from 'framer-motion'
import { Leaf, Moon, MoonStar, Palette, Sun } from 'lucide-react'
import { THEMES } from '@/context/ThemeContext'
import useTheme from '@/hooks/useTheme'
import { cn } from '@/utils/cn'

const ICONS = {
  sun: Sun,
  moon: Moon,
  'moon-star': MoonStar,
  leaf: Leaf,
}

const PREVIEWS = {
  light: 'bg-zinc-50',
  dark: 'bg-zinc-900',
  midnight: 'bg-[#0A1116]',
  emerald: 'bg-[#04140D]',
}

/**
 * Theme section — pick one of the four themes. The selection is
 * persisted and applied instantly by the ThemeProvider.
 */
export default function ThemeSettings() {
  const { theme, setTheme } = useTheme()

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="rounded-2xl border border-border bg-card p-6 shadow-sm sm:p-8 dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur"
    >
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/15 text-amber-600 dark:text-amber-400">
          <Palette size={19} strokeWidth={1.75} />
        </span>
        <div>
          <h2 className="text-base font-semibold text-foreground dark:text-white">Theme</h2>
          <p className="text-sm text-muted-foreground dark:text-zinc-400">
            Choose how the dashboard looks.
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        {THEMES.map(({ id, label, icon }) => {
          const Icon = ICONS[icon] ?? Palette
          const selected = theme === id
          return (
            <button
              key={id}
              type="button"
              onClick={() => setTheme(id)}
              aria-pressed={selected}
              className={cn(
                'group rounded-xl border p-4 text-left transition-all duration-200',
                selected
                  ? 'border-indigo-400/50 bg-indigo-500/[0.06] ring-2 ring-indigo-500/30 dark:border-[var(--color-accent-400)]/50 dark:ring-[var(--color-accent-500)]/30'
                  : 'border-border hover:border-zinc-300 dark:border-white/10 dark:hover:border-white/20'
              )}
            >
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2.5">
                  <Icon size={17} className="text-muted-foreground dark:text-zinc-400" />
                  <span className="text-sm font-medium text-foreground dark:text-white">
                    {label}
                  </span>
                </span>
                <span
                  className={cn(
                    'flex h-5 w-5 items-center justify-center rounded-full border-2 transition-colors',
                    selected
                      ? 'border-[var(--color-accent-500)] bg-[var(--color-accent-500)]'
                      : 'border-zinc-300 dark:border-zinc-600'
                  )}
                >
                  {selected && <span className="h-1.5 w-1.5 rounded-full bg-card" />}
                </span>
              </div>
              <p className="mt-2 text-xs text-muted-foreground dark:text-zinc-400">
                {id === 'light' && 'Clean and bright'}
                {id === 'dark' && 'Easy on the eyes'}
                {id === 'midnight' && 'Deep navy, blue accent'}
                {id === 'emerald' && 'Deep green, fresh accent'}
              </p>
              <div
                className={cn(
                  'mt-3 h-10 rounded-lg border border-black/5',
                  PREVIEWS[id]
                )}
              />
            </button>
          )
        })}
      </div>

      <p className="mt-4 text-xs text-muted-foreground dark:text-zinc-500">
        Themes apply instantly and are saved for next time.
      </p>
    </motion.div>
  )
}
