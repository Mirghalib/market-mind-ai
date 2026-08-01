import { useEffect, useRef } from 'react'
import { animate, motion, useInView } from 'framer-motion'
import { HelpCircle, TrendingDown, TrendingUp } from 'lucide-react'
import { cn } from '@/utils/cn'

const tones = {
  indigo: {
    icon: 'bg-indigo-500/15 text-indigo-600 dark:text-indigo-400',
    glow: 'from-indigo-500/20 to-transparent',
    hover: 'hover:border-indigo-400/40 hover:shadow-indigo-500/10',
  },
  purple: {
    icon: 'bg-purple-500/15 text-purple-600 dark:text-purple-400',
    glow: 'from-purple-500/20 to-transparent',
    hover: 'hover:border-purple-400/40 hover:shadow-purple-500/10',
  },
  cyan: {
    icon: 'bg-cyan-500/15 text-cyan-600 dark:text-cyan-400',
    glow: 'from-cyan-500/20 to-transparent',
    hover: 'hover:border-cyan-400/40 hover:shadow-cyan-500/10',
  },
  emerald: {
    icon: 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400',
    glow: 'from-emerald-500/20 to-transparent',
    hover: 'hover:border-emerald-400/40 hover:shadow-emerald-500/10',
  },
  amber: {
    icon: 'bg-amber-500/15 text-amber-600 dark:text-amber-400',
    glow: 'from-amber-500/20 to-transparent',
    hover: 'hover:border-amber-400/40 hover:shadow-amber-500/10',
  },
  rose: {
    icon: 'bg-rose-500/15 text-rose-600 dark:text-rose-400',
    glow: 'from-rose-500/20 to-transparent',
    hover: 'hover:border-rose-400/40 hover:shadow-rose-500/10',
  },
}

/**
 * Animated count-up number, starts when scrolled into view.
 */
function AnimatedNumber({ value, className }) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-40px' })

  useEffect(() => {
    if (!inView) return
    const controls = animate(0, value, {
      duration: 1.2,
      ease: 'easeOut',
      onUpdate: (v) => {
        if (ref.current) ref.current.textContent = Math.round(v).toLocaleString()
      },
    })
    return () => controls.stop()
  }, [inView, value])

  return (
    <span ref={ref} className={className}>
      0
    </span>
  )
}

/**
 * Admin analytics stat card: icon chip, animated count, optional
 * growth chip, tooltip, hover glow and entrance animation.
 */
export default function AdminStatCard({
  icon: Icon,
  label,
  value,
  delta,
  hint,
  tone = 'indigo',
  className,
}) {
  const styles = tones[tone]
  const numericDelta = !Number.isNaN(Number(delta))
  const positive = numericDelta ? Number(delta) >= 0 : true

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: 'easeOut' }}
      whileHover={{ y: -4 }}
      className={cn(
        'group relative overflow-hidden rounded-2xl border border-border bg-card p-5 shadow-sm transition-all duration-300 dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur',
        styles.hover,
        className
      )}
    >
      {/* Hover glow */}
      <div
        aria-hidden
        className={cn(
          'pointer-events-none absolute inset-x-0 -top-20 h-40 bg-gradient-to-b opacity-0 transition-opacity duration-300 group-hover:opacity-100',
          styles.glow
        )}
      />

      <div className="relative flex items-start justify-between gap-3">
        <span
          className={cn(
            'flex h-10 w-10 shrink-0 items-center justify-center rounded-xl transition-transform duration-300 group-hover:scale-110',
            styles.icon
          )}
        >
          <Icon size={19} strokeWidth={1.75} />
        </span>

        <div className="flex items-center gap-2">
          {delta !== undefined && delta !== null && delta !== '' && (
            <span
              className={cn(
                'inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold',
                positive
                  ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400'
                  : 'bg-red-500/15 text-red-600 dark:text-red-400'
              )}
            >
              {numericDelta ? (
                <>
                  {positive ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                  {positive ? '+' : ''}
                  {delta}%
                </>
              ) : (
                <>{delta}</>
              )}
            </span>
          )}
          {hint && (
            <span
              role="tooltip"
              title={hint}
              className="flex h-6 w-6 cursor-help items-center justify-center rounded-full text-muted-foreground transition-colors hover:bg-muted hover:text-foreground dark:text-zinc-500 dark:hover:bg-zinc-800 dark:hover:text-zinc-200"
            >
              <HelpCircle size={14} />
            </span>
          )}
        </div>
      </div>

      <div className="relative mt-4">
        <AnimatedNumber
          value={value}
          className="text-2xl font-bold tracking-tight text-foreground dark:text-white"
        />
        <p className="mt-0.5 text-sm text-muted-foreground dark:text-zinc-400">{label}</p>
      </div>
    </motion.div>
  )
}
