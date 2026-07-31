import { cn } from '@/utils/cn'

export default function Input({
  label,
  error,
  className,
  id,
  ...props
}) {
  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={id}
          className="mb-1.5 block text-sm font-medium text-zinc-300"
        >
          {label}
        </label>
      )}
      <input
        id={id}
        className={cn(
          'h-11 w-full rounded-lg border border-zinc-700 bg-zinc-900',
          'px-3.5 text-sm text-zinc-100 placeholder-zinc-500',
          'focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30',
          error && 'border-red-500 focus:border-red-500 focus:ring-red-500/30',
          className
        )}
        {...props}
      />
      {error && <p className="mt-1.5 text-sm text-red-400">{error}</p>}
    </div>
  )
}
