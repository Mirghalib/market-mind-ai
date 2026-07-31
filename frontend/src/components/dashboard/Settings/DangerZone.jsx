import { useState } from 'react'
import { Trash2 } from 'lucide-react'
import Button from '@/components/ui/Button'

/**
 * Destructive account actions. Confirmations are local-only;
 * wire the confirmed callbacks to real APIs in the page.
 */
export default function DangerZone() {
  const [confirming, setConfirming] = useState(false)

  return (
    <div
      className="rounded-2xl border border-red-200 bg-red-50/50 p-6 shadow-sm sm:p-8 dark:border-red-500/20 dark:bg-red-500/[0.04] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur"
    >
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-red-500/15 text-red-600 dark:text-red-400">
          <Trash2 size={19} strokeWidth={1.75} />
        </span>
        <div>
          <h2 className="text-base font-semibold text-zinc-900 dark:text-white">Danger zone</h2>
          <p className="text-sm text-zinc-500 dark:text-zinc-400">
            Irreversible actions for your account.
          </p>
        </div>
      </div>

      <div className="mt-6 flex flex-col items-start justify-between gap-4 rounded-xl border border-zinc-200 bg-zinc-50 p-4 sm:flex-row sm:items-center dark:border-white/5 dark:bg-white/[0.02]">
        <div>
          <p className="text-sm font-medium text-zinc-900 dark:text-white">Delete account</p>
          <p className="mt-0.5 text-sm text-zinc-500 dark:text-zinc-400">
            Permanently remove your account and all saved strategies.
          </p>
        </div>
        {confirming ? (
          <div className="flex items-center gap-2">
            <Button
              type="button"
              variant="danger"
              size="sm"
              onClick={() => setConfirming(false)}
            >
              Confirm delete
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => setConfirming(false)}
            >
              Cancel
            </Button>
          </div>
        ) : (
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => setConfirming(true)}
          >
            Delete account
          </Button>
        )}
      </div>
    </div>
  )
}
