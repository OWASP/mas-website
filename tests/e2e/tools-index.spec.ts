import { test, expect } from '@playwright/test';

test.describe('MASTG Tools Index', () => {
  test('should have Status column', async ({ page }) => {
    await page.goto('/MASTG/tools/');
    const statusHeader = page.locator('th:has-text("Status")').first();
    await expect(statusHeader).toBeVisible();
  });

  test('should filter by platform', async ({ page }) => {
    await page.goto('/MASTG/tools/');
    const androidCheckbox = page.locator('label:has-text("Android") input').first();
    await androidCheckbox.check();
    await expect(page).toHaveURL(/android/);
    await expect(androidCheckbox).toBeChecked();
  });

  test('should filter by status (Show Deprecated)', async ({ page }) => {
    await page.goto('/MASTG/tools/');
    const deprecatedCheckbox = page.locator('label:has-text("Show Deprecated") input').first();
    await deprecatedCheckbox.check();
    await expect(page).toHaveURL(/deprecated/);
    await expect(deprecatedCheckbox).toBeChecked();
  });

  test('should filter by "Hide Unused"', async ({ page }) => {
    await page.goto('/MASTG/tools/');
    const unusedCheckbox = page.locator('label:has-text("Hide Unused") input').first();
    await unusedCheckbox.check();
    await expect(page).toHaveURL(/hideunused/);
    await expect(unusedCheckbox).toBeChecked();
  });

  test('should combine filters and search', async ({ page }) => {
    await page.goto('/MASTG/tools/');
    const iosCheckbox = page.locator('label:has-text("iOS") input').first();
    await iosCheckbox.check();
    const searchInput = page.locator('input[id*="search"]').last();
    await searchInput.fill('frida');
    await searchInput.dispatchEvent('keyup');
    await expect(page).toHaveURL(/ios/);
    await expect(page).toHaveURL(/q:frida/);
  });

  test('should clear all filters', async ({ page }) => {
    await page.goto('/MASTG/tools/#android;deprecated');
    const clearButton = page.locator('button:has-text("Clear All Filters")');
    await clearButton.click();
    await expect(page).toHaveURL(/^[^#]*#?$/); // URL should not have hash parameters
  });
});
