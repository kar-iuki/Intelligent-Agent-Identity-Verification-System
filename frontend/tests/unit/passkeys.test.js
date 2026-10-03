import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { detectPasskeySupport, usePasskeySupport } from '../../src/composables/usePasskeySupport.js'
import { readLocal, writeLocal, removeLocal, markRegistered, registered, skipPrompt, dismissPrompt, optedIn, shouldPrompt, clearStaleCredential } from '../../src/utils/passkeyStorage.js'

beforeEach(() => { vi.restoreAllMocks(); localStorage.clear() })
describe('capability detection', () => {
  it('handles SSR, missing WebAuthn, and insecure contexts', async () => {
    for (const win of [null, {}, { isSecureContext:false, PublicKeyCredential:{} }]) expect(await detectPasskeySupport(win)).toEqual({ supported:false, conditionalUI:false })
  })
  it('handles all capability combinations and missing optional API', async () => {
    for (const supported of [false,true]) for (const conditionalUI of [false,true]) {
      expect(await detectPasskeySupport({ PublicKeyCredential:{ isUserVerifyingPlatformAuthenticatorAvailable:async () => supported, isConditionalMediationAvailable:async () => conditionalUI } })).toEqual({ supported, conditionalUI })
    }
    expect(await detectPasskeySupport({ PublicKeyCredential:{ isUserVerifyingPlatformAuthenticatorAvailable:async () => true } })).toEqual({ supported:true, conditionalUI:false })
  })
  it('treats either rejection and missing required API as unsupported', async () => {
    const fail = async () => { throw Error('blocked') }
    for (const credential of [{}, { isUserVerifyingPlatformAuthenticatorAvailable:fail }, { isUserVerifyingPlatformAuthenticatorAvailable:async () => true, isConditionalMediationAvailable:fail }]) {
      expect(await detectPasskeySupport({ PublicKeyCredential:credential })).toEqual({ supported:false, conditionalUI:false })
    }
  })
  it('hook resolves after mounting and ignores results after unmount', async () => {
    let resolve
    vi.stubGlobal('PublicKeyCredential', { isUserVerifyingPlatformAuthenticatorAvailable:() => new Promise(r => { resolve = r }) })
    const wrapper = mount({ setup:usePasskeySupport, template:'<span>{{supported}}/{{conditionalUI}}</span>' })
    expect(wrapper.text()).toBe('false/false'); resolve(true); await flushPromises(); expect(wrapper.text()).toBe('true/false'); wrapper.unmount()
    const second = mount({ setup:usePasskeySupport, template:'<span>{{supported}}</span>' })
    const state = second.vm; second.unmount(); resolve(true); await flushPromises(); expect(state.supported).toBe(false)
    vi.unstubAllGlobals()
  })
})
describe('storage and prompt rules', () => {
  const eligible = () => ({ userId:'one', supported:true, eligible:true, shown:false, ready:true })
  it('handles blocked storage and malformed JSON', () => {
    localStorage.setItem('broken','{'); expect(readLocal('broken')).toBeNull()
    vi.spyOn(Storage.prototype,'getItem').mockImplementation(() => { throw Error() })
    vi.spyOn(Storage.prototype,'setItem').mockImplementation(() => { throw Error() })
    vi.spyOn(Storage.prototype,'removeItem').mockImplementation(() => { throw Error() })
    expect(readLocal('x',3)).toBe(3); expect(writeLocal('x',true)).toBe(false); expect(() => removeLocal('x')).not.toThrow()
  })
  it('scopes shared-browser hints and stale cleanup by credential', () => {
    markRegistered('one','first'); markRegistered('two','second')
    expect(readLocal('passkey_registered_any')).toBe(true)
    clearStaleCredential('first'); expect(registered('one')).toBeNull(); expect(registered('two').credentialId).toBe('second')
  })
  it('Skip defaults to permanent dismissal; configurable limit permits reminders', () => {
    skipPrompt('one'); expect(shouldPrompt(eligible())).toBe(false)
    optedIn('one'); skipPrompt('one',3); expect(readLocal('passkey_prompt_dismissed:one')).toBeNull()
    skipPrompt('one',3); skipPrompt('one',3); expect(readLocal('passkey_prompt_dismissed:one')).toBe(true)
  })
  it('checks every visibility gate freshly rather than caching hints', () => {
    expect(shouldPrompt(eligible())).toBe(true)
    for (const patch of [{ userId:null }, { supported:false }, { eligible:false }, { shown:true }, { ready:false }]) expect(shouldPrompt({ ...eligible(), ...patch })).toBe(false)
    dismissPrompt('one'); expect(shouldPrompt(eligible())).toBe(false)
    optedIn('one'); expect(shouldPrompt(eligible())).toBe(true)
    markRegistered('one',null); expect(shouldPrompt(eligible())).toBe(false)
    removeLocal('passkey_registered:one'); expect(shouldPrompt(eligible())).toBe(true)
    writeLocal('passkey_prompt_skip_count:one',1); expect(shouldPrompt(eligible())).toBe(false)
  })
})
