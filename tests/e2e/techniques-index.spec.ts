import { test, expect } from '@playwright/test';

test.describe('MASTG Techniques Index', () => {
  test('should not auto-add #hideunused to URL on page load', async ({ page }) => {
    await page.goto('/MASTG/techniques/');
    await page.waitForLoadState('networkidle');
    // Wait a bit to ensure any JavaScript URL manipulation has occurred
    await page.waitForTimeout(500);
    // Check that URL doesn't contain #hideunused
    const url = page.url();
    expect(url).not.toContain('#hideunused');
    expect(url).not.toContain('hideunused');
  });

  test('should have Status column', async ({ page }) => {
    await page.goto('/MASTG/techniques/');
    const statusHeader = page.locator('th:has-text("Status")').first();
    await expect(statusHeader).toBeVisible();
  });

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

  test('should filter by platform and "Hide Unused"', async ({ page }) => {
    await page.goto('/MASTG/techniques/');
    const iosCheckbox = page.locator('label:has-text("iOS") input').first();
    await iosCheckbox.check();
    await expect(page).toHaveURL(/ios/);
    const unusedCheckbox = page.locator('label:has-text("Hide Unused") input').first();
    await unusedCheckbox.check();
    await expect(page).toHaveURL(/hideunused/);
  });

  test('should filter by status (Show Deprecated)', async ({ page }) => {
    await page.goto('/MASTG/techniques/');
    const deprecatedCheckbox = page.locator('label:has-text("Show Deprecated") input').first();
    await deprecatedCheckbox.check();
    await expect(page).toHaveURL(/deprecated/);
    await expect(deprecatedCheckbox).toBeChecked();
  });

  test('should clear all filters', async ({ page }) => {
    await page.goto('/MASTG/techniques/#android;deprecated;hideunused');
    const clearButton = page.locator('button:has-text("Clear All Filters")');
    await clearButton.click();
    await expect(page).toHaveURL(/^[^#]*#?$/); // URL should not have hash parameters
  });
});
