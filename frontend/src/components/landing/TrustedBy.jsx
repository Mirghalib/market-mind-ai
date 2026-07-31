import { useEffect, useRef } from 'react'
import { motion, useInView, animate } from 'framer-motion'
import {
  Aperture,
  Boxes,
  Command,
  Globe,
  Hexagon,
  Layers,
  Rocket,
  Zap,
} from 'lucide-react'
import { cn } from '@/utils/cn'

const companies = [
  { name: 'NovaTech', icon: Rocket },
  { name: 'Hexagon', icon: Hexagon },
  { name: 'Lumina', icon: Zap },
  { name: 'Vertex', icon: Command },
  { name: 'Orbit', icon: Globe },
  { name: 'Stackly', icon: Layers },
  { name: 'Pulse', icon: Aperture },
  { name: 'Blaize', icon: Boxes },
]

const stats = [
  { label: 'Strategies Generated', value: 1000, suffix: '+' },
  { label: 'Businesses', value: 500, suffix: '+' },
  { label: 'Customer Satisfaction', value: 95, suffix: '%' },
]

function Counter({ value, suffix }) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-40px' })

  useEffect(() => {
    if (!inView) return
    const controls = animate(0, value, {
      duration: 1.4,
      ease: 'easeOut',
      onUpdate: (v) => {
        if (ref.current) ref.current.textContent = `${Math.round(v)}${suffix}`
      },
    })
    return () => controls.stop()
  })

  return <span ref={ref}>0{suffix}</span>
}

function LogoMark({ name, icon: Icon }) {
  return (
    <div className="flex shrink-0 items-center gap-2.5 text-zinc-500 transition-colors duration-200 hover:text-zinc-300">
      <Icon size={20} />
      <span className="text-base font-semibold tracking-tight">{name}</span>
    </div>
  )
}

export default function TrustedBy() {
  return (
    <section
      id="trusted-by"
      aria-label="Trusted by leading companies"
      className="border-y border-zinc-800/60 bg-zinc-950 py-16"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <p className="text-center text-sm font-medium text-zinc-500">
          Trusted by <span className="text-zinc-300">500+ businesses</span>{' '}
          worldwide
        </p>

        {/* Logo marquee */}
        <div className="relative mt-10 overflow-hidden [mask-image:linear-gradient(to_right,transparent,black_15%,black_85%,transparent)]">
          <motion.div
            animate={{ x: ['0%', '-50%'] }}
            transition={{ duration: 30, repeat: Infinity, ease: 'linear' }}
            className="flex w-max gap-16 pr-16 hover:[animation-play-state:paused]"
          >
            {[...companies, ...companies].map((company, i) => (
              <LogoMark
                key={`${company.name}-${i}`}
                name={company.name}
                icon={company.icon}
              />
            ))}
          </motion.div>
        </div>

        {/* Stat cards */}
        <div className="mt-14 grid gap-5 sm:grid-cols-3">
          {stats.map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-60px' }}
              transition={{ duration: 0.5, delay: i * 0.1, ease: 'easeOut' }}
              className="group relative overflow-hidden rounded-2xl border border-white/10 bg-white/[0.03] p-6 text-center backdrop-blur transition-colors duration-300 hover:border-indigo-500/30 hover:bg-white/[0.05]"
            >
              <div className="pointer-events-none absolute -top-16 left-1/2 h-32 w-32 -translate-x-1/2 rounded-full bg-indigo-500/10 blur-2xl transition-opacity duration-300 group-hover:opacity-100 sm:opacity-0" />

              <p className="text-4xl font-bold tracking-tight text-white">
                <Counter value={stat.value} suffix={stat.suffix} />
              </p>
              <p className="mt-2 text-sm text-zinc-500">{stat.label}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
