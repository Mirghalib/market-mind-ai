import { useState } from 'react'
import { motion } from 'framer-motion'
import { Check, Copy, Eye, EyeOff, Key, RefreshCw } from 'lucide-react'
import Button from '@/components/ui/Button'
import { cn } from '@/utils/cn'

const PLACEHOLDER_KEY = 'mmai_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

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
 * API key placeholder. Copy and reveal are client-side only;
 * no key is stored or fetched. Wire to your API later.
 */
export default function ApiKeySettings() {
  const [visible, setVisible] = useState(false)
  const [copied, setCopied] = useState(false)

  const masked = `${PLACEHOLDER_KEY.slice(0, 12)}${'•'.repeat(20)}`

  const handleCopy = async () => {
    try {
      await copyToClipboard(PLACEHOLDER_KEY)
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
      className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm sm:p-8 dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur"
    >
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/15 text-cyan-600 dark:text-cyan-400">
          <Key size={19} strokeWidth={1.75} />
        </span>
        <div>
          <h2 className="text-base font-semibold text-zinc-900 dark:text-white">API key</h2>
          <p className="text-sm text-zinc-500 dark:text-zinc-400">
            Used to integrate Market Mind AI with your tools.
          </p>
        </div>
      </div>

      <div className="mt-6">
        <p className="mb-1.5 text-sm font-medium text-zinc-700 dark:text-zinc-300">
          Your key
        </p>
        <div className="flex flex-col gap-2 sm:flex-row">
          <div className="flex h-11 flex-1 items-center gap-2 overflow-hidden rounded-lg border border-zinc-200 bg-zinc-50 px-3.5 font-mono text-sm text-zinc-600 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300">
            <span className="truncate">{visible ? PLACEHOLDER_KEY : masked}</span>
            <button
              type="button"
              onClick={() => setVisible((v) => !v)}
              aria-label={visible ? 'Hide API key' : 'Show API key'}
              className="ml-auto shrink-0 text-zinc-400 transition-colors hover:text-zinc-900 dark:hover:text-white"
            >
              {visible ? <EyeOff size={15} /> : <Eye size={15} />}
            </button>
          </div>
          <Button type="button" variant="outline" onClick={handleCopy}>
            {copied ? (
              <>
                <Check size={15} className="text-emerald-500" />
                Copied
              </>
            ) : (
              <>
                <Copy size={15} />
                Copy
              </>
            )}
          </Button>
        </div>
      </div>

      <div className="mt-5 flex flex-col items-start justify-between gap-4 rounded-xl border border-zinc-200 bg-zinc-50 p-4 sm:flex-row sm:items-center dark:border-white/5 dark:bg-white/[0.02]">
        <div>
          <p className="text-sm font-medium text-zinc-900 dark:text-white">Regenerate key</p>
          <p className="mt-0.5 text-sm text-zinc-500 dark:text-zinc-400">
            Invalidates the current key immediately.
          </p>
        </div>
        <Button type="button" variant="ghost" size="sm" onClick={() => {}}>
          <RefreshCw size={15} />
          Regenerate
        </Button>
      </div>
    </motion.div>
  )
}
