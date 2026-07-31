import { useEffect, useRef } from 'react'
import {
  motion,
  useInView,
  useScroll,
  useTransform,
  animate,
} from 'framer-motion'
import { BarChart3, Play, Sparkles } from 'lucide-react'
import Button from '@/components/ui/Button'

const stats = [
  { label: 'Happy Clients', value: 1200, suffix: '+' },
  { label: 'Strategies Generated', value: 8500, suffix: '+' },
  { label: 'Marketing Success Rate', value: 98, suffix: '%' },
]

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
      {/* Animated gradient blur background */}
      <div aria-hidden className="pointer-events-none absolute inset-0">
        <motion.div
          animate={{ x: [0, 60, 0], y: [0, 40, 0] }}
          transition={{ duration: 14, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute -top-32 -left-32 h-[30rem] w-[30rem] rounded-full bg-indigo-600/30 blur-3xl"
        />
        <motion.div
          animate={{ x: [0, -60, 0], y: [0, -40, 0] }}
          transition={{ duration: 16, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute -right-32 top-1/4 h-[26rem] w-[26rem] rounded-full bg-purple-600/25 blur-3xl"
        />
        <motion.div
          animate={{ x: [0, 40, 0], y: [0, -50, 0] }}
          transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute -bottom-40 left-1/3 h-[28rem] w-[28rem] rounded-full bg-cyan-500/15 blur-3xl"
        />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_0%,#09090b_75%)]" />
      </div>

      <div
        style={{ y, opacity }}
        className="relative z-10 mx-auto grid w-full max-w-7xl items-center gap-16 px-4 py-24 sm:px-6 lg:grid-cols-2 lg:gap-12 lg:px-8"
      >
        {/* Copy */}
        <div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <span className="inline-flex items-center gap-2 rounded-full border border-zinc-800 bg-zinc-900/80 px-3 py-1 text-xs text-zinc-400">
              <Sparkles size={14} className="text-indigo-400" />
              AI-powered marketing intelligence
            </span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="mt-6 text-4xl font-semibold tracking-tight text-white sm:text-5xl lg:text-6xl"
          >
            Your{' '}
            <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
              Intelligent AI
            </span>{' '}
            Marketing Strategist
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="mt-6 max-w-xl text-lg leading-relaxed text-zinc-400"
          >
            Generate complete AI-powered marketing strategies, customer
            personas, SEO ideas, content calendars, and email campaigns in
            seconds.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="mt-10 flex flex-col gap-4 sm:flex-row sm:items-center"
          >
            <Button to="/register" size="lg">
              Generate Strategy
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

          <motion.dl
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.45 }}
            className="mt-14 grid grid-cols-3 gap-6 border-t border-zinc-800 pt-8"
          >
            {stats.map((stat) => (
              <div key={stat.label}>
                <dt className="order-2 mt-1 block text-xs text-zinc-500 sm:text-sm">
                  {stat.label}
                </dt>
                <dd className="order-1 text-2xl font-semibold text-white sm:text-3xl">
                  <Counter value={stat.value} suffix={stat.suffix} />
                </dd>
              </div>
            ))}
          </motion.dl>
        </div>

        {/* Illustration placeholder */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.7, delay: 0.3 }}
          className="relative hidden lg:block"
        >
          <div className="relative rounded-2xl border border-zinc-800 bg-zinc-900/60 p-6 shadow-2xl backdrop-blur">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-4">
              <div className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full bg-red-400" />
                <span className="h-2.5 w-2.5 rounded-full bg-amber-400" />
                <span className="h-2.5 w-2.5 rounded-full bg-emerald-400" />
              </div>
              <span className="rounded-full bg-indigo-500/15 px-2.5 py-0.5 text-xs font-medium text-indigo-300">
                AI Strategy
              </span>
            </div>

            <div className="space-y-4 pt-6">
              {['Market Analysis', 'Customer Personas', 'Content Calendar'].map(
                (label, i) => (
                  <motion.div
                    key={label}
                    animate={{ opacity: [0.5, 1, 0.5] }}
                    transition={{
                      duration: 2.5,
                      repeat: Infinity,
                      delay: i * 0.4,
                      ease: 'easeInOut',
                    }}
                    className="flex items-center gap-4 rounded-xl border border-zinc-800 bg-zinc-950/50 p-4"
                  >
                    <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-500/15">
                      <BarChart3 size={16} className="text-indigo-400" />
                    </span>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-white">{label}</p>
                      <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-zinc-800">
                        <motion.div
                          animate={{ width: ['30%', '85%', '50%'] }}
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
                  </motion.div>
                )
              )}
            </div>

            <motion.div
              animate={{ y: [0, -8, 0] }}
              transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
              className="absolute -right-4 -top-4 rounded-xl border border-zinc-700 bg-zinc-900 px-4 py-2 shadow-xl"
            >
              <p className="text-xs text-zinc-400">Strategy ready</p>
              <p className="text-sm font-semibold text-emerald-400">98% score</p>
            </motion.div>
          </div>

          <div className="absolute -inset-6 -z-10 rounded-3xl bg-gradient-to-tr from-indigo-500/20 via-purple-500/10 to-cyan-500/20 blur-2xl" />
        </motion.div>
      </div>
    </section>
  )
}
