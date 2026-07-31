import Skeleton from './Skeleton'
import { cn } from '@/utils/cn'

/**
 * Skeleton that mirrors the history table — toolbar with search
 * and filter pills, a table header, skeleton rows, and a
 * pagination footer.
 */
export default function HistorySkeleton({ rows = 5, className }) {
  return (
    <div
      aria-label="Loading history"
      className={cn(
        'overflow-hidden rounded-2xl border border-zinc-200 bg-white shadow-sm dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur',
        className
      )}
    >
      {/* Toolbar */}
      <div className="flex flex-col gap-3 border-b border-zinc-100 p-4 sm:flex-row sm:items-center sm:justify-between dark:border-white/5">
        <Skeleton className="h-10 w-full max-w-xs rounded-lg" />
        <div className="flex gap-2">
          <Skeleton className="h-7 w-14 rounded-lg" />
          <Skeleton className="h-7 w-20 rounded-lg" />
          <Skeleton className="h-7 w-16 rounded-lg" />
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full min-w-[680px] text-left text-sm">
          <thead>
            <tr className="border-b border-zinc-100 dark:border-white/5">
              {['Title', 'Type', 'Created', 'Status', 'Actions'].map((heading, i) => (
                <th key={heading} className="px-4 py-4 sm:px-6">
                  <Skeleton className={cn('h-3', i === 0 ? 'w-16' : i === 4 ? 'ml-auto w-14' : 'w-10')} />
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Array.from({ length: rows }).map((_, i) => (
              <tr
                key={i}
                className="border-b border-zinc-100 last:border-0 dark:border-white/5"
              >
                <td className="px-4 py-4 sm:px-6">
                  <div className="flex items-center gap-3">
                    <Skeleton className="h-8 w-8 rounded-lg" />
                    <Skeleton className="h-4 w-44" />
                  </div>
                </td>
                <td className="px-4 py-4">
                  <Skeleton className="h-4 w-20" />
                </td>
                <td className="px-4 py-4">
                  <Skeleton className="h-4 w-24" />
                </td>
                <td className="px-4 py-4">
                  <Skeleton className="h-5 w-16 rounded-full" />
                </td>
                <td className="px-4 py-4">
                  <div className="flex justify-end gap-1">
                    <Skeleton className="h-8 w-16 rounded-lg" />
                    <Skeleton className="h-8 w-8 rounded-lg" />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between border-t border-zinc-100 px-4 py-3 dark:border-white/5">
        <Skeleton className="h-3 w-40" />
        <div className="flex gap-1">
          <Skeleton className="h-8 w-8 rounded-lg" />
          <Skeleton className="h-8 w-8 rounded-lg" />
          <Skeleton className="h-8 w-8 rounded-lg" />
          <Skeleton className="h-8 w-8 rounded-lg" />
        </div>
      </div>
    </div>
  )
}
