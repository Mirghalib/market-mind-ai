import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'

const STORAGE_KEY = 'market_mind_ai_theme'

/**
 * Available themes. `id` is persisted; `label`/`icon` are for the switcher;
 * `isDark` drives the `dark:` Tailwind variant (Light is the only light theme).
 */
export const THEMES = [
  { id: 'light', label: 'Light', icon: 'sun', isDark: false },
  { id: 'dark', label: 'Dark', icon: 'moon', isDark: true },
  { id: 'midnight', label: 'Midnight', icon: 'moon-star', isDark: true },
  { id: 'emerald', label: 'Emerald', icon: 'leaf', isDark: true },
]

export const ThemeContext = createContext(null)

function getInitialTheme() {
  const stored = window.localStorage.getItem(STORAGE_KEY)
  const valid = THEMES.some((theme) => theme.id === stored)
  return valid ? stored : 'dark'
}

/**
 * Multi-theme provider. Applies `data-theme` + `.dark` on <html>,
 * persists the selection, and restores it on startup.
 */
export default function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(getInitialTheme)

  useEffect(() => {
    const root = document.documentElement
    root.setAttribute('data-theme', theme)
    const meta = THEMES.find((t) => t.id === theme)
    root.classList.toggle('dark', Boolean(meta?.isDark))
    window.localStorage.setItem(STORAGE_KEY, theme)
  }, [theme])

  const value = useMemo(() => {
    const meta = THEMES.find((t) => t.id === theme)
    return {
      theme,
      isDark: meta?.isDark ?? true,
      setTheme,
      toggleTheme: () => setTheme((current) => (current === 'light' ? 'dark' : 'light')),
    }
  }, [theme])

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}
