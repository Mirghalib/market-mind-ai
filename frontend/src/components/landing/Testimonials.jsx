import { motion } from 'framer-motion'
import { Quote, Star } from 'lucide-react'
import SectionTitle from '@/components/ui/SectionTitle'
import { cn } from '@/utils/cn'

const testimonials = [
  {
    name: 'Jessica Davis',
    role: 'Marketing Lead, NovaTech',
    quote:
      'We went from blank page to a full campaign strategy in minutes. Market Mind AI understands our brand better than most agencies we have worked with.',
    initials: 'JD',
    avatar: 'from-indigo-500 to-purple-500',
  },
  {
    name: 'Alex Kim',
    role: 'Founder, Stackly',
    quote:
      'The competitor intel alone pays for itself. We spotted a pricing shift a week before it hit the market and repositioned before anyone else.',
    initials: 'AK',
    avatar: 'from-purple-500 to-cyan-500',
  },
  {
    name: 'Sara Mitchell',
    role: 'CMO, Vertex',
    quote:
      'Our content calendar has never been this consistent. It generates on-brand ideas our team actually wants to publish — every single week.',
    initials: 'SM',
    avatar: 'from-cyan-500 to-emerald-500',
  },
]

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.12 } },
}

const cardVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: 'easeOut' } },
}

function Stars() {
  return (
    <div className="flex items-center gap-1" aria-label="5 out of 5 stars">
      {Array.from({ length: 5 }).map((_, i) => (
        <Star
          key={i}
          size={16}
          className="fill-amber-400 text-amber-400 drop-shadow-[0_0_6px_rgba(251,191,36,0.35)]"
        />
      ))}
    </div>
  )
}

export default function Testimonials() {
  return (
    <section
      id="testimonials"
      aria-label="Testimonials"
      className="relative overflow-hidden bg-zinc-950 py-24"
    >
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute top-0 left-1/2 h-64 w-[36rem] -translate-x-1/2 rounded-full bg-cyan-500/10 blur-3xl"
      />

      <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionTitle
          eyebrow="Testimonials"
          title="Loved by marketing teams"
          description="See how teams ship better strategies, faster — straight from the people using it."
          align="center"
        />

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-60px' }}
          className="mt-16 grid gap-6 md:grid-cols-3"
        >
          {testimonials.map((t) => (
            <motion.figure
              key={t.name}
              variants={cardVariants}
              className="group relative flex flex-col overflow-hidden rounded-2xl border border-zinc-800 bg-white/[0.03] p-7 shadow-lg shadow-black/20 backdrop-blur transition-all duration-300 hover:-translate-y-1.5 hover:border-white/20 hover:shadow-xl hover:shadow-cyan-500/10"
            >
              {/* Hover glow */}
              <div
                aria-hidden
                className="pointer-events-none absolute -top-20 left-1/2 h-40 w-40 -translate-x-1/2 rounded-full bg-indigo-500/15 blur-2xl opacity-0 transition-opacity duration-300 group-hover:opacity-100"
              />

              {/* Decorative quote mark */}
              <Quote
                aria-hidden
                size={28}
                className="absolute top-6 right-6 text-white/[0.06] transition-colors duration-300 group-hover:text-white/10"
              />

              <Stars />

              <blockquote className="relative mt-5 flex-1 text-sm leading-relaxed text-zinc-400">
                “{t.quote}”
              </blockquote>

              <figcaption className="relative mt-7 flex items-center gap-4 border-t border-zinc-800 pt-6">
                <span
                  aria-hidden
                  className={cn(
                    'flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-gradient-to-br text-sm font-semibold text-white shadow-lg',
                    t.avatar
                  )}
                >
                  {t.initials}
                </span>
                <div>
                  <p className="text-sm font-semibold text-white">{t.name}</p>
                  <p className="mt-0.5 text-xs text-zinc-400">{t.role}</p>
                </div>
              </figcaption>
            </motion.figure>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
