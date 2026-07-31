import { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { Clock, Eye, FileText, Search } from 'lucide-react'
import Badge from '@/components/ui/Badge'
import Button from '@/components/ui/Button'
import { cn } from '@/utils/cn'

const STATUS_VARIANTS = {
  completed: 'success',
  processing: 'primary',
  failed: 'danger',
}

/**
 * Reusable data table for past analyses.
 * `rows`: array of { id, title, type, createdAt, status, score? }.
 * `onView(row)` is an optional callback for the row action.
 * Search is local, so no backend is required.
 */
export default function HistoryTable({ rows = [], onView, className }) {
  const [query, setQuery] = useState('')

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return rows
    return rows.filter((row) =>
      [row.title, row.type, row.status].some((field) =>
        String(field ?? '').toLowerCase().includes(q)
      )
    )
  }, [rows, query])

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: 'easeOut' }}
      className={cn(
        'overflow-hidden rounded-2xl border border-white/10 bg-white/[0.03] shadow-lg shadow-black/20 backdrop-blur',
        className
      )}
    >
      {/* Toolbar */}
      <div className="flex flex-col gap-3 border-b border-white/5 p-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative w-full sm:max-w-xs">
          <Search
            size={15}
            className="pointer-events-none absolute top-1/2 left-3.5 -translate-y-1/2 text-zinc-500"
          />
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search analyses…"
            aria-label="Search analyses"
            className="h-10 w-full rounded-lg border border-zinc-700 bg-zinc-900 pr-3.5 pl-9 text-sm text-zinc-100 placeholder-zinc-500 transition-colors focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
          />
        </div>
        <p className="text-xs text-zinc-500">
          {filtered.length} of {rows.length} analyses
        </p>
      </div>

      {filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center px-6 py-16 text-center">
          <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/[0.05] text-zinc-500">
            <FileText size={22} strokeWidth={1.75} />
          </span>
          <p className="mt-4 text-sm font-medium text-white">
            {rows.length === 0 ? 'No analyses yet' : 'No matches found'}
          </p>
          <p className="mt-1 max-w-xs text-sm text-zinc-500">
            {rows.length === 0
              ? 'Your saved marketing strategies will appear here.'
              : 'Try a different search term.'}
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead>
              <tr className="border-b border-white/5 text-xs tracking-wide text-zinc-500 uppercase">
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
                  Action
                </th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((row, index) => (
                <motion.tr
                  key={row.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: index * 0.05, duration: 0.3 }}
                  className="border-b border-white/5 last:border-0"
                >
                  <td className="px-4 py-4 sm:px-6">
                    <div className="flex items-center gap-3">
                      <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-400">
                        <FileText size={15} />
                      </span>
                      <span className="font-medium text-white">{row.title}</span>
                    </div>
                  </td>
                  <td className="px-4 py-4 text-zinc-400">{row.type}</td>
                  <td className="px-4 py-4">
                    <span className="flex items-center gap-1.5 text-zinc-400">
                      <Clock size={13} />
                      {row.createdAt}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <Badge variant={STATUS_VARIANTS[row.status] ?? 'default'}>
                      {row.status}
                    </Badge>
                  </td>
                  <td className="px-4 py-4 text-right">
                    {onView && (
                      <Button variant="ghost" size="sm" onClick={() => onView(row)}>
                        <Eye size={15} />
                        View
                      </Button>
                    )}
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </motion.div>
  )
}
