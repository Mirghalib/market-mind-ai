import Skeleton from './Skeleton'
import { cn } from '@/utils/cn'

/**
 * Skeleton that mirrors the business strategy form — icon header,
 * two-column field grid, and a submit button placeholder.
 */
export default function FormSkeleton({ className }) {
  return (
    <div
      aria-label="Loading form"
      className={cn('rounded-2xl border border-border bg-card p-6 shadow-sm sm:p-8 dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur' ,
        className
      )}
    >
      <div className="flex items-center gap-3">
        <Skeleton className="h-10 w-10 rounded-xl" />
        <div className="space-y-2">
          <Skeleton className="h-4 w-48" />
          <Skeleton className="h-3 w-64" />
        </div>
      </div>

      <div className="mt-6 grid gap-5 sm:grid-cols-2">
        <div className="space-y-1.5">
          <Skeleton className="h-3 w-24" />
          <Skeleton className="h-11 rounded-lg" />
        </div>
        <div className="space-y-1.5">
          <Skeleton className="h-3 w-24" />
          <Skeleton className="h-11 rounded-lg" />
        </div>
        <div className="space-y-1.5 sm:col-span-2">
          <Skeleton className="h-3 w-28" />
          <Skeleton className="h-20 rounded-lg" />
        </div>
        <div className="space-y-1.5 sm:col-span-2">
          <Skeleton className="h-3 w-28" />
          <Skeleton className="h-20 rounded-lg" />
        </div>
        <div className="space-y-1.5">
          <Skeleton className="h-3 w-24" />
          <Skeleton className="h-11 rounded-lg" />
        </div>
        <div className="space-y-1.5">
          <Skeleton className="h-3 w-24" />
          <Skeleton className="h-11 rounded-lg" />
        </div>
      </div>

      <div className="mt-6 flex items-center gap-3">
        <Skeleton className="h-12 w-52 rounded-lg" />
        <Skeleton className="h-4 w-40" />
      </div>
    </div>
  )
}
