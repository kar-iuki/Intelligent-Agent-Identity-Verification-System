import { mount, flushPromises } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import RegisterPage from '../../src/views/RegisterPage.vue'
import CompleteProfilePage from '../../src/views/CompleteProfilePage.vue'

const currentUser = vi.hoisted(() => vi.fn())
vi.mock('vue-router', () => ({ useRouter: () => ({ push: vi.fn() }) }))
vi.mock('../../src/stores/authStore.js', () => ({
  useAuthStore: () => ({ state: {}, fetchCurrentUser: currentUser }),
}))

describe('verification consent', () => {
  it('requires explicit consent for both email and Google signup', async () => {
    const page = mount(RegisterPage, { global: { stubs: { RouterLink: true } } })
    const checkbox = page.get('input[type=checkbox]')
    const buttons = page.findAll('button')
    expect(checkbox.element.checked).toBe(false)
    expect(buttons.every(button => button.element.disabled)).toBe(true)
    await checkbox.setValue(true)
    expect(buttons.every(button => !button.element.disabled)).toBe(true)
    await checkbox.setValue(false)
    expect(buttons.every(button => button.element.disabled)).toBe(true)
    page.unmount()
  })

  it.each([true, false])('uses the server consent receipt during profile completion (%s)', async accepted => {
    currentUser.mockResolvedValue({ needsProfile: true, verificationConsentAccepted: accepted })
    const page = mount(CompleteProfilePage)
    await flushPromises()
    expect(page.find('input[type=checkbox]').exists()).toBe(!accepted)
    expect(page.get('button[type=submit]').element.disabled).toBe(!accepted)
    page.unmount()
  })
})
