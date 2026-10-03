export const MAX_SKIPS_BEFORE_PERMANENT_DISMISS = 1
export function readLocal(key, fallback = null) {
  try { return JSON.parse(window.localStorage.getItem(key)) ?? fallback } catch { return fallback }
}
export function writeLocal(key, value) {
  try { window.localStorage.setItem(key, JSON.stringify(value)); return true } catch { return false }
}
export function removeLocal(key) {
  try { window.localStorage.removeItem(key) } catch { /* Storage may be blocked. */ }
}
export const registered = userId => readLocal(`passkey_registered:${userId}`)
export function markRegistered(userId, credentialId) {
  writeLocal(`passkey_registered:${userId}`, { credentialId, createdAt: new Date().toISOString() })
  writeLocal('passkey_registered_any', true)
}
export function dismissPrompt(userId) { writeLocal(`passkey_prompt_dismissed:${userId}`, true) }
export function skipPrompt(userId, limit = MAX_SKIPS_BEFORE_PERMANENT_DISMISS) {
  const count = Number(readLocal(`passkey_prompt_skip_count:${userId}`, 0)) + 1
  writeLocal(`passkey_prompt_skip_count:${userId}`, count)
  if (count >= limit) dismissPrompt(userId)
}
export function optedIn(userId) {
  removeLocal(`passkey_prompt_dismissed:${userId}`)
  removeLocal(`passkey_prompt_skip_count:${userId}`)
}
export function shouldPrompt({ userId, supported, eligible, shown, ready }) {
  return !!(userId && supported && eligible && !shown && ready && !registered(userId)
    && readLocal(`passkey_prompt_dismissed:${userId}`) !== true
    && Number(readLocal(`passkey_prompt_skip_count:${userId}`, 0)) < MAX_SKIPS_BEFORE_PERMANENT_DISMISS)
}
export function clearStaleCredential(credentialId) {
  if (!credentialId) return
  try {
    const keys = Object.keys(window.localStorage).filter(k => k.startsWith('passkey_registered:'))
    for (const key of keys) if (readLocal(key)?.credentialId === credentialId) removeLocal(key)
  } catch { /* Hint only. */ }
}
