import { AreaChart, BarChart, DonutChart } from '@/components/dashboard/Charts'

const CHART_COLORS = ['#16394A', '#C89B3C', '#5F8B7F', '#E4C171', '#0E2732', '#63666D']

function toNumber(value) {
  const n = Number.parseFloat(String(value ?? '').replace(/[^0-9.-]/g, ''))
  return Number.isFinite(n) ? n : 0
}

/**
 * Web charts for the generated report, driven by the structured
 * `strategy.content` payload (when present):
 *  - Marketing score breakdown (donut)
 *  - Budget allocation (donut)
 *  - ROI projections (area chart)
 */
export default function ReportCharts({ content }) {
  if (!content) return null

  const score = content.marketingScore
  const strategy = content.marketingStrategy || {}
  const roi = content.estimatedROI

  const scoreBreakdown = score?.breakdown?.map((b) => ({
    label: b.area,
    value: b.score,
    color: CHART_COLORS[score.breakdown.indexOf(b) % CHART_COLORS.length],
  }))

  const budget = strategy.budgetAllocation?.map((a, i) => ({
    label: a.channel,
    value: a.percentage,
    color: CHART_COLORS[i % CHART_COLORS.length],
  }))

  const roiData = roi?.projections?.map((p) => ({
    label: p.period,
    value: toNumber(p.roiPercent),
  }))

  const hasAnything = scoreBreakdown || budget || (roiData && roiData.length > 0)
  if (!hasAnything) return null

  return (
    <div className="grid gap-5 lg:grid-cols-2">
      {scoreBreakdown && (
        <div className="rounded-2xl border border-border bg-card p-5 dark:border-white/10 dark:bg-white/[0.03]">
          <h3 className="text-sm font-semibold text-foreground dark:text-white">
            Marketing score breakdown
          </h3>
          <p className="mt-0.5 text-xs text-muted-foreground dark:text-zinc-400">
            Overall: {score.overall}/100
          </p>
          <div className="mt-4">
            <DonutChart
              data={scoreBreakdown}
              size={160}
              centerValue={score.overall}
              centerLabel="/ 100"
            />
          </div>
        </div>
      )}

      {budget && (
        <div className="rounded-2xl border border-border bg-card p-5 dark:border-white/10 dark:bg-white/[0.03]">
          <h3 className="text-sm font-semibold text-foreground dark:text-white">
            Budget allocation
          </h3>
          <p className="mt-0.5 text-xs text-muted-foreground dark:text-zinc-400">
            How the marketing budget is split across channels
          </p>
          <div className="mt-4">
            <DonutChart data={budget} size={160} centerLabel="Budget" />
          </div>
        </div>
      )}

      {roiData && roiData.length > 1 && (
        <div className="rounded-2xl border border-border bg-card p-5 lg:col-span-2 dark:border-white/10 dark:bg-white/[0.03]">
          <h3 className="text-sm font-semibold text-foreground dark:text-white">
            Estimated ROI over time
          </h3>
          <p className="mt-0.5 text-xs text-muted-foreground dark:text-zinc-400">
            Projected return as a percentage of investment
          </p>
          <div className="mt-4">
            <AreaChart data={roiData} height={200} />
          </div>
        </div>
      )}

      {roiData && roiData.length === 1 && (
        <div className="rounded-2xl border border-border bg-card p-5 dark:border-white/10 dark:bg-white/[0.03]">
          <h3 className="text-sm font-semibold text-foreground dark:text-white">
            Estimated ROI
          </h3>
          <div className="mt-4">
            <BarChart data={roiData} height={180} />
          </div>
        </div>
      )}
    </div>
  )
}
