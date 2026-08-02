import { motion } from 'framer-motion'
import { cn } from '@/utils/cn'

/**
 * Generic dependency-free pie chart with animated segments + legend.
 * data: [{ label, value, color }] — arcs sweep in sequentially on scroll.
 */
export default function PieChart({
  data,
  size = 200,
  thickness = 26,
  centerLabel,
  centerValue,
  className,
}) {
  const total = data.reduce((sum, d) => sum + d.value, 0) || 1
  const radius = (size - thickness) / 2
  const circumference = 2 * Math.PI * radius

  let cumulative = 0

  return (
    <div className={cn('flex flex-col items-center gap-6 sm:flex-row sm:gap-8', className)}>
      <div className="relative shrink-0" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="rgba(0,0,0,0.06)"
            strokeWidth={thickness}
            className="dark:stroke-white/10"
          />
          {data.map((d, i) => {
            const fraction = d.value / total
            const dashLength = fraction * circumference
            const startOffset = -cumulative * circumference
            cumulative += fraction

            return (
              <motion.circle
                key={d.label}
                cx={size / 2}
                cy={size / 2}
                r={radius}
                fill="none"
                stroke={d.color}
                strokeWidth={thickness}
                strokeLinecap="round"
                strokeDasharray={`${dashLength} ${circumference - dashLength}`}
                initial={{ strokeDashoffset: 0, opacity: 0 }}
                whileInView={{ strokeDashoffset: startOffset, opacity: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8, delay: i * 0.12, ease: 'easeOut' }}
              >
                <title>{`${d.label}: ${d.value}`}</title>
              </motion.circle>
            )
          })}
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          {centerValue && (
            <span className="text-2xl font-bold tracking-tight text-foreground dark:text-white">
              {centerValue}
            </span>
          )}
          {centerLabel && (
            <span className="text-xs text-muted-foreground dark:text-zinc-400">{centerLabel}</span>
          )}
        </div>
      </div>

      <ul className="w-full space-y-3">
        {data.map((d) => (
          <li key={d.label} className="flex items-center justify-between gap-3 text-sm">
            <span className="flex items-center gap-2.5 text-muted-foreground dark:text-zinc-400">
              <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: d.color }} />
              {d.label}
            </span>
            <span className="font-medium text-foreground dark:text-white">{d.value}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
