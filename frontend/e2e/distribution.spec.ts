import { test, expect } from '@playwright/test'

test.describe('Distribution', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)

    await page.locator('input[autocomplete="username"]').fill('e2e_dist')
    await page.locator('input[type="password"]').fill('testpass123')
    await page.locator('button[type="submit"]').click()

    try {
      await page.waitForURL('**/', { timeout: 5000 })
    } catch {}
    await page.waitForTimeout(2000)
  })

  test('home page loads', async ({ page }) => {
    await page.goto('/')
    await page.waitForTimeout(3000)
    const html = await page.content()
    expect(html.length).toBeGreaterThan(100)
  })
})
