/**
 * Simple stable device fingerprint for registration-time fraud checks.
 */
function hashString(input) {
  let hash = 2166136261
  for (let i = 0; i < input.length; i += 1) {
    hash ^= input.charCodeAt(i)
    hash = Math.imul(hash, 16777619)
  }
  return (hash >>> 0).toString(16).padStart(8, '0')
}

export function getDeviceFingerprint() {
  if (typeof navigator === 'undefined' || typeof screen === 'undefined') {
    return 'unknown-device'
  }

  const raw = [
    navigator.userAgent || '',
    screen.width || '',
    screen.height || '',
    navigator.language || '',
    navigator.platform || '',
  ].join('|')

  return `fp_${hashString(raw)}`
}

export function formatRetryAfter(seconds) {
  const total = Number(seconds)
  if (!Number.isFinite(total) || total <= 0) return 'a while'

  const hours = Math.floor(total / 3600)
  const minutes = Math.floor((total % 3600) / 60)

  if (hours > 0 && minutes > 0) {
    return `${hours} hour${hours === 1 ? '' : 's'} and ${minutes} minute${minutes === 1 ? '' : 's'}`
  }
  if (hours > 0) return `${hours} hour${hours === 1 ? '' : 's'}`
  if (minutes > 0) return `${minutes} minute${minutes === 1 ? '' : 's'}`
  return `${Math.ceil(total)} second${total === 1 ? '' : 's'}`
}

export function messageFromGuardrailError(err) {
  const status = err.response?.status
  const backendMessage = err.response?.data?.error
  const retryAfter = err.response?.headers?.['retry-after']

  if (status === 429) {
    const wait = formatRetryAfter(retryAfter)
    return `Too many failed attempts. Please try again in ${wait}.`
  }

  if (status === 409) {
    return backendMessage || 'This national ID cannot be used for registration.'
  }

  if (status === 400 && /permanent email|disposable|valid permanent/i.test(backendMessage || '')) {
    return 'Please use a valid permanent email address such as Gmail or Outlook'
  }

  return backendMessage || err.message || 'Request failed'
}

export default getDeviceFingerprint
