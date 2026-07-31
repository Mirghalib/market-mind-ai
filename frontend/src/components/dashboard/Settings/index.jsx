import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import ProfileForm from './ProfileForm'
import PreferencesForm from './PreferencesForm'
import DangerZone from './DangerZone'
import { cn } from '@/utils/cn'

const TABS = [
  { id: 'profile', label: 'Profile' },
  { id: 'preferences', label: 'Preferences' },
  { id: 'danger', label: 'Danger zone' },
]

/**
 * Settings section with animated tabs. Each tab is a reusable form
 * component; state lives here so they stay presentational.
 */
export default function Settings({ className }) {
  const [activeTab, setActiveTab] = useState('profile')

  return (
    <div className={cn('space-y-6', className)}>
      {/* Tabs */}
      <div
        role="tablist"
        aria-label="Settings tabs"
        className="inline-flex gap-1 rounded-xl border border-white/10 bg-white/[0.03] p-1"
      >
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            role="tab"
            id={`settings-tab-${tab.id}`}
            aria-selected={activeTab === tab.id}
            aria-controls={`settings-panel-${tab.id}`}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              'rounded-lg px-4 py-2 text-sm font-medium transition-colors',
              activeTab === tab.id
                ? 'bg-indigo-500/15 text-indigo-300'
                : 'text-zinc-400 hover:bg-white/5 hover:text-white'
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Panels */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          role="tabpanel"
          id={`settings-panel-${activeTab}`}
          aria-labelledby={`settings-tab-${activeTab}`}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.25, ease: 'easeOut' }}
        >
          {activeTab === 'profile' && <ProfileForm />}
          {activeTab === 'preferences' && <PreferencesForm />}
          {activeTab === 'danger' && <DangerZone />}
        </motion.div>
      </AnimatePresence>
    </div>
  )
}
