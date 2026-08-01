import { motion } from 'framer-motion'
import {
  Ban,
  FileDown,
  Mail,
  Sparkles,
  UserCheck,
  UserPlus,
  Users,
} from 'lucide-react'
import { cn } from '@/utils/cn'

const TYPE_STYLES = {
  user_registered: {
    icon: UserPlus,
    className: 'bg-indigo-500/15 text-indigo-600 dark:text-indigo-400',
  },
  strategy_generated: {
    icon: Sparkles,
    className: 'bg-purple-500/15 text-purple-600 dark:text-purple-400',
  },
  export_created: {
    icon: FileDown,
    className: 'bg-cyan-500/15 text-cyan-600 dark:text-cyan-400',
  },
  user_blocked: {
    icon: Ban,
    className: 'bg-rose-500/15 text-rose-600 dark:text-rose-400',
  },
  invitation_accepted: {
    icon: UserCheck,
    className: 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400',
  },
  email_sent: {
    icon: Mail,
    className: 'bg-amber-500/15 text-amber-600 dark:text-amber-400',
  },
}

function timeAgo(value) {
  if (!value) return ''
  const date = new Date(value)
  const seconds = Math.max(0, Math.floor((Date.now() - date.getTime()) / 1000))
  if (seconds < 60) return 'just now'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days}d ago`
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

export default function RecentActivity({ events = [], className }) {
  return (
    <div className={cn('flex h-full flex-col', className)}>
      <ul className="space-y-1">
        {events.map((event, i) => {
          const style = TYPE_STYLES[event.type] ?? {
            icon: Users,
            className: 'bg-muted text-muted-foreground dark:bg-zinc-800 dark:text-zinc-300',
          }
          const Icon = style.icon
          return (
            <motion.li
              key={`${event.type}-${i}`}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: i * 0.04 }}
              className="flex items-start gap-3 rounded-xl px-2 py-2.5 transition-colors hover:bg-muted/50 dark:hover:bg-white/[0.02]"
            >
              <span
                className={cn(
                  'mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg',
                  style.className
                )}
              >
                <Icon size={15} strokeWidth={1.75} />
              </span>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm text-foreground dark:text-zinc-200">
                  {event.message}
                </p>
                <p className="text-xs text-muted-foreground dark:text-zinc-500">
                  {timeAgo(event.created_at)}
                </p>
              </div>
            </motion.li>
          )
        })}
      </ul>
    </div>
  )
}
