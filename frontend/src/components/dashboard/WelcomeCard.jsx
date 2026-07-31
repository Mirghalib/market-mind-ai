import { motion } from 'framer-motion'
import { ArrowRight, Lightbulb, Sparkles } from 'lucide-react'
import Button from '@/components/ui/Button'
import { cn } from '@/utils/cn'

const DEFAULT_TIP =
  'Engage with your top 20% of customers this week — repeat buyers are 5x more likely to try a new product.'

function getGreeting() {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 18) return 'Good afternoon'
  return 'Good evening'
}

function getMotivationalMessage(name) {
  const messages = [
    `Ready to turn insights into action, ${name}?`,
    `Your next big marketing win starts today, ${name}.`,
    `Small steps compound into real growth, ${name}.`,
  ]
  return messages[new Date().getDate() % messages.length]
}

/**
 * Welcome dashboard card: time-based greeting, motivational message,
 * today's marketing tip, gradient background, and a primary CTA.
 * All copy is overridable via props, so it stays reusable.
 */
export default function WelcomeCard({
  name = 'there',
  greeting = getGreeting(),
  message,
  tip = DEFAULT_TIP,
  ctaLabel = 'Generate Strategy',
  ctaTo = '/dashboard',
  onCtaClick,
  className,
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className={cn(
        'relative overflow-hidden rounded-2xl border px-6 py-8 sm:px-8',
        'border-zinc-200 bg-white shadow-sm dark:border-white/10 dark:bg-zinc-900/50 dark:shadow-none',
        className
      )}
    >
      {/* Gradient background */}
      <div
        aria-hidden
        className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_left,rgba(99,102,241,0.14),transparent_55%),radial-gradient(ellipse_at_bottom_right,rgba(168,85,247,0.14),transparent_55%),linear-gradient(to_bottom_right,rgba(255,255,255,0),rgba(34,211,238,0.05))] dark:bg-[radial-gradient(ellipse_at_top_left,rgba(99,102,241,0.32),transparent_55%),radial-gradient(ellipse_at_bottom_right,rgba(168,85,247,0.32),transparent_55%),linear-gradient(to_bottom_right,rgba(255,255,255,0),rgba(34,211,238,0.08))]"
      />

      {/* Animated glows */}
      <motion.div
        aria-hidden
        animate={{ x: [0, 40, 0], y: [0, 20, 0], scale: [1, 1.15, 1] }}
        transition={{ duration: 12, repeat: Infinity, ease: 'easeInOut' }}
        className="pointer-events-none absolute -top-20 -right-20 h-64 w-64 rounded-full bg-indigo-500/10 blur-3xl dark:bg-indigo-500/25"
      />
      <motion.div
        aria-hidden
        animate={{ x: [0, -30, 0], y: [0, -15, 0], scale: [1, 1.1, 1] }}
        transition={{ duration: 14, repeat: Infinity, ease: 'easeInOut' }}
        className="pointer-events-none absolute -bottom-24 left-1/3 h-56 w-56 rounded-full bg-purple-500/10 blur-3xl dark:bg-purple-500/20"
      />

      <div className="relative">
        {/* Greeting + badge */}
        <div className="flex flex-wrap items-center gap-3">
          <span className="inline-flex items-center gap-1.5 rounded-full border border-zinc-200 bg-zinc-50 px-3 py-1 text-xs font-medium text-zinc-600 dark:border-white/10 dark:bg-white/5 dark:text-zinc-300">
            <Sparkles size={12} className="text-indigo-500 dark:text-indigo-400" />
            AI-Powered Insights
          </span>
        </div>

        <h2 className="mt-4 text-2xl font-bold tracking-tight text-zinc-900 sm:text-3xl dark:text-white">
          {greeting}, <span className="text-indigo-600 dark:text-indigo-400">{name}</span> 👋
        </h2>

        <p className="mt-2 max-w-xl text-sm leading-relaxed text-zinc-500 dark:text-zinc-400">
          {message ?? getMotivationalMessage(name)}
        </p>

        {/* Today's tip */}
        <div className="mt-6 flex max-w-xl items-start gap-3 rounded-xl border border-amber-200/70 bg-amber-50/70 p-4 dark:border-amber-400/20 dark:bg-amber-500/10">
          <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-amber-400/20 text-amber-600 dark:text-amber-400">
            <Lightbulb size={15} />
          </span>
          <div>
            <p className="text-xs font-semibold tracking-wide text-amber-700 uppercase dark:text-amber-400">
              Today's tip
            </p>
            <p className="mt-0.5 text-sm leading-relaxed text-amber-800 dark:text-amber-200/90">
              {tip}
            </p>
          </div>
        </div>

        {/* Primary CTA */}
        <div className="mt-7">
          <Button
            to={ctaTo}
            onClick={onCtaClick}
            size="lg"
            className="group shadow-lg shadow-indigo-500/25"
          >
            {ctaLabel}
            <ArrowRight
              size={18}
              className="transition-transform duration-200 group-hover:translate-x-0.5"
            />
          </Button>
        </div>
      </div>
    </motion.div>
  )
}
