import { motion } from 'framer-motion'
import { Info, Sparkles } from 'lucide-react'
import { APP_NAME } from '@/constants'

/**
 * About section — static product info, version, and links.
 */
export default function AboutSettings() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm sm:p-8 dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur"
    >
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/15 text-indigo-600 dark:text-indigo-400">
          <Info size={19} strokeWidth={1.75} />
        </span>
        <div>
          <h2 className="text-base font-semibold text-zinc-900 dark:text-white">About</h2>
          <p className="text-sm text-zinc-500 dark:text-zinc-400">
            Everything about this product.
          </p>
        </div>
      </div>

      <div className="mt-6 flex items-center gap-4">
        <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 shadow-lg shadow-indigo-500/25">
          <Sparkles size={22} className="text-white" />
        </span>
        <div>
          <p className="text-base font-semibold text-zinc-900 dark:text-white">{APP_NAME}</p>
          <p className="text-sm text-zinc-500 dark:text-zinc-400">
            AI-powered market intelligence platform
          </p>
        </div>
      </div>

      <dl className="mt-6 grid gap-4 sm:grid-cols-2">
        <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-4 dark:border-white/5 dark:bg-white/[0.02]">
          <dt className="text-xs font-medium tracking-wide text-zinc-500 uppercase dark:text-zinc-400">
            Version
          </dt>
          <dd className="mt-1 text-sm font-semibold text-zinc-900 dark:text-white">0.1.0</dd>
        </div>
        <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-4 dark:border-white/5 dark:bg-white/[0.02]">
          <dt className="text-xs font-medium tracking-wide text-zinc-500 uppercase dark:text-zinc-400">
            Status
          </dt>
          <dd className="mt-1 text-sm font-semibold text-emerald-600 dark:text-emerald-400">
            All systems operational
          </dd>
        </div>
      </dl>

      <div className="mt-6 flex flex-wrap gap-3">
        {['Documentation', 'Changelog', 'Support'].map((label) => (
          <a
            key={label}
            href="#"
            className="text-sm font-medium text-indigo-600 transition-colors hover:text-indigo-500 dark:text-indigo-400 dark:hover:text-indigo-300"
          >
            {label}
          </a>
        ))}
      </div>
    </motion.div>
  )
}
