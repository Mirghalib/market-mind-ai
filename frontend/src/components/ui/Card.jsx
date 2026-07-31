import { cn } from '@/utils/cn'

export default function Card({ children, className, ...props }) {
  return (
    <div
      className={cn(
        'rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm',
        'transition-all duration-200',
        'dark:border-zinc-800 dark:bg-zinc-900/50',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}
