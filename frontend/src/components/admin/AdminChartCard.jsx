import { motion } from 'framer-motion'
import { cn } from '@/utils/cn'

/**
 * Wrapper panel for admin charts: title, subtitle and an animated
 * children slot. Charts mount here get a fade/slide entrance.
 */
export default function AdminChartCard({
  title,
  subtitle,
  action,
  children,
  className,
  delay = 0,
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: 'easeOut' }}
      className={cn(
        'rounded-2xl border border-border bg-card p-6 shadow-sm dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur',
        className
      )}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-foreground dark:text-white">{title}</h3>
          {subtitle && (
            <p className="mt-0.5 text-sm text-muted-foreground dark:text-zinc-400">{subtitle}</p>
          )}
        </div>
        {action}
      </div>
      <div className="mt-6">{children}</div>
    </motion.div>
  )
}
