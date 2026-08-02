import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import { Sparkles } from 'lucide-react'
import { APP_NAME, NAV_LINKS } from '@/constants'
import Button from '@/components/ui/Button'
import ThemeSwitcher from '@/components/common/ThemeSwitcher'
import { cn } from '@/utils/cn'

export default function Navbar({ transparent = true }) {
  const [open, setOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const [activeSection, setActiveSection] = useState('home')
  const location = useLocation()
  const isHome = location.pathname === '/'

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  })

  // Scroll-spy: highlight the nav link for the section in view.
  useEffect(() => {
    const sections = NAV_LINKS.map((link) =>
      document.getElementById(link.href.slice(1))
    ).filter(Boolean)

    if (!sections.length) return

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveSection(entry.target.id)
          }
        })
      },
      { rootMargin: '-40% 0px -55% 0px' }
    )

    sections.forEach((section) => observer.observe(section))
    return () => observer.disconnect()
  }, [isHome])

  const handleNavClick = (event, href) => {
    // Close the mobile menu on any nav click.
    setOpen(false)

    // On the landing page, anchor-scroll; otherwise navigate home then scroll.
    if (isHome) return

    event.preventDefault()
    window.location.href = `/#${href.slice(1)}`
  }

  const solid = !transparent || scrolled || open

  return (
    <motion.header
      initial={{ y: -24, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className={cn(
        'fixed inset-x-0 top-0 z-50',
        'transition-all duration-300',
        solid
          ? 'border-b border-landing-border bg-landing-bg/80 backdrop-blur-md'
          : 'border-b border-transparent bg-transparent'
      )}
    >
      <nav className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link
          to="/"
          className="flex items-center gap-2"
          aria-label={`${APP_NAME} home`}
        >
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-accent-500 to-accent-700">
            <Sparkles size={16} className="text-white" />
          </span>
          <span className="text-sm font-semibold tracking-tight text-landing-text">
            {APP_NAME}
          </span>
        </Link>

        <div className="hidden items-center gap-1 md:flex">
          {NAV_LINKS.map((link) => (
            <a
              key={link.label}
              href={link.href}
              onClick={(e) => handleNavClick(e, link.href)}
              aria-current={
                isHome && activeSection === link.href.slice(1) ? 'true' : undefined
              }
              className={cn(
                'rounded-lg px-3.5 py-2 text-sm font-medium transition-colors duration-200',
                isHome && activeSection === link.href.slice(1)
                  ? 'text-landing-text'
                  : 'text-landing-muted hover:bg-landing-card hover:text-landing-text'
              )}
            >
              {link.label}
            </a>
          ))}
        </div>

        <div className="hidden items-center gap-3 md:flex">
          <ThemeSwitcher />
          <Button to="/login" variant="ghost" size="sm">
            Login
          </Button>
          <Button to="/register" size="sm">
            Start Free
          </Button>
        </div>

        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          aria-label={open ? 'Close navigation menu' : 'Open navigation menu'}
          aria-expanded={open}
          className="flex h-10 w-10 items-center justify-center rounded-lg text-landing-muted transition-colors hover:bg-landing-card hover:text-landing-text md:hidden"
        >
          <motion.div
            animate={{ rotate: open ? 90 : 0 }}
            transition={{ duration: 0.2 }}
            className="flex flex-col items-center justify-center gap-1.5"
          >
            <motion.span
              animate={open ? { rotate: 45, y: 4 } : { rotate: 0, y: 0 }}
              className="block h-0.5 w-5 rounded-full bg-current"
            />
            <motion.span
              animate={open ? { opacity: 0 } : { opacity: 1 }}
              className="block h-0.5 w-5 rounded-full bg-current"
            />
            <motion.span
              animate={open ? { rotate: -45, y: -4 } : { rotate: 0, y: 0 }}
              className="block h-0.5 w-5 rounded-full bg-current"
            />
          </motion.div>
        </button>
      </nav>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: 'easeInOut' }}
            className="overflow-hidden border-t border-landing-border bg-background/95 backdrop-blur-md md:hidden"
          >
            <div className="space-y-1 px-4 py-4">
              {NAV_LINKS.map((link, i) => (
                <motion.div
                  key={link.label}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.05 * i, duration: 0.2 }}
                >
                  <a
                    href={link.href}
                    onClick={(e) => handleNavClick(e, link.href)}
                    aria-current={
                      isHome && activeSection === link.href.slice(1) ? 'true' : undefined
                    }
                    className={cn(
                      'block rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                      isHome && activeSection === link.href.slice(1)
                        ? 'bg-landing-card text-landing-text'
                        : 'text-landing-muted hover:bg-landing-card hover:text-landing-text'
                    )}
                  >
                    {link.label}
                  </a>
                </motion.div>
              ))}

              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2, duration: 0.2 }}
                className="flex flex-col gap-2 border-t border-landing-border pt-4"
              >
                <Button to="/login" variant="outline" className="w-full">
                  Login
                </Button>
                <Button to="/register" className="w-full">
                  Start Free
                </Button>
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  )
}
