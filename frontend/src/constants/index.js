export const APP_NAME = 'Market Mind AI'

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

export const TOKEN_STORAGE_KEY = 'market_mind_ai_token'

export const NAV_LINKS = [
  { label: 'Features', href: '#features' },
  { label: 'How it works', href: '#how-it-works' },
  { label: 'Pricing', href: '#pricing' },
]

export const DASHBOARD_LINKS = [
  { label: 'Dashboard', href: '/dashboard', icon: 'LayoutDashboard' },
  { label: 'History', href: '/history', icon: 'History' },
  { label: 'Settings', href: '/settings', icon: 'Settings' },
]
