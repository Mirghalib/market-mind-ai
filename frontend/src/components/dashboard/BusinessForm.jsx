import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { motion } from 'framer-motion'
import {
  Building2,
  CheckCircle2,
  Coins,
  Globe,
  Loader2,
  Megaphone,
  Package,
  Palette,
  Swords,
  Target,
  Users,
  Wallet,
  Wand2,
} from 'lucide-react'
import Input from '@/components/ui/Input'
import Select from '@/components/ui/Select'
import Textarea from '@/components/ui/Textarea'
import Button from '@/components/ui/Button'
import { cn } from '@/utils/cn'
import {
  CURRENCY_OPTIONS,
  DEFAULT_CURRENCY,
  currencyForCountry,
} from '@/constants/currencies'

export const INDUSTRIES = [
  'Restaurant / Food',
  'SaaS / Software',
  'E-commerce / Online Store',
  'Gym & Fitness',
  'Real Estate',
  'Beauty Salon / Spa',
  'Hospital / Clinic',
  'Academy / Education',
  'Travel Agency',
  'Furniture Store',
  'Agency / Consulting',
  'Fintech',
  'Healthcare',
  'Local Business',
  'Other',
]

export const COUNTRIES = [
  'United States',
  'United Kingdom',
  'Pakistan',
  'India',
  'UAE',
  'Saudi Arabia',
  'Canada',
  'Australia',
  'Germany',
  'France',
  'Italy',
  'Spain',
  'Brazil',
  'Mexico',
  'Turkey',
  'Nigeria',
  'South Africa',
  'Egypt',
  'Japan',
  'China',
  'Singapore',
  'Malaysia',
  'Indonesia',
  'Thailand',
  'Philippines',
  'New Zealand',
  'Other',
]

export const BUDGET_PERIODS = ['month', 'quarter', 'year']

export const GOALS = [
  'Increase brand awareness',
  'Generate more leads',
  'Drive online sales',
  'Grow email list',
  'Improve engagement',
  'Launch a new product',
  'Increase foot traffic / visits',
  'Build customer loyalty',
]

export const TONES = [
  'Professional',
  'Friendly',
  'Bold',
  'Playful',
  'Luxury',
  'Minimal',
]

const defaultValues = {
  businessName: '',
  industry: '',
  product: '',
  targetAudience: '',
  country: '',
  currencyCode: 'USD',
  currencySymbol: '$',
  budgetAmount: '',
  budgetPeriod: 'month',
  marketingGoal: '',
  brandTone: '',
  competitors: '',
}

