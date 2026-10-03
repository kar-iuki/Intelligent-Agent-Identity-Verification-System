import { test, expect } from '@playwright/test'
const userId = '11111111-1111-1111-1111-111111111111'
async function virtualDevice(page, conditional = false) {
  const cdp = await page.context().newCDPSession(page)
  await cdp.send('WebAuthn.enable')
  const { authenticatorId } = await cdp.send('WebAuthn.addVirtualAuthenticator', { options:{ protocol:'ctap2', transport:'internal', hasResidentKey:true, hasUserVerification:true, isUserVerified:true, automaticPresenceSimulation:true } })
  await page.addInitScript(value => { PublicKeyCredential.isConditionalMediationAvailable = async () => value }, conditional)
  return { cdp, authenticatorId }
}
async function passwordLogin(page) {
  await page.goto('/login')
  await page.getByLabel('Email', { exact:true }).fill('agent@example.test')
  await page.getByLabel('Password', { exact:true }).fill('test-password')
  await page.getByRole('button', { name:'Sign In', exact:true }).click()
  await expect(page).toHaveURL(/agent\/dashboard/)
}
async function registerFromPopup(page) {
  await passwordLogin(page)
  await expect(page.getByRole('dialog')).toBeVisible()
  await page.getByRole('button', { name:'Set up passkey' }).click()
  await expect(page.getByText('Passkey added. Next time, sign in with one tap.')).toBeVisible()
  await expect(page.getByRole('dialog')).not.toBeVisible()
}
test.beforeEach(async ({ request }) => { await request.post('http://127.0.0.1:3101/test/reset') })

