import { useCallback, useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  Clock,
  Copy,
  Download,
  ExternalLink,
  FileText,
  Loader2,
  Mail,
  Presentation,
  FileType2,
  FileJson,
  FileDown,
  AlertTriangle,
  Share2,
} from 'lucide-react'
import DashboardHeader from '@/components/dashboard/DashboardHeader'
import HistoryTable from '@/components/dashboard/HistoryTable'
import Button from '@/components/ui/Button'
import Modal from '@/components/ui/Modal'
import Badge from '@/components/ui/Badge'
import Loader from '@/components/ui/Loader'
import { dashboardService } from '@/services/dashboard'
import { cn } from '@/utils/cn'

/**
 * Map backend GenerationHistoryRead records to the HistoryTable row
 * shape: { id, title, type, createdAt, status }.
 */
function toRows(records = []) {
  return records.map((record) => ({
    id: record.id,
    title: record.input_params?.project_name || 'Marketing strategy',
    type: record.model_used || 'AI strategy',
    createdAt: record.created_at
      ? new Date(record.created_at).toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric',
        })
      : '—',
    status: record.status === 'success' ? 'completed' : 'failed',
  }))
}

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

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
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

function errorMessage(err, fallback) {
  return (
    err.response?.data?.detail ||
    err.response?.data?.message ||
    err.message ||
    fallback
  )
}

