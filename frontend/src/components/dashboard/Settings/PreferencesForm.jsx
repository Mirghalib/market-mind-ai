import { useState } from 'react'
import { motion } from 'framer-motion'
import { Save, Sliders, Loader2 } from 'lucide-react'
import Select from '@/components/ui/Select'
import Button from '@/components/ui/Button'
import { cn } from '@/utils/cn'

function Toggle({ id, label, description, checked, onChange }) {
  return (
    <label htmlFor={id} className="flex cursor-pointer items-start justify-between gap-4">
      <div>
        <span className="block text-sm font-medium text-zinc-900 dark:text-white">{label}</span>
        {description && <span className="mt-0.5 block text-sm text-zinc-500 dark:text-zinc-400">{description}</span>}
      </div>
      <input
        id={id}
        type="checkbox"
        checked={checked}
        onChange={onChange}
        className="peer sr-only"
      />
      <span
        aria-hidden
        className={cn(
          'relative h-6 w-11 shrink-0 rounded-full transition-colors duration-200',
          checked ? 'bg-indigo-500' : 'bg-zinc-300 dark:bg-zinc-700'
        )}
      >
        <span
          className={cn(
            'absolute top-0.5 left-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform duration-200',
            checked && 'translate-x-5'
          )}
        />
      </span>
    </label>
  )
}

/**
 * Presentational preferences form with toggle switches and a
 * dashboard density select. Local state only.
 */
export default function PreferencesForm() {
  const [values, setValues] = useState({
    emailDigest: true,
    aiSuggestions: true,
    weeklyReports: false,
    density: 'comfortable',
  })
  const [saving, setSaving] = useState(false)

  const handleToggle = (key) => (event) => {
    setValues((current) => ({ ...current, [key]: event.target.checked }))
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    setSaving(true)
    window.setTimeout(() => setSaving(false), 900)
  }

  return (
    <motion.form
      onSubmit={handleSubmit}
      className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm sm:p-8 dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur"
    >
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-500/15 text-purple-600 dark:text-purple-400">
          <Sliders size={19} strokeWidth={1.75} />
        </span>
        <div>
          <h2 className="text-base font-semibold text-zinc-900 dark:text-white">Preferences</h2>
          <p className="text-sm text-zinc-500 dark:text-zinc-400">Customize your experience.</p>
        </div>
      </div>

      <div className="mt-6 divide-y divide-zinc-100 dark:divide-white/5">
        <div className="py-4 first:pt-0">
          <Toggle
            id="pref-email-digest"
            label="Email digest"
            description="Receive a weekly summary of your insights."
            checked={values.emailDigest}
            onChange={handleToggle('emailDigest')}
          />
        </div>
        <div className="py-4">
          <Toggle
            id="pref-ai-suggestions"
            label="AI suggestions"
            description="Show AI-generated recommendations in reports."
            checked={values.aiSuggestions}
            onChange={handleToggle('aiSuggestions')}
          />
        </div>
        <div className="py-4">
          <Toggle
            id="pref-weekly-reports"
            label="Weekly reports"
            description="Automatically generate a weekly performance report."
            checked={values.weeklyReports}
            onChange={handleToggle('weeklyReports')}
          />
        </div>
        <div className="py-4 last:pb-0">
          <Select
            id="pref-density"
            name="density"
            label="Dashboard density"
            value={values.density}
            onChange={(e) =>
              setValues((current) => ({ ...current, density: e.target.value }))
            }
          >
            <option value="comfortable">Comfortable</option>
            <option value="compact">Compact</option>
          </Select>
        </div>
      </div>

      <div className="mt-6">
        <Button type="submit" disabled={saving}>
          {saving ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              Saving…
            </>
          ) : (
            <>
              <Save size={16} />
              Save preferences
            </>
          )}
        </Button>
      </div>
    </motion.form>
  )
}
