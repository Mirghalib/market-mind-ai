import { motion } from 'framer-motion'
import { ArrowRight, Sparkles } from 'lucide-react'
import Navbar from '@/components/common/Navbar'
import Footer from '@/components/common/Footer'
import Button from '@/components/ui/Button'

export default function Landing() {
  return (
    <div className="flex min-h-screen flex-col bg-zinc-950 text-zinc-100">
      <Navbar />

      <main className="flex-1">
        <section className="mx-auto flex max-w-7xl flex-col items-center px-4 pt-24 pb-16 text-center sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <span className="inline-flex items-center gap-2 rounded-full border border-zinc-800 bg-zinc-900 px-3 py-1 text-xs text-zinc-400">
              <Sparkles size={14} className="text-indigo-400" />
              AI-powered market intelligence
            </span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="mt-6 max-w-3xl text-4xl font-semibold tracking-tight text-white sm:text-6xl"
          >
            Make smarter decisions with{' '}
            <span className="bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
              Market Mind AI
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="mt-6 max-w-xl text-lg text-zinc-400"
          >
            Real-time market insights, competitor analysis, and predictive
            trends — all in one place.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mt-10 flex items-center gap-4"
          >
            <Button to="/register" size="lg">
              Get started
              <ArrowRight size={18} />
            </Button>
            <Button to="/login" variant="outline" size="lg">
              Log in
            </Button>
          </motion.div>
        </section>
      </main>

      <Footer />
    </div>
  )
}
