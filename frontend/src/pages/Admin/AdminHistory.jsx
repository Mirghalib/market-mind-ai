import { useCallback, useEffect, useState } from 'react'
import {
  Clock,
  Download,
  ExternalLink,
  Eye,
  FileDown,
  FileJson,
  FileText,
  FileType2,
  Loader2,
  Presentation,
  Search,
  Trash2,
  User,
  Users,
} from 'lucide-react'
import DashboardHeader from '@/components/dashboard/DashboardHeader'
import Button from '@/components/ui/Button'
import Modal from '@/components/ui/Modal'
import Badge from '@/components/ui/Badge'
import Loader from '@/components/ui/Loader'
import { useToast } from '@/context/ToastContext'
import { adminService } from '@/services/admin'
import { cn } from '@/utils/cn'

const PAGE_SIZE = 10

const FORMAT_ICONS = {
  pdf: FileText,
  docx: FileType2,
  pptx: Presentation,
  markdown: FileDown,
  html: FileText,
  json: FileJson,
}

const FORMAT_LABELS = {
  pdf: 'PDF',
  docx: 'DOCX',
  pptx: 'PPTX',
  markdown: 'Markdown',
  html: 'HTML',
  json: 'JSON',
}

const STATUS_VARIANTS = {
  completed: 'success',
  processing: 'primary',
  pending: 'primary',
  failed: 'danger',
}

