import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Ban,
  CheckCircle2,
  Copy,
  Cpu,
  FileDown,
  KeyRound,
  Loader2,
  Mail,
  Plus,
  RefreshCw,
  Search,
  Shield,
  Sparkles,
  Trash2,
  UserCheck,
  UserCog,
  UserPlus,
  Users,
} from 'lucide-react'
import DashboardHeader from '@/components/dashboard/DashboardHeader'
import Loader from '@/components/ui/Loader'
import Modal from '@/components/ui/Modal'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'
import {
  AdminChartCard,
  AdminStatCard,
  QuickActions,
  RecentActivity,
} from '@/components/admin'
import {
  AreaChart,
  BarChart,
  DonutChart,
  LineChart,
  PieChart,
} from '@/components/dashboard/Charts'
import { useAuth } from '@/context/AuthContext'
import { useToast } from '@/context/ToastContext'
import { adminService } from '@/services/admin'
import { exportAnalyticsCsv } from '@/utils/analyticsCsv'
import { cn } from '@/utils/cn'

const PAGE_SIZE = 10

const CHART_COLORS = {
  indigo: '#6366f1',
  purple: '#a855f7',
  cyan: '#06b6d4',
  emerald: '#10b981',
  amber: '#f59e0b',
  rose: '#f43f5e',
}

