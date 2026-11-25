import { flushPromises, mount } from '@vue/test-utils'
import { expect, it, vi } from 'vitest'
import AgentDashboard from '../../src/views/AgentDashboard.vue'

const getStatus = vi.hoisted(() => vi.fn())
vi.mock('vue-router', () => ({ useRouter: () => ({ push: vi.fn() }) }))
vi.mock('../../src/stores/authStore.js', () => ({
  useAuthStore: () => ({ state: {}, fetchCurrentUser: async () => ({}) }),
}))
vi.mock('../../src/services/agentService.js', () => ({
  getRegistrationStatus: async () => ({ status: 'verification_pending' }),
  getProfile: async () => ({}),
}))
vi.mock('../../src/services/verificationService.js', () => ({ getVerificationStatus: getStatus }))

it('shows the admin approval when an open review is resolved', async () => {
  vi.useFakeTimers({ toFake: ['setInterval', 'clearInterval'] })
  getStatus.mockResolvedValueOnce({ status: 'review', isFinal: true, decision: { finalDecision: 'review' } })
  getStatus.mockResolvedValue({ status: 'verified', isFinal: true, decision: {
    finalDecision: 'verified', automatedDecision: 'review', adminReviewedAt: '2026-11-24T07:00:00Z',
  } })
  const page = mount(AgentDashboard, { shallow: true })
  try {
    await flushPromises()
    expect(page.text()).toContain('Your verification is under review')
    await vi.advanceTimersByTimeAsync(5000)
    await flushPromises()
    expect(page.text()).toContain('Approved by admin')
    expect(page.text()).toContain('Proceed to Platform')
  } finally {
    page.unmount()
    vi.useRealTimers()
  }
})
