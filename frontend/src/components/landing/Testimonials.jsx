import { motion } from 'framer-motion'
import { Quote, Star } from 'lucide-react'
import SectionTitle from '@/components/ui/SectionTitle'

const testimonials = [
  {
    name: 'Jessica Davis',
    role: 'Marketing Lead, NovaTech',
    quote:
      'We went from blank page to a full campaign strategy in minutes. Market Mind AI understands our brand better than most agencies we have worked with.',
    photo:
      'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=96&h=96&fit=crop&crop=faces',
  },
  {
    name: 'Alex Kim',
    role: 'Founder, Stackly',
    quote:
      'The competitor intel alone pays for itself. We spotted a pricing shift a week before it hit the market and repositioned before anyone else.',
    photo:
      'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=96&h=96&fit=crop&crop=faces',
  },
  {
    name: 'Sara Mitchell',
    role: 'CMO, Vertex',
    quote:
      'Our content calendar has never been this consistent. It generates on-brand ideas our team actually wants to publish — every single week.',
    photo:
      'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=96&h=96&fit=crop&crop=faces',
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
      className="relative overflow-hidden bg-landing-bg py-24"
    >
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-accent-500/50 to-transparent"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute top-0 left-1/2 h-64 w-[36rem] -translate-x-1/2 rounded-full bg-accent-500/10 blur-3xl"
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
              className="group relative flex flex-col overflow-hidden rounded-2xl border border-landing-border bg-landing-card p-7 shadow-lg shadow-black/20 backdrop-blur transition-all duration-300 hover:-translate-y-1.5 hover:border-landing-border-strong hover:shadow-xl hover:shadow-accent-500/10"
            >
              {/* Hover glow */}
              <div
                aria-hidden
                className="pointer-events-none absolute -top-20 left-1/2 h-40 w-40 -translate-x-1/2 rounded-full bg-accent-500/15 blur-2xl opacity-0 transition-opacity duration-300 group-hover:opacity-100"
              />

              {/* Decorative quote mark */}
              <Quote
                aria-hidden
                size={28}
                className="absolute top-6 right-6 text-landing-text/[0.06] transition-colors duration-300 group-hover:text-landing-text/10"
              />

              <Stars />

              <blockquote className="relative mt-5 flex-1 text-sm leading-relaxed text-landing-muted">
                “{t.quote}”
              </blockquote>

              <figcaption className="relative mt-7 flex items-center gap-4 border-t border-landing-border pt-6">
                <span
                  aria-hidden
                  className="h-11 w-11 shrink-0 overflow-hidden rounded-full ring-2 ring-accent-500/50 shadow-lg"
                >
                  <img
                    src={t.photo}
                    alt={t.name}
                    loading="lazy"
                    className="h-full w-full object-cover"
                  />
                </span>
                <div>
                  <p className="text-sm font-semibold text-landing-text">{t.name}</p>
                  <p className="mt-0.5 text-xs text-landing-muted">{t.role}</p>
                </div>
              </figcaption>
            </motion.figure>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