function ExportsTable({ rows }) {
  const [downloadingId, setDownloadingId] = useState(null)
  const [sharingRow, setSharingRow] = useState(null)
  const [emailRow, setEmailRow] = useState(null)
  const [shareUrl, setShareUrl] = useState('')
  const [shareBusy, setShareBusy] = useState(false)
  const [copied, setCopied] = useState(false)
  const [emailSending, setEmailSending] = useState(false)
  const [emailTo, setEmailTo] = useState('')
  const [emailError, setEmailError] = useState('')
  const [actionError, setActionError] = useState('')

  const handleDownload = async (row) => {
    setDownloadingId(row.id)
    setActionError('')
    try {
      const { data } = await dashboardService.downloadExport(row.id)
      downloadBlob(data, `${row.title ?? 'strategy'}.${row.format}`)
    } catch (err) {
      setActionError(errorMessage(err, 'Could not download the export.'))
    } finally {
      setDownloadingId(null)
    }
  }

  const openShare = async (row) => {
    setSharingRow(row)
    setShareBusy(true)
    setActionError('')
    try {
      const { data } = await dashboardService.shareExport(row.id, { expires_in_days: 7 })
      setShareUrl(data.url)
    } catch (err) {
      setActionError(errorMessage(err, 'Could not create the share link.'))
      setSharingRow(null)
    } finally {
      setShareBusy(false)
    }
  }

  const copyShare = async () => {
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(shareUrl)
      } else {
        const textarea = document.createElement('textarea')
        textarea.value = shareUrl
        document.body.appendChild(textarea)
        textarea.select()
        document.execCommand('copy')
        document.body.removeChild(textarea)
      }
      setCopied(true)
      window.setTimeout(() => setCopied(false), 2000)
    } catch {
      setActionError('Could not copy the link.')
    }
  }

  const sendEmail = async (e) => {
    e.preventDefault()
    setEmailSending(true)
    setEmailError('')
    try {
      await dashboardService.emailExport(emailRow.id, { to_email: emailTo })
      setEmailRow(null)
      setEmailTo('')
      setActionError('')
    } catch (err) {
      setEmailError(errorMessage(err, 'Could not send the email.'))
    } finally {
      setEmailSending(false)
    }
  }

  if (rows.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-2xl border border-border bg-card px-6 py-16 text-center dark:border-white/10">
        <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-muted text-muted-foreground dark:bg-white/[0.05]">
          <FileText size={22} strokeWidth={1.75} />
        </span>
        <p className="mt-4 text-sm font-medium text-foreground dark:text-white">
          No exports yet
        </p>
        <p className="mt-1 max-w-xs text-sm text-muted-foreground dark:text-zinc-400">
          Download a PDF, DOCX or PPTX from the Export Center after generating a
          strategy — your saved reports will appear here.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {actionError && (
        <div
          role="alert"
          className="rounded-2xl border border-red-500/30 bg-red-500/10 px-5 py-3 text-sm text-red-500 dark:text-red-400"
        >
          {actionError}
        </div>
      )}

      <div className="overflow-x-auto rounded-2xl border border-border bg-card shadow-sm dark:border-white/10 dark:bg-white/[0.03]">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead>
            <tr className="border-b border-border text-xs tracking-wide text-muted-foreground uppercase dark:border-white/5 dark:text-zinc-500">
              <th scope="col" className="px-4 py-3 font-medium sm:px-6">Report</th>
              <th scope="col" className="px-4 py-3 font-medium">Format</th>
              <th scope="col" className="px-4 py-3 font-medium">Created</th>
              <th scope="col" className="px-4 py-3 font-medium">Status</th>
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
                  className="border-b border-border last:border-0 dark:border-white/5"
                >
                  <td className="px-4 py-4 sm:px-6">
                    <div className="flex items-center gap-3">
                      <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-600 dark:text-indigo-400">
                        <Icon size={15} />
                      </span>
                      <div className="min-w-0">
                        <p className="truncate font-medium text-foreground dark:text-white">
                          {row.title}
                        </p>
                        <p className="text-xs text-muted-foreground dark:text-zinc-500">
                          {row.strategyName || 'Marketing strategy'}
                        </p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <Badge variant="default">{FORMAT_LABELS[row.format] ?? row.format}</Badge>
                  </td>
                  <td className="px-4 py-4">
                    <span className="flex items-center gap-1.5 text-muted-foreground dark:text-zinc-400">
                      <Clock size={13} />
                      {formatDate(row.createdAt)}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <Badge variant={STATUS_VARIANTS[row.status] ?? 'default'}>
                      {row.status}
                    </Badge>
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex items-center justify-end gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDownload(row)}
                        disabled={busy}
                      >
                        {busy ? (
                          <Loader2 size={15} className="animate-spin" />
                        ) : (
                          <Download size={15} />
                        )}
                        Download
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => openShare(row)}
                      >
                        <Share2 size={15} />
                        Share
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setEmailRow(row)}
                      >
                        <Mail size={15} />
                        Email
                      </Button>
                      {row.fileUrl && (
                        <a
                          href={row.fileUrl}
                          target="_blank"
                          rel="noreferrer"
                          className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-muted hover:text-foreground dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-white"
                          aria-label="Open report"
                          title="Open report"
                        >
                          <ExternalLink size={15} />
                        </a>
                      )}
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Share modal */}
      <Modal open={sharingRow !== null} onClose={() => setSharingRow(null)} title="Share report">
        <div className="space-y-4">
          {shareBusy ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 size={22} className="animate-spin text-indigo-500" />
            </div>
          ) : (
            <>
              <p className="text-sm text-muted-foreground dark:text-zinc-300">
                Anyone with this link can open the report. It expires in 7 days.
              </p>
              <div className="flex items-center gap-2 rounded-xl border border-border bg-card px-3 py-2.5 dark:border-white/10 dark:bg-zinc-900">
                <span className="min-w-0 flex-1 truncate text-sm text-muted-foreground dark:text-zinc-400">
                  {shareUrl}
                </span>
                <button
                  type="button"
                  onClick={copyShare}
                  className="shrink-0 rounded-lg bg-indigo-500/15 px-3 py-1.5 text-sm font-medium text-indigo-600 transition-colors hover:bg-indigo-500/25 dark:text-indigo-400"
                >
                  {copied ? 'Copied!' : 'Copy link'}
                </button>
                <a
                  href={shareUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="shrink-0 rounded-lg bg-indigo-500/15 px-3 py-1.5 text-sm font-medium text-indigo-600 transition-colors hover:bg-indigo-500/25 dark:text-indigo-400"
                >
                  Open
                </a>
              </div>
            </>
          )}
        </div>
      </Modal>

      {/* Email modal */}
      <Modal open={emailRow !== null} onClose={() => setEmailRow(null)} title="Email report">
        <form onSubmit={sendEmail} className="space-y-4">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-foreground dark:text-zinc-200">
              Recipient email
            </label>
            <input
              type="email"
              required
              value={emailTo}
              onChange={(e) => setEmailTo(e.target.value)}
              placeholder="stakeholder@company.com"
              className="h-11 w-full rounded-lg border border-border bg-card px-3.5 text-sm text-foreground transition-colors focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/30 focus:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
            />
          </div>
          {emailError && (
            <div
              role="alert"
              className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-500 dark:text-red-400"
            >
              {emailError}
            </div>
          )}
          <div className="flex justify-end gap-3 pt-1">
            <Button type="button" variant="outline" onClick={() => setEmailRow(null)}>
              Cancel
            </Button>
            <Button type="submit" disabled={emailSending}>
              {emailSending ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <Mail size={16} />
              )}
              Send report
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}

