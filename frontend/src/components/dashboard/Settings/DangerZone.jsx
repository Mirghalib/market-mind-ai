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
      className="rounded-2xl border border-red-500/20 bg-red-500/[0.04] p-6 shadow-lg shadow-black/20 backdrop-blur sm:p-8"
    >
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-red-500/15 text-red-400">
          <Trash2 size={19} strokeWidth={1.75} />
        </span>
        <div>
          <h2 className="text-base font-semibold text-white">Danger zone</h2>
          <p className="text-sm text-zinc-500">
            Irreversible actions for your account.
          </p>
        </div>
      </div>

      <div className="mt-6 flex flex-col items-start justify-between gap-4 rounded-xl border border-white/5 bg-white/[0.02] p-4 sm:flex-row sm:items-center">
        <div>
          <p className="text-sm font-medium text-white">Delete account</p>
          <p className="mt-0.5 text-sm text-zinc-500">
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
