import { BLOCKED_EMAIL_DOMAINS } from './blockedEmailDomains.js'

function intEnv(name, fallback) {
  const raw = process.env[name]
  if (raw === undefined || raw === '') return fallback
  const parsed = Number.parseInt(raw, 10)
  return Number.isFinite(parsed) ? parsed : fallback
}

export const fraudConfig = {
  maxFailedAttemptsPerIp: intEnv('FRAUD_MAX_FAILED_ATTEMPTS_PER_IP', 3),
  maxFailedAttemptsPerDevice: intEnv('FRAUD_MAX_FAILED_ATTEMPTS_PER_DEVICE', 3),
  lookbackHours: intEnv('FRAUD_LOOKBACK_HOURS', 24),
  maxStrikesBeforeReject: intEnv('FRAUD_MAX_STRIKES_BEFORE_REJECT', 3),
  blockedEmailDomains: BLOCKED_EMAIL_DOMAINS,
}

/**
 * Warn if fraud-related env vars are missing (defaults still apply).
 */
export function isFraudConfigValid() {
  const required = [
    'FRAUD_MAX_FAILED_ATTEMPTS_PER_IP',
    'FRAUD_MAX_FAILED_ATTEMPTS_PER_DEVICE',
    'FRAUD_LOOKBACK_HOURS',
  ]

  const missing = required.filter((key) => {
    const value = process.env[key]
    return value === undefined || value === ''
  })

  if (missing.length > 0) {
    console.warn(
      `[fraudConfig] Missing env vars (using defaults): ${missing.join(', ')}`
    )
    return false
  }

  return true
}

export function extractEmailDomain(email) {
  if (!email || typeof email !== 'string') return null
  const parts = email.trim().toLowerCase().split('@')
  if (parts.length !== 2 || !parts[1]) return null
  return parts[1]
}

export function isBlockedEmailDomain(email) {
  const domain = extractEmailDomain(email)
  if (!domain) return false
  return fraudConfig.blockedEmailDomains.some(
    (blocked) => domain === blocked || domain.endsWith(`.${blocked}`)
  )
}

export default fraudConfig