export default function History() {
  const [searchParams] = useSearchParams()
  const [tab, setTab] = useState(searchParams.get('q') ? 'generations' : 'generations')
  const [rows, setRows] = useState([])
  const [exports, setExports] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [pendingDelete, setPendingDelete] = useState(null)
  const [deleting, setDeleting] = useState(false)
  const initialQuery = searchParams.get('q') || ''

  const loadGenerations = useCallback(async () => {
    const { data } = await dashboardService.getHistory({ limit: 100 })
    setRows(toRows(data.items))
  }, [])

  const loadExports = useCallback(async () => {
    const { data } = await dashboardService.getExports({ limit: 100 })
    setExports(
      data.items.map((item) => ({
        id: item.id,
        title: item.strategy_name || 'Marketing strategy',
        format: item.format,
        status: item.status,
        createdAt: item.created_at,
        fileUrl: item.file_url,
      }))
    )
  }, [])

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      await Promise.all([loadGenerations(), loadExports()])
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          err.response?.data?.message ||
          err.message ||
          'Could not load your history.'
      )
    } finally {
      setLoading(false)
    }
  }, [loadGenerations, loadExports])

  useEffect(() => {
    load()
  }, [load])

  const confirmDelete = async () => {
    if (!pendingDelete) return
    setDeleting(true)
    try {
      await dashboardService.deleteHistory(pendingDelete.id)
      setRows((current) => current.filter((row) => row.id !== pendingDelete.id))
      setPendingDelete(null)
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          err.response?.data?.message ||
          err.message ||
          'Could not delete this record.'
      )
    } finally {
      setDeleting(false)
    }
  }

  return (
    <div className="mx-auto max-w-7xl space-y-8 p-6 sm:p-8">
      <DashboardHeader
        eyebrow="Library"
        title="History"
        subtitle="Browse, filter, and manage your past analyses and saved reports."
      />

      {/* Tabs: Generations | Exports */}
      <div className="flex gap-1 rounded-xl border border-border bg-card p-1 sm:w-fit dark:border-white/10 dark:bg-white/[0.03]">
        {[
          { key: 'generations', label: 'Generations' },
          { key: 'exports', label: 'Exports' },
        ].map((item) => (
          <button
            key={item.key}
            type="button"
            onClick={() => setTab(item.key)}
            aria-pressed={tab === item.key}
            className={cn(
              'flex-1 rounded-lg px-4 py-2 text-sm font-medium transition-colors sm:flex-none',
              tab === item.key
                ? 'bg-indigo-500/15 text-indigo-600 dark:text-indigo-300'
                : 'text-muted-foreground hover:bg-muted hover:text-foreground dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-white'
            )}
          >
            {item.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex items-center justify-center rounded-2xl border border-border bg-card py-20 dark:border-white/10">
          <Loader size="lg" />
        </div>
      ) : error ? (
        <div
          role="alert"
          className="rounded-2xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-sm text-red-400"
        >
          {error}
        </div>
      ) : tab === 'exports' ? (
        <ExportsTable rows={exports} />
      ) : (
        <HistoryTable
          rows={rows}
          onDelete={setPendingDelete}
          initialQuery={initialQuery}
        />
      )}

      {/* Delete confirmation */}
      <Modal
        open={pendingDelete !== null}
        onClose={() => setPendingDelete(null)}
        title="Delete analysis"
      >
        <div className="flex items-start gap-4">
          <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-red-500/15 text-red-500 dark:text-red-400">
            <AlertTriangle size={20} />
          </span>
          <div>
            <p className="text-sm text-muted-foreground dark:text-zinc-300">
              Are you sure you want to delete{' '}
              <span className="font-semibold text-foreground dark:text-white">
                {pendingDelete?.title}
              </span>
              ? This action cannot be undone.
            </p>
          </div>
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <Button variant="outline" onClick={() => setPendingDelete(null)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={confirmDelete} disabled={deleting}>
            {deleting ? 'Deleting…' : 'Delete'}
          </Button>
        </div>
      </Modal>
    </div>
  )
}
