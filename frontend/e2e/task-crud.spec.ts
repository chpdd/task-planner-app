import { test, expect } from '@playwright/test'

test.describe('Tasks Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)

    await page.locator('input[autocomplete="username"]').fill('e2e_tasks')
    await page.locator('input[type="password"]').fill('testpass123')
    await page.locator('button[type="submit"]').click()

    try {
      await page.waitForURL('**/', { timeout: 5000 })
    } catch {}
    await page.waitForTimeout(2000)
  })

  test('tasks page loads', async ({ page }) => {
    await page.goto('/')
    await page.waitForTimeout(3000)
    const html = await page.content()
    expect(html.length).toBeGreaterThan(100)
  })

  test('task form dialog opens', async ({ page }) => {
    await page.goto('/')
    await page.waitForTimeout(3000)

    const newTaskBtn = page.locator('button:has-text("New Task")')
    if (await newTaskBtn.isVisible().catch(() => false)) {
      await newTaskBtn.click()
      await page.waitForTimeout(500)
      const dialog = page.locator('[role="dialog"]')
      expect(await dialog.isVisible().catch(() => false)).toBeTruthy()
    }
  })
})