function errorMessage(err, fallback) {
  return (
    err.response?.data?.detail ||
    err.response?.data?.message ||
    err.message ||
    fallback
  )
}

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function Avatar({ user }) {
  if (user.profile_image) {
    return (
      <img
        src={user.profile_image}
        alt={user.full_name || user.email}
        className="h-9 w-9 shrink-0 rounded-full object-cover"
      />
    )
  }
  const initials = (user.full_name || user.email || 'U')
    .split(' ')
    .map((p) => p[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
  return (
    <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 text-xs font-semibold text-white">
      {initials}
    </span>
  )
}

function UserRow({ user, onAction }) {
  return (
    <tr className="border-b border-border last:border-0 hover:bg-muted/40 dark:border-white/5 dark:hover:bg-white/[0.02]">
      <td className="px-4 py-3 sm:px-6">
        <div className="flex items-center gap-3">
          <Avatar user={user} />
          <div className="min-w-0">
            <p className="truncate text-sm font-medium text-foreground dark:text-white">
              {user.full_name || '—'}
            </p>
            <p className="truncate text-xs text-muted-foreground dark:text-zinc-400">
              {user.email}
            </p>
          </div>
        </div>
      </td>
      <td className="px-4 py-3">
        <Badge variant={user.role_name === 'admin' ? 'primary' : 'default'}>
          {user.role_name || 'user'}
        </Badge>
      </td>
      <td className="px-4 py-3">
        {user.is_active ? (
          <span className="inline-flex items-center gap-1.5 text-sm font-medium text-emerald-600 dark:text-emerald-400">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
            Active
          </span>
        ) : (
          <span className="inline-flex items-center gap-1.5 text-sm font-medium text-red-500 dark:text-red-400">
            <span className="h-1.5 w-1.5 rounded-full bg-red-500" />
            Blocked
          </span>
        )}
      </td>
      <td className="hidden px-4 py-3 text-sm text-muted-foreground dark:text-zinc-400 lg:table-cell">
        {user.is_email_verified ? (
          <span className="inline-flex items-center gap-1 text-emerald-600 dark:text-emerald-400">
            <CheckCircle2 size={14} />
            Verified
          </span>
        ) : (
          <span className="text-zinc-500">Unverified</span>
        )}
      </td>
      <td className="hidden px-4 py-3 text-sm text-muted-foreground dark:text-zinc-400 xl:table-cell">
        {formatDate(user.created_at)}
      </td>
      <td className="hidden px-4 py-3 text-sm text-muted-foreground dark:text-zinc-400 xl:table-cell">
        {formatDate(user.last_login_at)}
      </td>
      <td className="hidden px-4 py-3 text-sm text-muted-foreground dark:text-zinc-400 md:table-cell">
        {user.total_strategies ?? 0}
      </td>
      <td className="hidden px-4 py-3 text-sm text-muted-foreground dark:text-zinc-400 md:table-cell">
        {user.total_exports ?? 0}
      </td>
      <td className="px-4 py-3">
        <div className="flex items-center justify-end gap-1">
          <button
            type="button"
            onClick={() => onAction('edit', user)}
            title="Edit user"
            className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-muted hover:text-foreground dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-white"
          >
            <UserCog size={15} />
          </button>
          <button
            type="button"
            onClick={() => onAction(user.is_active ? 'block' : 'unblock', user)}
            title={user.is_active ? 'Block user' : 'Unblock user'}
            className={cn(
              'flex h-8 w-8 items-center justify-center rounded-lg transition-colors',
              user.is_active
                ? 'text-muted-foreground hover:bg-amber-500/10 hover:text-amber-500 dark:text-zinc-400 dark:hover:text-amber-400'
                : 'text-emerald-600 hover:bg-emerald-500/10 dark:text-emerald-400'
            )}
          >
            {user.is_active ? <Ban size={15} /> : <CheckCircle2 size={15} />}
          </button>
          <button
            type="button"
            onClick={() => onAction('delete', user)}
            title="Delete user"
            className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-red-500/10 hover:text-red-500 dark:text-zinc-400 dark:hover:text-red-400"
          >
            <Trash2 size={15} />
          </button>
        </div>
      </td>
    </tr>
  )
}

function InviteModal({ onClose, onSuccess, roles }) {
  const [form, setForm] = useState({ email: '', full_name: '', role_name: 'user' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const { data } = await adminService.inviteUser(form)
      setResult(data)
      onSuccess?.()
    } catch (err) {
      setError(errorMessage(err, 'Could not create the invitation.'))
    } finally {
      setLoading(false)
    }
  }

  const copyLink = async () => {
    if (!result?.accept_url) return
    try {
      await navigator.clipboard.writeText(result.accept_url)
    } catch {
      // clipboard fallback
    }
  }

  return (
    <Modal open onClose={onClose} title="Invite user">
      {result ? (
        <div className="space-y-4">
          <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-600 dark:text-emerald-400">
            <p className="font-medium">Invitation created for {result.email}</p>
            <p className="mt-1 text-xs">{result.message}</p>
          </div>
          <div className="flex items-center gap-2 rounded-xl border border-border bg-muted px-3 py-2.5 dark:border-white/10 dark:bg-zinc-900">
            <span className="min-w-0 flex-1 truncate text-xs text-muted-foreground dark:text-zinc-400">
              {result.accept_url}
            </span>
            <button
              type="button"
              onClick={copyLink}
              className="flex shrink-0 items-center gap-1 rounded-lg bg-accent-500/15 px-2.5 py-1.5 text-xs font-medium text-accent-600 hover:bg-accent-500/25 dark:text-accent-300"
            >
              <Copy size={13} />
              Copy
            </button>
          </div>
          <div className="flex justify-end">
            <Button variant="outline" onClick={onClose}>
              Done
            </Button>
          </div>
        </div>
      ) : (
        <form onSubmit={submit} className="space-y-4">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-foreground dark:text-zinc-200">
              Name
            </label>
            <input
              type="text"
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              placeholder="Jane Cooper"
              className="h-11 w-full rounded-lg border border-border bg-card px-3.5 text-sm text-foreground transition-colors focus:border-accent-500 focus:ring-2 focus:ring-accent-500/30 focus:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
            />
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-foreground dark:text-zinc-200">
              Email
            </label>
            <input
              type="email"
              required
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              placeholder="jane@company.com"
              className="h-11 w-full rounded-lg border border-border bg-card px-3.5 text-sm text-foreground transition-colors focus:border-accent-500 focus:ring-2 focus:ring-accent-500/30 focus:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
            />
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-foreground dark:text-zinc-200">
              Role
            </label>
            <select
              value={form.role_name}
              onChange={(e) => setForm({ ...form, role_name: e.target.value })}
              className="h-11 w-full rounded-lg border border-border bg-card px-3.5 text-sm text-foreground transition-colors focus:border-accent-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
            >
              {roles.map((role) => (
                <option key={role.name} value={role.name}>
                  {role.name}
                </option>
              ))}
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
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <Mail size={16} />
              )}
              Send invitation
            </Button>
          </div>
        </form>
      )}
    </Modal>
  )
}

