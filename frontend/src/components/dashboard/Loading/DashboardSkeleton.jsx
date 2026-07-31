import Skeleton from './Skeleton'
import CardSkeleton from './CardSkeleton'
import { cn } from '@/utils/cn'

/**
 * Full-page skeleton that mirrors the Dashboard layout:
 * header, welcome banner, stat cards, form, and chart panel.
 */
export default function DashboardSkeleton({ className }) {
  return (
    <div
      aria-label="Loading dashboard"
      className={cn('mx-auto max-w-7xl space-y-8 p-6 sm:p-8', className)}
    >
      {/* Header */}
      <div className="space-y-2">
        <Skeleton className="h-3 w-24" />
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-4 w-72 max-w-full" />
      </div>

      {/* Welcome banner */}
      <div className="rounded-2xl border border-border bg-card p-6 shadow-sm sm:p-8 dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur">
        <Skeleton className="h-4 w-40" />
        <Skeleton className="mt-4 h-7 w-3/4 max-w-xl" />
        <Skeleton className="mt-2 h-4 w-full max-w-lg" />
        <Skeleton className="mt-6 h-11 w-48 rounded-lg" />
      </div>

      {/* Stat cards */}
      <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <CardSkeleton key={i} />
        ))}
      </div>

      {/* Form + results split */}
      <div className="grid gap-6 lg:grid-cols-5">
        <div className="space-y-5 rounded-2xl border border-border bg-card p-6 shadow-sm sm:p-8 lg:col-span-3 dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur">
          <div className="flex items-center gap-3">
            <Skeleton className="h-10 w-10 rounded-xl" />
            <div className="space-y-2">
              <Skeleton className="h-4 w-44" />
              <Skeleton className="h-3 w-56" />
            </div>
          </div>
          <div className="grid gap-5 sm:grid-cols-2">
            <Skeleton className="h-11 rounded-lg" />
            <Skeleton className="h-11 rounded-lg" />
            <Skeleton className="h-20 rounded-lg sm:col-span-2" />
            <Skeleton className="h-20 rounded-lg sm:col-span-2" />
          </div>
          <Skeleton className="h-12 w-52 rounded-lg" />
        </div>

        <div className="hidden space-y-5 lg:col-span-2 lg:block">
          {Array.from({ length: 2 }).map((_, i) => (
            <div
              key={i}
              className="rounded-2xl border border-border bg-card p-6 shadow-sm dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur"
            >
              <Skeleton className="h-11 w-11 rounded-xl" />
              <Skeleton className="mt-4 h-5 w-32" />
              <Skeleton className="mt-2 h-4 w-full" />
              <Skeleton className="mt-2 h-4 w-2/3" />
            </div>
          ))}
        </div>
      </div>

      {/* Chart panel */}
      <div className="rounded-2xl border border-border bg-card p-6 shadow-sm dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur">
        <Skeleton className="h-5 w-36" />
        <Skeleton className="mt-3 h-40 w-full rounded-xl" />
      </div>
    </div>
  )
}
