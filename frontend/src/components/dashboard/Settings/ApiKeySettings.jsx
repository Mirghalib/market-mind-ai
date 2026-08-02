import { useState } from 'react'
import { motion } from 'framer-motion'
import { Copy, Eye, EyeOff, Key } from 'lucide-react'
import Button from '@/components/ui/Button'

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

/**
 * API key section. The platform does not yet issue per-user API keys;
 * this card explains the status instead of pretending to work.
 */
export default function ApiKeySettings() {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await copyToClipboard('mmai_api_access_pending')
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // Ignore clipboard failures.
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="rounded-2xl border border-border bg-card p-6 shadow-sm sm:p-8 dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur"
    >
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/15 text-cyan-600 dark:text-cyan-400">
          <Key size={19} strokeWidth={1.75} />
        </span>
        <div>
          <h2 className="text-base font-semibold text-foreground dark:text-white">API key</h2>
          <p className="text-sm text-muted-foreground dark:text-zinc-400">
            Used to integrate Market Mind AI with your tools.
          </p>
        </div>
      </div>

      <div className="mt-6 rounded-xl border border-border bg-muted p-5 dark:border-white/5 dark:bg-white/[0.02]">
        <p className="text-sm font-medium text-foreground dark:text-white">
          API access is coming soon
        </p>
        <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground dark:text-zinc-400">
          Per-user API keys will be available in an upcoming release. For now, use
          the dashboard to generate, export, and share strategies — every feature
          you need is already here.
        </p>
        <div className="mt-4 flex flex-col gap-2 sm:flex-row sm:items-center">
          <div className="flex h-11 flex-1 items-center gap-2 overflow-hidden rounded-lg border border-border bg-card px-3.5 font-mono text-sm text-muted-foreground dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300">
            <span className="truncate">{'mmai_api_access_pending'}</span>
            <Eye size={15} className="ml-auto shrink-0 text-muted-foreground/50" />
          </div>
          <Button type="button" variant="outline" size="sm" onClick={handleCopy}>
            {copied ? 'Copied' : 'Copy'}
          </Button>
        </div>
      </div>
    </motion.div>
  )
}
