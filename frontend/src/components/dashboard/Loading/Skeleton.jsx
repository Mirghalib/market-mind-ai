import { cn } from '@/utils/cn'

/**
 * Generic shimmering skeleton block. Compose with `h-*` / `w-*` sizing utilities.
 */
export default function Skeleton({ className }) {
  return (
    <span
      aria-hidden
      className={cn(
        'block animate-pulse rounded-lg bg-zinc-800/80',
        className
      )}
    />
  )
}
