import { useEffect, useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import {
  ChevronLeft,
  ChevronRight,
  Clock,
  Eye,
  FileText,
  Search,
  Trash2,
} from 'lucide-react'
import Badge from '@/components/ui/Badge'
import Button from '@/components/ui/Button'
import { cn } from '@/utils/cn'

export const STATUS_FILTERS = ['all', 'completed', 'processing', 'failed']

const STATUS_VARIANTS = {
  completed: 'success',
  processing: 'primary',
  failed: 'danger',
}

const DEFAULT_PAGE_SIZE = 6

/**
 * Reusable data table for past analyses.
 * rows: [{ id, title, type, createdAt, status }]
 * - search (local), status filter, pagination, optional view/delete actions.
 * No backend — all state is local.
 */
export default function HistoryTable({
  rows = [],
  pageSize = DEFAULT_PAGE_SIZE,
  onView,
  onDelete,
  className,
}) {
  const [query, setQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [page, setPage] = useState(1)

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    return rows.filter((row) => {
      const matchesQuery =
        !q ||
        [row.title, row.type, row.status].some((field) =>
          String(field ?? '').toLowerCase().includes(q)
        )
      const matchesStatus = statusFilter === 'all' || row.status === statusFilter
      return matchesQuery && matchesStatus
    })
  }, [rows, query, statusFilter])

  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize))
  const safePage = Math.min(page, totalPages)

  // Keep the page in range when filters shrink the list.
  useEffect(() => {
    if (safePage !== page) setPage(safePage)
  }, [safePage, page])

  const paginated = filtered.slice((safePage - 1) * pageSize, safePage * pageSize)
  const from = filtered.length === 0 ? 0 : (safePage - 1) * pageSize + 1
  const to = Math.min(safePage * pageSize, filtered.length)

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: 'easeOut' }}
      className={cn('overflow-hidden rounded-2xl border border-border bg-card shadow-sm dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur' ,
        className
      )}
    >
      {/* Toolbar: search + filter */}
      <div className="flex flex-col gap-3 border-b border-border p-4 sm:flex-row sm:items-center sm:justify-between dark:border-white/5">
        <div className="relative w-full sm:max-w-xs">
          <Search
            size={15}
            className="pointer-events-none absolute top-1/2 left-3.5 -translate-y-1/2 text-muted-foreground dark:text-zinc-500"
          />
          <input
            type="search"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value)
              setPage(1)
            }}
            placeholder="Search analyses…"
            aria-label="Search analyses"
            className="h-10 w-full rounded-lg border border-border bg-card pr-3.5 pl-9 text-sm text-foreground placeholder-zinc-400 transition-colors focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100 dark:placeholder-zinc-500"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {STATUS_FILTERS.map((status) => (
            <button
              key={status}
              type="button"
              onClick={() => {
                setStatusFilter(status)
                setPage(1)
              }}
              aria-pressed={statusFilter === status}
              className={cn('rounded-lg px-3 py-1.5 text-xs font-medium capitalize transition-colors' ,
                statusFilter === status
                  ? 'bg-indigo-500/15 text-indigo-600 dark:text-indigo-300'
                  : 'text-muted-foreground hover:bg-muted hover:text-foreground dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-white'
              )}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center px-6 py-16 text-center">
          <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-muted text-muted-foreground dark:bg-white/[0.05]">
            <FileText size={22} strokeWidth={1.75} />
          </span>
          <p className="mt-4 text-sm font-medium text-foreground dark:text-white">
            {rows.length === 0 ? 'No analyses yet' : 'No matches found'}
          </p>
          <p className="mt-1 max-w-xs text-sm text-muted-foreground dark:text-zinc-400">
            {rows.length === 0
              ? 'Your saved marketing strategies will appear here.'
              : 'Try different search terms or filters.'}
          </p>
        </div>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[680px] text-left text-sm">
              <thead>
                <tr className="border-b border-border text-xs tracking-wide text-muted-foreground uppercase dark:border-white/5 dark:text-zinc-500">
                  <th scope="col" className="px-4 py-3 font-medium sm:px-6">
                    Title
                  </th>
                  <th scope="col" className="px-4 py-3 font-medium">
                    Type
                  </th>
                  <th scope="col" className="px-4 py-3 font-medium">
                    Created
                  </th>
                  <th scope="col" className="px-4 py-3 font-medium">
                    Status
                  </th>
                  <th scope="col" className="px-4 py-3 text-right font-medium">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {paginated.map((row, index) => (
                  <motion.tr
                    key={row.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: index * 0.04, duration: 0.3 }}
                    className="border-b border-border last:border-0 dark:border-white/5"
                  >
                    <td className="px-4 py-4 sm:px-6">
                      <div className="flex items-center gap-3">
                        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-600 dark:text-indigo-400">
                          <FileText size={15} />
                        </span>
                        <span className="font-medium text-foreground dark:text-white">
                          {row.title}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-4 text-muted-foreground dark:text-zinc-400">{row.type}</td>
                    <td className="px-4 py-4">
                      <span className="flex items-center gap-1.5 text-muted-foreground dark:text-zinc-400">
                        <Clock size={13} />
                        {row.createdAt}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      <Badge variant={STATUS_VARIANTS[row.status] ?? 'default'}>
                        {row.status}
                      </Badge>
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex items-center justify-end gap-1">
                        {onView && (
                          <Button variant="ghost" size="sm" onClick={() => onView(row)}>
                            <Eye size={15} />
                            View
                          </Button>
                        )}
                        {onDelete && (
                          <button
                            type="button"
                            onClick={() => onDelete(row)}
                            aria-label={`Delete ${row.title}`}
                            title="Delete"
                            className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-red-500/10 hover:text-red-500 dark:text-zinc-400 dark:hover:text-red-400"
                          >
                            <Trash2 size={15} />
                          </button>
                        )}
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex flex-col items-center justify-between gap-3 border-t border-border px-4 py-3 sm:flex-row dark:border-white/5">
            <p className="text-xs text-muted-foreground dark:text-zinc-400">
              Showing <span className="font-medium text-foreground dark:text-zinc-200">{from}</span>–
              <span className="font-medium text-foreground dark:text-zinc-200">{to}</span> of{' '}
              <span className="font-medium text-foreground dark:text-zinc-200">{filtered.length}</span>{' '}
              analyses
            </p>

            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={safePage === 1}
                aria-label="Previous page"
                className="flex h-8 w-8 items-center justify-center rounded-lg border border-border text-muted-foreground transition-colors hover:bg-zinc-100 hover:text-zinc-900 disabled:pointer-events-none disabled:opacity-40 dark:border-zinc-700 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-white"
              >
                <ChevronLeft size={15} />
              </button>

              {Array.from({ length: totalPages }, (_, i) => i + 1).map((num) => (
                <button
                  key={num}
                  type="button"
                  onClick={() => setPage(num)}
                  aria-label={`Page ${num}`}
                  aria-current={safePage === num ? 'page' : undefined}
                  className={cn('h-8 w-8 rounded-lg text-xs font-medium transition-colors' ,
                    safePage === num
                      ? 'bg-indigo-500 text-white'
                      : 'text-muted-foreground hover:bg-muted hover:text-foreground dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-white'
                  )}
                >
                  {num}
                </button>
              ))}

              <button
                type="button"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={safePage === totalPages}
                aria-label="Next page"
                className="flex h-8 w-8 items-center justify-center rounded-lg border border-border text-muted-foreground transition-colors hover:bg-zinc-100 hover:text-zinc-900 disabled:pointer-events-none disabled:opacity-40 dark:border-zinc-700 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-white"
              >
                <ChevronRight size={15} />
              </button>
            </div>
          </div>
        </>
      )}
    </motion.div>
  )
}
