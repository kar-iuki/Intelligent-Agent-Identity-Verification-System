import { test, expect } from '@playwright/test'

for (const viewport of [{ width:1440, height:1000 }, { width:390, height:844 }, { width:320, height:740 }]) {
  test(`landing page navigation and illustration at ${viewport.width}px`, async ({ page }) => {
    await page.setViewportSize(viewport)
    const errors = []
    page.on('pageerror', error => errors.push(error.message))
    await page.goto('/')
    await expect(page.getByRole('heading', { level:1 })).toContainText('Trust starts')
    await expect(page.locator('.auth-shell')).toHaveCount(0)
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
    await page.getByRole('button', { name:'02Selfie' }).click()
    await expect(page.locator('.floating-badge')).toContainText('A moment of movement')
    await expect(page.getByRole('button', { name:'Play illustration animation' })).toBeVisible()
    await page.getByRole('button', { name:'03Review' }).click()
    await expect(page.locator('.floating-badge')).toContainText('Clarity on what’s next')
    await page.locator('summary').filter({ hasText:'Which identity documents' }).click()
    await expect(page.locator('details[open]')).toContainText(['What do I need', 'Which identity documents'])
    for (const section of ['#how-it-works', '#why-verity', '#questions', '.cta-section']) {
      await page.locator(section).scrollIntoViewIfNeeded()
      await expect(page.locator(section).locator('.reveal').first().or(page.locator(section + '.reveal'))).toHaveCSS('opacity','1')
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
  await expect(page.getByRole('button', { name:'Play illustration animation' })).toBeVisible()
  await expect(page.locator('.identity-card')).toHaveCSS('animation-name','none')
  // Intercept session processing; this check concerns root routing only.
  await page.route('**/api/**', route => route.fulfill({ status:400, json:{ error:'Test callback' } }))
  await page.goto('/?error=access_denied')
  await expect(page).toHaveURL(/\/login/)
  await page.goto('/#access_token=test-token&type=recovery')
  await expect(page).toHaveURL(/\/reset-password/)
})
