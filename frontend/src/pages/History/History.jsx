export default function History() {
  return (
    <div className="mx-auto max-w-7xl p-6 sm:p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-white">History</h1>
        <p className="mt-1 text-sm text-zinc-400">
          Your past analyses and reports
        </p>
      </div>

      <div className="rounded-2xl border border-zinc-800 bg-zinc-900/50 p-6">
        <p className="text-sm text-zinc-500">
          No analyses yet. Your saved reports will appear here.
        </p>
      </div>
    </div>
  )
}