test('virtual authenticator: popup registration, explicit login, list, rename, remove, add', async ({ page }) => {
  await virtualDevice(page)
  await registerFromPopup(page)
  await page.getByRole('button', { name:'Sign Out' }).click()
  await expect(page.getByRole('button', { name:'Sign in with a passkey' })).toHaveClass(/prominent/)
  await page.getByRole('button', { name:'Sign in with a passkey' }).click()
  await expect(page).toHaveURL(/agent\/dashboard/)
  await expect(page.getByRole('dialog')).not.toBeVisible()
  await page.getByRole('link', { name:'Manage Passkeys' }).click()
  await expect(page.getByText('This device', { exact:true })).toBeVisible()
  await page.getByRole('button', { name:'Rename', exact:true }).click()
  await page.getByLabel('Passkey name').fill('My laptop')
  await page.getByRole('button', { name:'Save', exact:true }).click()
  await expect(page.getByRole('heading', { name:'My laptop' })).toBeVisible()
  await page.getByRole('button', { name:'Remove', exact:true }).click()
  await expect(page.getByRole('dialog')).toBeVisible()
  await page.getByRole('button', { name:'Remove passkey', exact:true }).click()
  await expect(page.getByText("To fully delete it, also remove it from your device's passkey or password manager.")).toBeVisible()
  await expect(page.getByText('No passkeys yet.', { exact:false })).toBeVisible()
  await page.getByRole('button', { name:'Add a passkey' }).click()
  await expect(page.getByText('Passkey added. Next time, sign in with one tap.')).toBeVisible()
})
for (const choice of ['Skip', "Don't ask again", 'Close dialog', 'Escape']) {
  test(`${choice} permanently suppresses future prompts across login and reload`, async ({ page }) => {
    await virtualDevice(page); await passwordLogin(page)
    await expect(page.getByRole('dialog')).toBeVisible()
    if (choice === 'Escape') await page.keyboard.press('Escape')
    else await page.getByRole('button', { name:choice, exact:true }).click()
    await expect(page.getByRole('dialog')).not.toBeVisible()
    expect(await page.evaluate(id => localStorage.getItem(`passkey_prompt_dismissed:${id}`), userId)).toBe('true')
    await page.reload(); await page.getByRole('button', { name:'Sign Out' }).click()
    await passwordLogin(page)
    await expect(page.getByRole('link', { name:'Manage Passkeys' })).toBeVisible()
    await expect(page.getByRole('dialog')).not.toBeVisible()
  })
}
test('new browser gets neutral fallback and variant prompt; duplicate registration is successful', async ({ page }) => {
  await virtualDevice(page); await registerFromPopup(page)
  await page.getByRole('button', { name:'Sign Out' }).click()
  await page.evaluate(id => localStorage.removeItem(`passkey_registered:${id}`), userId)
  // User cancels the native picker, as on another browser with no available key.
  await page.evaluate(() => { navigator.credentials.get = async () => { throw new DOMException('Cancelled','NotAllowedError') } })
  await page.getByRole('button', { name:'Sign in with a passkey' }).click()
  await expect(page.getByText('No passkey found on this browser.', { exact:false })).toBeVisible()
  await expect(page.getByLabel('Email', { exact:true })).toBeFocused()
  await passwordLogin(page)
  await expect(page.getByText('You have a passkey on another device.', { exact:false })).toBeVisible()
  await page.getByRole('button', { name:'Set up passkey' }).click()
  await expect(page.getByText("You're all set. A passkey is already available on this device")).toBeVisible()
  await expect(page.getByRole('dialog')).not.toBeVisible()
  await page.getByRole('link', { name:'Manage Passkeys' }).click()
  await expect(page.locator('li')).toHaveCount(1)
})
test('registration cancellation closes quietly, without permanent dismissal', async ({ page }) => {
  await virtualDevice(page); await passwordLogin(page)
  await page.evaluate(() => { navigator.credentials.create = async () => { throw new DOMException('Cancelled','NotAllowedError') } })
  await page.getByRole('button', { name:'Set up passkey' }).click()
  await expect(page.getByRole('dialog')).not.toBeVisible()
  expect(await page.evaluate(id => localStorage.getItem(`passkey_prompt_dismissed:${id}`), userId)).toBeNull()
})
test('another tab dismissal closes the open prompt', async ({ page, context }) => {
  await virtualDevice(page); await passwordLogin(page)
  await expect(page.getByRole('dialog')).toBeVisible()
  const other = await context.newPage(); await other.goto('/agent/platform')
  await other.evaluate(id => localStorage.setItem(`passkey_prompt_dismissed:${id}`, 'true'), userId)
  await expect(page.getByRole('dialog')).not.toBeVisible()
})
test('unsupported device shows no login, prompt, or management actions', async ({ page }) => {
  await page.addInitScript(() => { PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable = async () => false })
  await passwordLogin(page); await expect(page.getByRole('dialog')).not.toBeVisible()
  await page.getByRole('link', { name:'Manage Passkeys' }).click()
  await expect(page.getByRole('button', { name:'Add a passkey' })).not.toBeVisible()
  await page.goto('/login')
  await expect(page.getByRole('button', { name:'Sign in with a passkey' })).not.toBeVisible()
})
test('conditional autofill supplies mediation and transitions to a verified session', async ({ page }) => {
  await virtualDevice(page); await registerFromPopup(page)
  await page.getByRole('button', { name:'Sign Out' }).click()
  // CDP has no autofill-dropdown selection API. Simulate selecting that item,
  // while keeping the resulting native virtual-authenticator assertion real.
  await page.addInitScript(() => {
    PublicKeyCredential.isConditionalMediationAvailable = async () => true
    const get = navigator.credentials.get.bind(navigator.credentials)
    navigator.credentials.get = options => {
      window.passkeyMediation = options.mediation
      return get({ ...options, mediation:undefined })
    }
  })
  await page.reload()
  await expect(page).toHaveURL(/agent\/dashboard/)
  expect(await page.evaluate(() => window.passkeyMediation)).toBe('conditional')
  await expect(page.getByRole('dialog')).not.toBeVisible()
})
test('explicit button aborts conditional request and is usable at 320px', async ({ page }) => {
  await virtualDevice(page)
  await page.setViewportSize({ width:320, height:720 })
  await page.addInitScript(() => {
    PublicKeyCredential.isConditionalMediationAvailable = async () => true
    navigator.credentials.get = options => {
      if (options.mediation === 'conditional') return new Promise((_resolve,reject) => options.signal.addEventListener('abort', () => { window.conditionalAborted = true; reject(new DOMException('Cancelled','AbortError')) }))
      throw new DOMException('Cancelled','NotAllowedError')
    }
  })
  await page.goto('/login')
  await page.getByRole('button', { name:'Sign in with a passkey' }).click()
  await expect(page.getByText('No passkey found on this browser.', { exact:false })).toBeVisible()
  expect(await page.evaluate(() => window.conditionalAborted)).toBe(true)
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
})
