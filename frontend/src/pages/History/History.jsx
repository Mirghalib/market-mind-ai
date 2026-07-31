import { useState } from 'react'
import DashboardHeader from '@/components/dashboard/DashboardHeader'
import HistoryTable from '@/components/dashboard/HistoryTable'
import Button from '@/components/ui/Button'

const placeholderRows = [
  {
    id: 1,
    title: 'SaaS launch strategy',
    type: 'Full strategy',
    createdAt: 'Jul 28, 2026',
    status: 'completed',
  },
  {
    id: 2,
    title: 'Q3 email campaigns',
    type: 'Campaign',
    createdAt: 'Jul 25, 2026',
    status: 'completed',
  },
  {
    id: 3,
    title: 'Local SEO content plan',
    type: 'Content',
    createdAt: 'Jul 21, 2026',
    status: 'processing',
  },
  {
    id: 4,
    title: 'Competitor teardown',
    type: 'Analysis',
    createdAt: 'Jul 14, 2026',
    status: 'failed',
  },
]

export default function History() {
  const [rows] = useState(placeholderRows)

  const handleView = (row) => {
    // Route to a detail view or open a modal — no backend here.
    console.log('View analysis:', row.id)
  }

  return (
    <div className="mx-auto max-w-7xl space-y-8 p-6 sm:p-8">
      <DashboardHeader
        eyebrow="Library"
        title="History"
        subtitle="Browse your past analyses and saved reports."
        actions={<Button size="sm">Export all</Button>}
      />
      <HistoryTable rows={rows} onView={handleView} />
    </div>
  )
}
