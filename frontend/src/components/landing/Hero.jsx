import { useEffect, useRef } from 'react'
import {
  motion,
  useInView,
  useScroll,
  useTransform,
  animate,
} from 'framer-motion'
import {
  ArrowRight,
  BarChart3,
  Brain,
  Play,
  Sparkles,
  Star,
  Target,
  TrendingUp,
  Zap,
} from 'lucide-react'
import Button from '@/components/ui/Button'
import { cn } from '@/utils/cn'

const stats = [
  { label: 'Happy Clients', value: 1200, suffix: '+' },
  { label: 'Strategies Generated', value: 8500, suffix: '+' },
  { label: 'Marketing Success Rate', value: 98, suffix: '%' },
]

const floaters = [
  { icon: Brain, label: 'AI Insights', className: '-top-5 -left-6' },
  { icon: Target, label: '+32% ROI', className: '-bottom-6 -left-10' },
  { icon: TrendingUp, label: 'Growth', className: '-top-4 -right-8' },
]

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, delay: 0.1 * i, ease: 'easeOut' },
  }),
}

function Counter({ value, suffix }) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-60px' })

  useEffect(() => {
    if (!inView) return
    const controls = animate(0, value, {
      duration: 1.6,
      ease: 'easeOut',
      onUpdate: (v) => {
        if (ref.current) ref.current.textContent = `${Math.round(v)}${suffix}`
      },
    })
    return () => controls.stop()
  })

  return <span ref={ref}>0{suffix}</span>
}

