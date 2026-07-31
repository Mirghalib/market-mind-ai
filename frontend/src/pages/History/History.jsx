import { useCallback, useEffect, useState } from 'react'
import DashboardHeader from '@/components/dashboard/DashboardHeader'
import HistoryTable from '@/components/dashboard/HistoryTable'
import Button from '@/components/ui/Button'
import Modal from '@/components/ui/Modal'
import Loader from '@/components/ui/Loader'
import { AlertTriangle } from 'lucide-react'
import { dashboardService } from '@/services/dashboard'

/**
 * Map backend GenerationHistoryRead records to the HistoryTable row
 * shape: { id, title, type, createdAt, status }.
 */
function toRows(records = []) {
  return records.map((record) => ({
    id: record.id,
    title: record.input_params?.project_name || 'Marketing strategy',
    type: record.model_used || 'AI strategy',
    createdAt: record.created_at
      ? new Date(record.created_at).toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric',
        })
      : '—',
    status: record.status === 'success' ? 'completed' : 'failed',
  }))
}

export default function History() {
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [pendingDelete, setPendingDelete] = useState(null)
  const [deleting, setDeleting] = useState(false)

  const loadHistory = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const { data } = await dashboardService.getHistory({ limit: 100 })
      setRows(toRows(data.items))
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          err.response?.data?.message ||
          err.message ||
          'Could not load your history.'
      )
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadHistory()
  }, [loadHistory])

  const confirmDelete = async () => {
    if (!pendingDelete) return
    setDeleting(true)
    try {
      await dashboardService.deleteHistory(pendingDelete.id)
      setRows((current) => current.filter((row) => row.id !== pendingDelete.id))
      setPendingDelete(null)
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          err.response?.data?.message ||
          err.message ||
          'Could not delete this record.'
      )
    } finally {
      setDeleting(false)
    }
  }

  return (
    <div className="mx-auto max-w-7xl space-y-8 p-6 sm:p-8">
      <DashboardHeader
        eyebrow="Library"
        title="History"
        subtitle="Browse, filter, and manage your past analyses and saved reports."
      />

      {loading ? (
        <div className="flex items-center justify-center rounded-2xl border border-border bg-card py-20 dark:border-white/10">
          <Loader size="lg" />
        </div>
      ) : error ? (
        <div
          role="alert"
          className="rounded-2xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-sm text-red-400"
        >
          {error}
        </div>
      ) : (
        <HistoryTable rows={rows} onDelete={setPendingDelete} />
      )}

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
          <Button variant="danger" onClick={confirmDelete} disabled={deleting}>
            {deleting ? 'Deleting…' : 'Delete'}
          </Button>
        </div>
      </Modal>
    </div>
  )
}
