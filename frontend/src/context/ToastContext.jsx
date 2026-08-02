import { createContext, useCallback, useContext, useMemo, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { CheckCircle2, Info, X, XCircle } from 'lucide-react'
import { cn } from '@/utils/cn'

const ToastContext = createContext(null)

let toastId = 0

/**
 * Lightweight global toast system. Usage:
 *   const { showToast } = useToast()
 *   showToast('Saved!', 'success')
 */
export default function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const dismiss = useCallback((id) => {
    setToasts((current) => current.filter((t) => t.id !== id))
  }, [])

  const showToast = useCallback(
    (message, type = 'info') => {
      const id = ++toastId
      setToasts((current) => [...current, { id, message, type }])
      window.setTimeout(() => dismiss(id), 4500)
      return id
    },
    [dismiss]
  )

  const value = useMemo(() => ({ showToast }), [showToast])

  const ICONS = {
    success: <CheckCircle2 size={18} className="text-emerald-500" />,
    error: <XCircle size={18} className="text-red-500" />,
    info: <Info size={18} className="text-indigo-500" />,
  }

  const STYLES = {
    success: 'border-emerald-500/30 bg-card text-foreground dark:bg-zinc-900',
    error: 'border-red-500/30 bg-card text-foreground dark:bg-zinc-900',
    info: 'border-indigo-500/30 bg-card text-foreground dark:bg-zinc-900',
  }

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed right-4 bottom-4 z-[100] flex w-full max-w-sm flex-col gap-2">
        <AnimatePresence>
          {toasts.map((toast) => (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, y: 16, scale: 0.97 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 8, scale: 0.97 }}
              transition={{ duration: 0.2, ease: 'easeOut' }}
              role="status"
              className={cn(
                'pointer-events-auto flex items-start gap-3 rounded-xl border p-4 shadow-xl shadow-black/10',
                STYLES[toast.type]
              )}
            >
              <span className="mt-0.5 shrink-0">{ICONS[toast.type] ?? ICONS.info}</span>
              <p className="min-w-0 flex-1 text-sm leading-relaxed text-foreground dark:text-zinc-200">
                {toast.message}
              </p>
              <button
                type="button"
                onClick={() => dismiss(toast.id)}
                aria-label="Dismiss notification"
                className="shrink-0 rounded-lg p-1 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-white"
              >
                <X size={15} />
              </button>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider')
  }
  return context
}
