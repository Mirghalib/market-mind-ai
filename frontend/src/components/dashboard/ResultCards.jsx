import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import {
  CalendarDays,
  Check,
  ChevronDown,
  Copy,
  Download,
  Layers,
  Mail,
  Megaphone,
  Rocket,
  Search,
  Share2,
  Swords,
  Users,
} from 'lucide-react'
import { cn } from '@/utils/cn'

const tones = {
  indigo: 'bg-indigo-500/15 text-indigo-600 dark:text-indigo-400',
  purple: 'bg-purple-500/15 text-purple-600 dark:text-purple-400',
  cyan: 'bg-cyan-500/15 text-cyan-600 dark:text-cyan-400',
  emerald: 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400',
  amber: 'bg-amber-500/15 text-amber-600 dark:text-amber-400',
  rose: 'bg-rose-500/15 text-rose-600 dark:text-rose-400',
  blue: 'bg-blue-500/15 text-blue-600 dark:text-blue-400',
  fuchsia: 'bg-fuchsia-500/15 text-fuchsia-600 dark:text-fuchsia-400',
}

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.08 } },
}

const cardVariants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.45, ease: 'easeOut' } },
}

async function copyToClipboard(text) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text)
    return
  }
  // Fallback for browsers without the async Clipboard API.
  const textarea = document.createElement('textarea')
  textarea.value = text
  textarea.style.position = 'fixed'
  textarea.style.opacity = '0'
  document.body.appendChild(textarea)
  textarea.select()
  document.execCommand('copy')
  document.body.removeChild(textarea)
}

function buildCardText(card) {
  const header = `${card.title}\n${card.description ?? ''}`
  const items = (card.items ?? []).map((item) => `- ${item}`).join('\n')
  return [header, items].filter(Boolean).join('\n\n')
}

/**
 * Displays AI strategy results. Each item:
 * { id, title, description, icon, tone, items?, content? }
 * Cards are expandable (when they have more content) and offer
 * copy / download / share actions. `content` can be a string or
 * an array of { heading, points[] } sections rendered as blocks.
 */
