import { motion } from 'framer-motion'
import {
  BarChart3,
  Brain,
  CalendarDays,
  Mail,
  Search,
  Share2,
  Swords,
  Users,
} from 'lucide-react'
import SectionTitle from '@/components/ui/SectionTitle'
import { cn } from '@/utils/cn'

const accents = {
  indigo: {
    icon: 'border-indigo-400/10 bg-gradient-to-br from-indigo-500/25 to-indigo-500/5 text-indigo-400',
    glow: 'bg-indigo-500/15',
  },
  purple: {
    icon: 'border-purple-400/10 bg-gradient-to-br from-purple-500/25 to-purple-500/5 text-purple-400',
    glow: 'bg-purple-500/15',
  },
  cyan: {
    icon: 'border-cyan-400/10 bg-gradient-to-br from-cyan-500/25 to-cyan-500/5 text-cyan-400',
    glow: 'bg-cyan-500/15',
  },
  rose: {
    icon: 'border-rose-400/10 bg-gradient-to-br from-rose-500/25 to-rose-500/5 text-rose-400',
    glow: 'bg-rose-500/15',
  },
  amber: {
    icon: 'border-amber-400/10 bg-gradient-to-br from-amber-500/25 to-amber-500/5 text-amber-400',
    glow: 'bg-amber-500/15',
  },
  emerald: {
    icon: 'border-emerald-400/10 bg-gradient-to-br from-emerald-500/25 to-emerald-500/5 text-emerald-400',
    glow: 'bg-emerald-500/15',
  },
  blue: {
    icon: 'border-blue-400/10 bg-gradient-to-br from-blue-500/25 to-blue-500/5 text-blue-400',
    glow: 'bg-blue-500/15',
  },
  fuchsia: {
    icon: 'border-fuchsia-400/10 bg-gradient-to-br from-fuchsia-500/25 to-fuchsia-500/5 text-fuchsia-400',
    glow: 'bg-fuchsia-500/15',
  },
}

const features = [
  {
    icon: BarChart3,
    accent: 'indigo',
    title: 'Market Analysis',
    description:
      'Live market intelligence with competitor tracking and trend detection across your entire industry.',
  },
  {
    icon: Users,
    accent: 'purple',
    title: 'Customer Personas',
    description:
      'AI-generated buyer personas grounded in your data, refined automatically as your audience evolves.',
  },
  {
    icon: Search,
    accent: 'cyan',
    title: 'SEO Ideas',
    description:
      'Keyword gaps, content opportunities, and ranking insights surfaced for your niche on demand.',
  },
  {
    icon: CalendarDays,
    accent: 'rose',
    title: 'Content Calendar',
    description:
      'A month of ready-to-publish content, aligned to your strategy and scheduled for every channel.',
  },
  {
    icon: Mail,
    accent: 'amber',
    title: 'Email Campaigns',
    description:
      'High-converting campaign sequences drafted from your goals, with subject lines that get opened.',
  },
  {
    icon: Share2,
    accent: 'emerald',
    title: 'Social Strategy',
    description:
      'Platform-specific posting plans with hooks and formats tuned to each unique audience.',
  },
  {
    icon: Swords,
    accent: 'blue',
    title: 'Competitor Intel',
    description:
      'Track rival pricing, launches, and positioning to spot openings before anyone else does.',
  },
  {
    icon: Brain,
    accent: 'fuchsia',
    title: 'AI Strategy Chat',
    description:
      'Ask anything and get actionable answers grounded in your brand, data, and campaign goals.',
  },
]

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.08 } },
}

const cardVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: 'easeOut' } },
}

export default function Features() {
  return (
    <section
      id="features"
      aria-label="Features"
      className="relative overflow-hidden bg-zinc-950 py-24"
    >
      {/* Subtle top border glow */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-indigo-500/50 to-transparent"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute top-0 left-1/2 h-64 w-[36rem] -translate-x-1/2 rounded-full bg-indigo-500/10 blur-3xl"
      />

      <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionTitle
          eyebrow="Features"
          title="Everything you need to win"
          description="One platform for the full marketing workflow — from market research to ready-to-publish campaigns."
          align="center"
        />

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-60px' }}
          className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-4"
        >
          {features.map(({ icon: Icon, accent, title, description }) => {
            const styles = accents[accent]
            return (
              <motion.article
                key={title}
                variants={cardVariants}
                className="group relative overflow-hidden rounded-2xl border border-white/10 bg-white/[0.03] p-6 shadow-lg shadow-black/20 backdrop-blur transition-all duration-300 hover:-translate-y-1.5 hover:border-white/20 hover:shadow-xl hover:shadow-indigo-500/10"
              >
                {/* Hover glow */}
                <div
                  aria-hidden
                  className={cn(
                    'pointer-events-none absolute -top-16 left-1/2 h-32 w-32 -translate-x-1/2 rounded-full blur-2xl opacity-0 transition-opacity duration-300 group-hover:opacity-100',
                    styles.glow
                  )}
                />

                <span
                  className={cn(
                    'relative inline-flex h-12 w-12 items-center justify-center rounded-xl border shadow-lg transition-transform duration-300 group-hover:scale-110 group-hover:-rotate-3',
                    styles.icon
                  )}
                >
                  <Icon size={22} strokeWidth={1.75} />
                </span>

                <h3 className="relative mt-5 text-base font-semibold tracking-tight text-white">
                  {title}
                </h3>
                <p className="relative mt-2 text-sm leading-relaxed text-zinc-400">
                  {description}
                </p>
              </motion.article>
            )
          })}
        </motion.div>
      </div>
    </section>
  )
}
