import { startAuthentication, startRegistration, WebAuthnAbortService } from '@simplewebauthn/browser'
import api from './api.js'
import { markRegistered, clearStaleCredential } from '../utils/passkeyStorage.js'

export const FALLBACK_MESSAGE = 'No passkey found on this browser. You can sign in with your password or a one-time code, or use a passkey from your phone.'
export const isCancelled = error => error?.name === 'NotAllowedError' || error?.cause?.name === 'NotAllowedError'
export const isAborted = error => error?.name === 'AbortError' || error?.cause?.name === 'AbortError'
const isDuplicate = error => error?.name === 'InvalidStateError' || error?.cause?.name === 'InvalidStateError'
let generation = 0
export function cancelPasskeyCeremony() {
  generation++
  WebAuthnAbortService.cancelCeremony() // Uses AbortController for the pending navigator request.
}
function assertActive(id) { if (id !== generation) throw new DOMException('Cancelled', 'AbortError') }
export async function loginWithPasskey(conditional = false) {
  cancelPasskeyCeremony()
  const id = generation
  for (let attempt = 0; attempt < 2; attempt++) {
    let response
    try {
      const { data } = await api.post('/api/auth/passkey/login/options')
      assertActive(id)
      response = await startAuthentication({ optionsJSON: data.options, useBrowserAutofill: conditional })
      assertActive(id)
      const verified = await api.post('/api/auth/passkey/login/verify', { challengeId: data.challengeId, response })
      assertActive(id)
      markRegistered(verified.data.user.user_id, verified.data.credentialId)
      return verified.data
    } catch (error) {
      assertActive(id)
      if (error.response?.data?.code === 'CHALLENGE_EXPIRED' && attempt === 0) continue
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
