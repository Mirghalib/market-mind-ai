import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { cn } from '@/utils/cn'

const variants = {
  primary:
    'bg-indigo-500 text-white hover:bg-indigo-400 focus-visible:outline-indigo-500',
  secondary:
    'bg-white text-zinc-900 hover:bg-zinc-200 focus-visible:outline-white',
  outline:
    'border border-zinc-700 text-zinc-100 hover:bg-zinc-800 focus-visible:outline-zinc-500',
  ghost: 'text-zinc-300 hover:bg-zinc-800 hover:text-white focus-visible:outline-zinc-500',
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
    'inline-flex items-center justify-center gap-2 rounded-lg font-medium',
    'transition-colors focus-visible:outline-2 focus-visible:outline-offset-2',
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