function errorMessage(err, fallback) {
  return (
    err.response?.data?.detail ||
    err.response?.data?.message ||
    err.message ||
    fallback
  )
}

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function formatDateTime(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function formatBytes(bytes) {
  if (bytes === null || bytes === undefined) return '—'
  if (bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let value = bytes
  while (value >= 1024 && i < units.length - 1) {
    value /= 1024
    i += 1
  }
  return `${value.toFixed(1)} ${units[i]}`
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export default function AdminHistory() {
  const { showToast } = useToast()
  const [rows, setRows] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [formatFilter, setFormatFilter] = useState('')
  const [dateFilter, setDateFilter] = useState('')
  const [sortDir, setSortDir] = useState('desc')
  const [downloadingId, setDownloadingId] = useState(null)
  const [pendingDelete, setPendingDelete] = useState(null)
  const [deleting, setDeleting] = useState(false)
  const [detailRow, setDetailRow] = useState(null)
  const [detailUser, setDetailUser] = useState(null)
  const [detailLoading, setDetailLoading] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const params = { limit: PAGE_SIZE, offset: (page - 1) * PAGE_SIZE, sort_dir: sortDir }
      if (search) params.search = search
      if (formatFilter) params.export_format = formatFilter
      if (dateFilter) {
        const day = new Date(`${dateFilter}T00:00:00`)
        if (!Number.isNaN(day.getTime())) {
          params.date_from = day.toISOString()
          const next = new Date(day)
          next.setDate(next.getDate() + 1)
          params.date_to = next.toISOString()
        }
      }
      const { data } = await adminService.getExports(params)
      setRows(data.items)
      setTotal(data.total)
    } catch (err) {
      setError(errorMessage(err, 'Could not load exports.'))
    } finally {
      setLoading(false)
    }
  }, [page, search, formatFilter, dateFilter, sortDir])

  useEffect(() => {
    load()
  }, [load])

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  const handleDownload = async (row) => {
    setDownloadingId(row.id)
    try {
      const { data } = await adminService.downloadExport(row.id)
      downloadBlob(data, `${row.strategy_name || 'strategy'}.${row.format}`)
    } catch (err) {
      showToast(errorMessage(err, 'Could not download the export.'), 'error')
    } finally {
      setDownloadingId(null)
    }
  }

  const confirmDelete = async () => {
    if (!pendingDelete) return
    setDeleting(true)
    try {
      await adminService.deleteExport(pendingDelete.id)
      showToast('Export permanently deleted.', 'success')
      setPendingDelete(null)
      load()
    } catch (err) {
      showToast(errorMessage(err, 'Could not delete the export.'), 'error')
      setDeleting(false)
    }
  }

  const openDetail = async (row) => {
    setDetailRow(row)
    setDetailUser(null)
    if (!row.user_id) return
    setDetailLoading(true)
    try {
      const { data } = await adminService.getUser(row.user_id)
      setDetailUser(data)
    } catch {
      // User detail is best-effort; the row already has name/email.
    } finally {
      setDetailLoading(false)
    }
  }

  const toggleSort = () => {
    setSortDir((current) => (current === 'desc' ? 'asc' : 'desc'))
    setPage(1)
  }

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-6 sm:p-8">
      <DashboardHeader
        eyebrow="Admin"
        title="Platform History"
        subtitle="Every export from every user — search, filter, download and manage."
      />

      {/* Filters */}
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center">
        <div className="relative flex-1">
          <Search
            size={15}
            className="pointer-events-none absolute top-1/2 left-3.5 -translate-y-1/2 text-muted-foreground dark:text-zinc-500"
          />
          <input
            type="search"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setPage(1)
            }}
            placeholder="Search user, email or strategy…"
            className="h-10 w-full rounded-xl border border-border bg-card pr-4 pl-10 text-sm text-foreground shadow-sm transition-all focus:border-accent-500 focus:ring-2 focus:ring-accent-500/30 focus:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
          />
        </div>

        <select
          value={formatFilter}
          onChange={(e) => {
            setFormatFilter(e.target.value)
            setPage(1)
          }}
          className="h-10 rounded-xl border border-border bg-card px-3 text-sm text-foreground transition-colors focus:border-accent-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
        >
          <option value="">All formats</option>
          {Object.entries(FORMAT_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>

        <input
          type="date"
          value={dateFilter}
          onChange={(e) => {
            setDateFilter(e.target.value)
            setPage(1)
          }}
          className="h-10 rounded-xl border border-border bg-card px-3 text-sm text-foreground transition-colors focus:border-accent-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
        />

        <button
          type="button"
          onClick={toggleSort}
          className="flex h-10 items-center gap-2 rounded-xl border border-border bg-card px-4 text-sm font-medium text-foreground transition-colors hover:bg-muted dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100 dark:hover:bg-zinc-800"
        >
          <Clock size={15} />
          {sortDir === 'desc' ? 'Newest first' : 'Oldest first'}
        </button>
      </div>

      {error && (
        <div
          role="alert"
          className="rounded-2xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-sm text-red-400"
        >
          {error}
        </div>
      )}

      {/* Table */}
      <div className="overflow-x-auto rounded-2xl border border-border bg-card shadow-sm dark:border-white/10 dark:bg-white/[0.03]">
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <Loader size="lg" />
          </div>
        ) : rows.length === 0 ? (
          <div className="flex flex-col items-center justify-center px-6 py-16 text-center">
            <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-muted text-muted-foreground dark:bg-white/[0.05]">
              <FileText size={22} strokeWidth={1.75} />
            </span>
            <p className="mt-4 text-sm font-medium text-foreground dark:text-white">
              No exports found
            </p>
            <p className="mt-1 max-w-xs text-sm text-muted-foreground dark:text-zinc-400">
              Try adjusting your search or filters.
            </p>
          </div>
        ) : (
          <table className="w-full min-w-[1080px] text-left text-sm">
            <thead>
              <tr className="border-b border-border text-xs tracking-wide text-muted-foreground uppercase dark:border-white/5 dark:text-zinc-500">
                <th scope="col" className="px-4 py-3 font-medium sm:px-6">User</th>
                <th scope="col" className="px-4 py-3 font-medium">Strategy</th>
                <th scope="col" className="px-4 py-3 font-medium">Type</th>
                <th scope="col" className="px-4 py-3 font-medium">Created</th>
                <th scope="col" className="px-4 py-3 font-medium">Status</th>
                <th scope="col" className="hidden px-4 py-3 font-medium md:table-cell">Size</th>
                <th scope="col" className="px-4 py-3 text-right font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => {
                const Icon = FORMAT_ICONS[row.format] ?? FileText
                const busy = downloadingId === row.id
                return (
                  <tr
                    key={row.id}
                    className="border-b border-border last:border-0 hover:bg-muted/40 dark:border-white/5 dark:hover:bg-white/[0.02]"
                  >
                    <td className="px-4 py-4 sm:px-6">
                      <div className="flex items-center gap-3">
                        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 text-xs font-semibold text-white">
                          {(row.user_name || row.user_email || '?')
                            .split(' ')
                            .map((p) => p[0])
                            .slice(0, 2)
                            .join('')
                            .toUpperCase()}
                        </span>
                        <div className="min-w-0">
                          <p className="truncate font-medium text-foreground dark:text-white">
                            {row.user_name || '—'}
                          </p>
                          <p className="truncate text-xs text-muted-foreground dark:text-zinc-500">
                            {row.user_email}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="max-w-52 px-4 py-4">
                      <p className="truncate text-foreground dark:text-zinc-200">
                        {row.strategy_name || 'Marketing strategy'}
                      </p>
                    </td>
                    <td className="px-4 py-4">
                      <span className="inline-flex items-center gap-1.5">
                        <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-600 dark:text-indigo-400">
                          <Icon size={13} />
                        </span>
                        <Badge variant="default">{FORMAT_LABELS[row.format] ?? row.format}</Badge>
                      </span>
                    </td>
                    <td className="px-4 py-4 text-muted-foreground dark:text-zinc-400">
                      {formatDate(row.created_at)}
                    </td>
                    <td className="px-4 py-4">
                      <Badge variant={STATUS_VARIANTS[row.status] ?? 'default'}>
                        {row.status}
                      </Badge>
                    </td>
                    <td className="hidden px-4 py-4 text-muted-foreground md:table-cell dark:text-zinc-400">
                      {formatBytes(row.file_size)}
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          type="button"
                          title="View"
                          onClick={() => openDetail(row)}
                          className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-muted hover:text-foreground dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-white"
                        >
                          <Eye size={15} />
                        </button>
                        <button
                          type="button"
                          title="Download"
                          disabled={busy}
                          onClick={() => handleDownload(row)}
                          className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-muted hover:text-foreground disabled:pointer-events-none disabled:opacity-50 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-white"
                        >
                          {busy ? (
                            <Loader2 size={15} className="animate-spin" />
                          ) : (
                            <Download size={15} />
                          )}
                        </button>
                        {row.file_url && (
                          <a
                            href={row.file_url}
                            target="_blank"
                            rel="noreferrer"
                            title="Open file"
                            className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-muted hover:text-foreground dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-white"
                          >
                            <ExternalLink size={15} />
                          </a>
                        )}
                        <button
                          type="button"
                          title="Delete export"
                          onClick={() => setPendingDelete(row)}
                          className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-red-500/10 hover:text-red-500 dark:text-zinc-400 dark:hover:text-red-400"
                        >
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      {total > 0 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground dark:text-zinc-400">
            Showing {rows.length} of {total} exports
          </p>
          <div className="flex items-center gap-2">
            <button
              type="button"
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
              className="rounded-lg border border-border bg-card px-3 py-1.5 text-sm font-medium text-foreground transition-colors hover:bg-muted disabled:pointer-events-none disabled:opacity-50 dark:border-white/10 dark:bg-white/[0.03] dark:text-zinc-100"
            >
              Prev
            </button>
            <span className="text-sm text-muted-foreground dark:text-zinc-400">
              {page} / {totalPages}
            </span>
            <button
              type="button"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
              className="rounded-lg border border-border bg-card px-3 py-1.5 text-sm font-medium text-foreground transition-colors hover:bg-muted disabled:pointer-events-none disabled:opacity-50 dark:border-white/10 dark:bg-white/[0.03] dark:text-zinc-100"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Detail modal: strategy + user */}
      <Modal
        open={detailRow !== null}
        onClose={() => setDetailRow(null)}
        title={detailRow?.strategy_name || 'Export details'}
      >
        {detailRow && (
          <div className="space-y-5">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-xl border border-border bg-muted/50 p-4 dark:border-white/10">
                <p className="text-xs font-semibold tracking-wide text-muted-foreground uppercase dark:text-zinc-500">
                  Export
                </p>
                <p className="mt-1 text-sm font-medium text-foreground dark:text-white">
                  {FORMAT_LABELS[detailRow.format] ?? detailRow.format}
                </p>
                <p className="mt-1 text-xs text-muted-foreground dark:text-zinc-400">
                  {formatDateTime(detailRow.created_at)}
                </p>
                <div className="mt-2">
                  <Badge variant={STATUS_VARIANTS[detailRow.status] ?? 'default'}>
                    {detailRow.status}
                  </Badge>
                </div>
                {detailRow.file_size !== null && detailRow.file_size !== undefined && (
                  <p className="mt-2 text-xs text-muted-foreground dark:text-zinc-400">
                    {formatBytes(detailRow.file_size)}
                  </p>
                )}
              </div>
              <div className="rounded-xl border border-border bg-muted/50 p-4 dark:border-white/10">
                <p className="text-xs font-semibold tracking-wide text-muted-foreground uppercase dark:text-zinc-500">
                  Strategy
                </p>
                <p className="mt-1 text-sm font-medium text-foreground dark:text-white">
                  {detailRow.strategy_name || 'Marketing strategy'}
                </p>
                <p className="mt-1 text-xs text-muted-foreground dark:text-zinc-400">
                  ID: {detailRow.strategy_id}
                </p>
              </div>
            </div>

            <div className="rounded-xl border border-border bg-muted/50 p-4 dark:border-white/10">
              <p className="flex items-center gap-1.5 text-xs font-semibold tracking-wide text-muted-foreground uppercase dark:text-zinc-500">
                <User size={12} />
                Owner
              </p>
              {detailLoading ? (
                <div className="mt-2 flex items-center gap-2 text-sm text-muted-foreground dark:text-zinc-400">
                  <Loader2 size={14} className="animate-spin" />
                  Loading user…
                </div>
              ) : (
                <>
                  <p className="mt-1 text-sm font-medium text-foreground dark:text-white">
                    {detailRow.user_name || '—'}
                  </p>
                  <p className="text-xs text-muted-foreground dark:text-zinc-400">
                    {detailRow.user_email}
                  </p>
                  {detailUser && (
                    <div className="mt-2 flex flex-wrap gap-2">
                      <Badge variant={detailUser.is_active ? 'success' : 'danger'}>
                        {detailUser.is_active ? 'Active' : 'Blocked'}
                      </Badge>
                      {detailUser.is_email_verified && (
                        <Badge variant="primary">Verified</Badge>
                      )}
                    </div>
                  )}
                </>
              )}
            </div>

            <div className="flex flex-wrap justify-end gap-3 pt-1">
              {detailRow.file_url && (
                <a
                  href={detailRow.file_url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex h-9 items-center justify-center gap-2 rounded-lg border border-border px-4 text-sm font-medium text-foreground transition-all duration-200 hover:bg-muted dark:border-zinc-700 dark:text-zinc-100 dark:hover:bg-zinc-800"
                >
                  <ExternalLink size={14} />
                  Open file
                </a>
              )}
              <Button variant="outline" size="sm" onClick={() => handleDownload(detailRow)}>
                {downloadingId === detailRow.id ? (
                  <Loader2 size={14} className="animate-spin" />
                ) : (
                  <Download size={14} />
                )}
                Download
              </Button>
              <Button size="sm" onClick={() => setDetailRow(null)}>
                Close
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Delete confirmation */}
      <Modal
        open={pendingDelete !== null}
        onClose={() => setPendingDelete(null)}
        title="Delete export"
      >
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground dark:text-zinc-300">
            Are you sure you want to permanently delete the{' '}
            <span className="font-semibold text-foreground dark:text-white">
              {FORMAT_LABELS[pendingDelete?.format] ?? pendingDelete?.format}
            </span>{' '}
            export{' '}
            <span className="font-semibold text-foreground dark:text-white">
              {pendingDelete?.strategy_name}
            </span>
            ? This removes the record and the file on disk. This cannot be undone.
          </p>
          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={() => setPendingDelete(null)} disabled={deleting}>
              Cancel
            </Button>
            <Button variant="danger" onClick={confirmDelete} disabled={deleting}>
              {deleting ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <Trash2 size={16} />
              )}
              Delete permanently
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