export default function BusinessForm({ onSubmit, loading = false, className, focusKey }) {
  const {
    register,
    handleSubmit,
    reset,
    watch,
    setValue,
    formState: { errors, isSubmitting, isSubmitSuccessful },
  } = useForm({ defaultValues, mode: 'onTouched' })

  const [status, setStatus] = useState('idle') // 'idle' | 'submitting' | 'success'
  const [highlighted, setHighlighted] = useState(false)

  const watchedCountry = watch('country')
  const watchedCurrency = watch('currencyCode')

  // Auto-select the currency when the country changes, unless the user
  // has already manually overridden it.
  useEffect(() => {
    if (!watchedCountry) return
    const { code, symbol } = currencyForCountry(watchedCountry)
    setValue('currencyCode', code)
    setValue('currencySymbol', symbol)
  }, [watchedCountry, setValue])

  // Keep the symbol in sync when the user manually overrides the currency code.
  useEffect(() => {
    if (!watchedCurrency) return
    const option = CURRENCY_OPTIONS[watchedCurrency]
    if (option) setValue('currencySymbol', option.symbol)
  }, [watchedCurrency, setValue])

  // When the top "Generate Strategy" CTA is clicked, the dashboard
  // scrolls here, bumps `focusKey`, focuses the first input and briefly
  // highlights the card so the user knows where to start.
  useEffect(() => {
    if (!focusKey) return
    const el = document.getElementById('businessName')
    el?.focus({ preventScroll: true })
    setHighlighted(true)
    const timer = window.setTimeout(() => setHighlighted(false), 1600)
    return () => window.clearTimeout(timer)
  }, [focusKey])

  const submitForm = async (data) => {
    setStatus('submitting')
    try {
      await onSubmit?.(data)
      setStatus('success')
    } finally {
      setStatus('idle')
    }
  }

  // Reset the form back to editable state after showing the success message.
  useEffect(() => {
    if (!isSubmitSuccessful) return
    const timer = setTimeout(() => {
      reset()
      setStatus('idle')
    }, 4000)
    return () => clearTimeout(timer)
  }, [isSubmitSuccessful, reset])

  return (
    <motion.form
      onSubmit={handleSubmit(submitForm)}
      initial={{ opacity: 0, y: 16 }}
      animate={{
        opacity: 1,
        y: 0,
        boxShadow: highlighted
          ? '0 0 0 3px var(--color-accent-500), 0 8px 30px -6px rgba(99,102,241,0.35)'
          : '0 0 0 0px rgba(99,102,241,0)',
      }}
      transition={{ duration: highlighted ? 0.35 : 0.45, ease: 'easeOut' }}
      className={cn(
        'rounded-2xl border bg-card p-6 shadow-sm sm:p-8 dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur',
        highlighted
          ? 'border-accent-500/70 ring-2 ring-accent-500/40'
          : 'border-border',
        className
      )}
      noValidate
    >
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/15 text-indigo-600 dark:text-indigo-400">
          <Building2 size={19} strokeWidth={1.75} />
        </span>
        <div>
          <h2 className="text-base font-semibold text-foreground dark:text-white">
            Tell us about your business
          </h2>
          <p className="text-sm text-muted-foreground dark:text-zinc-400">
            We use this to tailor your marketing strategy.
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-5 sm:grid-cols-2">
        <Input
          id="businessName"
          label="Business name"
          placeholder="Acme Inc."
          error={errors.businessName?.message}
          {...register('businessName', {
            required: 'Business name is required',
            minLength: { value: 2, message: 'Business name must be at least 2 characters' },
          })}
        />
        <Select
          id="industry"
          label="Industry"
          error={errors.industry?.message}
          {...register('industry', { required: 'Select your industry' })}
        >
          <option value="">Select industry</option>
          {INDUSTRIES.map((industry) => (
            <option key={industry} value={industry}>
              {industry}
            </option>
          ))}
        </Select>

        <Input
          id="product"
          label="Product"
          placeholder="What are you selling?"
          error={errors.product?.message}
          {...register('product', {
            required: 'Tell us about your product',
            minLength: { value: 3, message: 'Product must be at least 3 characters' },
          })}
        />

        <div className="sm:col-span-2">
          <Textarea
            id="targetAudience"
            label="Target audience"
            rows={3}
            placeholder="e.g. Small business owners in the US looking to automate their marketing"
            error={errors.targetAudience?.message}
            {...register('targetAudience', {
              required: 'Describe your target audience',
              minLength: { value: 10, message: 'Give us a bit more detail (10+ characters)' },
            })}
          />
        </div>

        <Select
          id="country"
          label="Country"
          error={errors.country?.message}
          {...register('country', { required: 'Select your country' })}
        >
          <option value="">Select country</option>
          {COUNTRIES.map((country) => (
            <option key={country} value={country}>
              {country}
            </option>
          ))}
        </Select>
        <div className="grid grid-cols-2 gap-4">
          <Select
            id="currencyCode"
            label="Currency"
            error={errors.currencyCode?.message}
            {...register('currencyCode', { required: 'Select a currency' })}
          >
            {Object.values(CURRENCY_OPTIONS).map(({ code, symbol }) => (
              <option key={code} value={code}>
                {code} ({symbol.trim()})
              </option>
            ))}
          </Select>
          <Select
            id="budgetPeriod"
            label="Period"
            {...register('budgetPeriod')}
          >
            {BUDGET_PERIODS.map((period) => (
              <option key={period} value={period}>
                Per {period}
              </option>
            ))}
          </Select>
        </div>
        <div>
          <Input
            id="budgetAmount"
            label="Monthly budget"
            type="number"
            min="0"
            step="any"
            placeholder="e.g. 100000"
            error={errors.budgetAmount?.message}
            {...register('budgetAmount', {
              required: 'Enter your budget amount',
              min: { value: 0, message: 'Budget must be positive' },
            })}
          />
          {watchedCurrency && (
            <p className="mt-1.5 flex items-center gap-1.5 text-xs text-muted-foreground dark:text-zinc-500">
              <Coins size={12} />
              Currency auto-selected from your country — you can override it.
            </p>
          )}
        </div>

        <Select
          id="marketingGoal"
          label="Marketing goal"
          error={errors.marketingGoal?.message}
          {...register('marketingGoal', { required: 'Select a marketing goal' })}
        >
          <option value="">Select goal</option>
          {GOALS.map((goal) => (
            <option key={goal} value={goal}>
              {goal}
            </option>
          ))}
        </Select>
        <Select
          id="brandTone"
          label="Brand tone"
          error={errors.brandTone?.message}
          {...register('brandTone', { required: 'Select a brand tone' })}
        >
          <option value="">Select tone</option>
          {TONES.map((tone) => (
            <option key={tone} value={tone}>
              {tone}
            </option>
          ))}
        </Select>

        <div className="sm:col-span-2">
          <Textarea
            id="competitors"
            label="Competitors"
            rows={2}
            placeholder="e.g. Competitor A, Competitor B (comma-separated)"
            error={errors.competitors?.message}
            {...register('competitors', {
              required: 'List at least one competitor',
              minLength: { value: 3, message: 'Competitor names must be at least 3 characters' },
            })}
          />
        </div>
      </div>

      {/* Footer */}
      <div className="mt-6 flex flex-wrap items-center gap-3">
        {status === 'success' ? (
          <div
            role="status"
            className="flex w-full items-center gap-2 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-700 dark:border-emerald-500/20 dark:bg-emerald-500/10 dark:text-emerald-400"
          >
            <CheckCircle2 size={18} />
            Strategy generated successfully! Your results are ready below.
          </div>
        ) : (
          <Button type="submit" size="lg" disabled={isSubmitting || loading}>
            {isSubmitting || loading ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                Generating strategy…
              </>
            ) : (
              <>
                <Wand2 size={18} />
                Generate Strategy
              </>
            )}
          </Button>
        )}
        {status !== 'success' && (
          <p className="flex items-center gap-1.5 text-xs text-muted-foreground dark:text-zinc-400">
            <Target size={12} />
            <Users size={12} />
            Your details stay private.
          </p>
        )}
      </div>

      {/* Field legend */}
      <div className="mt-6 grid grid-cols-2 gap-2 border-t border-border pt-5 sm:grid-cols-3 dark:border-white/5">
        {[
          { icon: Package, label: 'Product' },
          { icon: Globe, label: 'Country' },
          { icon: Wallet, label: 'Budget' },
          { icon: Megaphone, label: 'Goal' },
          { icon: Palette, label: 'Tone' },
          { icon: Swords, label: 'Competitors' },
        ].map(({ icon: Icon, label }) => (
          <span
            key={label}
            className="flex items-center gap-2 text-xs text-muted-foreground dark:text-zinc-400"
          >
            <Icon size={13} className="shrink-0 text-indigo-500 dark:text-indigo-400" />
            {label}
          </span>
        ))}
      </div>
    </motion.form>
  )
}
