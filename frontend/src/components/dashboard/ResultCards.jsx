import { motion } from 'framer-motion'
import { Copy, RefreshCw } from 'lucide-react'
import Button from '@/components/ui/Button'
import { cn } from '@/utils/cn'

const tones = {
  indigo: 'bg-indigo-500/15 text-indigo-600 dark:text-indigo-400',
  purple: 'bg-purple-500/15 text-purple-600 dark:text-purple-400',
  cyan: 'bg-cyan-500/15 text-cyan-600 dark:text-cyan-400',
  emerald: 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400',
  amber: 'bg-amber-500/15 text-amber-600 dark:text-amber-400',
  rose: 'bg-rose-500/15 text-rose-600 dark:text-rose-400',
}

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.08 } },
}

const cardVariants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.45, ease: 'easeOut' } },
}

/**
 * Displays AI strategy results. Each item: { id, title, description, icon, tone, items? }.
 * `onCopy` / `onRegenerate` are optional callbacks (wired up by the page, no backend here).
 */
export default function ResultCards({
  results,
  onCopy,
  onRegenerate,
  className,
}) {
  if (!results?.length) return null

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className={cn('grid gap-5 sm:grid-cols-2 xl:grid-cols-3', className)}
    >
      {results.map(({ id, title, description, icon: Icon, tone = 'indigo', items }) => (
        <motion.article
          key={id}
          variants={cardVariants}
          className="group relative flex flex-col overflow-hidden rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-zinc-300 hover:shadow-md dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur dark:hover:border-white/20 dark:hover:shadow-xl"
        >
          <div
            aria-hidden
            className={cn(
              'pointer-events-none absolute -top-16 left-1/2 h-32 w-32 -translate-x-1/2 rounded-full blur-2xl opacity-0 transition-opacity duration-300 group-hover:opacity-100',
              tones[tone].replace('text-', 'bg-').replace(/-400/, '/15')
            )}
          />

          <div className="flex items-start justify-between gap-4">
            <span
              className={cn(
                'flex h-11 w-11 shrink-0 items-center justify-center rounded-xl',
                tones[tone]
              )}
            >
              <Icon size={20} strokeWidth={1.75} />
            </span>
            {(onCopy || onRegenerate) && (
              <div className="flex items-center gap-1">
                {onCopy && (
                  <button
                    type="button"
                    onClick={() => onCopy?.(id)}
                    aria-label={`Copy ${title}`}
                    title="Copy"
                    className="flex h-8 w-8 items-center justify-center rounded-lg text-zinc-500 transition-colors hover:bg-white/5 hover:text-white"
                  >
                    <Copy size={15} />
                  </button>
                )}
                {onRegenerate && (
                  <button
                    type="button"
                    onClick={() => onRegenerate?.(id)}
                    aria-label={`Regenerate ${title}`}
                    title="Regenerate"
                    className="flex h-8 w-8 items-center justify-center rounded-lg text-zinc-500 transition-colors hover:bg-white/5 hover:text-white"
                  >
                    <RefreshCw size={15} />
                  </button>
                )}
              </div>
            )}
          </div>

          <h3 className="mt-4 text-base font-semibold tracking-tight text-zinc-900 dark:text-white">
            {title}
          </h3>
          {description && (
            <p className="mt-1.5 text-sm leading-relaxed text-zinc-500 dark:text-zinc-400">{description}</p>
          )}

          {items?.length > 0 && (
            <ul className="mt-4 space-y-2 border-t border-zinc-100 pt-4 dark:border-white/5">
              {items.map((item) => (
                <li key={item} className="flex items-start gap-2 text-sm text-zinc-500 dark:text-zinc-400">
                  <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-indigo-500 dark:bg-indigo-400" />
                  {item}
                </li>
              ))}
            </ul>
          )}
        </motion.article>
      ))}
    </motion.div>
  )
}

export { tones }
