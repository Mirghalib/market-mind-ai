import { useState } from 'react'
import { Sparkles } from 'lucide-react'
import DashboardHeader from '@/components/dashboard/DashboardHeader'
import WelcomeCard from '@/components/dashboard/WelcomeCard'
import AnalyticsCards from '@/components/dashboard/Analytics/AnalyticsCards'
import BusinessForm from '@/components/dashboard/BusinessForm'
import ResultCards from '@/components/dashboard/ResultCards'
import { RESULT_PRESETS } from '@/components/dashboard/ResultPresets'
import { AreaChart } from '@/components/dashboard/Charts'

const chartData = [
  { label: 'W1', value: 28 },
  { label: 'W2', value: 40 },
  { label: 'W3', value: 36 },
  { label: 'W4', value: 55 },
  { label: 'W5', value: 48 },
  { label: 'W6', value: 66 },
]

export default function Dashboard() {
  const [generated, setGenerated] = useState(false)

  const handleSubmit = (formData) => {
    // Wire to your API here — form data is validated.
    console.log('Strategy form data:', formData)
    setGenerated(true)
  }

  return (
    <div className="mx-auto max-w-7xl space-y-8 p-6 sm:p-8">
      <DashboardHeader
        eyebrow="Overview"
        title="Dashboard"
        subtitle="Welcome back. Here is the state of your market insights."
      />

      <WelcomeCard
        name="Alex"
        message="Turn your business into a marketing strategy in seconds — your market analysis, personas, and campaigns are one prompt away."
        tip="Engage with your top 20% of customers this week — repeat buyers are 5x more likely to try a new product."
        ctaLabel="Generate Strategy"
        ctaTo="/dashboard"
      />

      {/* Analytics cards */}
      <AnalyticsCards className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4" />

      {/* Strategy generator */}
      <BusinessForm onSubmit={handleSubmit} />

      {/* Generated results */}
      {generated && (
        <div className="space-y-4">
          <DashboardHeader
            eyebrow="Your strategy"
            title="Generated results"
            subtitle="Copy, download, or share each section of your strategy."
          />
          <ResultCards results={RESULT_PRESETS} />
        </div>
      )}

      {/* Insight preview */}
      <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur">
        <div className="flex items-center gap-2">
          <Sparkles size={16} className="text-indigo-500 dark:text-indigo-400" />
          <h2 className="text-base font-semibold text-zinc-900 dark:text-white">Weekly insight</h2>
        </div>
        <p className="mt-2 text-sm leading-relaxed text-zinc-500 dark:text-zinc-400">
          Your engagement is trending up 9% this month. Consider doubling down
          on email campaigns — they convert 2.4x better than social for your
          industry.
        </p>
        <div className="mt-6">
          <AreaChart data={chartData} height={180} />
        </div>
      </div>
    </div>
  )
}
