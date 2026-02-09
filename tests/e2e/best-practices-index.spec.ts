import { test, expect } from '@playwright/test';

test.describe('MASTG Best Practices Index', () => {
  test('should have Status column', async ({ page }) => {
    await page.goto('/MASTG/best-practices/');
    const statusHeader = page.locator('th:has-text("Status")').first();
    await expect(statusHeader).toBeVisible();
  });

  test('should filter by platform', async ({ page }) => {
    await page.goto('/MASTG/best-practices/');
    const androidCheckbox = page.locator('label:has-text("Android") input').first();
    if ((await androidCheckbox.count()) > 0) {
      await androidCheckbox.check();
      await expect(page).toHaveURL(/android/);
      await expect(androidCheckbox).toBeChecked();
    }
  });

  test('should filter by status (Show Deprecated)', async ({ page }) => {
    await page.goto('/MASTG/best-practices/');
    const deprecatedCheckbox = page.locator('label:has-text("Show Deprecated") input').first();
    await deprecatedCheckbox.check();
    await expect(page).toHaveURL(/deprecated/);
    await expect(deprecatedCheckbox).toBeChecked();
  });

  test('should search for best practices', async ({ page }) => {
    await page.goto('/MASTG/best-practices/');
    const searchInput = page.locator('input[id*="search"]').last();
    await searchInput.fill('security');
    await searchInput.dispatchEvent('keyup');
    await expect(page).toHaveURL(/q:security/);
  });

  test('should combine filters', async ({ page }) => {
    await page.goto('/MASTG/best-practices/');
    const iosCheckbox = page.locator('label:has-text("iOS") input').first();
    if ((await iosCheckbox.count()) > 0) {
      await iosCheckbox.check();
      const searchInput = page.locator('input[id*="search"]').last();
      await searchInput.fill('data');
      await searchInput.dispatchEvent('keyup');
      await expect(page).toHaveURL(/ios/);
      await expect(page).toHaveURL(/q:data/);
    }
  });

  test('should clear all filters', async ({ page }) => {
    await page.goto('/MASTG/best-practices/#android;deprecated');
    const clearButton = page.locator('button:has-text("Clear All Filters")');
    await clearButton.click();
    await expect(page).toHaveURL(/^[^#]*#?$/); // URL should not have hash parameters
  });
});
