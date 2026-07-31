import Loader from '@/components/ui/Loader'
import { cn } from '@/utils/cn'

/**
 * Centered full-viewport loading state for route transitions / initial fetches.
 */
export default function FullPage({ label = 'Loading…', className }) {
  return (
    <div
      role="status"
      aria-live="polite"
      className={cn(
        'flex min-h-screen flex-col items-center justify-center gap-4 bg-zinc-950',
        className
      )}
    >
      <Loader size="lg" />
      <p className="text-sm text-zinc-500">{label}</p>
    </div>
  )
}
