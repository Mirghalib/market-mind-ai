import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { motion } from 'framer-motion'
import {
  Building2,
  CheckCircle2,
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

export const INDUSTRIES = [
  'SaaS',
  'E-commerce',
  'Agency',
  'Local Business',
  'Fintech',
  'Healthcare',
  'Education',
  'Other',
]

export const COUNTRIES = [
  'United States',
  'United Kingdom',
  'Canada',
  'Australia',
  'Germany',
  'France',
  'India',
  'Other',
]

export const BUDGETS = [
  'Under $1,000 / mo',
  '$1,000 – $5,000 / mo',
  '$5,000 – $20,000 / mo',
  '$20,000 – $50,000 / mo',
  '$50,000+ / mo',
]

export const GOALS = [
  'Increase brand awareness',
  'Generate more leads',
  'Drive online sales',
  'Grow email list',
  'Improve engagement',
  'Launch a new product',
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
  budget: '',
  marketingGoal: '',
  brandTone: '',
  competitors: '',
}

export default function BusinessForm({ onSubmit, className }) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting, isSubmitSuccessful },
  } = useForm({ defaultValues, mode: 'onTouched' })

  const [status, setStatus] = useState('idle') // 'idle' | 'submitting' | 'success'

  const submitForm = async (data) => {
    setStatus('submitting')
    // Simulated async submission — wire to your API here.
    await new Promise((resolve) => setTimeout(resolve, 1200))
    await onSubmit?.(data)
    setStatus('success')
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
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: 'easeOut' }}
      className={cn('rounded-2xl border border-border bg-card p-6 shadow-sm sm:p-8 dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur' ,
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
        <Select
          id="budget"
          label="Monthly budget"
          error={errors.budget?.message}
          {...register('budget', { required: 'Select a budget range' })}
        >
          <option value="">Select budget</option>
          {BUDGETS.map((budget) => (
            <option key={budget} value={budget}>
              {budget}
            </option>
          ))}
        </Select>

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
          <Button type="submit" size="lg" disabled={isSubmitting}>
            {isSubmitting ? (
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
