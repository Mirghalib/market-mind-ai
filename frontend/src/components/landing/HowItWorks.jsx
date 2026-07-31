import { motion } from 'framer-motion'
import {
  ClipboardList,
  PenLine,
  Rocket,
  Sparkles,
} from 'lucide-react'
import SectionTitle from '@/components/ui/SectionTitle'
import { cn } from '@/utils/cn'

const steps = [
  {
    icon: ClipboardList,
    accent: 'indigo',
    title: 'Define Your Goals',
    description:
      'Tell us your business, audience, and objectives. Our AI maps out the questions that matter for your strategy.',
  },
  {
    icon: Sparkles,
    accent: 'purple',
    title: 'AI Generates Strategy',
    description:
      'In seconds, get market analysis, customer personas, SEO ideas, content calendars, and campaigns tailored to you.',
  },
  {
    icon: PenLine,
    accent: 'cyan',
    title: 'Review & Refine',
    description:
      'Tweak any section or regenerate on the fly until everything sounds exactly like your brand.',
  },
  {
    icon: Rocket,
    accent: 'amber',
    title: 'Launch & Track',
    description:
      'Export to your channels, publish, and watch performance updates roll in as your strategy evolves.',
  },
]

const accents = {
  indigo: {
    circle:
      'from-indigo-500/25 to-indigo-500/5 border-indigo-400/25 text-indigo-300',
    glow: 'bg-indigo-500/20',
    line: 'from-indigo-500/60 to-indigo-500/0',
  },
  purple: {
    circle:
      'from-purple-500/25 to-purple-500/5 border-purple-400/25 text-purple-300',
    glow: 'bg-purple-500/20',
    line: 'from-purple-500/60 to-purple-500/0',
  },
  cyan: {
    circle:
      'from-cyan-500/25 to-cyan-500/5 border-cyan-400/25 text-cyan-300',
    glow: 'bg-cyan-500/20',
    line: 'from-cyan-500/60 to-cyan-500/0',
  },
  amber: {
    circle:
      'from-amber-500/25 to-amber-500/5 border-amber-400/25 text-amber-300',
    glow: 'bg-amber-500/20',
    line: 'from-amber-500/60 to-amber-500/0',
  },
}

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.12 } },
}

const cardVariants = {
  hidden: { opacity: 0, y: 28 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.55, ease: 'easeOut' } },
}

function StepCard({ step, index, isLast }) {
  const { icon: Icon, accent, title, description } = step
  const styles = accents[accent]

  return (
    <div className="relative flex gap-6 lg:flex-col lg:gap-0">
      {/* Connector line */}
      {!isLast && (
        <div
          aria-hidden
          className="absolute top-14 left-7 h-[calc(100%-1.75rem)] w-px bg-gradient-to-b from-white/15 to-transparent lg:top-8 lg:left-16 lg:h-px lg:w-full lg:bg-gradient-to-r"
        />
      )}

      <div className="relative shrink-0">
        <motion.div
          whileInView={{ scale: 1 }}
          initial={{ scale: 0.6, opacity: 0 }}
          viewport={{ once: true, margin: '-40px' }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          className={cn(
            'relative flex h-14 w-14 items-center justify-center rounded-full border bg-gradient-to-br shadow-lg backdrop-blur lg:h-16 lg:w-16',
            styles.circle
          )}
        >
          <Icon size={22} strokeWidth={1.75} className="lg:size-6" />
          <span className="absolute -top-1.5 -right-1.5 flex h-6 w-6 items-center justify-center rounded-full border border-zinc-800 bg-zinc-900 text-xs font-semibold text-white shadow-md">
            {index + 1}
          </span>
        </motion.div>
      </div>

      <motion.article
        variants={cardVariants}
        className="group relative flex-1 overflow-hidden rounded-2xl border border-zinc-800 bg-white/[0.03] p-6 shadow-lg shadow-black/20 backdrop-blur transition-all duration-300 hover:-translate-y-1.5 hover:border-white/20 hover:shadow-xl lg:mt-8 hover:shadow-indigo-500/10"
      >
        <div
          aria-hidden
          className={cn(
            'pointer-events-none absolute -top-16 left-1/2 h-32 w-32 -translate-x-1/2 rounded-full blur-2xl opacity-0 transition-opacity duration-300 group-hover:opacity-100',
            styles.glow
          )}
        />

        <p className={cn('text-xs font-semibold tracking-widest uppercase', {
          'text-indigo-400': accent === 'indigo',
          'text-purple-400': accent === 'purple',
          'text-cyan-400': accent === 'cyan',
          'text-amber-400': accent === 'amber',
        })}>
          Step {index + 1}
        </p>
        <h3 className="relative mt-2 text-lg font-semibold tracking-tight text-white">
          {title}
        </h3>
        <p className="relative mt-2 text-sm leading-relaxed text-zinc-400">
          {description}
        </p>
      </motion.article>
    </div>
  )
}

export default function HowItWorks() {
  return (
    <section
      id="how-it-works"
      aria-label="How it works"
      className="relative overflow-hidden bg-zinc-950 py-24"
    >
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-purple-500/50 to-transparent"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute top-0 left-1/2 h-64 w-[36rem] -translate-x-1/2 rounded-full bg-purple-500/10 blur-3xl"
      />

      <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionTitle
          eyebrow="How it works"
          title="From idea to strategy in four steps"
          description="A clear, guided flow from your goals to a shipped, high-performing marketing strategy."
          align="center"
        />

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-80px' }}
          className="mt-16 grid gap-10 lg:grid-cols-4 lg:gap-8"
        >
          {steps.map((step, i) => (
            <StepCard
              key={step.title}
              step={step}
              index={i}
              isLast={i === steps.length - 1}
            />
          ))}
        </motion.div>
      </div>
    </section>
  )
}
