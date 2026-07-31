import { cn } from '@/utils/cn'

export default function SectionTitle({
  eyebrow,
  title,
  description,
  align = 'left',
  className,
}) {
  return (
    <div
      className={cn(
        'max-w-2xl',
        align === 'center' && 'mx-auto text-center',
        className
      )}
    >
      {eyebrow && (
        <p className="mb-3 text-sm font-semibold tracking-wide text-indigo-500 uppercase dark:text-indigo-400">
          {eyebrow}
        </p>
      )}
      <h2 className="text-3xl font-semibold tracking-tight text-foreground dark:text-white">
        {title}
      </h2>
      {description && (
        <p className="mt-3 text-base leading-relaxed text-muted-foreground dark:text-zinc-400">
          {description}
        </p>
      )}
    </div>
  )
}
