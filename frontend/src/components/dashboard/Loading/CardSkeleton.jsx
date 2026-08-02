import Skeleton from './Skeleton'
import { cn } from '@/utils/cn'

/**
 * Skeleton composition that mirrors a StatsCard — icon chip,
 * metric line, label line.
 */
export default function CardSkeleton({ className }) {
  return (
    <div
      aria-label="Loading card"
      className={cn('rounded-2xl border border-border bg-card p-5 shadow-sm dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur' ,
        className
      )}
    >
      <Skeleton className="h-10 w-10 rounded-xl" />
      <Skeleton className="mt-4 h-7 w-24" />
      <Skeleton className="mt-2 h-4 w-16" />
    </div>
  )
}
