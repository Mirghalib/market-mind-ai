import DashboardHeader from '@/components/dashboard/DashboardHeader'
import Settings from '@/components/dashboard/Settings'

export default function SettingsPage() {
  return (
    <div className="mx-auto max-w-6xl space-y-8 p-6 sm:p-8">
      <DashboardHeader
        eyebrow="Account"
        title="Settings"
        subtitle="Manage your profile, theme, notifications, and API access."
      />
      <Settings />
    </div>
  )
}
