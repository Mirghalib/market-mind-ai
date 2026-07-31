import AreaChart from '../Charts/AreaChart'

const defaultData = [
  { label: 'Jan', value: 32 },
  { label: 'Feb', value: 41 },
  { label: 'Mar', value: 38 },
  { label: 'Apr', value: 55 },
  { label: 'May', value: 49 },
  { label: 'Jun', value: 62 },
  { label: 'Jul', value: 74 },
]

/**
 * Engagement-over-time panel. Composes the reusable AreaChart
 * with representative placeholder data.
 */
export default function EngagementChart({ data = defaultData, className }) {
  return (
    <div
      className={`rounded-2xl border border-white/10 bg-white/[0.03] p-6 shadow-lg shadow-black/20 backdrop-blur ${className ?? ''}`}
    >
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-semibold text-white">Engagement over time</h3>
          <p className="mt-0.5 text-sm text-zinc-500">
            Monthly audience interaction
          </p>
        </div>
      </div>
      <div className="mt-6">
        <AreaChart data={data} />
      </div>
    </div>
  )
}
