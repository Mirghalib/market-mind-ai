import { ChevronDown } from 'lucide-react'
import { cn } from '@/utils/cn'

export default function Select({ label, error, className, id, children, ...props }) {
  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={id}
          className="mb-1.5 block text-sm font-medium text-zinc-700 dark:text-zinc-300"
        >
          {label}
        </label>
      )}
      <div className="relative">
        <select
          id={id}
          className={cn(
            'h-11 w-full cursor-pointer appearance-none rounded-lg border',
            'border-zinc-300 bg-white px-3.5 pr-10 text-sm text-zinc-900',
            'shadow-sm transition-all duration-200',
            'hover:border-zinc-400 dark:border-zinc-700 dark:bg-zinc-900',
            'dark:text-zinc-100 dark:hover:border-zinc-600',
            'focus:border-indigo-500 focus:outline-none focus:ring-2',
            'focus:ring-indigo-500/30 dark:focus:ring-indigo-500/40',
            'disabled:cursor-not-allowed disabled:opacity-50',
            error &&
              'border-red-500 focus:border-red-500 focus:ring-red-500/30 dark:border-red-500 dark:focus:ring-red-500/40',
            className
          )}
          {...props}
        >
          {children}
        </select>
        <ChevronDown
          size={16}
          className="pointer-events-none absolute right-3.5 top-1/2 -translate-y-1/2 text-zinc-400 dark:text-zinc-500"
        />
      </div>
      {error && <p className="mt-1.5 text-sm text-red-500 dark:text-red-400">{error}</p>}
    </div>
  )
}
