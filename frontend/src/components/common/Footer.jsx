import { Link } from 'react-router-dom'
import { AtSign, Globe, Rss, Share2, Sparkles } from 'lucide-react'
import { APP_NAME } from '@/constants'

const columns = [
  {
    title: 'Product',
    links: [
      { label: 'Features', href: '#features' },
      { label: 'How it works', href: '#how-it-works' },
      { label: 'Pricing', href: '#pricing' },
      { label: 'FAQ', href: '#faq' },
    ],
  },
  {
    title: 'Company',
    links: [
      { label: 'About', href: '#about' },
      { label: 'Blog', href: '#' },
      { label: 'Careers', href: '#' },
      { label: 'Contact', href: '#' },
    ],
  },
  {
    title: 'Resources',
    links: [
      { label: 'Documentation', href: '#' },
      { label: 'API Reference', href: '#' },
      { label: 'Guides', href: '#' },
      { label: 'Support', href: '#' },
    ],
  },
  {
    title: 'Legal',
    links: [
      { label: 'Privacy Policy', href: '#' },
      { label: 'Terms of Service', href: '#' },
      { label: 'Cookie Policy', href: '#' },
    ],
  },
]

const socials = [
  { label: 'X (Twitter)', icon: Share2 },
  { label: 'LinkedIn', icon: AtSign },
  { label: 'YouTube', icon: Globe },
  { label: 'Blog', icon: Rss },
]

export default function Footer() {
  return (
    <footer className="border-t border-zinc-800/80 bg-zinc-950">
      <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="grid gap-12 lg:grid-cols-6 lg:gap-8">
          {/* Brand column */}
          <div className="lg:col-span-2">
            <Link to="/" className="flex items-center gap-2" aria-label={`${APP_NAME} home`}>
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-purple-500">
                <Sparkles size={16} className="text-white" />
              </span>
              <span className="text-sm font-semibold tracking-tight text-white">
                {APP_NAME}
              </span>
            </Link>

            <p className="mt-5 max-w-sm text-sm leading-relaxed text-zinc-500">
              AI-powered marketing intelligence that turns your goals into
              ready-to-publish strategies — market analysis, personas, content,
              and campaigns in seconds.
            </p>

            <div className="mt-6 flex items-center gap-3">
              {socials.map(({ label, icon: Icon }) => (
                <a
                  key={label}
                  href="#"
                  aria-label={label}
                  className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/[0.03] text-zinc-400 transition-all duration-200 hover:-translate-y-0.5 hover:border-indigo-400/40 hover:bg-indigo-500/10 hover:text-indigo-300"
                >
                  <Icon size={18} />
                </a>
              ))}
            </div>
          </div>

          {/* Link columns */}
          {columns.map((column) => (
            <div key={column.title}>
              <h3 className="text-sm font-semibold text-white">{column.title}</h3>
              <ul className="mt-5 space-y-3.5">
                {column.links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      className="text-sm text-zinc-500 transition-colors duration-200 hover:text-white"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Copyright bar */}
        <div className="mt-14 flex flex-col items-center justify-between gap-4 border-t border-zinc-800/80 pt-8 sm:flex-row">
          <p className="text-sm text-zinc-500">
            &copy; {new Date().getFullYear()} {APP_NAME}. All rights reserved.
          </p>
          <p className="text-sm text-zinc-500">
            Built for the hackathon
          </p>
        </div>
      </div>
    </footer>
  )
}
