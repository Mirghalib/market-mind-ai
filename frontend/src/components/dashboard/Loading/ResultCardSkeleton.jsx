import Skeleton from './Skeleton'
import { cn } from '@/utils/cn'

/**
 * Single skeleton card mirroring an AI result card: icon chip,
 * action buttons, title, description lines, and a footer.
 */
export function ResultCardSkeletonItem({ className }) {
  return (
    <div
      aria-label="Loading result card"
      className={cn('rounded-2xl border border-border bg-card p-6 shadow-sm dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur' ,
        className
      )}
    >
      <div className="flex items-start justify-between gap-4">
        <Skeleton className="h-11 w-11 rounded-xl" />
        <div className="flex gap-1">
          <Skeleton className="h-8 w-8 rounded-lg" />
          <Skeleton className="h-8 w-8 rounded-lg" />
          <Skeleton className="h-8 w-8 rounded-lg" />
        </div>
      </div>
      <Skeleton className="mt-4 h-5 w-40" />
      <Skeleton className="mt-2 h-4 w-full" />
      <Skeleton className="mt-2 h-4 w-2/3" />
      <div className="mt-4 space-y-2 border-t border-border pt-4 dark:border-white/5">
        <Skeleton className="h-3.5 w-full" />
        <Skeleton className="h-3.5 w-5/6" />
      </div>
      <Skeleton className="mt-4 h-9 w-full rounded-lg" />
    </div>
  )
}

/**
 * Grid of result-card skeletons. `count` controls how many are rendered.
 */
export default function ResultCardSkeleton({ count = 3, className }) {
  return (
    <div
      aria-label="Loading results"
      className={cn('grid gap-5 sm:grid-cols-2 xl:grid-cols-3' , className)}
    >
      {Array.from({ length: count }).map((_, i) => (
        <ResultCardSkeletonItem key={i} />
      ))}
    </div>
  )
}
