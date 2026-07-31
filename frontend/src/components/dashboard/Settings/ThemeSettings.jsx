import { motion } from 'framer-motion'
import { Moon, Palette, Sun } from 'lucide-react'
import useTheme from '@/hooks/useTheme'
import { cn } from '@/utils/cn'

const THEME_OPTIONS = [
  {
    id: 'light',
    label: 'Light',
    description: 'Clean and bright',
    icon: Sun,
    preview: 'bg-zinc-50',
  },
  {
    id: 'dark',
    label: 'Dark',
    description: 'Easy on the eyes',
    icon: Moon,
    preview: 'bg-zinc-900',
  },
]

/**
 * Theme section — wire the selected theme to the app's ThemeProvider.
 * Light/dark previews are cosmetic; the actual theme is applied by the toggle.
 */
export default function ThemeSettings() {
  const { theme } = useTheme()

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm sm:p-8 dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur"
    >
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/15 text-amber-600 dark:text-amber-400">
          <Palette size={19} strokeWidth={1.75} />
        </span>
        <div>
          <h2 className="text-base font-semibold text-zinc-900 dark:text-white">Theme</h2>
          <p className="text-sm text-zinc-500 dark:text-zinc-400">
            Choose how the dashboard looks.
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        {THEME_OPTIONS.map(({ id, label, description, icon: Icon, preview }) => {
          const selected = theme === id
          return (
            <button
              key={id}
              type="button"
              aria-pressed={selected}
              className={cn(
                'group rounded-xl border p-4 text-left transition-all duration-200',
                selected
                  ? 'border-indigo-400/50 bg-indigo-500/[0.06] ring-2 ring-indigo-500/30'
                  : 'border-zinc-200 hover:border-zinc-300 dark:border-white/10 dark:hover:border-white/20'
              )}
            >
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2.5">
                  <Icon size={17} className="text-zinc-500 dark:text-zinc-400" />
                  <span className="text-sm font-medium text-zinc-900 dark:text-white">
                    {label}
                  </span>
                </span>
                <span
                  className={cn(
                    'flex h-5 w-5 items-center justify-center rounded-full border-2 transition-colors',
                    selected
                      ? 'border-indigo-500 bg-indigo-500'
                      : 'border-zinc-300 dark:border-zinc-600'
                  )}
                >
                  {selected && <span className="h-1.5 w-1.5 rounded-full bg-white" />}
                </span>
              </div>
              <p className="mt-2 text-xs text-zinc-500 dark:text-zinc-400">{description}</p>
              <div className={cn('mt-3 h-10 rounded-lg border border-black/5', preview)} />
            </button>
          )
        })}
      </div>

      <p className="mt-4 text-xs text-zinc-400 dark:text-zinc-500">
        Tip: use the sun/moon button in the top bar to switch themes instantly.
      </p>
    </motion.div>
  )
}