function CreateUserModal({ onClose, onSuccess, roles }) {
  const [form, setForm] = useState({ email: '', password: '', full_name: '', role_name: 'user' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await adminService.createUser(form)
      onSuccess?.()
      onClose()
    } catch (err) {
      setError(errorMessage(err, 'Could not create the user.'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal open onClose={onClose} title="Create user">
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-foreground dark:text-zinc-200">
            Full name
          </label>
          <input
            type="text"
            value={form.full_name}
            onChange={(e) => setForm({ ...form, full_name: e.target.value })}
            placeholder="Jane Cooper"
            className="h-11 w-full rounded-lg border border-border bg-card px-3.5 text-sm text-foreground transition-colors focus:border-accent-500 focus:ring-2 focus:ring-accent-500/30 focus:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
          />
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium text-foreground dark:text-zinc-200">
            Email
          </label>
          <input
            type="email"
            required
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            placeholder="jane@company.com"
            className="h-11 w-full rounded-lg border border-border bg-card px-3.5 text-sm text-foreground transition-colors focus:border-accent-500 focus:ring-2 focus:ring-accent-500/30 focus:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
          />
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium text-foreground dark:text-zinc-200">
            Password
          </label>
          <input
            type="password"
            required
            minLength={8}
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            placeholder="At least 8 characters"
            className="h-11 w-full rounded-lg border border-border bg-card px-3.5 text-sm text-foreground transition-colors focus:border-accent-500 focus:ring-2 focus:ring-accent-500/30 focus:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
          />
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium text-foreground dark:text-zinc-200">
            Role
          </label>
          <select
            value={form.role_name}
            onChange={(e) => setForm({ ...form, role_name: e.target.value })}
            className="h-11 w-full rounded-lg border border-border bg-card px-3.5 text-sm text-foreground transition-colors focus:border-accent-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
          >
            {roles.map((role) => (
              <option key={role.name} value={role.name}>
                {role.name}
              </option>
            ))}
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
            {loading ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />}
            Create user
          </Button>
        </div>
      </form>
    </Modal>
  )
}

function EditUserModal({ user, onClose, onSuccess, roles }) {
  const [form, setForm] = useState({
    full_name: user.full_name || '',
    role_name: user.role_name || 'user',
    is_active: user.is_active,
    is_email_verified: user.is_email_verified,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')
    try {
      const { data } = await adminService.updateUser(user.id, form)
      onSuccess?.(data)
      setSuccess('User updated successfully.')
    } catch (err) {
      setError(errorMessage(err, 'Could not update the user.'))
    } finally {
      setLoading(false)
    }
  }

  const quickAction = async (fn, okMsg, failMsg) => {
    setLoading(true)
    setError('')
    setSuccess('')
    try {
      await fn()
      setSuccess(okMsg)
      onSuccess?.()
    } catch (err) {
      setError(errorMessage(err, failMsg))
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal open onClose={onClose} title={`Edit user — ${user.email}`}>
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-foreground dark:text-zinc-200">
            Full name
          </label>
          <input
            type="text"
            value={form.full_name}
            onChange={(e) => setForm({ ...form, full_name: e.target.value })}
            className="h-11 w-full rounded-lg border border-border bg-card px-3.5 text-sm text-foreground transition-colors focus:border-accent-500 focus:ring-2 focus:ring-accent-500/30 focus:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
          />
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium text-foreground dark:text-zinc-200">
            Role
          </label>
          <select
            value={form.role_name}
            onChange={(e) => setForm({ ...form, role_name: e.target.value })}
            className="h-11 w-full rounded-lg border border-border bg-card px-3.5 text-sm text-foreground transition-colors focus:border-accent-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
          >
            {roles.map((role) => (
              <option key={role.name} value={role.name}>
                {role.name}
              </option>
            ))}
          </select>
        </div>
        <label className="flex items-center justify-between gap-3 rounded-xl border border-border bg-muted/50 px-4 py-3 dark:border-white/10">
          <span className="text-sm font-medium text-foreground dark:text-zinc-200">
            Account active
          </span>
          <input
            type="checkbox"
            checked={form.is_active}
            onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
            className="h-4 w-4 accent-indigo-500"
          />
        </label>
        <label className="flex items-center justify-between gap-3 rounded-xl border border-border bg-muted/50 px-4 py-3 dark:border-white/10">
          <span className="text-sm font-medium text-foreground dark:text-zinc-200">
            Email verified
          </span>
          <input
            type="checkbox"
            checked={form.is_email_verified}
            onChange={(e) => setForm({ ...form, is_email_verified: e.target.checked })}
            className="h-4 w-4 accent-indigo-500"
          />
        </label>

        {error && (
          <div
            role="alert"
            className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-500 dark:text-red-400"
          >
            {error}
          </div>
        )}
        {success && (
          <div
            role="status"
            className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-600 dark:text-emerald-400"
          >
            {success}
          </div>
        )}

        <div className="flex flex-wrap items-center gap-2 pt-1">
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={loading}
            onClick={() =>
              quickAction(
                async () => {
                  await adminService.resetPassword(user.id, { new_password: 'Reset@12345' })
                },
                'Password reset to Reset@12345.',
                'Could not reset the password.'
              )
            }
          >
            <KeyRound size={14} />
            Reset password
          </Button>
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={loading}
            onClick={() =>
              quickAction(
                async () => {
                  await adminService.verifyEmail(user.id)
                },
                'Email marked as verified.',
                'Could not verify the email.'
              )
            }
          >
            <CheckCircle2 size={14} />
            Verify email
          </Button>
          <div className="ml-auto flex gap-2">
            <Button type="button" variant="outline" size="sm" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" size="sm" disabled={loading}>
              {loading ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
              Save
            </Button>
          </div>
        </div>
      </form>
    </Modal>
  )
}

function DeleteConfirmModal({ user, onClose, onConfirm }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const confirm = async () => {
    setLoading(true)
    setError('')
    try {
      await onConfirm()
      onClose()
    } catch (err) {
      setError(errorMessage(err, 'Could not delete the user.'))
      setLoading(false)
    }
  }

  return (
    <Modal open onClose={onClose} title="Delete user">
      <div className="space-y-4">
        <p className="text-sm text-muted-foreground dark:text-zinc-300">
          Are you sure you want to delete{' '}
          <span className="font-semibold text-foreground dark:text-white">
            {user.full_name || user.email}
          </span>
          ? The account will be soft-deleted and can be restored.
        </p>
        {error && (
          <div
            role="alert"
            className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-500 dark:text-red-400"
          >
            {error}
          </div>
        )}
        <div className="flex justify-end gap-3">
          <Button variant="outline" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button variant="danger" onClick={confirm} disabled={loading}>
            {loading ? <Loader2 size={16} className="animate-spin" /> : <Trash2 size={16} />}
            Delete
          </Button>
        </div>
      </div>
    </Modal>
  )
}

export default function AdminDashboard() {
  const { userName } = useAuth()
  const { showToast: toast } = useToast()
  const [analytics, setAnalytics] = useState(null)
  const [error, setError] = useState('')
  const [users, setUsers] = useState([])
  const [total, setTotal] = useState(0)
  const [loadingUsers, setLoadingUsers] = useState(false)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [roles, setRoles] = useState([])
  const [tab, setTab] = useState('overview')
  const [modal, setModal] = useState(null) // 'invite' | 'create' | 'edit' | 'delete'
  const [selectedUser, setSelectedUser] = useState(null)
  const [notice, setNotice] = useState('')

  const showNotice = useCallback((msg) => {
    setNotice(msg)
    window.setTimeout(() => setNotice(''), 3500)
  }, [])

  const loadAnalytics = useCallback(() => {
    setError('')
    adminService
      .getAnalytics()
      .then(({ data }) => setAnalytics(data))
      .catch((err) => {
        setError(errorMessage(err, 'Could not load admin analytics.'))
      })
  }, [])

  useEffect(() => {
    loadAnalytics()
  }, [loadAnalytics])

  useEffect(() => {
    adminService
      .getRoles()
      .then(({ data }) => setRoles(data.items || []))
      .catch(() => {})
  }, [])

  const loadUsers = useCallback(async () => {
    setLoadingUsers(true)
    setError('')
    try {
      const params = { limit: PAGE_SIZE, offset: (page - 1) * PAGE_SIZE }
      if (search) params.search = search
      if (roleFilter) params.role = roleFilter
      if (statusFilter) params.status = statusFilter
      const { data } = await adminService.getUsers(params)
      setUsers(data.items)
      setTotal(data.total)
    } catch (err) {
      setError(errorMessage(err, 'Could not load users.'))
    } finally {
      setLoadingUsers(false)
    }
  }, [page, search, roleFilter, statusFilter])

  useEffect(() => {
    if (tab === 'users') loadUsers()
  }, [loadUsers, tab])

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  const stats = analytics?.stats
  const growth = analytics?.growth ?? {}

  const adminStats = useMemo(
    () => [
      {
        icon: Users,
        label: 'Total Users',
        value: stats?.total_users ?? 0,
        delta: growth.total_users ?? null,
        hint: 'All registered accounts, including admins.',
        tone: 'indigo',
      },
      {
        icon: UserCheck,
        label: 'Active Users',
        value:
          (analytics?.user_status ?? []).find((s) => s.label === 'Active')?.value ?? 0,
        delta: growth.active_users ?? null,
        hint: 'Accounts currently enabled.',
        tone: 'emerald',
      },
      {
        icon: Ban,
        label: 'Blocked Users',
        value:
          (analytics?.user_status ?? []).find((s) => s.label === 'Blocked')?.value ?? 0,
        delta: growth.blocked_users ?? null,
        hint: 'Accounts disabled by an admin.',
        tone: 'rose',
      },
      {
        icon: Sparkles,
        label: 'Strategies Generated',
        value: stats?.total_strategies ?? 0,
        delta: growth.total_strategies ?? null,
        hint: 'Total marketing strategies created.',
        tone: 'purple',
      },
      {
        icon: FileDown,
        label: 'Total Exports',
        value: stats?.total_exports ?? 0,
        delta: growth.total_exports ?? null,
        hint: 'Strategies exported as files.',
        tone: 'cyan',
      },
      {
        icon: Cpu,
        label: 'AI Requests Today',
        value: analytics?.ai_requests_today ?? 0,
        delta: growth.ai_requests_today ?? null,
        hint: 'AI generations started since midnight UTC.',
        tone: 'amber',
      },
    ],
    [analytics, growth, stats]
  )

  const exportFormats = (analytics?.export_formats ?? []).map((item) => ({
    label: item.label.toUpperCase(),
    value: item.value,
    color: CHART_COLORS.indigo,
  }))

  const userStatus = (analytics?.user_status ?? []).map((item) => ({
    label: item.label,
    value: item.value,
    color:
      item.label === 'Active'
        ? CHART_COLORS.emerald
        : item.label === 'Blocked'
          ? CHART_COLORS.rose
          : CHART_COLORS.amber,
  }))

  const strategySuccess = (analytics?.strategy_success ?? []).map((item) => ({
    label: item.label,
    value: item.value,
    color:
      item.label === 'completed'
        ? CHART_COLORS.emerald
        : item.label === 'failed'
          ? CHART_COLORS.rose
          : item.label === 'draft'
            ? CHART_COLORS.amber
            : CHART_COLORS.cyan,
  }))

  const monthlyRegistrations = analytics?.monthly_registrations ?? []
  const topUsers = analytics?.top_users ?? []
  const strategyTrend = analytics?.strategy_trend ?? []
  const activityEvents = analytics?.recent_activity ?? []

  const handleExportAnalytics = () => {
    const ok = exportAnalyticsCsv(analytics)
    if (ok) showNotice('Analytics exported as CSV.')
  }

  const handleAction = (action, user) => {
    setSelectedUser(user)
    if (action === 'edit') setModal('edit')
    else if (action === 'delete') setModal('delete')
    else if (action === 'block' || action === 'unblock') {
      const isActive = action === 'unblock'
      adminService
        .updateUser(user.id, { is_active: isActive })
        .then(() => {
          showNotice(isActive ? `${user.email} unblocked.` : `${user.email} blocked.`)
          loadUsers()
          loadAnalytics()
        })
        .catch((err) => showNotice(errorMessage(err, 'Could not update the user.')))
    }
  }

  const handleDelete = async () => {
    await adminService.deleteUser(selectedUser.id)
    showNotice(`${selectedUser.email} deleted.`)
    loadUsers()
    loadAnalytics()
  }

  const handleInviteSuccess = () => {
    showNotice('Invitation created.')
    loadAnalytics()
  }

  const handleCreateSuccess = () => {
    loadUsers()
    loadAnalytics()
  }

  const debouncedSearch = (value) => {
    setSearch(value)
    setPage(1)
  }

  return (
    <div className="mx-auto max-w-7xl space-y-8 p-6 sm:p-8">
      <DashboardHeader
        eyebrow="Admin"
        title="Admin Dashboard"
        subtitle={`Welcome, ${userName ?? 'Admin'} — platform overview and analytics.`}
        actions={
          <div className="flex gap-2">
            <Button size="sm" variant="outline" onClick={() => setModal('invite')}>
              <UserPlus size={16} />
              Invite user
            </Button>
            <Button size="sm" onClick={() => setModal('create')}>
              <Plus size={16} />
              Create user
            </Button>
          </div>
        }
      />

      {notice && (
        <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-600 dark:text-emerald-400">
          {notice}
        </div>
      )}

      <div className="flex items-center gap-3 rounded-2xl border border-accent-500/20 bg-accent-500/[0.06] px-5 py-4">
        <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent-500/15 text-accent-600 dark:text-accent-300">
          <Shield size={18} />
        </span>
        <p className="text-sm text-foreground dark:text-zinc-300">
          You are signed in with the <span className="font-semibold">Admin</span> role.
          Only admins can view this page.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 rounded-xl border border-border bg-card p-1 sm:w-fit dark:border-white/10 dark:bg-white/[0.03]">
        {[
          { key: 'overview', label: 'Overview' },
          { key: 'users', label: 'Users' },
        ].map((item) => (
          <button
            key={item.key}
            type="button"
            onClick={() => setTab(item.key)}
            aria-pressed={tab === item.key}
            className={cn(
              'flex-1 rounded-lg px-4 py-2 text-sm font-medium transition-colors sm:flex-none',
              tab === item.key
                ? 'bg-accent-500/15 text-accent-600 dark:text-accent-300'
                : 'text-muted-foreground hover:bg-muted hover:text-foreground dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-white'
            )}
          >
            {item.label}
          </button>
        ))}
      </div>

      {error && (
        <div
          role="alert"
          className="rounded-2xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-sm text-red-400"
        >
          {error}
        </div>
      )}

      {tab === 'overview' ? (
        analytics ? (
          <>
            {/* Stat cards */}
            <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
              {adminStats.map((stat) => (
                <AdminStatCard key={stat.label} {...stat} />
              ))}
            </div>

            {/* Quick actions */}
            <QuickActions
              onInvite={() => setModal('invite')}
              onCreate={() => setModal('create')}
              onUsers={() => setTab('users')}
              onExport={handleExportAnalytics}
            />

            {/* Charts */}
            <div className="grid gap-6 lg:grid-cols-2">
              <AdminChartCard
                title="Strategies generated over time"
                subtitle="Daily strategies, last 30 days"
                className="lg:col-span-2"
              >
                <LineChart data={strategyTrend} height={240} stroke={CHART_COLORS.indigo} />
              </AdminChartCard>

              <AdminChartCard
                title="Export formats"
                subtitle="Strategies exported by format"
                delay={0.05}
              >
                <PieChart
                  data={exportFormats}
                  centerValue={stats?.total_exports ?? 0}
                  centerLabel="exports"
                />
              </AdminChartCard>

              <AdminChartCard
                title="Users by status"
                subtitle="Active, blocked and pending verification"
                delay={0.1}
              >
                <PieChart
                  data={userStatus}
                  centerValue={stats?.total_users ?? 0}
                  centerLabel="users"
                />
              </AdminChartCard>

              <AdminChartCard
                title="Most active users"
                subtitle="Top 10 by strategies generated"
                className="lg:col-span-2"
                delay={0.15}
              >
                {topUsers.length > 0 ? (
                  <BarChart data={topUsers} height={240} color={CHART_COLORS.purple} />
                ) : (
                  <p className="py-10 text-center text-sm text-muted-foreground dark:text-zinc-400">
                    No strategies generated yet.
                  </p>
                )}
              </AdminChartCard>

              <AdminChartCard
                title="Monthly registrations"
                subtitle="New users per month, last 12 months"
                delay={0.2}
              >
                <AreaChart data={monthlyRegistrations} height={220} stroke={CHART_COLORS.cyan} />
              </AdminChartCard>

              <AdminChartCard
                title="Strategy success distribution"
                subtitle="Completed, failed, draft and generating"
                delay={0.25}
              >
                <DonutChart
                  data={strategySuccess}
                  centerValue={stats?.total_strategies ?? 0}
                  centerLabel="strategies"
                />
              </AdminChartCard>
            </div>

            {/* Recent activity */}
            <AdminChartCard title="Recent activity" subtitle="Latest platform events" delay={0.3}>
              {activityEvents.length > 0 ? (
                <RecentActivity events={activityEvents} />
              ) : (
                <p className="py-10 text-center text-sm text-muted-foreground dark:text-zinc-400">
                  No activity yet.
                </p>
              )}
            </AdminChartCard>
          </>
        ) : (
          !error && (
            <div className="flex items-center justify-center rounded-2xl border border-border bg-card py-20 dark:border-white/10">
              <Loader size="lg" />
            </div>
          )
        )
      ) : (
        <div className="space-y-4">
          {/* Filters */}
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <div className="relative flex-1">
              <Search
                size={15}
                className="pointer-events-none absolute top-1/2 left-3.5 -translate-y-1/2 text-muted-foreground dark:text-zinc-500"
              />
              <input
                type="search"
                value={search}
                onChange={(e) => debouncedSearch(e.target.value)}
                placeholder="Search by name or email…"
                className="h-10 w-full rounded-xl border border-border bg-card pr-4 pl-10 text-sm text-foreground shadow-sm transition-all focus:border-accent-500 focus:ring-2 focus:ring-accent-500/30 focus:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
              />
            </div>
            <select
              value={roleFilter}
              onChange={(e) => {
                setRoleFilter(e.target.value)
                setPage(1)
              }}
              className="h-10 rounded-xl border border-border bg-card px-3 text-sm text-foreground transition-colors focus:border-accent-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
            >
              <option value="">All roles</option>
              {roles.map((role) => (
                <option key={role.name} value={role.name}>
                  {role.name}
                </option>
              ))}
            </select>
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value)
                setPage(1)
              }}
              className="h-10 rounded-xl border border-border bg-card px-3 text-sm text-foreground transition-colors focus:border-accent-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
            >
              <option value="">All statuses</option>
              <option value="active">Active</option>
              <option value="blocked">Blocked</option>
            </select>
          </div>

          {/* Table */}
          <div className="overflow-x-auto rounded-2xl border border-border bg-card shadow-sm dark:border-white/10 dark:bg-white/[0.03]">
            {loadingUsers ? (
              <div className="flex items-center justify-center py-16">
                <Loader size="lg" />
              </div>
            ) : users.length === 0 ? (
              <div className="flex flex-col items-center justify-center px-6 py-16 text-center">
                <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-muted text-muted-foreground dark:bg-white/[0.05]">
                  <Users size={22} strokeWidth={1.75} />
                </span>
                <p className="mt-4 text-sm font-medium text-foreground dark:text-white">
                  No users found
                </p>
                <p className="mt-1 max-w-xs text-sm text-muted-foreground dark:text-zinc-400">
                  Try adjusting your search or filters.
                </p>
              </div>
            ) : (
              <table className="w-full min-w-[1000px] text-left text-sm">
                <thead>
                  <tr className="border-b border-border text-xs tracking-wide text-muted-foreground uppercase dark:border-white/5 dark:text-zinc-500">
                    <th scope="col" className="px-4 py-3 font-medium sm:px-6">User</th>
                    <th scope="col" className="px-4 py-3 font-medium">Role</th>
                    <th scope="col" className="px-4 py-3 font-medium">Status</th>
                    <th scope="col" className="hidden px-4 py-3 font-medium lg:table-cell">Email</th>
                    <th scope="col" className="hidden px-4 py-3 font-medium xl:table-cell">Joined</th>
                    <th scope="col" className="hidden px-4 py-3 font-medium xl:table-cell">Last login</th>
                    <th scope="col" className="hidden px-4 py-3 font-medium md:table-cell">Strategies</th>
                    <th scope="col" className="hidden px-4 py-3 font-medium md:table-cell">Exports</th>
                    <th scope="col" className="px-4 py-3 text-right font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <UserRow key={user.id} user={user} onAction={handleAction} />
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* Pagination */}
          {total > 0 && (
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground dark:text-zinc-400">
                Showing {users.length} of {total} users
              </p>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => p - 1)}
                  className="rounded-lg border border-border bg-card px-3 py-1.5 text-sm font-medium text-foreground transition-colors hover:bg-muted disabled:pointer-events-none disabled:opacity-50 dark:border-white/10 dark:bg-white/[0.03] dark:text-zinc-100"
                >
                  Prev
                </button>
                <span className="text-sm text-muted-foreground dark:text-zinc-400">
                  {page} / {totalPages}
                </span>
                <button
                  type="button"
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => p + 1)}
                  className="rounded-lg border border-border bg-card px-3 py-1.5 text-sm font-medium text-foreground transition-colors hover:bg-muted disabled:pointer-events-none disabled:opacity-50 dark:border-white/10 dark:bg-white/[0.03] dark:text-zinc-100"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Modals */}
      {modal === 'invite' && (
        <InviteModal
          onClose={() => setModal(null)}
          onSuccess={handleInviteSuccess}
          roles={roles}
        />
      )}
      {modal === 'create' && (
        <CreateUserModal
          onClose={() => setModal(null)}
          onSuccess={handleCreateSuccess}
          roles={roles}
        />
      )}
      {modal === 'edit' && selectedUser && (
        <EditUserModal
          user={selectedUser}
          onClose={() => setModal(null)}
          onSuccess={loadUsers}
          roles={roles}
        />
      )}
      {modal === 'delete' && selectedUser && (
        <DeleteConfirmModal
          user={selectedUser}
          onClose={() => setModal(null)}
          onConfirm={handleDelete}
        />
      )}
    </div>
  )
}
