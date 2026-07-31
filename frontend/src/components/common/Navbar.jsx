import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Menu, X } from 'lucide-react'
import { APP_NAME, NAV_LINKS } from '@/constants'
import Button from '@/components/ui/Button'

export default function Navbar() {
  const [open, setOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 border-b border-zinc-800/80 bg-zinc-950/80 backdrop-blur">
      <nav className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link to="/" className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-sm bg-indigo-500" />
          <span className="text-sm font-semibold text-white">{APP_NAME}</span>
        </Link>

        <div className="hidden items-center gap-8 md:flex">
          {NAV_LINKS.map((link) => (
            <a
              key={link.label}
              href={link.href}
              className="text-sm text-zinc-400 transition-colors hover:text-white"
            >
              {link.label}
            </a>
          ))}
        </div>

        <div className="hidden items-center gap-3 md:flex">
          <Button to="/login" variant="ghost" size="sm">
            Log in
          </Button>
          <Button to="/register" size="sm">
            Get started
          </Button>
        </div>

        <button
          type="button"
          className="text-zinc-300 md:hidden"
          onClick={() => setOpen((v) => !v)}
          aria-label="Toggle navigation"
        >
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>
      </nav>

      {open && (
        <div className="border-t border-zinc-800 px-4 pb-4 pt-2 md:hidden">
          {NAV_LINKS.map((link) => (
            <a
              key={link.label}
              href={link.href}
              className="block py-2 text-sm text-zinc-400 hover:text-white"
              onClick={() => setOpen(false)}
            >
              {link.label}
            </a>
          ))}
          <div className="mt-3 flex gap-3">
            <Button to="/login" variant="outline" size="sm" className="flex-1">
              Log in
            </Button>
            <Button to="/register" size="sm" className="flex-1">
              Get started
            </Button>
          </div>
        </div>
      )}
    </header>
  )
}
