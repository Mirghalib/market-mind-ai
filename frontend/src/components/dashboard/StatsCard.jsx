import { motion } from 'framer-motion'
import { TrendingDown, TrendingUp } from 'lucide-react'
import { cn } from '@/utils/cn'

const tones = {
  indigo: {
    icon: 'bg-indigo-500/15 text-indigo-600 dark:text-indigo-400',
    hover: 'hover:border-indigo-400/40 hover:shadow-md hover:shadow-indigo-500/10 dark:hover:shadow-indigo-500/10',
  },
  purple: {
    icon: 'bg-purple-500/15 text-purple-600 dark:text-purple-400',
    hover: 'hover:border-purple-400/40 hover:shadow-md hover:shadow-purple-500/10 dark:hover:shadow-purple-500/10',
  },
  cyan: {
    icon: 'bg-cyan-500/15 text-cyan-600 dark:text-cyan-400',
    hover: 'hover:border-cyan-400/40 hover:shadow-md hover:shadow-cyan-500/10 dark:hover:shadow-cyan-500/10',
  },
  emerald: {
    icon: 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400',
    hover: 'hover:border-emerald-400/40 hover:shadow-md hover:shadow-emerald-500/10 dark:hover:shadow-emerald-500/10',
  },
}

/**
 * Metric card. `delta` is an optional signed percentage (e.g. "+12.4").
 * Renders an up/down trend chip when provided.
 */
export default function StatsCard({
  icon: Icon,
  label,
  value,
  delta,
  hint,
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
      whileHover={{ y: -3 }}
      className={cn('rounded-2xl border border-border bg-card p-5 shadow-sm transition-colors duration-300 dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur' ,
        styles.hover,
        className
      )}
    >
      <div className="flex items-center justify-between">
        <span
          className={cn('flex h-10 w-10 items-center justify-center rounded-xl' ,
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

      <p className="mt-4 text-2xl font-bold tracking-tight text-foreground dark:text-white">{value}</p>
      <p className="mt-0.5 text-sm text-muted-foreground dark:text-zinc-400">{label}</p>
      {hint && <p className="mt-2 text-xs text-muted-foreground dark:text-zinc-600">{hint}</p>}
    </motion.div>
  )
}
