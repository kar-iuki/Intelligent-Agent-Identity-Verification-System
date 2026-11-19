import { test, expect } from '@playwright/test'

for (const viewport of [{ width:1440, height:1000 }, { width:390, height:844 }, { width:320, height:740 }]) {
  test(`landing page navigation and verification preview at ${viewport.width}px`, async ({ page }) => {
    await page.setViewportSize(viewport)
    const errors = []
    page.on('pageerror', error => errors.push(error.message))
    await page.goto('/')
    await expect(page.getByRole('heading', { level:1 })).toContainText('Your identity,')
    await expect(page.locator('.auth-shell')).toHaveCount(0)
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
    for (const [name, capture] of [['Passport','Open to the photo page'], ['Driver’s licence','Capture the front'], ['National ID','Capture both sides']]) {
      const choice = page.getByRole('button', { name, exact:true })
      await choice.click()
      await expect(choice).toHaveAttribute('aria-pressed','true')
      await expect(page.locator('.capture-copy')).toContainText(capture)
      await expect(page.locator('.document-stage img')).toHaveJSProperty('complete',true)
      expect(await page.locator('.document-stage img').evaluate(img => img.naturalWidth)).toBeGreaterThan(0)
    }
    await page.getByRole('button', { name:'Guided', exact:true }).click()
    await page.getByRole('button', { name:'Try blurry photo' }).click()
    await page.getByRole('button', { name:'Check sample' }).click()
    await expect(page.getByRole('heading', { name:'The print is blurred' })).toBeVisible()
    await page.getByRole('button', { name:'Retake photo' }).click()
    await page.getByRole('button', { name:'Capture sample' }).click()
    await page.getByRole('button', { name:'Check sample' }).click()
    await expect(page.getByRole('heading', { name:'Your sample is readable' })).toBeVisible()
    await page.getByRole('button', { name:'Selfie', exact:true }).click()
    await expect(page.getByRole('heading', { name:'Take a live selfie' })).toBeVisible()
    await expect(page.getByRole('button', { name:'Play verification preview' })).toBeVisible()
    await page.getByRole('button', { name:'Review', exact:true }).click()
    await expect(page.getByRole('heading', { name:'Check your result' })).toBeVisible()
    await page.locator('summary').filter({ hasText:'Which identity documents' }).click()
    await expect(page.locator('details[open]')).toContainText('Which identity documents')
    for (const section of ['#guide', '#how-it-works', '#questions']) {
      const heading = page.locator(section).getByRole('heading').first()
      await heading.scrollIntoViewIfNeeded()
      await expect(heading).toBeInViewport()
    }
    if (viewport.width < 800) {
      await page.getByRole('button', { name:'Open navigation' }).click()
      await expect(page.getByRole('navigation', { name:'Mobile navigation' })).toBeVisible()
      await page.keyboard.press('Escape')
      await expect(page.getByRole('navigation', { name:'Mobile navigation' })).toHaveCount(0)
    }
    await page.evaluate(() => window.scrollTo(0, 0))
    await page.screenshot({ path:`test-results/landing-${viewport.width}.png`, fullPage:true })
    await expect(page.locator('.hero-actions a').first()).toHaveAttribute('href','/register')
    await page.locator('.hero-actions a').first().click()
    await expect(page).toHaveURL(/\/register$/)
    await page.goto('/')
    await page.locator('.site-footer a[href="/login"]').click()
    await expect(page).toHaveURL(/\/login$/)
    expect(errors).toEqual([])
  })
}

test('reduced motion and authentication callback routes are preserved', async ({ page }) => {
  await page.emulateMedia({ reducedMotion:'reduce' })
  await page.goto('/')
  await expect(page.getByRole('button', { name:'Play verification preview' })).toBeVisible()
  await expect(page.getByRole('button', { name:'Document', exact:true })).toHaveAttribute('aria-pressed','true')
  await page.clock.install()
  await page.clock.fastForward(6000)
  await expect(page.getByRole('heading', { name:'Capture your photo ID' })).toBeVisible()
  // Intercept session processing; this check concerns root routing only.
  await page.route('**/api/**', route => route.fulfill({ status:400, json:{ error:'Test callback' } }))
  await page.goto('/?error=access_denied')
  await expect(page).toHaveURL(/\/login/)
  await page.goto('/#access_token=test-token&type=recovery')
  await expect(page).toHaveURL(/\/reset-password/)
})
