import { cn } from '@/utils/cn'

const sizes = {
  sm: 'h-4 w-4 border-2',
  md: 'h-8 w-8 border-[3px]',
  lg: 'h-12 w-12 border-4',
}

export default function Loader({ size = 'md', className }) {
  return (
    <span
      role="status"
      aria-label="Loading"
      className={cn(
        'inline-block animate-spin rounded-full border-transparent',
        'border-t-indigo-500',
        sizes[size],
        className
      )}
    />
  )
}
