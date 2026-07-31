import { Activity, FileText, Shield, TrendingUp, UserPlus, Users } from 'lucide-react'
import DashboardHeader from '@/components/dashboard/DashboardHeader'
import StatsCard from '@/components/dashboard/StatsCard'
import { useAuth } from '@/context/AuthContext'

const adminStats = [
  { icon: Users, label: 'Total Users', value: '1,248', delta: '+5.2', tone: 'indigo' },
  { icon: FileText, label: 'Strategies Generated', value: '8,532', delta: '+12.8', tone: 'purple' },
  { icon: Activity, label: 'Active Sessions', value: '312', delta: '+3.1', tone: 'cyan' },
  { icon: TrendingUp, label: 'Conversion Rate', value: '4.6%', delta: '+0.8', tone: 'emerald' },
]

export default function AdminDashboard() {
  const { userName } = useAuth()

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

      <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
        {adminStats.map((stat) => (
          <StatsCard key={stat.label} {...stat} />
        ))}
      </div>
    </div>
  )
}
