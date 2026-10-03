import { beforeEach, it, expect, vi } from 'vitest'
const mocks = vi.hoisted(() => ({ post:vi.fn(), authentication:vi.fn(), registration:vi.fn(), cancel:vi.fn() }))
vi.mock('../../src/services/api.js', () => ({ default:{ post:mocks.post } }))
vi.mock('@simplewebauthn/browser', () => ({ startAuthentication:mocks.authentication, startRegistration:mocks.registration, WebAuthnAbortService:{ cancelCeremony:mocks.cancel } }))
import { registerPasskey, loginWithPasskey, cancelPasskeyCeremony } from '../../src/services/passkeyService.js'
import { registered, markRegistered } from '../../src/utils/passkeyStorage.js'
beforeEach(() => { vi.resetAllMocks(); localStorage.clear(); cancelPasskeyCeremony() })
const options = { data:{ options:{ challenge:'random' }, challengeId:'id' } }
const expired = { response:{ data:{ code:'CHALLENGE_EXPIRED' } } }
it('automatically restarts an expired login exactly once', async () => {
  mocks.post.mockResolvedValueOnce(options).mockRejectedValueOnce(expired).mockResolvedValueOnce(options).mockResolvedValueOnce({ data:{ user:{ user_id:'one' }, credentialId:'key' } })
  mocks.authentication.mockResolvedValue({ id:'key' })
  await loginWithPasskey(); expect(mocks.authentication).toHaveBeenCalledTimes(2); expect(registered('one').credentialId).toBe('key')
})
it('stops after two expired challenges and leaves local state unchanged', async () => {
  mocks.post.mockResolvedValueOnce(options).mockRejectedValueOnce(expired).mockResolvedValueOnce(options).mockRejectedValueOnce(expired)
  mocks.registration.mockResolvedValue({ id:'key' })
  await expect(registerPasskey('one')).rejects.toBe(expired); expect(mocks.registration).toHaveBeenCalledTimes(2); expect(registered('one')).toBeNull()
})
it('does not change registration flags on network failure or cancellation', async () => {
  for (const error of [new Error('network'),new DOMException('Cancelled','NotAllowedError')]) {
    mocks.post.mockResolvedValueOnce(options); mocks.registration.mockRejectedValueOnce(error)
    await expect(registerPasskey('one')).rejects.toBe(error); expect(registered('one')).toBeNull()
  }
})
it('duplicate confirms availability without guessing a credential ID', async () => {
  mocks.post.mockResolvedValueOnce(options); mocks.registration.mockRejectedValueOnce(new DOMException('Exists','InvalidStateError'))
  expect((await registerPasskey('one')).duplicate).toBe(true); expect(registered('one').credentialId).toBeNull(); expect(mocks.post).toHaveBeenCalledTimes(1)
})
it('cancellation while fetching options cannot start a late navigator request', async () => {
  let resolve
  mocks.post.mockImplementationOnce(() => new Promise(r => { resolve = r }))
  const ceremony = loginWithPasskey(true); cancelPasskeyCeremony(); resolve(options)
  await expect(ceremony).rejects.toMatchObject({ name:'AbortError' }); expect(mocks.authentication).not.toHaveBeenCalled()
})
it('failed known credential clears only its stale hint', async () => {
  markRegistered('one','key'); markRegistered('two','other')
  mocks.post.mockResolvedValueOnce(options).mockRejectedValueOnce({ response:{ data:{ code:'PASSKEY_FAILED' } } })
  mocks.authentication.mockResolvedValue({ id:'key' })
  await expect(loginWithPasskey()).rejects.toBeDefined(); expect(registered('one')).toBeNull(); expect(registered('two').credentialId).toBe('other')
})
