import { cn } from '@/utils/cn'

export default function Input({ label, error, className, id, ...props }) {
  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={id}
          className="mb-1.5 block text-sm font-medium text-foreground dark:text-zinc-300"
        >
          {label}
        </label>
      )}
      <input
        id={id}
        className={cn('h-11 w-full rounded-lg border border-border bg-card px-3.5' ,
          'text-sm text-foreground placeholder-muted-foreground shadow-sm',
          'transition-all duration-200',
          'hover:border-zinc-400 dark:border-zinc-700 dark:bg-zinc-900',
          'dark:text-zinc-100 dark:placeholder-zinc-500 dark:hover:border-zinc-600',
          'focus:border-indigo-500 focus:outline-none focus:ring-2',
          'focus:ring-indigo-500/30 dark:focus:ring-indigo-500/40',
          error &&
            'border-red-500 focus:border-red-500 focus:ring-red-500/30 dark:border-red-500 dark:focus:ring-red-500/40',
          className
        )}
        {...props}
      />
      {error && <p className="mt-1.5 text-sm text-red-500 dark:text-red-400">{error}</p>}
    </div>
  )
}
