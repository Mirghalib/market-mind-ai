import { useEffect, useState } from 'react'
import { Activity, FileText, Shield, TrendingUp, UserPlus, Users } from 'lucide-react'
import DashboardHeader from '@/components/dashboard/DashboardHeader'
import StatsCard from '@/components/dashboard/StatsCard'
import Loader from '@/components/ui/Loader'
import { useAuth } from '@/context/AuthContext'
import { adminService } from '@/services/admin'

export default function AdminDashboard() {
  const { userName } = useAuth()
  const [stats, setStats] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    adminService
      .getStats()
      .then(({ data }) => {
        if (!cancelled) setStats(data)
      })
      .catch((err) => {
        if (!cancelled) {
          setError(
            err.response?.data?.detail ||
              err.response?.data?.message ||
              err.message ||
              'Could not load admin statistics.'
          )
        }
      })
    return () => {
      cancelled = true
    }
  }, [])

  const adminStats = [
    { icon: Users, label: 'Total Users', value: stats?.total_users ?? 0, delta: 'live', tone: 'indigo' },
    { icon: FileText, label: 'Strategies Generated', value: stats?.total_strategies ?? 0, delta: 'live', tone: 'purple' },
    { icon: Activity, label: 'Total Exports', value: stats?.total_exports ?? 0, delta: 'live', tone: 'cyan' },
    { icon: TrendingUp, label: 'Generations', value: stats?.total_generations ?? 0, delta: 'live', tone: 'emerald' },
  ]

  return (
    <div className="mx-auto max-w-7xl space-y-8 p-6 sm:p-8">
      <DashboardHeader
        eyebrow="Admin"
        title="Admin Dashboard"
        subtitle={`Welcome, ${userName ?? 'Admin'} — here is an overview of the platform.`}
        actions={
          <button
            type="button"
            className="inline-flex items-center gap-2 rounded-lg bg-indigo-500 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-400"
          >
            <UserPlus size={16} />
            Invite user
          </button>
        }
      />

      <div className="flex items-center gap-3 rounded-2xl border border-indigo-500/20 bg-indigo-500/[0.06] px-5 py-4">
        <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-500/15 text-indigo-600 dark:text-indigo-400">
          <Shield size={18} />
        </span>
        <p className="text-sm text-foreground dark:text-zinc-300">
          You are signed in with the <span className="font-semibold">Admin</span> role.
          Only admins can view this page.
        </p>
      </div>

      {error && (
        <div
          role="alert"
          className="rounded-2xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-sm text-red-400"
        >
          {error}
        </div>
      )}

      {stats ? (
        <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
          {adminStats.map((stat) => (
            <StatsCard key={stat.label} {...stat} />
          ))}
        </div>
      ) : (
        !error && (
          <div className="flex items-center justify-center rounded-2xl border border-border bg-card py-20 dark:border-white/10">
            <Loader size="lg" />
          </div>
        )
      )}
    </div>
  )
}
