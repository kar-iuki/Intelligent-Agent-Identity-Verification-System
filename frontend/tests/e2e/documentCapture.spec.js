import { test, expect } from '@playwright/test'

async function setupCapture(page, cameraOnly) {
  const user = { user_id:'11111111-1111-1111-1111-111111111111', email:'agent@example.test', role:'agent', profile_complete:true }
  const agent = { agent_id:'test-agent', full_name:'Test Agent', user_id:user.user_id }
  await page.route('**/api/auth/me', route => route.fulfill({ json:{ token:'test-token', user, agent, role:'agent', profileComplete:true } }))
  await page.route('**/api/auth/passkeys', route => route.fulfill({ json:{ passkeys:[] } }))
  await page.route('**/api/agent/profile', route => route.fulfill({ json:{ email:user.email, agent } }))
  await page.route('**/api/agent/registration/status', route => route.fulfill({ json:{ status:'documents_submitted', documentCameraRequired:cameraOnly } }))
  await page.route('**/api/agent/documents/quality-check', route => route.fulfill({ json:{ passed:true } }))
  // Keep layout/capture tests independent of GPU and remote model availability.
  await page.route('**/@mediapipe_tasks-vision.js*', route => route.fulfill({ contentType:'text/javascript', body:`
    export const FilesetResolver = { forVisionTasks: async () => ({}) };
    export class FaceLandmarker {
      static async createFromOptions() { return new FaceLandmarker(); }
      detectForVideo() { return { faceLandmarks:[] }; }
      close() {}
    }
    export class DrawingUtils { drawConnectors() {} }
  ` }))
  await page.addInitScript(() => {
    localStorage.setItem('auth_token', 'test-token')
    localStorage.setItem('auth_role', 'agent')
    localStorage.setItem('auth_user', JSON.stringify({ user_id:'11111111-1111-1111-1111-111111111111', email:'agent@example.test', profile_complete:true }))
    navigator.mediaDevices.getUserMedia = async () => {
      const canvas = document.createElement('canvas')
      canvas.width = 720; canvas.height = 1280
      const ctx = canvas.getContext('2d')
      ctx.fillStyle = '#627d98'; ctx.fillRect(0, 0, 720, 1280)
      const stream = canvas.captureStream(10)
      // Emit a frame after the video has attached to the stream.
      setTimeout(() => ctx.fillRect(0, 0, 720, 1280), 100)
      return stream
    }
  })
  await page.goto('/agent/dashboard')
  await expect(page).toHaveURL(/agent\/dashboard/)
}

async function checkFrame(page, selector, buttonName) {
  const frame = page.locator(selector)
  await expect(frame).toBeVisible()
  await expect.poll(async () => frame.evaluate(el => el.querySelector('video').videoHeight)).toBe(1280)
  const bounds = await frame.boundingBox()
  expect(bounds.height).toBeLessThanOrEqual(page.viewportSize().height * 0.32 + 1)
  expect(Math.abs(bounds.width / bounds.height - 720 / 1280)).toBeLessThan(0.01)
  await expect(page.getByRole('button', { name:buttonName, exact:true })).toBeInViewport()
  await expect(page.locator('.title')).toBeInViewport()
}

for (const viewport of [{ width:390, height:844 }, { width:360, height:640 }, { width:1366, height:768 }]) {
  test(`retry capture keeps portrait preview, instructions and controls visible at ${viewport.width}x${viewport.height}`, async ({ page }) => {
    await page.setViewportSize(viewport)
    await setupCapture(page, true)
    await page.getByRole('button', { name:/National ID/ }).click()
    await expect(page.getByRole('button', { name:'Upload file', exact:true })).toHaveCount(0)
    await checkFrame(page, '.media-frame', 'Capture')
    await page.getByRole('button', { name:'Capture', exact:true }).click()
    // Smaller preview must not reduce the submitted photograph's resolution.
    expect(await page.locator('canvas.hidden').evaluate(el => [el.width, el.height])).toEqual([720, 1280])
    await page.getByRole('button', { name:'Check quality & continue' }).click()
    await expect(page.getByRole('heading', { name:'ID back' })).toBeVisible()
    await checkFrame(page, '.media-frame', 'Capture')
    await page.getByRole('button', { name:'Capture', exact:true }).click()
    await page.getByRole('button', { name:'Check quality & continue' }).click()
    await expect(page.getByRole('heading', { name:'Live selfie check' })).toBeVisible()
    await checkFrame(page, '.stage', 'Take photo')
    await expect(page.locator('.challenge-banner')).toBeInViewport()
    await page.screenshot({ path:`test-results/capture-${viewport.width}.png` })
  })
}

test('a refreshed retry still excludes uploads for passport and driving licence', async ({ page }) => {
  await setupCapture(page, true)
  await page.reload()
  for (const name of ['Passport', "Driver's licence"]) {
    await page.getByRole('button', { name:new RegExp(name) }).click()
    await expect(page.getByRole('button', { name:'Upload file', exact:true })).toHaveCount(0)
    await expect(page.locator('input[type="file"]')).toHaveCount(0)
    await page.getByRole('button', { name:'Back', exact:true }).click()
  }
})

test('first attempt still offers the file picker', async ({ page }) => {
  await setupCapture(page, false)
  await page.getByRole('button', { name:/Passport/ }).click()
  await page.getByRole('button', { name:'Upload file', exact:true }).click()
  await expect(page.locator('input[type="file"]')).toHaveCount(1)
})
