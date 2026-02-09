import { test, expect } from '@playwright/test';

test.describe('MASTG Apps Index', () => {
  test('should have Status column', async ({ page }) => {
    await page.goto('/MASTG/apps/');
    const statusHeader = page.locator('th:has-text("Status")').first();
    await expect(statusHeader).toBeVisible();
  });

  test('should filter by platform', async ({ page }) => {
    await page.goto('/MASTG/apps/');
    const androidCheckbox = page.locator('label:has-text("Android") input').first();
    if ((await androidCheckbox.count()) > 0) {
      await androidCheckbox.check();
      await expect(page).toHaveURL(/android/);
      await expect(androidCheckbox).toBeChecked();
    }
  });

  test('should filter by status (Show Deprecated)', async ({ page }) => {
    await page.goto('/MASTG/apps/');
    const deprecatedCheckbox = page.locator('label:has-text("Show Deprecated") input').first();
    await deprecatedCheckbox.check();
    await expect(page).toHaveURL(/deprecated/);
    await expect(deprecatedCheckbox).toBeChecked();
  });

  test('should search for apps', async ({ page }) => {
    await page.goto('/MASTG/apps/');
    const searchInput = page.locator('input[id*="search"]').last();
    await searchInput.fill('test');
    await searchInput.dispatchEvent('keyup');
    await expect(page).toHaveURL(/q:test/);
  });

  test('should clear all filters', async ({ page }) => {
    await page.goto('/MASTG/apps/#android;deprecated');
    const clearButton = page.locator('button:has-text("Clear All Filters")');
    await clearButton.click();
    await expect(page).toHaveURL(/^[^#]*#?$/); // URL should not have hash parameters
  });
});
