import { motion } from 'framer-motion'
import {
  BarChart3,
  CalendarDays,
  LineChart,
  Mail,
  Megaphone,
  Search,
  Share2,
  Target,
} from 'lucide-react'
import SectionTitle from '@/components/ui/SectionTitle'
import { cn } from '@/utils/cn'

const capabilities = [
  {
    icon: BarChart3,
    title: 'Market Analysis',
    description:
      'Live market size, growth rate, key trends, and drivers synthesized from your brief.',
  },
  {
    icon: Target,
    title: 'Customer Personas',
    description:
      'Demographics, pain points, buying triggers, and objections — fully mapped.',
  },
  {
    icon: Search,
    title: 'SEO Strategy',
    description:
      'Priority keywords, content topics, and on-page recommendations for your niche.',
  },
  {
    icon: CalendarDays,
    title: 'Content Calendar',
    description:
      'A month of ready-to-publish content aligned to every channel and funnel stage.',
  },
  {
    icon: Mail,
    title: 'Email Campaigns',
    description:
      'Subject lines, nurture sequences, and conversion-focused copy drafted for you.',
  },
  {
    icon: Megaphone,
    title: 'Ad Campaigns',
    description:
      'Google & Meta campaign structures with budgets, audiences, and expected outcomes.',
  },
  {
    icon: Share2,
    title: 'Social Strategy',
    description:
      'Platform-specific posting cadence, content mix, and community management.',
  },
  {
    icon: LineChart,
    title: 'ROI Projections',
    description:
      '90-day ROI forecasts, payback period, and a phased implementation roadmap.',
  },
]

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.06 } },
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.45, ease: 'easeOut' } },
}

export default function Capabilities() {
  return (
    <section
      id="capabilities"
      aria-label="Capabilities"
      className="bg-landing-bg py-24"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionTitle
          eyebrow="Capabilities"
          title="Powered by AI, built for marketers"
          description="Every strategy ships with eight fully integrated modules — from market research to a measurable 90-day growth plan."
          align="center"
        />

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-60px' }}
          className="mt-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-4"
        >
          {capabilities.map(({ icon: Icon, title, description }) => (
            <motion.div
              key={title}
              variants={itemVariants}
              className="group rounded-2xl border border-landing-border bg-landing-card p-5 backdrop-blur transition-all duration-300 hover:-translate-y-1 hover:border-landing-border-strong"
            >
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-accent-500/15 text-accent-400 transition-transform duration-300 group-hover:scale-110">
                <Icon size={19} strokeWidth={1.75} />
              </span>
              <h3 className={cn('mt-4 text-sm font-semibold text-landing-text')}>
                {title}
              </h3>
              <p className="mt-1.5 text-xs leading-relaxed text-landing-muted">
                {description}
              </p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
