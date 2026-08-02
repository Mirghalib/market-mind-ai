import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import {
  Download,
  FileDown,
  FileJson,
  FileText,
  FileType2,
  Loader2,
  Presentation,
  Share2,
  XCircle,
} from 'lucide-react'
import { dashboardService } from '@/services/dashboard'
import { cn } from '@/utils/cn'

const FORMATS = [
  { key: 'pdf', label: 'PDF', icon: FileText },
  { key: 'docx', label: 'DOCX', icon: FileType2 },
  { key: 'pptx', label: 'PPTX', icon: Presentation },
  { key: 'markdown', label: 'Markdown', icon: FileDown },
  { key: 'html', label: 'HTML', icon: FileText },
  { key: 'json', label: 'JSON', icon: FileJson },
]

/**
 * Public branded preview of a shared report. Renders the server-side
 * HTML preview page (works without authentication) and overlays a
 * per-format download bar. Invalid/expired links show a clear error.
 */
export default function SharedReport() {
  const { token } = useParams()
  const [html, setHtml] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [copying, setCopying] = useState(false)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError('')
    dashboardService
      .getSharePreview(token)
      .then(({ data }) => {
        if (!cancelled) setHtml(data)
      })
      .catch((err) => {
        if (!cancelled) {
          setError(
            err.response?.data?.detail ||
              err.response?.data?.message ||
              err.message ||
              'This report link is invalid or has expired.'
          )
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [token])

  const download = (format) => {
    const a = document.createElement('a')
    a.href = `/api/v1/s/${token}/download?format=${format}`
    a.download = ''
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }

  const copyLink = async () => {
    const url = window.location.href
    setCopying(true)
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(url)
      } else {
        const textarea = document.createElement('textarea')
        textarea.value = url
        document.body.appendChild(textarea)
        textarea.select()
        document.execCommand('copy')
        document.body.removeChild(textarea)
      }
    } finally {
      setCopying(false)
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-3 bg-zinc-50 text-zinc-500 dark:bg-zinc-950 dark:text-zinc-400">
        <Loader2 size={28} className="animate-spin text-indigo-500" />
        <p className="text-sm">Loading shared report…</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-zinc-50 px-6 text-center dark:bg-zinc-950">
        <span className="flex h-16 w-16 items-center justify-center rounded-2xl bg-red-500/10 text-red-500">
          <XCircle size={30} />
        </span>
        <h1 className="text-xl font-semibold text-zinc-900 dark:text-white">
          Report unavailable
        </h1>
        <p className="max-w-md text-sm leading-relaxed text-zinc-500 dark:text-zinc-400">
          {error}
        </p>
        <a
          href="/"
          className="mt-2 rounded-lg bg-indigo-500 px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-indigo-400"
        >
          Go to Market Mind AI
        </a>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950">
      {/* Download toolbar */}
      <div className="sticky top-0 z-40 border-b border-zinc-200 bg-white/90 backdrop-blur dark:border-zinc-800 dark:bg-zinc-900/90">
        <div className="mx-auto flex max-w-4xl flex-wrap items-center gap-2 px-4 py-3">
          <span className="mr-1 flex items-center gap-2 text-sm font-semibold text-zinc-800 dark:text-zinc-100">
            <Download size={16} className="text-indigo-500" />
            Download
          </span>
          {FORMATS.map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              type="button"
              onClick={() => download(key)}
              className={cn(
                'inline-flex items-center gap-1.5 rounded-lg border border-zinc-200 bg-white px-3 py-1.5 text-xs font-medium text-zinc-700 transition-colors hover:border-indigo-400 hover:text-indigo-600 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-200 dark:hover:text-indigo-300'
              )}
            >
              <Icon size={13} />
              {label}
            </button>
          ))}
          <button
            type="button"
            onClick={copyLink}
            className="ml-auto inline-flex items-center gap-1.5 rounded-lg bg-indigo-500 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-indigo-400"
          >
            <Share2 size={13} />
            {copying ? 'Copied!' : 'Copy link'}
          </button>
        </div>
      </div>

      {/* Server-rendered branded preview */}
      <div dangerouslySetInnerHTML={{ __html: html }} />
    </div>
  )
}
