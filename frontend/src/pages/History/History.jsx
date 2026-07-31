import { useState } from 'react'
import DashboardHeader from '@/components/dashboard/DashboardHeader'
import HistoryTable from '@/components/dashboard/HistoryTable'
import Button from '@/components/ui/Button'
import Modal from '@/components/ui/Modal'
import { AlertTriangle } from 'lucide-react'

const placeholderRows = [
  { id: 1, title: 'SaaS launch strategy', type: 'Full strategy', createdAt: 'Jul 28, 2026', status: 'completed' },
  { id: 2, title: 'Q3 email campaigns', type: 'Campaign', createdAt: 'Jul 25, 2026', status: 'completed' },
  { id: 3, title: 'Local SEO content plan', type: 'Content', createdAt: 'Jul 21, 2026', status: 'processing' },
  { id: 4, title: 'Competitor teardown', type: 'Analysis', createdAt: 'Jul 14, 2026', status: 'failed' },
  { id: 5, title: 'Summer sale promotion', type: 'Campaign', createdAt: 'Jul 9, 2026', status: 'completed' },
  { id: 6, title: 'Brand awareness push', type: 'Full strategy', createdAt: 'Jul 2, 2026', status: 'completed' },
  { id: 7, title: 'LinkedIn content refresh', type: 'Content', createdAt: 'Jun 26, 2026', status: 'processing' },
  { id: 8, title: 'Product launch email', type: 'Campaign', createdAt: 'Jun 19, 2026', status: 'completed' },
  { id: 9, title: 'Market entry analysis', type: 'Analysis', createdAt: 'Jun 11, 2026', status: 'failed' },
]

export default function History() {
  const [rows, setRows] = useState(placeholderRows)
  const [pendingDelete, setPendingDelete] = useState(null)

  const handleView = (row) => {
    // Route to a detail view later — no backend here.
    console.log('View analysis:', row.id)
  }

  const confirmDelete = () => {
    if (!pendingDelete) return
    setRows((current) => current.filter((row) => row.id !== pendingDelete.id))
    setPendingDelete(null)
  }

  return (
    <div className="mx-auto max-w-7xl space-y-8 p-6 sm:p-8">
      <DashboardHeader
        eyebrow="Library"
        title="History"
        subtitle="Browse, filter, and manage your past analyses and saved reports."
        actions={<Button size="sm">Export all</Button>}
      />

      <HistoryTable
        rows={rows}
        onView={handleView}
        onDelete={setPendingDelete}
      />

      {/* Delete confirmation */}
      <Modal
        open={pendingDelete !== null}
        onClose={() => setPendingDelete(null)}
        title="Delete analysis"
      >
        <div className="flex items-start gap-4">
          <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-red-500/15 text-red-500 dark:text-red-400">
            <AlertTriangle size={20} />
          </span>
          <div>
            <p className="text-sm text-muted-foreground dark:text-zinc-300">
              Are you sure you want to delete{' '}
              <span className="font-semibold text-foreground dark:text-white">
                {pendingDelete?.title}
              </span>
              ? This action cannot be undone.
            </p>
          </div>
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <Button variant="outline" onClick={() => setPendingDelete(null)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={confirmDelete}>
            Delete
          </Button>
        </div>
      </Modal>
    </div>
  )
}
