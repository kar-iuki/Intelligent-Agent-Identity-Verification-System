const kenyaCalendar = new Intl.DateTimeFormat('sv-SE', {
  timeZone: 'Africa/Nairobi', year: 'numeric', month: '2-digit', day: '2-digit',
})

function yearsBefore(today, years) {
  const year = Number(today.slice(0, 4)) - years
  const monthDay = today.slice(4)
  // On a leap day, the earlier year may only have 28 days in February.
  if (monthDay === '-02-29' && new Date(Date.UTC(year, 1, 29)).getUTCMonth() !== 1) {
    return year + '-02-28'
  }
  return year + monthDay
}

export function validateDateOfBirth(value, now = new Date()) {
  if (typeof value !== 'string' || !value.trim()) return 'Date of birth is required'
  const dob = value.trim()
  if (!/^\d{4}-\d{2}-\d{2}$/.test(dob)) return 'Enter a valid date of birth'
  const date = new Date(dob + 'T00:00:00Z')
  if (Number.isNaN(date.getTime()) || date.toISOString().slice(0, 10) !== dob) {
    return 'Enter a valid date of birth'
  }
  const today = kenyaCalendar.format(now)
  if (dob > today) return 'Date of birth must be in the past'
  if (dob > yearsBefore(today, 18)) return 'You must be at least 18 years old to register as an agent'
  if (dob < yearsBefore(today, 120)) return 'Enter a valid date of birth'
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
