import { useEffect, useRef } from 'react'
import { animate, motion, useInView } from 'framer-motion'
import { TrendingDown, TrendingUp } from 'lucide-react'
import { cn } from '@/utils/cn'

const tones = {
  indigo: {
    icon: 'bg-indigo-500/15 text-indigo-600 dark:text-indigo-400',
    progress: 'from-indigo-500 to-purple-500',
    sparkline: '#818cf8',
    hover: 'hover:border-indigo-400/40 hover:shadow-indigo-500/10 dark:hover:shadow-indigo-500/10',
  },
  purple: {
    icon: 'bg-purple-500/15 text-purple-600 dark:text-purple-400',
    progress: 'from-purple-500 to-fuchsia-500',
    sparkline: '#c084fc',
    hover: 'hover:border-purple-400/40 hover:shadow-purple-500/10 dark:hover:shadow-purple-500/10',
  },
  cyan: {
    icon: 'bg-cyan-500/15 text-cyan-600 dark:text-cyan-400',
    progress: 'from-cyan-500 to-blue-500',
    sparkline: '#22d3ee',
    hover: 'hover:border-cyan-400/40 hover:shadow-cyan-500/10 dark:hover:shadow-cyan-500/10',
  },
  emerald: {
    icon: 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400',
    progress: 'from-emerald-500 to-teal-500',
    sparkline: '#34d399',
    hover: 'hover:border-emerald-400/40 hover:shadow-emerald-500/10 dark:hover:shadow-emerald-500/10',
  },
  amber: {
    icon: 'bg-amber-500/15 text-amber-600 dark:text-amber-400',
    progress: 'from-amber-500 to-orange-500',
    sparkline: '#fbbf24',
    hover: 'hover:border-amber-400/40 hover:shadow-amber-500/10 dark:hover:shadow-amber-500/10',
  },
  rose: {
    icon: 'bg-rose-500/15 text-rose-600 dark:text-rose-400',
    progress: 'from-rose-500 to-red-500',
    sparkline: '#fb7185',
    hover: 'hover:border-rose-400/40 hover:shadow-rose-500/10 dark:hover:shadow-rose-500/10',
  },
}

/**
 * Animated count-up number. Starts when scrolled into view.
 * Supports suffixes/prefixes and locale-aware formatting.
 */
function AnimatedNumber({ value, prefix = '', suffix = '', className }) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-40px' })

  useEffect(() => {
    if (!inView) return
    const controls = animate(0, value, {
      duration: 1.2,
      ease: 'easeOut',
      onUpdate: (v) => {
        if (ref.current) {
          ref.current.textContent = `${prefix}${Math.round(v).toLocaleString()}${suffix}`
        }
      },
    })
    return () => controls.stop()
  }, [inView, value, prefix, suffix])

  return (
    <span ref={ref} className={className}>
      {prefix}0{suffix}
    </span>
  )
}

/**
 * Sparkline placeholder — pure SVG polyline animated with a draw effect.
 * `points` is a percentage array (0-100) mapping to the viewBox height.
 */
function MiniSparkline({ points, color, className }) {
  const width = 120
  const height = 36
  const stepX = width / (points.length - 1)
  const line = points
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${i * stepX} ${height - (p / 100) * height}`)
    .join(' ')

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      aria-hidden
      className={cn('h-9 w-full' , className)}
    >
      <motion.path
        d={line}
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        initial={{ pathLength: 0, opacity: 0 }}
        whileInView={{ pathLength: 1, opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 1.1, delay: 0.3, ease: 'easeInOut' }}
      />
    </svg>
  )
}

/**
 * Reusable analytics card: icon chip, animated count-up value,
 * delta chip, progress bar, and a mini sparkline placeholder.
 */
export default function AnalyticsCard({
  icon: Icon,
  label,
  value,
  prefix = '',
  suffix = '',
  delta,
  progress = 0,
  progressLabel,
  points = [30, 45, 38, 60, 52, 72, 64],
  tone = 'indigo',
  className,
}) {
  const styles = tones[tone]
  const positive = Number(delta) >= 0

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: 'easeOut' }}
      whileHover={{ y: -4 }}
      className={cn('group relative overflow-hidden rounded-2xl border border-border bg-card p-5 shadow-sm transition-all duration-300 dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur' ,
        styles.hover,
        className
      )}
    >
      {/* Hover glow */}
      <div
        aria-hidden
        className={cn('pointer-events-none absolute -top-16 left-1/2 h-32 w-32 -translate-x-1/2 rounded-full blur-2xl opacity-0 transition-opacity duration-300 group-hover:opacity-100' ,
          styles.icon
        )}
      />

      <div className="relative flex items-start justify-between gap-3">
        <span
          className={cn('flex h-10 w-10 shrink-0 items-center justify-center rounded-xl transition-transform duration-300 group-hover:scale-110' ,
            styles.icon
          )}
        >
          <Icon size={19} strokeWidth={1.75} />
        </span>
        {delta !== undefined && (
          <span
            className={cn('inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold' ,
              positive
                ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400'
                : 'bg-red-500/15 text-red-600 dark:text-red-400'
            )}
          >
            {positive ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
            {positive ? '+' : ''}
            {delta}%
          </span>
        )}
      </div>

      <div className="relative mt-4">
        <AnimatedNumber
          value={value}
          prefix={prefix}
          suffix={suffix}
          className="text-2xl font-bold tracking-tight text-foreground dark:text-white"
        />
        <p className="mt-0.5 text-sm text-muted-foreground dark:text-zinc-400">{label}</p>
      </div>

      {/* Progress bar */}
      <div className="relative mt-4">
        <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted dark:bg-white/5">
          <motion.div
            initial={{ width: 0 }}
            whileInView={{ width: `${Math.min(progress, 100)}%` }}
            viewport={{ once: true }}
            transition={{ duration: 1, delay: 0.3, ease: 'easeOut' }}
            className={cn('h-full rounded-full bg-gradient-to-r' , styles.progress)}
          />
        </div>
        {progressLabel && (
          <p className="mt-1.5 text-xs text-muted-foreground dark:text-zinc-500">{progressLabel}</p>
        )}
      </div>

      {/* Mini chart placeholder */}
      <div className="relative mt-4 opacity-80 transition-opacity duration-300 group-hover:opacity-100">
        <MiniSparkline points={points} color={styles.sparkline} />
      </div>
    </motion.div>
  )
}
