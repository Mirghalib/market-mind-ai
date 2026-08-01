import { useEffect, useState } from 'react'
import DashboardHeader from '@/components/dashboard/DashboardHeader'
import WelcomeCard from '@/components/dashboard/WelcomeCard'
import AnalyticsCards from '@/components/dashboard/Analytics/AnalyticsCards'
import BusinessForm from '@/components/dashboard/BusinessForm'
import { StrategyView } from '@/components/dashboard/StrategyView'
import { useAuth } from '@/context/AuthContext'
import { useToast } from '@/context/ToastContext'
import { dashboardService } from '@/services/dashboard'

export default function Dashboard() {
  const { userName } = useAuth()
  const { showToast } = useToast()
  const [stats, setStats] = useState(null)
  const [strategy, setStrategy] = useState(null)
  const [businessName, setBusinessName] = useState('')
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')
  const [focusKey, setFocusKey] = useState(0)

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

  // Smoothly scroll to the strategy generator and focus the first input.
  // This CTA never calls the API directly — it only navigates the user
  // to the form.
  const scrollToGenerator = () => {
    const el = document.getElementById('strategy-generator')
    el?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    setFocusKey((key) => key + 1)
  }

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
      setBusinessName(formData.businessName)
      showToast('Marketing strategy generated successfully.', 'success')
      // Refresh the stats so the counters reflect the new generation.
      try {
        const { data: fresh } = await dashboardService.getStats()
        setStats(fresh)
      } catch {
        // Stats refresh is best-effort.
      }
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        err.message ||
        'Strategy generation failed. Try again.'
      setError(msg)
      showToast(msg, 'error')
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
        onCtaClick={scrollToGenerator}
      />

      {/* Analytics cards — driven by the live dashboard stats */}
      <AnalyticsCards
        className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4"
        stats={stats}
      />

      {/* Strategy generator */}
      <div id="strategy-generator" className="scroll-mt-24">
        <BusinessForm onSubmit={handleSubmit} loading={generating} focusKey={focusKey} />
      </div>

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
          <StrategyView
            strategy={strategy}
            onReset={() => setStrategy(null)}
            businessName={businessName}
          />
        </div>
      )}
    </div>
  )
}
