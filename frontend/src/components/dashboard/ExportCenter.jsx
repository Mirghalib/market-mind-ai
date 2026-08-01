import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import {
  Check,
  Copy,
  Download,
  FileDown,
  FileText,
  FileType2,
  Loader2,
  Mail,
  Presentation,
  Share2,
  X,
} from 'lucide-react'
import Button from '@/components/ui/Button'
import Modal from '@/components/ui/Modal'
import { dashboardService } from '@/services/dashboard'
import { useAuth } from '@/context/AuthContext'
import { useToast } from '@/context/ToastContext'
import { cn } from '@/utils/cn'

async function copyToClipboard(text) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text)
    return
  }
  const textarea = document.createElement('textarea')
  textarea.value = text
  textarea.style.position = 'fixed'
  textarea.style.opacity = '0'
  document.body.appendChild(textarea)
  textarea.select()
  document.execCommand('copy')
  document.body.removeChild(textarea)
}

function saveBlob(blob, filename) {
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

/**
 * A per-button state machine: idle | loading | success | error.
 */
const IDLE = { status: 'idle' }

/**
 * Export Center shown after AI generation. Provides:
 *  - Download PDF / DOCX / PPTX (server-rendered, blob download)
 *  - Copy Markdown
 *  - Share (public report URL)
 *  - Email Report (SMTP link delivery)
 */
export default function ExportCenter({ strategyId, businessName }) {
  const { user } = useAuth()
  const { showToast } = useToast()
  const [states, setStates] = useState({})
  const [error, setError] = useState('')
  const [shareOpen, setShareOpen] = useState(false)
  const [emailOpen, setEmailOpen] = useState(false)
  const [sharedUrl, setSharedUrl] = useState('')

  const setState = (key, value) =>
    setStates((current) => ({ ...current, [key]: value }))

  const download = async (format) => {
    setState(format, { status: 'loading' })
    setError('')
    try {
      const { data } = await dashboardService.exportFile({
        strategy_id: strategyId,
        format,
      })
      saveBlob(data, `${businessName ?? 'strategy'}.${format}`)
      setState(format, { status: 'success' })
      showToast(`${format.toUpperCase()} report downloaded.`, 'success')
      setTimeout(() => setState(format, IDLE), 2000)
    } catch (err) {
      setState(format, { status: 'error' })
      const msg = errorMessage(err, `Could not download the ${format.toUpperCase()} report.`)
      setError(msg)
      showToast(msg, 'error')
    }
  }

  const copyMarkdown = async () => {
    setState('markdown', { status: 'loading' })
    setError('')
    try {
      const { data } = await dashboardService.exportFile({
        strategy_id: strategyId,
        format: 'markdown',
      })
      const text = await data.text()
      await copyToClipboard(text)
      setState('markdown', { status: 'success' })
      showToast('Markdown copied to clipboard.', 'success')
      setTimeout(() => setState('markdown', IDLE), 2000)
    } catch (err) {
      setState('markdown', { status: 'error' })
      const msg = errorMessage(err, 'Could not copy the Markdown report.')
      setError(msg)
      showToast(msg, 'error')
    }
  }

  const openShare = async () => {
    setError('')
    try {
      // Ensure a PDF export exists, then create a secure share link.
      await dashboardService.exportFile({
        strategy_id: strategyId,
        format: 'pdf',
      })
      const { data: exports } = await dashboardService.getExports({
        strategy_id: strategyId,
        limit: 1,
      })
      const latest = exports.items?.[0]
      if (!latest?.id) throw new Error('No export record found.')
      const { data } = await dashboardService.shareExport(latest.id, { expires_in_days: 7 })
      setSharedUrl(data.url)
      setShareOpen(true)
    } catch (err) {
      const msg = errorMessage(err, 'Could not prepare the report for sharing.')
      setError(msg)
      showToast(msg, 'error')
    }
  }

  const handleNativeShare = async () => {
    if (!navigator.share) return
    try {
      await navigator.share({ title: 'Marketing Strategy Report', url: sharedUrl })
    } catch {
      // User cancelled the native share sheet.
    }
  }

  const emailSent = (email) => {
    setEmailOpen(false)
    setState('email', { status: 'success' })
    showToast(`Report sent to ${email}.`, 'success')
    setTimeout(() => setState('email', IDLE), 4000)
  }

  const buttons = [
    { key: 'pdf', label: 'Download PDF', icon: FileText, format: 'pdf' },
    { key: 'docx', label: 'Download DOCX', icon: FileType2, format: 'docx' },
    { key: 'pptx', label: 'Download PPTX', icon: Presentation, format: 'pptx' },
    { key: 'markdown', label: 'Copy Markdown', icon: Copy, onClick: copyMarkdown },
    { key: 'share', label: 'Share', icon: Share2, onClick: openShare },
    { key: 'email', label: 'Email Report', icon: Mail, onClick: () => setEmailOpen(true) },
  ]

  return (
    <div className="rounded-2xl border border-indigo-500/20 bg-indigo-500/[0.04] p-5 dark:border-indigo-400/20">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold tracking-wide text-indigo-600 uppercase dark:text-indigo-400">
            Export Center
          </p>
          <p className="mt-1 text-sm text-muted-foreground dark:text-zinc-400">
            Download a professional report or share it with your team.
          </p>
        </div>
      </div>

      <div className="mt-4 grid gap-2.5 sm:grid-cols-2 lg:grid-cols-3">
        {buttons.map(({ key, label, icon: Icon, format, onClick }) => {
          const state = states[key] ?? IDLE
          const busy = state.status === 'loading'
          const success = state.status === 'success'
          const click = onClick ?? (format ? () => download(format) : () => {})
          return (
            <button
              key={key}
              type="button"
              onClick={click}
              disabled={busy}
              className={cn(
                'flex items-center justify-center gap-2 rounded-xl border px-4 py-2.5 text-sm font-medium transition-all duration-200',
                success
                  ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
                  : 'border-border bg-card text-foreground hover:border-indigo-500/50 hover:bg-indigo-500/5 dark:border-white/10 dark:bg-white/[0.03] dark:text-zinc-100 dark:hover:bg-white/[0.06]',
                busy && 'pointer-events-none opacity-60'
              )}
            >
              {busy ? (
                <Loader2 size={16} className="animate-spin" />
              ) : success ? (
                <Check size={16} />
              ) : (
                <Icon size={16} />
              )}
              {success ? (key === 'markdown' ? 'Copied!' : 'Downloaded!') : label}
            </button>
          )
        })}
      </div>

      {error && (
        <div
          role="alert"
          className="mt-4 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-500 dark:text-red-400"
        >
          {error}
        </div>
      )}

      {/* Share modal */}
      <Modal open={shareOpen} onClose={() => setShareOpen(false)} title="Share report">
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground dark:text-zinc-300">
            Your report is ready. Share the secure link so stakeholders can open it
            directly — the link expires in 7 days.
          </p>
          <div className="flex items-center gap-2 rounded-xl border border-border bg-card px-3 py-2.5 dark:border-white/10 dark:bg-zinc-900">
            <span className="min-w-0 flex-1 truncate text-sm text-muted-foreground dark:text-zinc-400">
              {sharedUrl}
            </span>
            <button
              type="button"
              onClick={async () => {
                await copyToClipboard(sharedUrl)
                setShareOpen(false)
                setState('share', { status: 'success' })
                setTimeout(() => setState('share', IDLE), 2000)
              }}
              className="shrink-0 rounded-lg bg-indigo-500/15 px-3 py-1.5 text-sm font-medium text-indigo-600 transition-colors hover:bg-indigo-500/25 dark:text-indigo-400"
            >
              Copy link
            </button>
            <a
              href={sharedUrl}
              target="_blank"
              rel="noreferrer"
              className="shrink-0 rounded-lg bg-indigo-500/15 px-3 py-1.5 text-sm font-medium text-indigo-600 transition-colors hover:bg-indigo-500/25 dark:text-indigo-400"
            >
              Open
            </a>
          </div>
          {navigator.share && (
            <Button variant="outline" className="w-full" onClick={handleNativeShare}>
              <Share2 size={16} />
              Share via…
            </Button>
          )}
        </div>
      </Modal>

      {/* Email modal */}
      <AnimatePresence>
        {emailOpen && (
          <EmailModal
            onClose={() => setEmailOpen(false)}
            defaultEmail={user?.email ?? ''}
            onSent={emailSent}
            strategyId={strategyId}
          />
        )}
      </AnimatePresence>
    </div>
  )
}

function EmailModal({ onClose, defaultEmail, onSent, strategyId }) {
  const [email, setEmail] = useState(defaultEmail)
  const [format, setFormat] = useState('pdf')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      // Ensure the report exists in the requested format, then email its link.
      await dashboardService.exportFile({ strategy_id: strategyId, format })
      const { data } = await dashboardService.getExports({
        strategy_id: strategyId,
        limit: 1,
      })
      const latest = data.items?.[0]
      if (!latest) throw new Error('No export record found.')
      await dashboardService.emailExport(latest.id, { to_email: email })
      onSent(email)
    } catch (err) {
      setError(errorMessage(err, 'Could not send the email.'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal open onClose={onClose} title="Email report">
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-foreground dark:text-zinc-200">
            Recipient email
          </label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="stakeholder@company.com"
            className="h-11 w-full rounded-lg border border-border bg-card px-3.5 text-sm text-foreground placeholder-zinc-400 transition-colors focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
          />
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-foreground dark:text-zinc-200">
            Report format
          </label>
          <select
            value={format}
            onChange={(e) => setFormat(e.target.value)}
            className="h-11 w-full rounded-lg border border-border bg-card px-3.5 text-sm text-foreground transition-colors focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
          >
            <option value="pdf">PDF</option>
            <option value="docx">DOCX</option>
            <option value="pptx">PPTX</option>
          </select>
        </div>

        {error && (
          <div
            role="alert"
            className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-500 dark:text-red-400"
          >
            {error}
          </div>
        )}

        <div className="flex justify-end gap-3 pt-1">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={loading}>
            {loading ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Sending…
              </>
            ) : (
              <>
                <Mail size={16} />
                Send report
              </>
            )}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
