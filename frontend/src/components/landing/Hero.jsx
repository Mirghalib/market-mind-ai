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
      ref={sectionRef}
      className="relative flex min-h-screen items-center overflow-hidden bg-zinc-950 pt-16 text-zinc-100"
    >
      {/* ===== Animated gradient background ===== */}
      <div aria-hidden className="pointer-events-none absolute inset-0">
        <motion.div
          animate={{ x: [0, 80, 0], y: [0, 40, 0], scale: [1, 1.15, 1] }}
          transition={{ duration: 16, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute -top-40 -left-40 h-[34rem] w-[34rem] rounded-full bg-indigo-600/30 blur-3xl"
        />
        <motion.div
          animate={{ x: [0, -80, 0], y: [0, -50, 0], scale: [1, 1.1, 1] }}
          transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute -right-40 top-1/4 h-[30rem] w-[30rem] rounded-full bg-purple-600/25 blur-3xl"
        />
        <motion.div
          animate={{ x: [0, 50, 0], y: [0, -60, 0] }}
          transition={{ duration: 20, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute -bottom-40 left-1/3 h-[32rem] w-[32rem] rounded-full bg-cyan-500/15 blur-3xl"
        />

        {/* Subtle grid overlay */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:56px_56px] [mask-image:radial-gradient(ellipse_at_center,black_30%,transparent_75%)]" />

        {/* Vignette to keep focus on copy */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_0%,#09090b_80%)]" />
      </div>

      <div
        style={{ y, opacity }}
        className="relative z-10 mx-auto grid w-full max-w-7xl items-center gap-20 px-4 py-24 sm:px-6 lg:grid-cols-2 lg:gap-12 lg:px-8"
      >
        {/* ===== Copy column ===== */}
        <div>
          <motion.div variants={fadeUp} initial="hidden" animate="visible" custom={0}>
            <span className="inline-flex items-center gap-2 rounded-full border border-zinc-700/60 bg-white/5 px-3.5 py-1.5 text-xs font-medium text-zinc-300 backdrop-blur">
              <Sparkles size={14} className="text-indigo-400" />
              AI-powered marketing intelligence
            </span>
          </motion.div>

          <motion.h1
            variants={fadeUp}
            initial="hidden"
            animate="visible"
            custom={1}
            className="mt-6 text-4xl font-bold leading-[1.1] tracking-tight text-white sm:text-5xl lg:text-[3.5rem]"
          >
            Your{' '}
            <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
              Intelligent AI
            </span>{' '}
            Marketing Strategist
          </motion.h1>

          <motion.p
            variants={fadeUp}
            initial="hidden"
            animate="visible"
            custom={2}
            className="mt-6 max-w-xl text-lg leading-relaxed text-zinc-400"
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
              className="group shadow-lg shadow-indigo-500/25"
            >
              Generate Strategy
              <ArrowRight
                size={18}
                className="transition-transform duration-200 group-hover:translate-x-0.5"
              />
            </Button>
            <Button
              onClick={() => console.log('Watch demo clicked')}
              variant="outline"
              size="lg"
            >
              <Play size={18} className="fill-current" />
              Watch Demo
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
                    'flex h-8 w-8 items-center justify-center rounded-full border-2 border-zinc-950 text-[10px] font-semibold text-white',
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
                <span className="ml-1.5 text-sm font-medium text-white">4.9/5</span>
              </div>
              <p className="mt-0.5 text-xs text-zinc-500">
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
            className="mt-14 grid grid-cols-3 gap-6 border-t border-zinc-800 pt-8"
          >
            {stats.map((stat) => (
              <div key={stat.label}>
                <dd className="text-2xl font-semibold text-white sm:text-3xl">
                  <Counter value={stat.value} suffix={stat.suffix} />
                </dd>
                <dt className="mt-1 text-xs text-zinc-500 sm:text-sm">
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
          <div className="absolute -inset-8 -z-10 rounded-[2.5rem] bg-gradient-to-tr from-indigo-500/20 via-purple-500/10 to-cyan-500/20 blur-3xl" />

          {/* Main glass panel */}
          <div className="relative rounded-3xl border border-white/10 bg-white/[0.04] p-6 shadow-2xl backdrop-blur-xl">
            {/* Window chrome */}
            <div className="flex items-center justify-between border-b border-white/5 pb-4">
              <div className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-full bg-red-400/80" />
                <span className="h-2.5 w-2.5 rounded-full bg-amber-400/80" />
                <span className="h-2.5 w-2.5 rounded-full bg-emerald-400/80" />
              </div>
              <span className="rounded-full border border-indigo-400/20 bg-indigo-500/15 px-2.5 py-0.5 text-xs font-medium text-indigo-300">
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
                  className="h-40 w-full max-w-[2.2rem] rounded-t-lg bg-gradient-to-t from-indigo-500/25 to-indigo-400/60"
                />
              ))}
            </div>

            {/* Metric rows */}
            <div className="mt-6 space-y-3">
              {['Market Analysis', 'Customer Personas', 'Content Calendar'].map(
                (label, i) => (
                  <div
                    key={label}
                    className="flex items-center gap-4 rounded-xl border border-white/5 bg-white/[0.03] p-3.5"
                  >
                    <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-indigo-500/15">
                      <BarChart3 size={16} className="text-indigo-400" />
                    </span>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-white">{label}</p>
                      <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-white/5">
                        <motion.div
                          animate={{ width: ['35%', '88%', '55%'] }}
                          transition={{
                            duration: 2.5,
                            repeat: Infinity,
                            delay: i * 0.4,
                            ease: 'easeInOut',
                          }}
                          className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-purple-500"
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
                'absolute z-10 flex items-center gap-2.5 rounded-2xl border border-white/10 bg-white/[0.06] px-4 py-3 shadow-xl backdrop-blur-xl',
                pos
              )}
            >
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-500/20">
                <Icon size={15} className="text-indigo-300" />
              </span>
              <div>
                <p className="text-xs text-zinc-400">{label}</p>
                <p className="text-sm font-semibold text-white">98% score</p>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
