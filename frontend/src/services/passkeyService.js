import { startAuthentication, startRegistration, WebAuthnAbortService } from '@simplewebauthn/browser'
import api from './api.js'
import { markRegistered, clearStaleCredential } from '../utils/passkeyStorage.js'

export const FALLBACK_MESSAGE = 'No passkey found on this browser. You can sign in with your password or a one-time code, or use a passkey from your phone.'
export function passkeyErrorMessage(error, fallback) {
  const code = error?.response?.data?.code
  if (code === 'PASSKEY_NOT_CONFIGURED') return 'Passkeys have not been configured on the server yet. Please sign in another way.'
  if (code === 'PASSKEY_ORIGIN_NOT_ALLOWED') return 'Open the app at its configured address to set up or use a passkey.'
  if (error?.response?.status === 503) return 'The passkey service is temporarily unavailable. Please try again shortly.'
  if (error?.response?.status === 429) return 'Please wait a few minutes before trying your passkey again.'
  return fallback
}
export const isCancelled = error => error?.name === 'NotAllowedError' || error?.cause?.name === 'NotAllowedError'
export const isAborted = error => error?.name === 'AbortError' || error?.cause?.name === 'AbortError'
const isDuplicate = error => error?.name === 'InvalidStateError' || error?.cause?.name === 'InvalidStateError'
let generation = 0
let ready = null
let priming = null
let primeSeq = 0
export function cancelPasskeyCeremony() {
  generation++
  WebAuthnAbortService.cancelCeremony() // Uses AbortController for the pending navigator request.
}
export function clearPreparedPasskey() { ready = null; primeSeq++ }
function assertActive(id) { if (id !== generation) throw new DOMException('Cancelled', 'AbortError') }
export function passkeyHints(hints = {}) {
  const email = String(hints.email || '').trim().toLowerCase()
  const credentialIds = [...new Set((hints.credentialIds || []).filter(id => typeof id === 'string' && id.length > 0 && id.length <= 512))].slice(0, 10).sort()
  return { email, credentialIds, key: `${email}|${credentialIds.join(',')}` }
}
export function primePasskeyLogin(hints = {}) {
  const wanted = passkeyHints(hints)
  if (ready?.key === wanted.key && Date.now() - ready.at < 240000) return Promise.resolve(ready)
  if (priming?.key === wanted.key) return priming.promise
  const seq = ++primeSeq
  const body = {}
  if (wanted.email) body.email = wanted.email
  if (wanted.credentialIds.length) body.credentialIds = wanted.credentialIds
  const promise = api.post('/api/auth/passkey/login/options', body).then(({ data }) => {
    if (seq !== primeSeq) return ready
    ready = { ...data, key: wanted.key, at: Date.now() }
    return ready
  }).finally(() => { if (priming?.key === wanted.key) priming = null })
  priming = { key: wanted.key, promise }
  return promise
}
export async function loginWithPasskey(conditional = false, hints = {}) {
  const wanted = passkeyHints(conditional ? {} : hints)
  const fresh = value => value && Date.now() - value.at < 240000
  const exact = fresh(ready) && ready.key === wanted.key ? ready : null
  // Any prepared challenge keeps the click inside the browser's user gesture.
  // The server accepts it either way; a matching email list is used when ready.
  const cached = exact || (!conditional && fresh(ready) ? ready : null)
  cancelPasskeyCeremony()
  const id = generation
  // A click must reach the browser before the first await, or Chrome drops the
  // gesture and reports that no passkey is available.
  const immediate = !conditional && cached
    ? startAuthentication({ optionsJSON: cached.options, useBrowserAutofill: false })
    : null
  let current = cached
  for (let attempt = 0; attempt < 2; attempt++) {
    let response
    try {
      if (!current) {
        current = await primePasskeyLogin(wanted)
        assertActive(id)
      }
      response = immediate && attempt === 0
        ? await immediate
        : await startAuthentication({ optionsJSON: current.options, useBrowserAutofill: conditional })
      assertActive(id)
      if (ready?.key === current.key) ready = null
      const verified = await api.post('/api/auth/passkey/login/verify', { challengeId: current.challengeId, response })
      assertActive(id)
      markRegistered(verified.data.user.user_id, verified.data.credentialId)
      return verified.data
    } catch (error) {
      assertActive(id)
      if (error.response?.data?.code === 'CHALLENGE_EXPIRED' && attempt === 0) { current = null; ready = null; continue }
      if (response?.id && error.response?.data?.code === 'PASSKEY_FAILED') clearStaleCredential(response.id)
      throw error
    }
  }
}
export async function registerPasskey(userId, manage = false) {
  cancelPasskeyCeremony()
  const id = generation
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const { data } = await api.post('/api/auth/passkey/register/options', { manage })
      assertActive(id)
      let response
      try { response = await startRegistration({ optionsJSON: data.options }) }
      catch (error) {
        assertActive(id)
        if (isDuplicate(error)) {
          // The browser does not disclose which excluded credential matched.
          // Do not invent a credential ID or incorrectly badge another device.
          markRegistered(userId, null)
          return { duplicate: true, message: "You're all set. A passkey is already available on this device" }
        }
        throw error
      }
      assertActive(id)
      const verified = await api.post('/api/auth/passkey/register/verify', { challengeId: data.challengeId, response })
      assertActive(id)
      markRegistered(userId, verified.data.credential_id)
      return { ...verified.data, message: 'Passkey added. Next time, sign in with one tap.' }
    } catch (error) {
      assertActive(id)
      if (error.response?.data?.code === 'CHALLENGE_EXPIRED' && attempt === 0) continue
      throw error
    }
  }
}
export async function signalRemoved(rpId, credentialId) {
  try { await window.PublicKeyCredential?.signalUnknownCredential?.({ rpId, credentialId }) } catch { /* Best effort. */ }
}
export async function signalAcceptedPasskeys(data) {
  if (!data?.rpId || !data?.userHandle || !window.PublicKeyCredential) return
  const allAcceptedCredentialIds = (data.passkeys || []).map(key => key.credential_id).filter(Boolean)
  try {
    await window.PublicKeyCredential.signalAllAcceptedCredentials?.({ rpId: data.rpId, userId: data.userHandle, allAcceptedCredentialIds })
    if (data.userName) {
      await window.PublicKeyCredential.signalCurrentUserDetails?.({ rpId: data.rpId, userId: data.userHandle, name: data.userName, displayName: data.userName })
    }
  } catch { /* The browser may not support passkey signals. */ }
}
export async function syncPasskeyHints() {
  const { data } = await api.get('/api/auth/passkeys')
  await signalAcceptedPasskeys(data)
  return data
}
