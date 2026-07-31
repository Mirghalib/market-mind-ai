export const APP_NAME = 'Market Mind AI'

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

export const TOKEN_STORAGE_KEY = 'market_mind_ai_token'

export const NAV_LINKS = [
  { label: 'Home', href: '/' },
  { label: 'Features', href: '#features' },
  { label: 'Pricing', href: '#pricing' },
  { label: 'About', href: '#about' },
]

export const DASHBOARD_LINKS = [
  { label: 'Dashboard', href: '/dashboard', icon: 'LayoutDashboard' },
  { label: 'History', href: '/history', icon: 'History' },
  { label: 'Settings', href: '/settings', icon: 'Settings' },
]
