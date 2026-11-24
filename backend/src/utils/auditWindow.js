// Business days are Monday–Friday in Africa/Nairobi (UTC+03:00).
// Keep the local time of day across the retention window.
export function auditExpiresAt(startedAt, businessDays = 3) {
  if (!startedAt) return null
  const date = new Date(startedAt)
  if (!Number.isFinite(date.getTime())) return null
  date.setTime(date.getTime() + 3 * 60 * 60 * 1000)
  let remaining = businessDays
  while (remaining) {
    date.setUTCDate(date.getUTCDate() + 1)
    if (![0, 6].includes(date.getUTCDay())) remaining--
  }
  return new Date(date.getTime() - 3 * 60 * 60 * 1000).toISOString()
}

export function auditWindow(status, decision, now = new Date(), submittedAt = null) {
  const decidedAt = decision?.final_decision === status ? decision.decided_at : null
  const verifiedAt = status === 'verified' ? decidedAt : null
  const start = decidedAt || submittedAt
  const expiresAt = auditExpiresAt(start, ['review', 'rejected'].includes(status) ? 5 : 3)
  return { verifiedAt, expiresAt, open: Boolean(expiresAt && new Date(start) <= now && new Date(expiresAt) > now) }
}

// Uploads have unique storage paths but document rows can be reused on a retry.
// Associate a file with its first subsequent submission, not the latest retry.
export function fileExpiresAt(uploadedAt, requests) {
  const time = new Date(uploadedAt).getTime()
  if (!uploadedAt || !Number.isFinite(time)) return null
  const request = requests.find(row => new Date(row.created_at).getTime() >= time)
  if (!request || request.status === 'pending') return auditExpiresAt(uploadedAt)
  const decision = Array.isArray(request.kyc_decisions) ? request.kyc_decisions[0] : request.kyc_decisions
  return auditWindow(request.status, decision, new Date(), request.created_at).expiresAt
}

export async function loadRetentionRequests(client, agentId) {
  const requests = []
  for (let offset = 0; ; offset += 100) {
    const { data, error } = await client.from('verification_requests')
      .select('status, created_at, kyc_decisions(final_decision, decided_at)').eq('agent_id', agentId)
      .order('created_at').order('request_id').range(offset, offset + 99)
    if (error) throw error
    requests.push(...(data || []))
    if (!data || data.length < 100) return requests
  }
}
