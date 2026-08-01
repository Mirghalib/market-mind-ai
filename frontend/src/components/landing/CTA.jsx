import { motion } from 'framer-motion'
import { ArrowRight, Sparkles } from 'lucide-react'
import Button from '@/components/ui/Button'

export default function CTA() {
  return (
    <section
      id="cta"
      aria-label="Get started"
      className="relative overflow-hidden bg-landing-bg py-24"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-60px' }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
          className="relative overflow-hidden rounded-3xl border border-landing-border px-6 py-16 text-center shadow-2xl sm:px-12 sm:py-20"
        >
          {/* Gradient background */}
          <div
            aria-hidden
            className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_left,rgba(99,102,241,0.35),transparent_55%),radial-gradient(ellipse_at_bottom_right,rgba(168,85,247,0.35),transparent_55%),linear-gradient(to_bottom,var(--color-landing-bg),var(--color-landing-card))]"
          />

          {/* Animated aurora glows */}
          <motion.div
            aria-hidden
            animate={{ x: [0, 60, 0], y: [0, 30, 0], scale: [1, 1.15, 1] }}
            transition={{ duration: 14, repeat: Infinity, ease: 'easeInOut' }}
            className="pointer-events-none absolute -top-32 -left-24 h-72 w-72 rounded-full bg-accent-500/30 blur-3xl"
          />
          <motion.div
            aria-hidden
            animate={{ x: [0, -50, 0], y: [0, -40, 0], scale: [1, 1.1, 1] }}
            transition={{ duration: 16, repeat: Infinity, ease: 'easeInOut' }}
            className="pointer-events-none absolute -right-24 -bottom-32 h-72 w-72 rounded-full bg-accent-500/30 blur-3xl"
          />

          {/* Subtle grid overlay */}
          <div
            aria-hidden
            className="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.04)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.04)_1px,transparent_1px)] bg-[size:44px_44px] [mask-image:radial-gradient(ellipse_at_center,black_40%,transparent_75%)]"
          />

          <div className="relative">
            <span className="inline-flex items-center gap-2 rounded-full border border-landing-border bg-landing-card px-4 py-1.5 text-xs font-medium text-landing-muted backdrop-blur">
              <Sparkles size={14} className="text-accent-400" />
              Start growing today
            </span>

            <h2 className="mx-auto mt-6 max-w-2xl text-3xl font-bold tracking-tight text-landing-text sm:text-4xl lg:text-5xl">
              Ready to build your next great{' '}
              <span className="bg-gradient-to-r from-accent-400 via-accent-500 to-accent-300 bg-clip-text text-transparent">
                marketing strategy?
              </span>
            </h2>

            <p className="mx-auto mt-5 max-w-xl text-base leading-relaxed text-landing-muted">
              Join 1,200+ marketing teams already shipping smarter campaigns.
              Free to start, no credit card required.
            </p>

            <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Button
                to="/register"
                size="lg"
                className="group w-full shadow-lg shadow-accent-500/30 sm:w-auto"
              >
                Get Started Free
                <ArrowRight
                  size={18}
                  className="transition-transform duration-200 group-hover:translate-x-0.5"
                />
              </Button>
              <Button
                to="/login"
                variant="outline"
                size="lg"
                className="w-full border-landing-border sm:w-auto"
              >
                Login
              </Button>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
