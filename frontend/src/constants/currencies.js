/**
 * Country → currency mapping for the strategy form.
 * Mirrors backend/app/services/ai/currencies.py so the auto-selected
 * currency matches what the backend formats.
 */
export const COUNTRY_CURRENCIES = {
  'United States': { code: 'USD', symbol: '$' },
  USA: { code: 'USD', symbol: '$' },
  'United Kingdom': { code: 'GBP', symbol: '£' },
  UK: { code: 'GBP', symbol: '£' },
  Pakistan: { code: 'PKR', symbol: 'Rs.' },
  India: { code: 'INR', symbol: '₹' },
  UAE: { code: 'AED', symbol: 'AED ' },
  'United Arab Emirates': { code: 'AED', symbol: 'AED ' },
  'Saudi Arabia': { code: 'SAR', symbol: 'SAR ' },
  Canada: { code: 'CAD', symbol: 'C$' },
  Australia: { code: 'AUD', symbol: 'A$' },
  Germany: { code: 'EUR', symbol: '€' },
  France: { code: 'EUR', symbol: '€' },
  Italy: { code: 'EUR', symbol: '€' },
  Spain: { code: 'EUR', symbol: '€' },
  Netherlands: { code: 'EUR', symbol: '€' },
  Brazil: { code: 'BRL', symbol: 'R$' },
  Mexico: { code: 'MXN', symbol: 'MX$' },
  Turkey: { code: 'TRY', symbol: '₺' },
  Nigeria: { code: 'NGN', symbol: '₦' },
  'South Africa': { code: 'ZAR', symbol: 'R' },
  Egypt: { code: 'EGP', symbol: 'E£' },
  Japan: { code: 'JPY', symbol: '¥' },
  China: { code: 'CNY', symbol: '¥' },
  Singapore: { code: 'SGD', symbol: 'S$' },
  Malaysia: { code: 'MYR', symbol: 'RM' },
  Indonesia: { code: 'IDR', symbol: 'Rp' },
  Thailand: { code: 'THB', symbol: '฿' },
  Philippines: { code: 'PHP', symbol: '₱' },
  'New Zealand': { code: 'NZD', symbol: 'NZ$' },
  Ireland: { code: 'EUR', symbol: '€' },
  Switzerland: { code: 'CHF', symbol: 'CHF ' },
  Sweden: { code: 'SEK', symbol: 'kr' },
  Norway: { code: 'NOK', symbol: 'kr' },
  Denmark: { code: 'DKK', symbol: 'kr' },
  Poland: { code: 'PLN', symbol: 'zł' },
  Portugal: { code: 'EUR', symbol: '€' },
  Belgium: { code: 'EUR', symbol: '€' },
  Austria: { code: 'EUR', symbol: '€' },
  Greece: { code: 'EUR', symbol: '€' },
  Qatar: { code: 'QAR', symbol: 'QR ' },
  Kuwait: { code: 'KWD', symbol: 'KD ' },
  Oman: { code: 'OMR', symbol: 'OMR ' },
  Bahrain: { code: 'BHD', symbol: 'BD ' },
  Jordan: { code: 'JOD', symbol: 'JD ' },
  Morocco: { code: 'MAD', symbol: 'MAD ' },
  Bangladesh: { code: 'BDT', symbol: '৳' },
  'Sri Lanka': { code: 'LKR', symbol: 'Rs.' },
  Nepal: { code: 'NPR', symbol: 'Rs.' },
  Vietnam: { code: 'VND', symbol: '₫' },
  'South Korea': { code: 'KRW', symbol: '₩' },
  'Hong Kong': { code: 'HKD', symbol: 'HK$' },
  Taiwan: { code: 'TWD', symbol: 'NT$' },
  Argentina: { code: 'ARS', symbol: 'AR$' },
  Chile: { code: 'CLP', symbol: 'CLP$' },
  Colombia: { code: 'COP', symbol: 'COL$' },
  Peru: { code: 'PEN', symbol: 'S/' },
  Ukraine: { code: 'UAH', symbol: '₴' },
  Romania: { code: 'RON', symbol: 'lei' },
  'Czech Republic': { code: 'CZK', symbol: 'Kč' },
  Hungary: { code: 'HUF', symbol: 'Ft' },
  Croatia: { code: 'EUR', symbol: '€' },
  Finland: { code: 'EUR', symbol: '€' },
  Other: { code: 'USD', symbol: '$' },
}

/** All supported currency codes (for manual override). */
export const CURRENCY_OPTIONS = Object.entries(
  COUNTRY_CURRENCIES
).reduce((acc, [country, { code, symbol }]) => {
  if (!acc[code]) acc[code] = { code, symbol }
  return acc
}, {})

export const DEFAULT_CURRENCY = { code: 'USD', symbol: '$' }

/** Currency for a country (auto-selected), defaulting to USD. */
export function currencyForCountry(country) {
  return COUNTRY_CURRENCIES[country] ?? DEFAULT_CURRENCY
}

/** Format a budget amount with the right symbol, e.g. "Rs. 100,000 / month". */
export function formatBudget(amount, symbol = '$', period = 'month') {
  const value = Number(amount)
  if (!Number.isFinite(value) || value <= 0) return ''
  let display
  if (value >= 1_000_000) display = `${(value / 1_000_000).toLocaleString(undefined, { maximumFractionDigits: 1 })}M`
  else display = Math.round(value).toLocaleString()
  const sym = symbol || '$'
  let label
  if (sym.endsWith(' ') || ['$', '£', '€', '₹', '¥', '₩', '₫', 'R', 'kr'].includes(sym)) {
    label = `${sym}${display}`.trim()
  } else {
    label = `${sym} ${display}`.trim()
  }
  return period && period !== 'month' ? `${label} / ${period}` : `${label} / month`
}
