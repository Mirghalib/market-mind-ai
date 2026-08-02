import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Bell, Loader2, Save } from 'lucide-react'
import Button from '@/components/ui/Button'
import { cn } from '@/utils/cn'

const STORAGE_KEY = 'market_mind_ai_notification_prefs'

const DEFAULTS = {
  emailDigest: true,
  aiSuggestions: true,
  weeklyReports: false,
  productUpdates: true,
}

function Toggle({ id, label, description, checked, onChange }) {
  return (
    <label htmlFor={id} className="flex cursor-pointer items-start justify-between gap-4">
      <div>
        <span className="block text-sm font-medium text-foreground dark:text-white">{label}</span>
        {description && <span className="mt-0.5 block text-sm text-muted-foreground dark:text-zinc-400">{description}</span>}
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
        className={cn('relative h-6 w-11 shrink-0 rounded-full transition-colors duration-200' ,
          checked ? 'bg-indigo-500' : 'bg-border dark:bg-zinc-700'
        )}
      >
        <span
          className={cn('absolute top-0.5 left-0.5 h-5 w-5 rounded-full bg-card shadow transition-transform duration-200' ,
            checked && 'translate-x-5'
          )}
        />
      </span>
    </label>
  )
}

/**
 * Notification preferences with toggle switches.
 * Preferences are persisted locally so they survive reloads.
 */
export default function NotificationsForm() {
  const [values, setValues] = useState(() => {
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY)
      return stored ? { ...DEFAULTS, ...JSON.parse(stored) } : DEFAULTS
    } catch {
      return DEFAULTS
    }
  })
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  const handleToggle = (key) => (event) => {
    setValues((current) => ({ ...current, [key]: event.target.checked }))
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    setSaving(true)
    setSaved(false)
    window.setTimeout(() => {
      try {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(values))
      } catch {
        // Storage unavailable — ignore.
      }
      setSaving(false)
      setSaved(true)
      window.setTimeout(() => setSaved(false), 2500)
    }, 500)
  }

  return (
    <motion.form
      onSubmit={handleSubmit}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="rounded-2xl border border-border bg-card p-6 shadow-sm sm:p-8 dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur"
    >
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-500/15 text-purple-600 dark:text-purple-400">
          <Bell size={19} strokeWidth={1.75} />
        </span>
        <div>
          <h2 className="text-base font-semibold text-foreground dark:text-white">Notifications</h2>
          <p className="text-sm text-muted-foreground dark:text-zinc-400">
            Choose what you want to hear about.
          </p>
        </div>
      </div>

      <div className="mt-6 divide-y divide-border dark:divide-white/5">
        <div className="py-4 first:pt-0">
          <Toggle
            id="notif-email-digest"
            label="Email digest"
            description="Receive a weekly summary of your insights."
            checked={values.emailDigest}
            onChange={handleToggle('emailDigest')}
          />
        </div>
        <div className="py-4">
          <Toggle
            id="notif-ai-suggestions"
            label="AI suggestions"
            description="Get notified when new AI recommendations are ready."
            checked={values.aiSuggestions}
            onChange={handleToggle('aiSuggestions')}
          />
        </div>
        <div className="py-4">
          <Toggle
            id="notif-weekly-reports"
            label="Weekly reports"
            description="Automatically generate and notify about a weekly report."
            checked={values.weeklyReports}
            onChange={handleToggle('weeklyReports')}
          />
        </div>
        <div className="py-4 last:pb-0">
          <Toggle
            id="notif-product-updates"
            label="Product updates"
            description="Be first to know about new features and improvements."
            checked={values.productUpdates}
            onChange={handleToggle('productUpdates')}
          />
        </div>
      </div>

      <div className="mt-6 flex items-center gap-3">
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
        {saved && (
          <span className="text-sm font-medium text-emerald-600 dark:text-emerald-400">
            Preferences saved
          </span>
        )}
      </div>
    </motion.form>
  )
}
