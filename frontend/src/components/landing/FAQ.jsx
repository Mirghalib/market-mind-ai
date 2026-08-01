import { useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { ChevronDown } from 'lucide-react'
import SectionTitle from '@/components/ui/SectionTitle'
import { cn } from '@/utils/cn'

const faqs = [
  {
    question: 'How does Market Mind AI generate strategies?',
    answer:
      'Tell us about your business, audience, and goals, and our AI drafts a complete marketing strategy — market analysis, personas, SEO ideas, content calendars, and campaigns. You can regenerate any section or refine it until it sounds exactly like your brand.',
  },
  {
    question: 'Do I need a credit card to start?',
    answer:
      'No. The Free plan lets you generate up to three strategies per month without entering any payment details. Upgrade to Pro whenever you are ready — billing is handled securely through our partners.',
  },
  {
    question: 'Can I cancel my subscription anytime?',
    answer:
      'Yes. You can cancel or change plans at any time from your settings, and you will keep access until the end of your current billing period. No hidden fees, no lock-in.',
  },
  {
    question: 'Is my business data safe?',
    answer:
      'Absolutely. Your data is encrypted in transit and at rest, never sold, and never used to train models for other customers. You can export or delete everything you create at any time.',
  },
  {
    question: 'Does it work for my industry?',
    answer:
      'Market Mind AI is built for a wide range of industries — SaaS, e-commerce, agencies, local businesses, and more. The AI adapts to your niche, competitors, and audience as you use it.',
  },
]

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.07 } },
}

const itemVariants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } },
}

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState(0)
  const buttonsRef = useRef([])

  const toggle = (index) => {
    setOpenIndex((current) => (current === index ? -1 : index))
  }

  const handleKeyDown = (event, index) => {
    const buttons = buttonsRef.current
    if (!buttons.length) return

    let next = index
    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault()
        next = (index + 1) % buttons.length
        break
      case 'ArrowUp':
        event.preventDefault()
        next = (index - 1 + buttons.length) % buttons.length
        break
      case 'Home':
        event.preventDefault()
        next = 0
        break
      case 'End':
        event.preventDefault()
        next = buttons.length - 1
        break
      default:
        return
    }
    buttons[next].focus()
  }

  return (
    <section
      id="faq"
      aria-label="Frequently asked questions"
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

      <div className="relative mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <SectionTitle
          eyebrow="FAQ"
          title="Frequently asked questions"
          description="Everything you need to know about the product. Still curious? Reach out and we will help."
          align="center"
        />

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-60px' }}
          className="mt-14 space-y-4"
        >
          {faqs.map((faq, index) => {
            const isOpen = openIndex === index
            return (
              <motion.div
                key={faq.question}
                variants={itemVariants}
                className={cn(
                  'overflow-hidden rounded-2xl border backdrop-blur transition-colors duration-300',
                  isOpen
                    ? 'border-accent-400/30 bg-landing-card-hover shadow-lg shadow-accent-500/10'
                    : 'border-landing-border bg-landing-card hover:border-landing-border-strong'
                )}
              >
                <h3>
                  <button
                    type="button"
                    ref={(el) => (buttonsRef.current[index] = el)}
                    onClick={() => toggle(index)}
                    onKeyDown={(e) => handleKeyDown(e, index)}
                    aria-expanded={isOpen}
                    aria-controls={`faq-panel-${index}`}
                    id={`faq-button-${index}`}
                    tabIndex={index === openIndex ? 0 : -1}
                    className="flex w-full cursor-pointer items-center justify-between gap-4 px-6 py-5 text-left focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-accent-500"
                  >
                    <span className="text-sm font-medium text-landing-text sm:text-base">
                      {faq.question}
                    </span>
                    <motion.span
                      animate={{ rotate: isOpen ? 180 : 0 }}
                      transition={{ duration: 0.3, ease: 'easeInOut' }}
                      className={cn(
                        'flex h-8 w-8 shrink-0 items-center justify-center rounded-full border transition-colors duration-300',
                        isOpen
                          ? 'border-accent-400/40 bg-accent-500/20 text-accent-300'
                          : 'border-landing-border bg-landing-card text-landing-muted'
                      )}
                    >
                      <ChevronDown size={16} strokeWidth={2.25} />
                    </motion.span>
                  </button>
                </h3>

                <AnimatePresence initial={false}>
                  {isOpen && (
                    <motion.div
                      id={`faq-panel-${index}`}
                      role="region"
                      aria-labelledby={`faq-button-${index}`}
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3, ease: 'easeInOut' }}
                    >
                      <p className="px-6 pb-6 text-sm leading-relaxed text-landing-muted">
                        {faq.answer}
                      </p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            )
          })}
        </motion.div>
      </div>
    </section>
  )
}
