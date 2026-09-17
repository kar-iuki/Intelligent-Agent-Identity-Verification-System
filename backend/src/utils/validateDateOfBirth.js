/**
 * Validate an ISO date string (YYYY-MM-DD) for agent registration.
 * @returns {string|null} Error message or null if valid
 */
export function validateDateOfBirth(value) {
  if (!value || typeof value !== 'string') {
    return 'Date of birth is required'
  }

  const trimmed = value.trim()
  if (!/^\d{4}-\d{2}-\d{2}$/.test(trimmed)) {
    return 'Enter a valid date of birth'
  }

  const date = new Date(`${trimmed}T00:00:00`)
  if (Number.isNaN(date.getTime())) {
    return 'Enter a valid date of birth'
  }

  const now = new Date()
  if (date >= now) {
    return 'Date of birth must be in the past'
  }

  const ageMs = now.getTime() - date.getTime()
  const ageYears = ageMs / (365.25 * 24 * 60 * 60 * 1000)
  if (ageYears < 18) {
    return 'You must be at least 18 years old'
  }
  if (ageYears > 120) {
    return 'Enter a valid date of birth'
  }

  return null
}

/** Format DB date (YYYY-MM-DD) for OCR comparison. */
export function formatDobForOcr(dateOfBirth) {
  if (!dateOfBirth) return ''
  const str = String(dateOfBirth).slice(0, 10)
  const [year, month, day] = str.split('-')
  if (year && month && day) {
    return `${day}/${month}/${year}`
  }
  return str
}