export default function ResultCards({ results, className }) {
  const [expanded, setExpanded] = useState({})
  const [copiedId, setCopiedId] = useState(null)
  const [sharedId, setSharedId] = useState(null)

  if (!results?.length) return null

  const toggleExpand = (id) => {
    setExpanded((current) => ({ ...current, [id]: !current[id] }))
  }

  const handleCopy = async (card) => {
    const text = buildCardText(card)
    try {
      await copyToClipboard(text)
      setCopiedId(card.id)
      setTimeout(() => setCopiedId(null), 2000)
    } catch {
      // Ignore clipboard failures — no API integration.
    }
  }

  const handleDownload = (card) => {
    const blob = new Blob([buildCardText(card)], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${card.title.toLowerCase().replace(/\s+/g, '-')}.txt`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const handleShare = async (card) => {
    const text = buildCardText(card)
    if (navigator.share) {
      try {
        await navigator.share({ title: card.title, text })
        return
      } catch {
        // User cancelled the native share sheet — fall through.
      }
    }
    try {
      await copyToClipboard(text)
      setSharedId(card.id)
      setTimeout(() => setSharedId(null), 2000)
    } catch {
      // Ignore share failures — no API integration.
    }
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className={cn('grid gap-5 sm:grid-cols-2 xl:grid-cols-3', className)}
    >
      {results.map((card) => {
        const isExpanded = expanded[card.id]
        const hasMore = card.content?.length > 0
        const Icon = card.icon
        return (
          <motion.article
            key={card.id}
            variants={cardVariants}
            className="group relative flex flex-col overflow-hidden rounded-2xl border border-zinc-200 bg-white shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-zinc-300 hover:shadow-md dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur dark:hover:border-white/20 dark:hover:shadow-xl"
          >
            {/* Hover glow */}
            <div
              aria-hidden
              className={cn(
                'pointer-events-none absolute -top-16 left-1/2 h-32 w-32 -translate-x-1/2 rounded-full blur-2xl opacity-0 transition-opacity duration-300 group-hover:opacity-100',
                tones[card.tone ?? 'indigo'].replace('text-', 'bg-').replace(/-400/, '/15')
              )}
            />

            {/* Header */}
            <div className="flex items-start justify-between gap-4 p-6 pb-4">
              <span
                className={cn(
                  'flex h-11 w-11 shrink-0 items-center justify-center rounded-xl',
                  tones[card.tone ?? 'indigo']
                )}
              >
                <Icon size={20} strokeWidth={1.75} />
              </span>

              <div className="flex items-center gap-1">
                <ActionButton
                  label="Copy"
                  onClick={() => handleCopy(card)}
                  active={copiedId === card.id}
                  activeIcon={<Check size={14} />}
                  icon={<Copy size={14} />}
                />
                <ActionButton
                  label="Download"
                  onClick={() => handleDownload(card)}
                  icon={<Download size={14} />}
                />
                <ActionButton
                  label="Share"
                  onClick={() => handleShare(card)}
                  active={sharedId === card.id}
                  activeIcon={<Check size={14} />}
                  icon={<Share2 size={14} />}
                />
              </div>
            </div>

            <div className="px-6">
              <h3 className="text-base font-semibold tracking-tight text-zinc-900 dark:text-white">
                {card.title}
              </h3>
              {card.description && (
                <p className="mt-1.5 text-sm leading-relaxed text-zinc-500 dark:text-zinc-400">
                  {card.description}
                </p>
              )}
            </div>

            {/* Summary items */}
            {card.items?.length > 0 && (
              <ul className="mt-4 space-y-2 px-6">
                {card.items.map((item) => (
                  <li
                    key={item}
                    className="flex items-start gap-2 text-sm text-zinc-500 dark:text-zinc-400"
                  >
                    <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-indigo-500 dark:bg-indigo-400" />
                    {item}
                  </li>
                ))}
              </ul>
            )}

            {/* Expandable details */}
            <AnimatePresence initial={false}>
              {isExpanded && hasMore && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3, ease: 'easeInOut' }}
                  className="overflow-hidden"
                >
                  <div className="mt-4 space-y-4 border-t border-zinc-100 px-6 pt-4 dark:border-white/5">
                    {card.content.map((section) => (
                      <div key={section.heading}>
                        <p className="text-xs font-semibold tracking-wide text-zinc-700 uppercase dark:text-zinc-300">
                          {section.heading}
                        </p>
                        <ul className="mt-2 space-y-1.5">
                          {section.points.map((point) => (
                            <li
                              key={point}
                              className="flex items-start gap-2 text-sm text-zinc-500 dark:text-zinc-400"
                            >
                              <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-zinc-300 dark:bg-zinc-600" />
                              {point}
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Expand toggle */}
            {hasMore && (
              <button
                type="button"
                onClick={() => toggleExpand(card.id)}
                aria-expanded={isExpanded}
                className="mt-4 flex items-center justify-center gap-1.5 border-t border-zinc-100 py-3 text-sm font-medium text-indigo-600 transition-colors hover:bg-zinc-50 dark:border-white/5 dark:text-indigo-400 dark:hover:bg-white/[0.02]"
              >
                {isExpanded ? 'Show less' : 'Show more'}
                <motion.span
                  animate={{ rotate: isExpanded ? 180 : 0 }}
                  transition={{ duration: 0.25, ease: 'easeInOut' }}
                  className="flex"
                >
                  <ChevronDown size={15} />
                </motion.span>
              </button>
            )}
          </motion.article>
        )
      })}
    </motion.div>
  )
}

function ActionButton({ label, onClick, icon, active, activeIcon }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={label}
      title={label}
      className={cn(
        'flex h-8 w-8 items-center justify-center rounded-lg transition-colors',
        active
          ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400'
          : 'text-zinc-500 hover:bg-zinc-100 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-white'
      )}
    >
      {active ? activeIcon : icon}
    </button>
  )
}

export { tones }
