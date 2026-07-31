import { useState } from 'react'
import { motion } from 'framer-motion'
import { Loader2, Save, User } from 'lucide-react'
import Input from '@/components/ui/Input'
import Select from '@/components/ui/Select'
import Button from '@/components/ui/Button'

const ROLES = ['Marketing Lead', 'Founder', 'Marketer', 'Agency Owner', 'Other']

/**
 * Presentational profile form. Fields are controlled locally;
 * onSubmit receives the current values (wire to an API in the page).
 */
export default function ProfileForm() {
  const [values, setValues] = useState({
    name: '',
    email: '',
    company: '',
    role: '',
  })
  const [saving, setSaving] = useState(false)

  const handleChange = (event) => {
    const { name, value } = event.target
    setValues((current) => ({ ...current, [name]: value }))
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    setSaving(true)
    // Simulated save so the UI demonstrates a real flow. Replace with your API call.
    window.setTimeout(() => setSaving(false), 900)
  }

  return (
    <motion.form
      onSubmit={handleSubmit}
      className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm sm:p-8 dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur"
    >
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/15 text-indigo-600 dark:text-indigo-400">
          <User size={19} strokeWidth={1.75} />
        </span>
        <div>
          <h2 className="text-base font-semibold text-zinc-900 dark:text-white">Profile</h2>
          <p className="text-sm text-zinc-500 dark:text-zinc-400">Update your personal information.</p>
        </div>
      </div>

      <div className="mt-6 grid gap-5 sm:grid-cols-2">
        <Input
          id="profile-name"
          name="name"
          label="Full name"
          placeholder="Jane Cooper"
          value={values.name}
          onChange={handleChange}
        />
        <Input
          id="profile-email"
          name="email"
          type="email"
          label="Email address"
          placeholder="jane@company.com"
          value={values.email}
          onChange={handleChange}
        />
        <Input
          id="profile-company"
          name="company"
          label="Company"
          placeholder="Acme Inc."
          value={values.company}
          onChange={handleChange}
        />
        <Select
          id="profile-role"
          name="role"
          label="Role"
          value={values.role}
          onChange={handleChange}
        >
          <option value="">Select role</option>
          {ROLES.map((role) => (
            <option key={role} value={role}>
              {role}
            </option>
          ))}
        </Select>
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
              Save changes
            </>
          )}
        </Button>
      </div>
    </motion.form>
  )
}
