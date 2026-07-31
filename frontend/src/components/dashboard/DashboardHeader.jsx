import { motion } from 'framer-motion'
import { cn } from '@/utils/cn'

/**
 * Reusable page header. Compose with any content and pass actions
 * (buttons, menus, toggles) through the `actions` slot.
 */
export default function DashboardHeader({
  title,
  subtitle,
  eyebrow,
  actions,
  className,
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className={cn('flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between', className)}
    >
      <div>
        {eyebrow && (
          <p className="text-xs font-semibold tracking-widest text-indigo-600 uppercase dark:text-indigo-400">
            {eyebrow}
          </p>
        )}
        <h1 className="mt-1 text-2xl font-semibold tracking-tight text-zinc-900 sm:text-3xl dark:text-white">
          {title}
        </h1>
        {subtitle && <p className="mt-1.5 text-sm text-zinc-500 dark:text-zinc-400">{subtitle}</p>}
      </div>
      {actions && <div className="flex shrink-0 items-center gap-3">{actions}</div>}
    </motion.div>
  )
}
