import { motion } from 'framer-motion'
import { Check, Sparkles } from 'lucide-react'
import SectionTitle from '@/components/ui/SectionTitle'
import Button from '@/components/ui/Button'
import { cn } from '@/utils/cn'

const tiers = [
  {
    name: 'Free',
    price: '$0',
    period: '/month',
    tagline: 'Explore the essentials and get a feel for the platform.',
    features: [
      '3 strategy generations / month',
      'Basic market analysis',
      'Customer persona drafts',
      'Community support',
    ],
    cta: { label: 'Start Free', to: '/register', variant: 'outline' },
    featured: false,
  },
  {
    name: 'Pro',
    price: '$29',
    period: '/month',
    tagline: 'For marketers who need a full AI-powered workflow.',
    features: [
      'Unlimited strategy generations',
      'Advanced market & competitor intel',
      'SEO ideas & content calendar',
      'Email & social campaign drafts',
      'Priority support',
    ],
    cta: { label: 'Get Pro', to: '/register', variant: 'primary' },
    featured: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    tagline: 'Dedicated solutions for teams that need more control.',
    features: [
      'Everything in Pro',
      'Custom AI model training',
      'Team seats & SSO',
      'API access & integrations',
      'Dedicated success manager',
    ],
    cta: { label: 'Contact Sales', to: '/register', variant: 'outline' },
    featured: false,
  },
]

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.12 } },
}

const cardVariants = {
  hidden: { opacity: 0, y: 28 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.55, ease: 'easeOut' } },
}

function TierCard({ tier, index }) {
  return (
    <motion.div
      variants={cardVariants}
      className={cn(
        'group relative flex flex-col overflow-hidden rounded-2xl border p-8 backdrop-blur transition-all duration-300',
        tier.featured
          ? 'border-accent-400/40 bg-gradient-to-b from-accent-500/[0.12] to-landing-card shadow-2xl shadow-accent-500/20 hover:-translate-y-2 hover:shadow-accent-500/30 lg:scale-105'
          : 'border-landing-border bg-landing-card shadow-lg shadow-black/20 hover:-translate-y-1.5 hover:border-landing-border-strong hover:shadow-xl hover:shadow-accent-500/10'
      )}
    >
      {tier.featured && (
        <>
          {/* Gradient border glow */}
          <div
            aria-hidden
            className="pointer-events-none absolute inset-0 rounded-2xl opacity-0 transition-opacity duration-300 group-hover:opacity-100"
          >
            <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-accent-400/80 to-transparent" />
          </div>
          {/* Badge */}
          <span className="absolute top-0 right-0 flex items-center gap-1.5 rounded-bl-2xl border border-l-0 border-t-0 border-accent-400/30 bg-accent-500/20 px-4 py-2 text-xs font-semibold text-accent-200 backdrop-blur">
            <Sparkles size={13} className="text-accent-300" />
            Most Popular
          </span>
        </>
      )}

      <h3
        className={cn(
          'text-lg font-semibold tracking-tight',
          tier.featured ? 'text-landing-text' : 'text-landing-text'
        )}
      >
        {tier.name}
      </h3>

      <div className="mt-5 flex items-baseline gap-1.5">
        <span className="text-4xl font-bold tracking-tight text-landing-text">
          {tier.price}
        </span>
        {tier.period && (
          <span className="text-sm text-landing-muted">{tier.period}</span>
        )}
      </div>

      <p className="mt-3 text-sm leading-relaxed text-landing-muted">{tier.tagline}</p>

      <ul className="mt-8 flex-1 space-y-3.5">
        {tier.features.map((feature) => (
          <li key={feature} className="flex items-start gap-3">
            <span
              className={cn(
                'mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full',
                tier.featured
                  ? 'bg-accent-500/25 text-accent-300'
                  : 'bg-landing-card text-landing-muted'
              )}
            >
              <Check size={12} strokeWidth={3} />
            </span>
            <span className="text-sm text-landing-muted">{feature}</span>
          </li>
        ))}
      </ul>

      <Button
        to={tier.cta.to}
        variant={tier.cta.variant}
        size="lg"
        className={cn(
          'mt-8 w-full',
          tier.featured && 'shadow-lg shadow-accent-500/25'
        )}
      >
        {tier.cta.label}
      </Button>
    </motion.div>
  )
}

export default function Pricing() {
  return (
    <section
      id="pricing"
      aria-label="Pricing"
      className="relative overflow-hidden bg-landing-bg py-24"
    >
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-accent-500/50 to-transparent"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute top-0 left-1/2 h-64 w-[36rem] -translate-x-1/2 rounded-full bg-accent-500/10 blur-3xl"
      />

      <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionTitle
          eyebrow="Pricing"
          title="Simple, transparent pricing"
          description="Start free and upgrade when you are ready. No hidden fees, cancel anytime."
          align="center"
        />

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-60px' }}
          className="mx-auto mt-16 grid max-w-5xl gap-6 lg:grid-cols-3 lg:items-stretch"
        >
          {tiers.map((tier, i) => (
            <TierCard key={tier.name} tier={tier} index={i} />
          ))}
        </motion.div>

        <p className="mt-10 text-center text-xs text-landing-muted">
          All plans include secure billing via our partners. No payment is
          required to get started.
        </p>
      </div>
    </section>
  )
}
