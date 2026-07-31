export default function Dashboard() {
  return (
    <div className="mx-auto max-w-7xl p-6 sm:p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-white">Dashboard</h1>
        <p className="mt-1 text-sm text-zinc-400">
          Overview of your market insights
        </p>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {['Market overview', 'Competitor insights', 'Trend predictions'].map(
          (title) => (
            <div
              key={title}
              className="rounded-2xl border border-zinc-800 bg-zinc-900/50 p-6"
            >
              <h2 className="font-medium text-white">{title}</h2>
              <p className="mt-2 text-sm text-zinc-500">
                Content coming soon.
              </p>
            </div>
          )
        )}
      </div>
    </div>
  )
}
