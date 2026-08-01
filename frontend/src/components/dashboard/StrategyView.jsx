import { Rocket, Users, Layers, CalendarDays, Mail, Megaphone, Search } from 'lucide-react'
import ExportCenter from '@/components/dashboard/ExportCenter'
import ReportCharts from '@/components/dashboard/ReportCharts'

/**
 * Map the backend's StrategyGenerationResponse (summary + sections)
 * into the result-card shape expected by <ResultCards />.
 */
const ICONS = {
  'Marketing Strategy': Rocket,
  'Customer Persona': Users,
  'SWOT Analysis': Layers,
  'Content Calendar': CalendarDays,
  'Email Campaign': Mail,
  'Advertisement Ideas': Megaphone,
  'SEO Ideas': Search,
}

const TONES = [
  'indigo',
  'purple',
  'cyan',
  'emerald',
  'amber',
  'rose',
  'blue',
  'fuchsia',
]

export function strategyToCards(strategy) {
  const sections = strategy?.sections ?? []
  return sections.map((section, index) => {
    const title = section.title
    const content = section.content ?? ''
    const firstLine = content.split(/\n/)[0]?.trim() ?? ''
    const details = content
      .split(/\n/)
      .slice(1)
      .filter((line) => line.trim().length > 0)

    return {
      id: `${title.toLowerCase().replace(/\s+/g, '-')}-${index}`,
      title,
      description: firstLine,
      icon: ICONS[title] ?? Rocket,
      tone: TONES[index % TONES.length],
      items: details.length > 0 ? details.slice(0, 4) : [],
      content: [
        {
          heading: 'Details',
          points: details.length > 0 ? details : [firstLine],
        },
      ],
    }
  })
}

/**
 * Render the full strategy: a summary banner plus the section cards.
 */
export function StrategyView({ strategy, onReset, businessName }) {
  if (!strategy) return null

  const cards = strategyToCards(strategy)

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-indigo-500/20 bg-indigo-500/[0.06] px-5 py-4">
        <p className="text-xs font-semibold tracking-wide text-indigo-600 uppercase dark:text-indigo-400">
          Strategy summary
        </p>
        <p className="mt-1 text-sm leading-relaxed text-foreground dark:text-zinc-300">
          {strategy.summary}
        </p>
        <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-muted-foreground dark:text-zinc-400">
          <span>Model: {strategy.model_used}</span>
          <span aria-hidden>·</span>
          <span>ID: {strategy.strategy_id?.slice(0, 8)}</span>
          {onReset && (
            <button
              type="button"
              onClick={onReset}
              className="ml-auto font-medium text-indigo-600 transition-colors hover:text-indigo-500 dark:text-indigo-400 dark:hover:text-indigo-300"
            >
              Generate another
            </button>
          )}
        </div>
      </div>

      {/* Export Center — professional report downloads */}
      <ExportCenter
        strategyId={strategy.strategy_id}
        businessName={businessName}
      />

      {/* Web charts driven by the structured content */}
      <ReportCharts content={strategy.content} />

      <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
        {cards.map((card) => (
          <div
            key={card.id}
            className="rounded-2xl border border-border bg-card p-5 shadow-sm dark:border-white/10 dark:bg-white/[0.03]"
          >
            <div className="flex items-center gap-2.5">
              <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-500/15 text-indigo-600 dark:text-indigo-400">
                <card.icon size={17} strokeWidth={1.75} />
              </span>
              <h3 className="text-sm font-semibold text-foreground dark:text-white">
                {card.title}
              </h3>
            </div>
            <p className="mt-3 text-sm leading-relaxed text-muted-foreground dark:text-zinc-400">
              {card.content[0]?.points?.join(' ')}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}
