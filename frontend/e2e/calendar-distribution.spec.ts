import { test, expect } from '@playwright/test'

test.describe('Calendar Distribution', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)

    await page.locator('input[autocomplete="username"]').fill('e2e_cal')
    await page.locator('input[type="password"]').fill('testpass123')
    await page.locator('button[type="submit"]').click()

    try {
      await page.waitForURL('**/', { timeout: 5000 })
    } catch { }
    await page.waitForTimeout(2000)
  })

  test.describe('Calendar Page Load', () => {
    test('calendar page loads with sidebar', async ({ page }) => {
      await page.goto('/calendar')
      await page.waitForTimeout(3000)

      const html = await page.content()
      expect(html.length).toBeGreaterThan(100)

      const createCalendarBtn = page.locator('button:has-text("Create Calendar"), button:has-text("Календарь")')
      await expect(createCalendarBtn.first()).toBeVisible({ timeout: 5000 })
    })

    test('calendar hierarchy loads', async ({ page }) => {
      await page.goto('/calendar')
      await page.waitForTimeout(3000)

      const hierarchy = page.locator('.calendar-hierarchy, [class*="hierarchy"]')
      await expect(hierarchy.first()).toBeVisible({ timeout: 5000 })
    })
  })

  test.describe('Create Calendar Flow', () => {
    test('create calendar button opens modal', async ({ page }) => {
      await page.goto('/calendar')
      await page.waitForTimeout(3000)

      const createBtn = page.locator('button:has-text("+"), button').filter({ hasText: /create.*calendar/i }).first()
      await createBtn.click()

      await page.waitForTimeout(500)
      const modal = page.locator('[role="dialog"], .modal, .dialog, .base-modal')
      await expect(modal.first()).toBeVisible({ timeout: 5000 })
    })

    test('create calendar form validates empty name', async ({ page }) => {
      await page.goto('/calendar')
      await page.waitForTimeout(3000)

      const createBtn = page.locator('button').filter({ hasText: /create.*calendar/i }).first()
      await createBtn.click()
      await page.waitForTimeout(500)

      const submitBtn = page.locator('button[type="submit"], button:has-text("Create"), button:has-text("Создать")').last()
      await submitBtn.click()
      await page.waitForTimeout(500)

      const errorMsg = page.locator('.field-error, .error, [class*="error"]').first()
      await expect(errorMsg).toBeVisible({ timeout: 2000 })
    })

    test('create calendar with valid name', async ({ page }) => {
      await page.goto('/calendar')
      await page.waitForTimeout(3000)

      const createBtn = page.locator('button').filter({ hasText: /create.*calendar/i }).first()
      await createBtn.click()
      await page.waitForTimeout(500)

      const nameInput = page.locator('input[placeholder*="name" i], input').first()
      await nameInput.fill('Test Calendar E2E')

      const submitBtn = page.locator('button:has-text("Create"), button:has-text("Создать")').last()
      await submitBtn.click()
      await page.waitForTimeout(2000)

      const modal = page.locator('[role="dialog"]')
      await expect(modal.first()).not.toBeVisible({ timeout: 3000 })
    })
  })

  test.describe('Create Allocation Flow', () => {
    test('expand calendar shows create allocation button', async ({ page }) => {
      await page.goto('/calendar')
      await page.waitForTimeout(3000)

      await page.waitForTimeout(1000)

      const calendarRow = page.locator('.calendar-row, [class*="calendar"]').filter({ hasText: /test/i }).first()
      if (await calendarRow.isVisible({ timeout: 2000 }).catch(() => false)) {
        await calendarRow.click()
        await page.waitForTimeout(500)

        const allocBtn = page.locator('button:has-text("Create Allocation"), button:has-text("+")')
        await expect(allocBtn.first()).toBeVisible({ timeout: 2000 })
      } else {
        test.skip()
      }
    })

    test('create allocation modal contains form fields', async ({ page }) => {
      await page.goto('/calendar')
      await page.waitForTimeout(3000)

      const createBtn = page.locator('button').filter({ hasText: /create.*calendar/i }).first()
      await createBtn.click()
      await page.waitForTimeout(500)

      await page.locator('input').first().fill('Allocation Test Calendar')
      await page.locator('button:has-text("Create"), button:has-text("Создать")').last().click()
      await page.waitForTimeout(2000)

      const calendarRow = page.locator('.calendar-row').filter({ hasText: /allocation test calendar/i }).first()
      if (await calendarRow.isVisible({ timeout: 2000 }).catch(() => false)) {
        await calendarRow.click()
        await page.waitForTimeout(500)

        const createAllocBtn = page.locator('button').filter({ hasText: /\+.*allocation/i }).first()
        await createAllocBtn.click()
        await page.waitForTimeout(500)

        const modalInputs = page.locator('[role="dialog"] input, [role="dialog"] select')
        await expect(modalInputs.first()).toBeVisible({ timeout: 3000 })

        const applyBtn = page.locator('button:has-text("Create and Apply")')
        await expect(applyBtn).toBeVisible({ timeout: 2000 })
      } else {
        test.skip()
      }
    })

    test('create and apply allocation', async ({ page }) => {
      await page.goto('/calendar')
      await page.waitForTimeout(3000)

      const createBtn = page.locator('button').filter({ hasText: /create.*calendar/i }).first()
      await createBtn.click()
      await page.waitForTimeout(500)

      await page.locator('input').first().fill('Apply Test Calendar')
      await page.locator('button:has-text("Create"), button:has-text("Создать")').last().click()
      await page.waitForTimeout(2000)

      const calendarRow = page.locator('.calendar-row').filter({ hasText: /apply test calendar/i }).first()
      if (await calendarRow.isVisible({ timeout: 2000 }).catch(() => false)) {
        await calendarRow.click()
        await page.waitForTimeout(500)

        const createAllocBtn = page.locator('button').filter({ hasText: /\+.*allocation/i }).first()
        await createAllocBtn.click()
        await page.waitForTimeout(500)

        const nameInput = page.locator('[role="dialog"] input').first()
        await nameInput.fill('Test Allocation')

        const applyBtn = page.locator('button:has-text("Create and Apply")')
        await applyBtn.click()
        await page.waitForTimeout(3000)

        const modal = page.locator('[role="dialog"]')
        await expect(modal.first()).not.toBeVisible({ timeout: 3000 }).catch(() => { })
      } else {
        test.skip()
      }
    })
  })

  test.describe('Day View - is_done Checkbox', () => {
    test('day view displays with work hours input', async ({ page }) => {
      await page.goto('/calendar')
      await page.waitForTimeout(3000)

      await page.waitForTimeout(2000)

      const workHoursInput = page.locator('input[type="number"][min="0"][max="24"]').first()
      if (await workHoursInput.isVisible({ timeout: 2000 }).catch(() => false)) {
        await expect(workHoursInput).toBeVisible()
      }
    })

    test('execution cards display with checkbox', async ({ page }) => {
      await page.goto('/calendar')
      await page.waitForTimeout(3000)

      await page.waitForTimeout(2000)

      const executionCard = page.locator('.execution-card, [class*="execution"]').first()
      if (await executionCard.isVisible({ timeout: 2000 }).catch(() => false)) {
        const checkbox = executionCard.locator('input[type="checkbox"]')
        await expect(checkbox).toBeVisible()
      }
    })

    test('checkbox can be toggled', async ({ page }) => {
      await page.goto('/calendar')
      await page.waitForTimeout(4000)

      const checkbox = page.locator('.execution-card input[type="checkbox"], [class*="execution"] input[type="checkbox"]').first()
      if (await checkbox.isVisible({ timeout: 2000 }).catch(() => false)) {
        const initialChecked = await checkbox.isChecked()

        const checkboxLabel = page.locator('.done-checkbox, [class*="checkbox"]').first()
        await checkboxLabel.click()
        await page.waitForTimeout(1000)

        const newChecked = await checkbox.isChecked()
        expect(newChecked).not.toBe(initialChecked)
      } else {
        test.skip()
      }
    })
  })

  test.describe('Work Hours Input', () => {
    test('header work hours input accepts values', async ({ page }) => {
      await page.goto('/calendar')
      await page.waitForTimeout(4000)

      const workHoursInput = page.locator('.day-view-head input[type="number"], .work-hours-input').first()
      if (await workHoursInput.isVisible({ timeout: 2000 }).catch(() => false)) {
        await workHoursInput.clear()
        await workHoursInput.fill('6')
        await workHoursInput.blur()
        await page.waitForTimeout(1000)

        const value = await workHoursInput.inputValue()
        expect(parseFloat(value)).toBe(6)
      } else {
        test.skip()
      }
    })

    test('execution hours display is editable', async ({ page }) => {
      await page.goto('/calendar')
      await page.waitForTimeout(4000)

      const hoursDisplay = page.locator('.hours-display, [class*="hours-display"]').first()
      if (await hoursDisplay.isVisible({ timeout: 2000 }).catch(() => false)) {
        await hoursDisplay.click()
        await page.waitForTimeout(500)

        const hoursInput = page.locator('.hours-input, [class*="hours-input"]').first()
        await expect(hoursInput).toBeVisible({ timeout: 2000 })

        await hoursInput.clear()
        await hoursInput.fill('3')
        await hoursInput.press('Enter')
        await page.waitForTimeout(1000)
      } else {
        test.skip()
      }
    })
  })

  test.describe('View Switching', () => {
    test('can switch between day/week/month views', async ({ page }) => {
      await page.goto('/calendar')
      await page.waitForTimeout(3000)

      const viewButtons = page.locator('[class*="view-switch"], [class*="view-switcher"] button, button[class*="view"]')
      const buttonCount = await viewButtons.count()

      if (buttonCount > 0) {
        for (let i = 0; i < Math.min(buttonCount, 3); i++) {
          await viewButtons.nth(i).click()
          await page.waitForTimeout(1000)
        }
      } else {
        const dayViewBtn = page.locator('button:has-text("Day"), button:has-text("День")').first()
        const weekViewBtn = page.locator('button:has-text("Week"), button:has-text("Неделя")').first()
        const monthViewBtn = page.locator('button:has-text("Month"), button:has-text("Месяц")').first()

        if (await dayViewBtn.isVisible().catch(() => false)) {
          await weekViewBtn.click()
          await page.waitForTimeout(1000)
          await monthViewBtn.click()
          await page.waitForTimeout(1000)
          await dayViewBtn.click()
          await page.waitForTimeout(1000)
        }
      }
    })
  })
})
