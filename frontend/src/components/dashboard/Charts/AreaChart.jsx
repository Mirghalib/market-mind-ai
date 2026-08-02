import { useId } from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/utils/cn'

/**
 * Generic dependency-free area chart.
 * data: [{ label, value }] — renders an animated SVG area + line.
 */
export default function AreaChart({
  data,
  height = 220,
  stroke = '#16394A',
  fill = 'rgba(22,57,74,0.15)',
  className,
}) {
  const gradientId = useId()
  const width = 600
  const padding = 8

  const max = Math.max(...data.map((d) => d.value), 1)
  const stepX = (width - padding * 2) / Math.max(data.length - 1, 1)

  const points = data.map((d, i) => ({
    x: padding + i * stepX,
    y: height - padding - (d.value / max) * (height - padding * 2),
  }))

  const linePath = points
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`)
    .join(' ')
  const areaPath = `${linePath} L ${points[points.length - 1].x} ${height} L ${points[0].x} ${height} Z`

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label="Area chart"
      className={cn('w-full', className)}
      style={{ height }}
    >
      <defs>
        <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={stroke} stopOpacity="0.3" />
          <stop offset="100%" stopColor={stroke} stopOpacity="0" />
        </linearGradient>
      </defs>

      <motion.path
        d={areaPath}
        fill={`url(#${gradientId})`}
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8, delay: 0.3 }}
      />
      <motion.path
        d={linePath}
        fill="none"
        stroke={stroke}
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        initial={{ pathLength: 0 }}
        whileInView={{ pathLength: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 1.2, ease: 'easeInOut' }}
      />

      {points.map((p, i) => (
        <circle key={i} cx={p.x} cy={p.y} r="3.5" fill={stroke}>
          <title>{`${data[i].label}: ${data[i].value}`}</title>
        </circle>
      ))}
    </svg>
  )
}
