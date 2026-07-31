import { Cpu, FileText, Gauge, Layers } from 'lucide-react'
import AnalyticsCard from './AnalyticsCard'

const defaultCards = [
  {
    icon: Gauge,
    label: 'Marketing Score',
    value: 86,
    suffix: '',
    delta: '+9.2',
    progress: 86,
    progressLabel: '86 / 100 — strong momentum',
    points: [35, 42, 40, 55, 62, 58, 74],
    tone: 'indigo',
  },
  {
    icon: Layers,
    label: 'Strategies',
    value: 12,
    suffix: '',
    delta: '+3',
    progress: 60,
    progressLabel: '60% toward monthly goal',
    points: [20, 35, 30, 45, 40, 55, 60],
    tone: 'purple',
  },
  {
    icon: FileText,
    label: 'Saved Reports',
    value: 24,
    suffix: '',
    delta: '+5',
    progress: 48,
    progressLabel: '24 reports this quarter',
    points: [40, 38, 45, 42, 50, 55, 52],
    tone: 'cyan',
  },
  {
    icon: Cpu,
    label: 'AI Usage',
    value: 68,
    suffix: '%',
    delta: '-2.1',
    progress: 68,
    progressLabel: '68% of monthly credits used',
    points: [50, 55, 48, 60, 65, 62, 68],
    tone: 'amber',
  },
]

/**
 * The four core analytics cards: Marketing Score, Strategies,
 * Saved Reports, AI Usage. Overridable via `cards` for reuse.
 */
export default function AnalyticsCards({ cards = defaultCards, className }) {
  return (
    <div className={className}>
      {cards.map((card) => (
        <AnalyticsCard key={card.label} {...card} />
      ))}
    </div>
  )
}
