/**
 * Serialize the admin analytics payload to a CSV file download.
 * Returns true on success so callers can toast about it.
 */
export function exportAnalyticsCsv(analytics) {
  if (!analytics) return false

  const rows = []

  const pushSection = (title, data, labelName = 'Label', valueName = 'Value') => {
    if (title) rows.push([title])
    for (const item of data ?? []) {
      rows.push([String(item?.label ?? ''), String(item?.value ?? 0)])
    }
    rows.push([])
  }

  rows.push(['Market Mind AI — Platform Analytics'])
  rows.push([`Generated at ${new Date().toISOString()}`])
  rows.push([])

  rows.push(['Stats'])
  const stats = analytics.stats ?? {}
  for (const [key, value] of Object.entries(stats)) {
    rows.push([key, String(value)])
  }
  rows.push([])

  pushSection('Strategies generated (last 30 days)', analytics.strategy_trend)
  pushSection('Export formats', analytics.export_formats)
  pushSection('User status', analytics.user_status)
  pushSection('Top users', analytics.top_users, 'User', 'Strategies')
  pushSection('Monthly registrations', analytics.monthly_registrations)
  pushSection('Strategy success', analytics.strategy_success)
  rows.push(['AI requests today', String(analytics.ai_requests_today ?? 0)])
  rows.push([])

  pushSection('Recent activity', analytics.recent_activity, 'Type', 'Message')

  const csv = rows
    .map((row) => row.map((cell) => `"${String(cell).replaceAll('"', '""')}"`).join(','))
    .join('\r\n')

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `admin-analytics-${new Date().toISOString().slice(0, 10)}.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  return true
}
