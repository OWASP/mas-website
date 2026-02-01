import { test, expect } from '@playwright/test';

test.describe('MASTG Techniques Index', () => {
  test('should display "Used in" column and links (if present)', async ({ page }) => {
    await page.goto('/MASTG/techniques/');
    const usedHeader = page.locator('th:has-text("Used"), th:has-text("Used in"), th:has-text("Used In")').first();
    if ((await usedHeader.count()) === 0) test.skip();
    const usedInLink = page.locator('td a[href*="/MASTG/tests/"]').first();
    if ((await usedInLink.count()) > 0) {
      await expect(usedInLink).toBeVisible();
      await usedInLink.click();
      await expect(page).toHaveURL(/MASTG\/tests/);
    } else {
      test.skip();
    }
  });

  test('should filter by platform and "Show Unused"', async ({ page }) => {
    await page.goto('/MASTG/techniques/');
    const iosCheckbox = page.locator('label:has-text("iOS") input').first();
    await iosCheckbox.check();
    await expect(page).toHaveURL(/ios/);
    const unusedCheckbox = page.locator('label:has-text("Show Unused") input').first();
    await unusedCheckbox.check();
    await expect(page).toHaveURL(/unused/);
  });
});
