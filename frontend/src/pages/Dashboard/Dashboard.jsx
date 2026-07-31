import { useEffect, useState } from 'react'
import { Sparkles, TrendingDown, TrendingUp } from 'lucide-react'
import DashboardHeader from '@/components/dashboard/DashboardHeader'
import WelcomeCard from '@/components/dashboard/WelcomeCard'
import AnalyticsCards from '@/components/dashboard/Analytics/AnalyticsCards'
import BusinessForm from '@/components/dashboard/BusinessForm'
import { StrategyView } from '@/components/dashboard/StrategyView'
import { AreaChart } from '@/components/dashboard/Charts'
import { useAuth } from '@/context/AuthContext'
import { dashboardService } from '@/services/dashboard'
import { cn } from '@/utils/cn'

const chartData = [
  { label: 'W1', value: 28 },
  { label: 'W2', value: 40 },
  { label: 'W3', value: 36 },
  { label: 'W4', value: 55 },
  { label: 'W5', value: 48 },
  { label: 'W6', value: 66 },
]

export default function Dashboard() {
  const { userName } = useAuth()
  const [stats, setStats] = useState(null)
  const [strategy, setStrategy] = useState(null)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')

  // Load personal dashboard stats on mount.
  useEffect(() => {
    let cancelled = false
    dashboardService
      .getStats()
      .then(({ data }) => {
        if (!cancelled) setStats(data)
      })
      .catch(() => {
        // Non-fatal: the dashboard still renders with zero states.
      })
    return () => {
      cancelled = true
    }
  }, [])

  const handleSubmit = async (formData) => {
    setGenerating(true)
    setError('')
    try {
      const { data } = await dashboardService.generate({
        project_name: formData.businessName,
        industry: formData.industry,
        target_audience: formData.targetAudience,
        goals: [formData.marketingGoal],
        tone: 'professional',
      })
      setStrategy(data)
      // Refresh the stats so the counters reflect the new generation.
      try {
        const { data: fresh } = await dashboardService.getStats()
        setStats(fresh)
      } catch {
        // Stats refresh is best-effort.
      }
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          err.response?.data?.message ||
          err.message ||
          'Strategy generation failed. Try again.'
      )
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="mx-auto max-w-7xl space-y-8 p-6 sm:p-8">
      <DashboardHeader
        eyebrow="Overview"
        title="Dashboard"
        subtitle="Welcome back. Here is the state of your market insights."
      />

      <WelcomeCard
        name={userName ?? 'there'}
        message="Turn your business into a marketing strategy in seconds — your market analysis, personas, and campaigns are one prompt away."
        tip="Engage with your top 20% of customers this week — repeat buyers are 5x more likely to try a new product."
        ctaLabel="Generate Strategy"
        ctaTo="/dashboard"
      />

      {/* Analytics cards — driven by the live dashboard stats */}
      <AnalyticsCards
        className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4"
        stats={stats}
      />

      {/* Strategy generator */}
      <BusinessForm onSubmit={handleSubmit} loading={generating} />

      {error && (
        <div
          role="alert"
          className="rounded-2xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-sm text-red-400"
        >
          {error}
        </div>
      )}

      {/* Generated results */}
      {strategy && (
        <div className="space-y-4">
          <DashboardHeader
            eyebrow="Your strategy"
            title="Generated results"
            subtitle="Your AI-generated marketing strategy is ready below."
          />
          <StrategyView strategy={strategy} onReset={() => setStrategy(null)} />
        </div>
      )}

      {/* Insight preview */}
      <div className="rounded-2xl border border-border bg-card p-6 shadow-sm dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur">
        <div className="flex items-center gap-2">
          <Sparkles size={16} className="text-indigo-500 dark:text-indigo-400" />
          <h2 className="text-base font-semibold text-foreground dark:text-white">Weekly insight</h2>
        </div>
        <p className="mt-2 text-sm leading-relaxed text-muted-foreground dark:text-zinc-400">
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
