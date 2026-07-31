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
        'relative overflow-hidden rounded-2xl border border-white/10 px-6 py-8 sm:px-8',
        className
      )}
    >
      {/* Gradient background */}
      <div
        aria-hidden
        className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_left,rgba(99,102,241,0.3),transparent_55%),radial-gradient(ellipse_at_bottom_right,rgba(168,85,247,0.3),transparent_55%)]"
      />

      {/* Animated glow */}
      <motion.div
        aria-hidden
        animate={{ x: [0, 40, 0], y: [0, 20, 0], scale: [1, 1.1, 1] }}
        transition={{ duration: 12, repeat: Infinity, ease: 'easeInOut' }}
        className="pointer-events-none absolute -top-20 -right-20 h-64 w-64 rounded-full bg-indigo-500/20 blur-3xl"
      />

      <div className="relative flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-zinc-300">
            <Sparkles size={12} className="text-indigo-400" />
            AI-Powered Insights
          </span>
          <h2 className="mt-4 text-xl font-semibold tracking-tight text-white sm:text-2xl">
            {title}
          </h2>
          {description && (
            <p className="mt-2 max-w-xl text-sm leading-relaxed text-zinc-400">
              {description}
            </p>
          )}
        </div>
        {actions && <div className="flex shrink-0 flex-wrap items-center gap-3">{actions}</div>}
      </div>
    </motion.div>
  )
}
