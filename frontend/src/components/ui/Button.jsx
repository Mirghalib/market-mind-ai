import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { cn } from '@/utils/cn'

const variants = {
  primary:
    'bg-[var(--color-accent-500)] text-white hover:bg-[var(--color-accent-400)] active:bg-[var(--color-accent-600)]',
  secondary:
    'bg-muted text-foreground hover:bg-zinc-700 dark:bg-white dark:text-zinc-900 dark:hover:bg-zinc-200',
  outline:
    'border border-border text-foreground hover:bg-muted dark:border-zinc-700 dark:text-zinc-100 dark:hover:bg-zinc-800',
  ghost:
    'text-muted-foreground hover:bg-muted dark:text-zinc-300 dark:hover:bg-zinc-800',
  danger: 'bg-red-500 text-white hover:bg-red-400 active:bg-red-600',
}

const sizes = {
  sm: 'h-9 px-4 text-sm',
  md: 'h-11 px-6 text-sm',
  lg: 'h-12 px-8 text-base',
}

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  to,
  className,
  ...props
}) {
  const classes = cn(
    'inline-flex cursor-pointer items-center justify-center gap-2 rounded-lg font-medium',
    'transition-all duration-200 focus-visible:outline-2 focus-visible:outline-offset-2',
    'focus-visible:outline-[var(--color-accent-500)]',
    'disabled:pointer-events-none disabled:opacity-50',
    variants[variant],
    sizes[size],
    className
  )

  const content = (
    <motion.span
      className="inline-flex items-center gap-2"
      whileTap={{ scale: 0.97 }}
    >
      {children}
    </motion.span>
  )

  if (to) {
    return (
      <Link to={to} className={classes}>
        {content}
      </Link>
    )
  }

  return (
    <button className={classes} {...props}>
      {content}
    </button>
  )
}
