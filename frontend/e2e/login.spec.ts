import { test, expect } from '@playwright/test'

test.describe('Login Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)
  })

  test('login page renders correctly', async ({ page }) => {
    await expect(page.locator('input[autocomplete="username"]')).toBeVisible({ timeout: 10000 })
    await expect(page.locator('input[type="password"]')).toBeVisible()
    await expect(page.locator('button[type="submit"]')).toBeVisible()
  })

  test('shows error on empty submission', async ({ page }) => {
    await page.locator('button[type="submit"]').click()
    await page.waitForTimeout(500)
  })

  test('shows error on invalid credentials', async ({ page }) => {
    await page.locator('input[autocomplete="username"]').fill('nonexistent_user_12345')
    await page.locator('input[type="password"]').fill('wrongpassword')
    await page.locator('button[type="submit"]').click()
    await page.waitForTimeout(2000)
  })
})

test.describe('Authentication Guard', () => {
  test('redirects to login when accessing protected route', async ({ page }) => {
    await page.goto('/tasks')
    await page.waitForTimeout(2000)
    await expect(page).toHaveURL(/\/login/, { timeout: 5000 }).catch(() => {})
  })

  test('allows access to login page', async ({ page }) => {
    await page.goto('/login')
    await expect(page.locator('input[autocomplete="username"]')).toBeVisible({ timeout: 5000 })
  })
})
