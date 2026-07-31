import { useState } from 'react'
import { motion } from 'framer-motion'
import { Building2, Loader2, Target, Users, Wand2 } from 'lucide-react'
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

const initialValues = {
  businessName: '',
  industry: '',
  targetAudience: '',
  goals: '',
}

export default function BusinessForm({ onSubmit, submitting = false, className }) {
  const [values, setValues] = useState(initialValues)
  const [errors, setErrors] = useState({})

  const handleChange = (event) => {
    const { name, value } = event.target
    setValues((current) => ({ ...current, [name]: value }))
    setErrors((current) => ({ ...current, [name]: undefined }))
  }

  const handleSubmit = (event) => {
    event.preventDefault()

    const nextErrors = {}
    if (!values.businessName.trim()) {
      nextErrors.businessName = 'Business name is required'
    }
    if (!values.industry) {
      nextErrors.industry = 'Select your industry'
    }
    if (!values.targetAudience.trim()) {
      nextErrors.targetAudience = 'Describe your target audience'
    }
    if (!values.goals.trim()) {
      nextErrors.goals = 'Tell us your marketing goals'
    }
    setErrors(nextErrors)

    if (Object.keys(nextErrors).length > 0) return

    onSubmit(values)
  }

  return (
    <motion.form
      onSubmit={handleSubmit}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: 'easeOut' }}
      className={cn(
        'rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm sm:p-8 dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur',
        className
      )}
      noValidate
    >
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/15 text-indigo-600 dark:text-indigo-400">
          <Building2 size={19} strokeWidth={1.75} />
        </span>
        <div>
          <h2 className="text-base font-semibold text-zinc-900 dark:text-white">Tell us about your business</h2>
          <p className="text-sm text-zinc-500 dark:text-zinc-400">
            We use this to tailor your marketing strategy.
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-5 sm:grid-cols-2">
        <Input
          id="businessName"
          name="businessName"
          label="Business name"
          placeholder="Acme Inc."
          value={values.businessName}
          onChange={handleChange}
          error={errors.businessName}
        />
        <Select
          id="industry"
          name="industry"
          label="Industry"
          value={values.industry}
          onChange={handleChange}
          error={errors.industry}
        >
          <option value="">Select industry</option>
          {INDUSTRIES.map((industry) => (
            <option key={industry} value={industry}>
              {industry}
            </option>
          ))}
        </Select>

        <div className="sm:col-span-2">
          <Textarea
            id="targetAudience"
            name="targetAudience"
            label="Target audience"
            rows={3}
            placeholder="e.g. Small business owners in the US looking to automate their marketing"
            value={values.targetAudience}
            onChange={handleChange}
            error={errors.targetAudience}
          />
        </div>

        <div className="sm:col-span-2">
          <Textarea
            id="goals"
            name="goals"
            label="Marketing goals"
            rows={3}
            placeholder="e.g. Increase leads by 30% and grow our email list this quarter"
            value={values.goals}
            onChange={handleChange}
            error={errors.goals}
          />
        </div>
      </div>

      <div className="mt-6 flex flex-wrap items-center gap-3">
        <Button type="submit" size="lg" disabled={submitting}>
          {submitting ? (
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
        <p className="flex items-center gap-1.5 text-xs text-zinc-500 dark:text-zinc-400">
          <Target size={12} />
          <Users size={12} />
          Your details stay private.
        </p>
      </div>
    </motion.form>
  )
}
