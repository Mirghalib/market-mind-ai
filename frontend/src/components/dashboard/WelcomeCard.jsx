import { motion } from 'framer-motion'
import { Sparkles } from 'lucide-react'
import { cn } from '@/utils/cn'

/**
 * Gradient hero banner shown at the top of the dashboard.
 * Pass a personalized greeting/description and any CTAs via `actions`.
 */
export default function WelcomeCard({
  title,
  description,
  actions,
  className,
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className={cn(
        'relative overflow-hidden rounded-2xl border border-zinc-200 bg-white px-6 py-8 shadow-sm sm:px-8 dark:border-white/10 dark:bg-zinc-900/50 dark:shadow-none',
        className
      )}
    >
      {/* Gradient background */}
      <div
        aria-hidden
        className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_left,rgba(99,102,241,0.12),transparent_55%),radial-gradient(ellipse_at_bottom_right,rgba(168,85,247,0.12),transparent_55%)] dark:bg-[radial-gradient(ellipse_at_top_left,rgba(99,102,241,0.3),transparent_55%),radial-gradient(ellipse_at_bottom_right,rgba(168,85,247,0.3),transparent_55%)]"
      />

      {/* Animated glow */}
      <motion.div
        aria-hidden
        animate={{ x: [0, 40, 0], y: [0, 20, 0], scale: [1, 1.1, 1] }}
        transition={{ duration: 12, repeat: Infinity, ease: 'easeInOut' }}
        className="pointer-events-none absolute -top-20 -right-20 h-64 w-64 rounded-full bg-indigo-500/10 blur-3xl dark:bg-indigo-500/20"
      />

      <div className="relative flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-full border border-zinc-200 bg-zinc-50 px-3 py-1 text-xs font-medium text-zinc-600 dark:border-white/10 dark:bg-white/5 dark:text-zinc-300">
            <Sparkles size={12} className="text-indigo-500 dark:text-indigo-400" />
            AI-Powered Insights
          </span>
          <h2 className="mt-4 text-xl font-semibold tracking-tight text-zinc-900 sm:text-2xl dark:text-white">
            {title}
          </h2>
          {description && (
            <p className="mt-2 max-w-xl text-sm leading-relaxed text-zinc-500 dark:text-zinc-400">
              {description}
            </p>
          )}
        </div>
        {actions && <div className="flex shrink-0 flex-wrap items-center gap-3">{actions}</div>}
      </div>
    </motion.div>
  )
}
