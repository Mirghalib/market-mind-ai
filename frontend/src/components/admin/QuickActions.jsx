import { Download, UserPlus, Users, UserSquare } from 'lucide-react'
import { cn } from '@/utils/cn'

const actions = [
  {
    key: 'invite',
    label: 'Invite User',
    description: 'Send an invitation link',
    icon: UserPlus,
    className: 'text-indigo-600 dark:text-indigo-400',
  },
  {
    key: 'create',
    label: 'Create User',
    description: 'Provision an account directly',
    icon: UserSquare,
    className: 'text-purple-600 dark:text-purple-400',
  },
  {
    key: 'users',
    label: 'View All Users',
    description: 'Open the user management table',
    icon: Users,
    className: 'text-cyan-600 dark:text-cyan-400',
  },
  {
    key: 'export',
    label: 'Export Analytics',
    description: 'Download analytics as CSV',
    icon: Download,
    className: 'text-emerald-600 dark:text-emerald-400',
  },
]

export default function QuickActions({ onInvite, onCreate, onUsers, onExport, className }) {
  const handle = (key) => {
    if (key === 'invite') onInvite?.()
    else if (key === 'create') onCreate?.()
    else if (key === 'users') onUsers?.()
    else if (key === 'export') onExport?.()
  }

  return (
    <div className={cn('grid gap-3 sm:grid-cols-2', className)}>
      {actions.map(({ key, label, description, icon: Icon, className: iconClass }) => (
        <button
          key={key}
          type="button"
          onClick={() => handle(key)}
          className="group flex items-center gap-3 rounded-2xl border border-border bg-card p-4 text-left shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-accent-400/40 hover:shadow-lg hover:shadow-accent-500/10 dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur"
        >
          <span
            className={cn(
              'flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-muted transition-transform duration-200 group-hover:scale-110 dark:bg-zinc-800',
              iconClass
            )}
          >
            <Icon size={18} strokeWidth={1.75} />
          </span>
          <span className="min-w-0">
            <span className="block text-sm font-semibold text-foreground dark:text-white">
              {label}
            </span>
            <span className="block truncate text-xs text-muted-foreground dark:text-zinc-400">
              {description}
            </span>
          </span>
        </button>
      ))}
    </div>
  )
}
