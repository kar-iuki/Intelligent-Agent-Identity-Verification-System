import { test, expect } from '@playwright/test'

const states = ['verified', 'review', 'rejected', 'pending']
async function mockApp(page, theme) {
  await page.addInitScript(theme => {
    localStorage.setItem('verity-theme', theme)
    const role = location.pathname.startsWith('/admin') ? 'admin' : location.pathname.startsWith('/agent') ? 'agent' : null
    if (role) {
      localStorage.setItem('auth_token', 'test-token')
      localStorage.setItem('auth_role', role)
      localStorage.setItem('auth_user', JSON.stringify({ user_id:'theme-test', email:'preview@example.test', role }))
    } else {
      for (const key of ['auth_token','auth_role','auth_user','auth_agent']) localStorage.removeItem(key)
    }
  }, theme)
  await page.route('**/api/**', async route => {
    const path = new URL(route.request().url()).pathname
    let json = {}
    if (path === '/api/admin/agents') json = { agents:states.map((status, i) => ({ status, agent:{ agent_id:String(i), full_name:['Verified Agent','Review Agent','Rejected Agent','Pending Agent'][i], national_id:`TEST-${i}`, created_at:'2026-10-30' } })) }
    if (path === '/api/admin/stats') json = { totalAgents:4, awaitingReview:1, verifiedToday:1, rejectedToday:1, pendingVerification:1 }
    if (path === '/api/admin/model/status') json = { modelLoaded:true }
    if (path === '/api/agent/audit') json = { logs:['SUCCESS','REVIEW','BLOCKED','PENDING'].map((outcome,i) => ({ logId:String(i), action:'VERIFICATION_INITIATED', outcome, timestamp:'2026-10-30' })) }
    if (path === '/api/auth/captcha') json = { captchaId:'test-captcha', svg:'<svg xmlns="http://www.w3.org/2000/svg" />' }
    await route.fulfill({ json })
  })
}
async function contrast(locator) {
  return locator.evaluate(el => {
    const rgb = value => value.match(/[\d.]+/g).slice(0,3).map(Number)
    const luminance = channels => channels.map(x => x / 255).map(x => x <= .04045 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4).reduce((sum, x, i) => sum + x * [.2126,.7152,.0722][i], 0)
    const style = getComputedStyle(el)
    const a = luminance(rgb(style.color)), b = luminance(rgb(style.backgroundColor))
    return (Math.max(a,b) + .05) / (Math.min(a,b) + .05)
  })
}
for (const theme of ['light','dark']) {
  test(`${theme}: consistent admin and audit statuses with readable contrast`, async ({ page }) => {
    await mockApp(page, theme)
    await page.goto('/admin/dashboard')
    await expect(page.locator('tbody .badge')).toHaveCount(4)
    const colors = {}
    for (const state of states) {
      const badge = page.locator(`.badge.${state}`).first()
      colors[state] = await badge.evaluate(el => getComputedStyle(el).color)
      expect(await contrast(badge)).toBeGreaterThanOrEqual(4.5)
    }
    expect(colors.pending).toEqual(colors.review)
    expect(new Set([colors.verified,colors.review,colors.rejected]).size).toBe(3)
    await expect(page.locator('.stat-icon.grey')).toHaveCSS('color', colors.pending)
    await expect(page.locator('.stat-icon.green')).toHaveCSS('color', colors.verified)
    await expect(page.locator('.stat-icon.red')).toHaveCSS('color', colors.rejected)
    await page.screenshot({ path:`test-results/colours-admin-${theme}.png`, fullPage:true })
    await page.goto('/agent/audit')
    await expect(page.locator('.badge')).toHaveCount(4)
    for (const [outcome,state] of [['SUCCESS','verified'],['REVIEW','review'],['BLOCKED','rejected'],['PENDING','pending']]) {
      const badge = page.locator('.badge').filter({ hasText:outcome })
      await expect(badge).toHaveCSS('color', colors[state])
      expect(await contrast(badge)).toBeGreaterThanOrEqual(4.5)
    }
    await page.setViewportSize({ width:390, height:844 })
    await page.goto('/login')
    await expect(page.getByRole('heading',{ name:'Sign in to your workspace' })).toBeVisible()
    expect(await contrast(page.locator('.btn-primary'))).toBeGreaterThanOrEqual(4.5)
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
    await page.screenshot({ path:`test-results/colours-login-${theme}.png`, fullPage:true })
  })
}
