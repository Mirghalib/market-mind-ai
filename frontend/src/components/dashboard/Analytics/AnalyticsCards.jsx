import { Cpu, FileText, Gauge, Layers } from 'lucide-react'
import AnalyticsCard from './AnalyticsCard'

/**
 * The four core analytics cards: Marketing Score, Strategies,
 * Saved Reports, AI Usage. Accepts live stats from the backend
 * (total_strategies, total_generations, total_exports); falls back
 * to sensible defaults while loading.
 */
export default function AnalyticsCards({ stats, className }) {
  const cards = [
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
      value: stats?.total_strategies ?? 0,
      suffix: '',
      delta: stats?.total_strategies > 0 ? 'live' : '',
      progress: Math.min(100, (stats?.total_strategies ?? 0) * 10),
      progressLabel: 'Total AI strategies generated',
      points: [20, 35, 30, 45, 40, 55, 60],
      tone: 'purple',
    },
    {
      icon: FileText,
      label: 'Exports',
      value: stats?.total_exports ?? 0,
      suffix: '',
      delta: stats?.total_exports > 0 ? 'live' : '',
      progress: Math.min(100, (stats?.total_exports ?? 0) * 10),
      progressLabel: 'Strategies exported as files',
      points: [40, 38, 45, 42, 50, 55, 52],
      tone: 'cyan',
    },
    {
      icon: Cpu,
      label: 'Generations',
      value: stats?.total_generations ?? 0,
      suffix: '',
      delta: stats?.total_generations > 0 ? 'live' : '',
      progress: Math.min(100, (stats?.total_generations ?? 0) * 8),
      progressLabel: 'Total AI generations',
      points: [50, 55, 48, 60, 65, 62, 68],
      tone: 'amber',
    },
  ]

  return (
    <div className={className}>
      {cards.map((card) => (
        <AnalyticsCard key={card.label} {...card} />
      ))}
    </div>
  )
}
