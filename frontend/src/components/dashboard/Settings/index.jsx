import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Bell, Info, Key, Palette, User } from 'lucide-react'
import ProfileForm from './ProfileForm'
import ThemeSettings from './ThemeSettings'
import NotificationsForm from './NotificationsForm'
import ApiKeySettings from './ApiKeySettings'
import AboutSettings from './AboutSettings'
import { cn } from '@/utils/cn'

const SECTIONS = [
  { id: 'profile', label: 'Profile', icon: User },
  { id: 'theme', label: 'Theme', icon: Palette },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'api-key', label: 'API key', icon: Key },
  { id: 'about', label: 'About', icon: Info },
]

/**
 * Settings page composed of stacked sections with a sticky side nav
 * that highlights the section currently in view. Reusable and presentational.
 */
export default function Settings({ className }) {
  const [activeSection, setActiveSection] = useState('profile')

  const scrollToSection = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  // Scroll-spy: highlight the section nearest the top of the viewport.
  useEffect(() => {
    const onScroll = () => {
      const offsets = SECTIONS.map(({ id }) => {
        const el = document.getElementById(id)
        return el ? { id, top: el.getBoundingClientRect().top } : null
      }).filter(Boolean)

      let current = SECTIONS[0].id
      for (const { id, top } of offsets) {
        if (top <= 120) current = id
      }
      setActiveSection(current)
    }

    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <div className={cn('grid gap-8 lg:grid-cols-[220px_1fr]', className)}>
      {/* Section nav */}
      <nav
        aria-label="Settings sections"
        className="top-24 self-start rounded-2xl border border-zinc-200 bg-white p-2 shadow-sm lg:sticky dark:border-white/10 dark:bg-white/[0.03] dark:shadow-none"
      >
        {SECTIONS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            type="button"
            onClick={() => scrollToSection(id)}
            aria-current={activeSection === id ? 'true' : undefined}
            className={cn(
              'flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors',
              activeSection === id
                ? 'bg-indigo-500/10 text-indigo-600 dark:text-indigo-300'
                : 'text-zinc-500 hover:bg-zinc-100 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-white/5 dark:hover:text-white'
            )}
          >
            <Icon size={16} strokeWidth={1.75} />
            {label}
          </button>
        ))}
      </nav>

      {/* Sections */}
      <div className="min-w-0 space-y-8">
        <AnimatePresence mode="wait">
          <motion.div
            key="sections"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
            className="space-y-8"
          >
            <section id="profile" aria-label="Profile settings" className="scroll-mt-24">
              <ProfileForm />
            </section>
            <section id="theme" aria-label="Theme settings" className="scroll-mt-24">
              <ThemeSettings />
            </section>
            <section id="notifications" aria-label="Notification settings" className="scroll-mt-24">
              <NotificationsForm />
            </section>
            <section id="api-key" aria-label="API key settings" className="scroll-mt-24">
              <ApiKeySettings />
            </section>
            <section id="about" aria-label="About" className="scroll-mt-24">
              <AboutSettings />
            </section>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  )
}
