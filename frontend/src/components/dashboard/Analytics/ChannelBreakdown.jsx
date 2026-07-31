import { motion } from 'framer-motion'
import { cn } from '@/utils/cn'

const defaultChannels = [
  { label: 'Organic Search', value: 42, color: '#818cf8' },
  { label: 'Social Media', value: 28, color: '#c084fc' },
  { label: 'Email', value: 18, color: '#22d3ee' },
  { label: 'Direct', value: 12, color: '#34d399' },
]

/**
 * Horizontal channel breakdown with animated progress bars.
 * Accepts any [{ label, value, color }] array.
 */
export default function ChannelBreakdown({ channels = defaultChannels, className }) {
  const total = channels.reduce((sum, c) => sum + c.value, 0) || 1

  return (
    <div
      className={cn('rounded-2xl border border-border bg-card p-6 shadow-sm dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur' ,
        className
      )}
    >
      <h3 className="text-base font-semibold text-foreground dark:text-white">Channel breakdown</h3>
      <p className="mt-0.5 text-sm text-muted-foreground dark:text-zinc-400">
        Where your audience comes from
      </p>

      <ul className="mt-6 space-y-5">
        {channels.map((channel, i) => (
          <li key={channel.label}>
            <div className="flex items-center justify-between text-sm">
              <span className="flex items-center gap-2.5 text-foreground dark:text-zinc-300">
                <span
                  className="h-2.5 w-2.5 rounded-full"
                  style={{ backgroundColor: channel.color }}
                />
                {channel.label}
              </span>
              <span className="font-medium text-foreground dark:text-white">{channel.value}%</span>
            </div>
            <div className="mt-2 h-2 overflow-hidden rounded-full bg-muted dark:bg-white/5">
              <motion.div
                initial={{ width: 0 }}
                whileInView={{ width: `${(channel.value / total) * 100}%` }}
                viewport={{ once: true }}
                transition={{ duration: 0.8, delay: i * 0.1, ease: 'easeOut' }}
                className="h-full rounded-full"
                style={{ backgroundColor: channel.color }}
              />
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