export default function Hero() {
  const sectionRef = useRef(null)
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ['start start', 'end start'],
  })
  const y = useTransform(scrollYProgress, [0, 1], [0, 80])
  const opacity = useTransform(scrollYProgress, [0, 0.8], [1, 0])

  return (
    <section
      id="home"
      ref={sectionRef}
      className="relative flex min-h-screen items-center overflow-hidden bg-landing-bg pt-16 text-landing-text"
    >
      {/* ===== Animated gradient background ===== */}
      <div aria-hidden className="pointer-events-none absolute inset-0">
        <motion.div
          animate={{ x: [0, 80, 0], y: [0, 40, 0], scale: [1, 1.15, 1] }}
          transition={{ duration: 16, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute -top-40 -left-40 h-[34rem] w-[34rem] rounded-full bg-accent-600/30 blur-3xl"
        />
        <motion.div
          animate={{ x: [0, -80, 0], y: [0, -50, 0], scale: [1, 1.1, 1] }}
          transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute -right-40 top-1/4 h-[30rem] w-[30rem] rounded-full bg-accent-500/25 blur-3xl"
        />
        <motion.div
          animate={{ x: [0, 50, 0], y: [0, -60, 0] }}
          transition={{ duration: 20, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute -bottom-40 left-1/3 h-[32rem] w-[32rem] rounded-full bg-accent-400/15 blur-3xl"
        />

        {/* Subtle grid overlay */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:56px_56px] [mask-image:radial-gradient(ellipse_at_center,black_30%,transparent_75%)]" />

        {/* Vignette to keep focus on copy */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_0%,var(--color-landing-bg)_80%)]" />
      </div>

      <div
        style={{ y, opacity }}
        className="relative z-10 mx-auto grid w-full max-w-7xl items-center gap-20 px-4 py-24 sm:px-6 lg:grid-cols-2 lg:gap-12 lg:px-8"
      >
        {/* ===== Copy column ===== */}
        <div>
          <motion.div variants={fadeUp} initial="hidden" animate="visible" custom={0}>
            <span className="inline-flex items-center gap-2 rounded-full border border-landing-border bg-landing-card px-3.5 py-1.5 text-xs font-medium text-landing-muted backdrop-blur">
              <Sparkles size={14} className="text-accent-400" />
              AI-powered marketing intelligence
            </span>
          </motion.div>

          <motion.h1
            variants={fadeUp}
            initial="hidden"
            animate="visible"
            custom={1}
            className="mt-6 text-4xl font-bold leading-[1.1] tracking-tight text-landing-text sm:text-5xl lg:text-[3.5rem]"
          >
            Your{' '}
            <span className="bg-gradient-to-r from-accent-400 via-accent-500 to-accent-300 bg-clip-text text-transparent">
              Intelligent AI
            </span>{' '}
            Marketing Strategist
          </motion.h1>

          <motion.p
            variants={fadeUp}
            initial="hidden"
            animate="visible"
            custom={2}
            className="mt-6 max-w-xl text-lg leading-relaxed text-landing-muted"
          >
            Generate complete AI-powered marketing strategies, customer
            personas, SEO ideas, content calendars, and email campaigns in
            seconds.
          </motion.p>

          {/* CTAs */}
          <motion.div
            variants={fadeUp}
            initial="hidden"
            animate="visible"
            custom={3}
            className="mt-10 flex flex-col gap-4 sm:flex-row sm:items-center"
          >
            <Button
              to="/register"
              size="lg"
              className="group shadow-lg shadow-accent-500/25"
            >
              Generate Strategy
              <ArrowRight
                size={18}
                className="transition-transform duration-200 group-hover:translate-x-0.5"
              />
            </Button>
            <Button
              onClick={() => {
                // Scroll to features section instead of a dead button.
                document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })
              }}
              variant="outline"
              size="lg"
            >
              <Play size={18} className="fill-current" />
              See How It Works
            </Button>
          </motion.div>

          {/* Trusted badge */}
          <motion.div
            variants={fadeUp}
            initial="hidden"
            animate="visible"
            custom={4}
            className="mt-10 flex flex-wrap items-center gap-x-4 gap-y-3"
          >
            <div className="flex -space-x-2.5">
              {['JD', 'AK', 'SM', 'PL'].map((initials, i) => (
                <span
                  key={initials}
                  className={cn(
                    'flex h-8 w-8 items-center justify-center rounded-full border-2 border-landing-bg text-[10px] font-semibold text-white',
                    ['bg-indigo-500', 'bg-purple-500', 'bg-cyan-500', 'bg-rose-500'][i]
                  )}
                >
                  {initials}
                </span>
              ))}
            </div>
            <div>
              <div className="flex items-center gap-0.5">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Star key={i} size={14} className="fill-amber-400 text-amber-400" />
                ))}
                <span className="ml-1.5 text-sm font-medium text-landing-text">4.9/5</span>
              </div>
              <p className="mt-0.5 text-xs text-landing-muted">
                Trusted by 1,200+ marketing teams
              </p>
            </div>
          </motion.div>

          {/* Statistics */}
          <motion.dl
            variants={fadeUp}
            initial="hidden"
            animate="visible"
            custom={5}
            className="mt-14 grid grid-cols-3 gap-6 border-t border-landing-border pt-8"
          >
            {stats.map((stat) => (
              <div key={stat.label}>
                <dd className="text-2xl font-semibold text-landing-text sm:text-3xl">
                  <Counter value={stat.value} suffix={stat.suffix} />
                </dd>
                <dt className="mt-1 text-xs text-landing-muted sm:text-sm">
                  {stat.label}
                </dt>
              </div>
            ))}
          </motion.dl>
        </div>

        {/* ===== Visual column: glassmorphism dashboard ===== */}
        <motion.div
          initial={{ opacity: 0, scale: 0.94, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.3, ease: 'easeOut' }}
          className="relative hidden lg:block"
        >
          {/* Glow behind panel */}
          <div className="absolute -inset-8 -z-10 rounded-[2.5rem] bg-gradient-to-tr from-accent-500/20 via-accent-500/10 to-accent-400/20 blur-3xl" />

          {/* Main glass panel */}
          <div className="relative rounded-3xl border border-landing-border bg-landing-card p-6 shadow-2xl backdrop-blur-xl">
            {/* Window chrome */}
            <div className="flex items-center justify-between border-b border-landing-border pb-4">
              <div className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-full bg-red-400/80" />
                <span className="h-2.5 w-2.5 rounded-full bg-amber-400/80" />
                <span className="h-2.5 w-2.5 rounded-full bg-emerald-400/80" />
              </div>
              <span className="rounded-full border border-accent-400/20 bg-accent-500/15 px-2.5 py-0.5 text-xs font-medium text-accent-300">
                <Zap size={10} className="mr-1 inline" />
                Live
              </span>
            </div>

            {/* Chart area */}
            <div className="mt-6 flex items-end justify-between gap-3">
              {[35, 55, 42, 70, 58, 85, 66, 95, 78, 90].map((h, i) => (
                <motion.div
                  key={i}
                  initial={{ height: 0 }}
                  animate={{ height: `${h}%` }}
                  transition={{ duration: 0.8, delay: 0.5 + i * 0.06, ease: 'easeOut' }}
                  className="h-40 w-full max-w-[2.2rem] rounded-t-lg bg-gradient-to-t from-accent-500/25 to-accent-400/60"
                />
              ))}
            </div>

            {/* Metric rows */}
            <div className="mt-6 space-y-3">
              {['Market Analysis', 'Customer Personas', 'Content Calendar'].map(
                (label, i) => (
                  <div
                    key={label}
                    className="flex items-center gap-4 rounded-xl border border-landing-border bg-landing-card p-3.5"
                  >
                    <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-accent-500/15">
                      <BarChart3 size={16} className="text-accent-400" />
                    </span>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-landing-text">{label}</p>
                      <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-landing-card">
                        <motion.div
                          animate={{ width: ['35%', '88%', '55%'] }}
                          transition={{
                            duration: 2.5,
                            repeat: Infinity,
                            delay: i * 0.4,
                            ease: 'easeInOut',
                          }}
                          className="h-full rounded-full bg-gradient-to-r from-accent-500 to-accent-400"
                        />
                      </div>
                    </div>
                  </div>
                )
              )}
            </div>
          </div>

          {/* Floating glass stat cards */}
          {floaters.map(({ icon: Icon, label, className: pos }, i) => (
            <motion.div
              key={label}
              animate={{ y: [0, -10, 0] }}
              transition={{
                duration: 4 + i,
                repeat: Infinity,
                ease: 'easeInOut',
                delay: i * 0.6,
              }}
              className={cn(
                'absolute z-10 flex items-center gap-2.5 rounded-2xl border border-landing-border-strong bg-landing-card-hover px-4 py-3 shadow-xl backdrop-blur-xl',
                pos
              )}
            >
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent-500/20">
                <Icon size={15} className="text-accent-300" />
              </span>
              <div>
                <p className="text-xs text-landing-muted">{label}</p>
                <p className="text-sm font-semibold text-landing-text">98% score</p>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
