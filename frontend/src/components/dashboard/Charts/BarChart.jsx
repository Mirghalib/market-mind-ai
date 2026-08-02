import { motion } from 'framer-motion'
import { cn } from '@/utils/cn'

/**
 * Generic dependency-free bar chart.
 * data: [{ label, value }] — animated bars scaling from the baseline.
 */
export default function BarChart({
  data,
  height = 220,
  color = '#16394A',
  className,
}) {
  const max = Math.max(...data.map((d) => d.value), 1)

  return (
    <div className={cn('flex w-full items-end gap-3', className)} style={{ height }}>
      {data.map((d, i) => {
        const barHeight = (d.value / max) * 100
        return (
          <div
            key={d.label}
            className="group flex flex-1 flex-col items-center gap-2"
            style={{ height: '100%' }}
          >
            <div className="flex w-full flex-1 items-end justify-center">
              <motion.div
                initial={{ height: 0 }}
                whileInView={{ height: `${barHeight}%` }}
                viewport={{ once: true }}
                transition={{ duration: 0.7, delay: i * 0.06, ease: 'easeOut' }}
                className="w-full max-w-9 rounded-t-md transition-colors duration-200"
                style={{
                  background: `linear-gradient(to top, ${color}55, ${color})`,
                }}
              >
                <title>{`${d.label}: ${d.value}`}</title>
              </motion.div>
            </div>
            <span className="w-full truncate text-center text-[10px] text-muted-foreground dark:text-zinc-400">
              {d.label}
            </span>
          </div>
        )
      })}
    </div>
  )
}
