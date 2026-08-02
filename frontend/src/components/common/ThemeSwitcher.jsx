import { useEffect, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Check, Leaf, Moon, MoonStar, Palette, Sun } from 'lucide-react'
import { THEMES } from '@/context/ThemeContext'
import useTheme from '@/hooks/useTheme'
import { cn } from '@/utils/cn'

const ICONS = {
  sun: Sun,
  moon: Moon,
  'moon-star': MoonStar,
  leaf: Leaf,
}

const SWATCH_CLASSES = {
  light: 'bg-zinc-50 border-zinc-300',
  dark: 'bg-zinc-900 border-zinc-600',
  midnight: 'bg-[#0A1116] border-indigo-900',
  emerald: 'bg-[#04140D] border-emerald-900',
}

/**
 * Reusable theme switcher. Renders the active theme icon (desktop)
 * and opens a dropdown with all available themes. Clicking applies
 * the theme instantly — no reload.
 */
export default function ThemeSwitcher({ align = 'right', className }) {
  const { theme, setTheme } = useTheme()
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  const active = THEMES.find((t) => t.id === theme)
  const ActiveIcon = ICONS[active?.icon] ?? Palette

  useEffect(() => {
    if (!open) return
    const onPointerDown = (event) => {
      if (ref.current && !ref.current.contains(event.target)) setOpen(false)
    }
    const onKeyDown = (event) => {
      if (event.key === 'Escape') setOpen(false)
    }
    document.addEventListener('pointerdown', onPointerDown)
    document.addEventListener('keydown', onKeyDown)
    return () => {
      document.removeEventListener('pointerdown', onPointerDown)
      document.removeEventListener('keydown', onKeyDown)
    }
  }, [open])

  const selectTheme = (id) => {
    setTheme(id)
    setOpen(false)
  }

  return (
    <div ref={ref} className={cn('relative', className)}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-label={`Theme: ${active?.label ?? theme}. Change theme`}
        aria-expanded={open}
        aria-haspopup="listbox"
        className={cn(
          'flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-zinc-500 transition-colors',
          'hover:bg-zinc-100 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-white'
        )}
      >
        <ActiveIcon size={19} />
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            role="listbox"
            aria-label="Select theme"
            initial={{ opacity: 0, y: 8, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.98 }}
            transition={{ duration: 0.18, ease: 'easeOut' }}
            className={cn(
              'absolute top-full mt-2 w-56 origin-top overflow-hidden rounded-2xl border border-border bg-card p-1.5 shadow-xl shadow-black/10 dark:border-zinc-700 dark:bg-zinc-900 dark:shadow-black/40',
              align === 'right' ? 'right-0' : 'left-0'
            )}
          >
            <p className="px-3 py-2 text-xs font-semibold tracking-wide text-muted-foreground uppercase dark:text-zinc-500">
              Theme
            </p>
            {THEMES.map(({ id, label, icon }) => {
              const Icon = ICONS[icon] ?? Palette
              const selected = theme === id
              return (
                <button
                  key={id}
                  type="button"
                  role="option"
                  aria-selected={selected}
                  onClick={() => selectTheme(id)}
                  className={cn(
                    'flex w-full items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors',
                    selected
                      ? 'bg-indigo-500/10 text-indigo-600 dark:text-indigo-300'
                      : 'text-muted-foreground hover:bg-muted hover:text-foreground dark:text-zinc-300 dark:hover:bg-zinc-800 dark:hover:text-white'
                  )}
                >
                  <span
                    aria-hidden
                    className={cn(
                      'flex h-6 w-6 items-center justify-center rounded-full border',
                      SWATCH_CLASSES[id]
                    )}
                  >
                    <Icon size={12} className="text-muted-foreground dark:text-zinc-300" />
                  </span>
                  <span className="flex-1 text-left">{label}</span>
                  {selected && <Check size={15} className="text-indigo-500 dark:text-indigo-400" />}
                </button>
              )
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
