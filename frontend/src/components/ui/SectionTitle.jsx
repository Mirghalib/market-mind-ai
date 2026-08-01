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
        <p className="mb-3 text-sm font-semibold tracking-wide text-accent-500 uppercase">
          {eyebrow}
        </p>
      )}
      <h2 className="text-3xl font-semibold tracking-tight text-landing-text">
        {title}
      </h2>
      {description && (
        <p className="mt-3 text-base leading-relaxed text-landing-muted">
          {description}
        </p>
      )}
    </div>
  )
}
