import { Users, Zap, Target, TrendingUp } from 'lucide-react'
import StatsCard from '../StatsCard'

const defaultStats = [
  {
    icon: Users,
    label: 'Audience Reach',
    value: '48.2k',
    delta: '+12.4',
    tone: 'indigo',
  },
  {
    icon: Zap,
    label: 'Engagement',
    value: '8,946',
    delta: '+4.1',
    tone: 'purple',
  },
  {
    icon: Target,
    label: 'Conversion Rate',
    value: '3.7%',
    delta: '-0.6',
    tone: 'cyan',
  },
  {
    icon: TrendingUp,
    label: 'Growth Score',
    value: '86',
    delta: '+9.2',
    tone: 'emerald',
  },
]

/**
 * KPI band for the analytics view. Accepts custom stats or renders
 * representative placeholders. Composes the reusable StatsCard.
 */
export default function OverviewStats({ stats = defaultStats, className }) {
  return (
    <div className={className}>
      {stats.map((stat) => (
        <StatsCard key={stat.label} {...stat} />
      ))}
    </div>
  )
}
