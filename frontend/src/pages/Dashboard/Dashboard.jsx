import { useState } from 'react'
import {
  Building2,
  ClipboardList,
  Mail,
  Search,
  Sparkles,
  TrendingUp,
  Users,
} from 'lucide-react'
import DashboardHeader from '@/components/dashboard/DashboardHeader'
import WelcomeCard from '@/components/dashboard/WelcomeCard'
import StatsCard from '@/components/dashboard/StatsCard'
import BusinessForm from '@/components/dashboard/BusinessForm'
import ResultCards from '@/components/dashboard/ResultCards'
import { AreaChart } from '@/components/dashboard/Charts'

const placeholderResults = [
  {
    id: 'personas',
    title: 'Customer Personas',
    description:
      'Two core buyer personas to guide your messaging and channel choices.',
    icon: Users,
    tone: 'purple',
    items: ['SaaS Marketers', 'Growth Founders'],
  },
  {
    id: 'content',
    title: 'Content Calendar',
    description:
      'A 4-week content plan mapped to your goals and audience behavior.',
    icon: ClipboardList,
    tone: 'cyan',
    items: ['3 blog posts', '2 email campaigns', 'Weekly social cadence'],
  },
  {
    id: 'seo',
    title: 'SEO Opportunities',
    description:
      'High-intent keywords your competitors rank for but you do not.',
    icon: Search,
    tone: 'emerald',
    items: ['12 keyword gaps found', '5 quick-win topics'],
  },
]

const chartData = [
  { label: 'W1', value: 28 },
  { label: 'W2', value: 40 },
  { label: 'W3', value: 36 },
  { label: 'W4', value: 55 },
  { label: 'W5', value: 48 },
  { label: 'W6', value: 66 },
]

export default function Dashboard() {
  const [submitting, setSubmitting] = useState(false)
  const [generated, setGenerated] = useState(false)

  const handleSubmit = (formData) => {
    setSubmitting(true)
    // Simulated generation — replace with your API call.
    window.setTimeout(() => {
      setSubmitting(false)
      setGenerated(true)
    }, 1200)
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

      {/* KPI stats */}
      <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
        <StatsCard
          icon={TrendingUp}
          label="Growth Score"
          value="86"
          delta="+9.2"
          tone="indigo"
        />
        <StatsCard
          icon={Users}
          label="Audience Reach"
          value="48.2k"
          delta="+12.4"
          tone="purple"
        />
        <StatsCard
          icon={Building2}
          label="Strategies"
          value="12"
          delta="+3"
          tone="cyan"
        />
        <StatsCard
          icon={Mail}
          label="Campaigns Drafted"
          value="24"
          delta="-2.1"
          tone="emerald"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        {/* Strategy generator */}
        <div className="lg:col-span-3">
          <BusinessForm onSubmit={handleSubmit} submitting={submitting} />
        </div>

        {/* Generated results */}
        <div className="lg:col-span-2">
          <ResultCards
            results={generated ? placeholderResults : []}
            onCopy={() => undefined}
            onRegenerate={() => undefined}
          />
        </div>
      </div>

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
