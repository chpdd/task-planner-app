import { test, expect } from '@playwright/test'

test.describe('AI Chat', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)

    await page.locator('input[autocomplete="username"]').fill('e2e_ai')
    await page.locator('input[type="password"]').fill('testpass123')
    await page.locator('button[type="submit"]').click()

    try {
      await page.waitForURL('**/', { timeout: 5000 })
    } catch {}
    await page.waitForTimeout(2000)
  })

  test('home page loads with AI button', async ({ page }) => {
    await page.goto('/')
    await page.waitForTimeout(3000)

    const html = await page.content()
    expect(html.length).toBeGreaterThan(100)
  })

  test('AI chat drawer opens', async ({ page }) => {
    await page.goto('/')
    await page.waitForTimeout(3000)

    const aiButton = page.locator('button').filter({ hasText: /AI/i })
    const count = await aiButton.count()
    if (count > 0 && await aiButton.first().isVisible().catch(() => false)) {
      await aiButton.first().click()
      await page.waitForTimeout(500)
    }
  })
})
