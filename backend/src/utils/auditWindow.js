// Business days are Monday–Friday in Africa/Nairobi (UTC+03:00).
// Preserve the time of verification, allowing three complete business days.
export function auditExpiresAt(verifiedAt) {
  if (!verifiedAt) return null
  const date = new Date(verifiedAt)
  if (!Number.isFinite(date.getTime())) return null
  date.setTime(date.getTime() + 3 * 60 * 60 * 1000)
  let remaining = 3
  while (remaining) {
    date.setUTCDate(date.getUTCDate() + 1)
    if (![0, 6].includes(date.getUTCDay())) remaining--
  }
  return new Date(date.getTime() - 3 * 60 * 60 * 1000).toISOString()
}

export function auditWindow(status, decision, now = new Date()) {
  const verifiedAt = status === 'verified' && decision?.final_decision === 'verified'
    ? decision.decided_at : null
  const expiresAt = auditExpiresAt(verifiedAt)
  return { verifiedAt, expiresAt, open: Boolean(expiresAt && new Date(verifiedAt) <= now && new Date(expiresAt) > now) }
}
