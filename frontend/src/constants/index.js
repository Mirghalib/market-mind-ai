export const APP_NAME = 'Market Mind AI'

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export const TOKEN_STORAGE_KEY = 'market_mind_ai_token'

export const NAV_LINKS = [
  { label: 'Home', href: '#home' },
  { label: 'Features', href: '#features' },
  { label: 'How It Works', href: '#how-it-works' },
  { label: 'Pricing', href: '#pricing' },
  { label: 'FAQ', href: '#faq' },
  { label: 'About', href: '#about' },
]

export const DASHBOARD_LINKS = [
  { label: 'Dashboard', href: '/dashboard', icon: 'LayoutDashboard' },
  { label: 'History', href: '/history', icon: 'History' },
  { label: 'Settings', href: '/settings', icon: 'Settings' },
]

export const ADMIN_LINKS = [
  { label: 'Admin Dashboard', href: '/admin/dashboard', icon: 'Shield' },
]
