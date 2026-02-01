import { test, expect } from '@playwright/test';

test.describe('MASTG Tests Index', () => {
  test('should filter by platform', async ({ page }) => {
    await page.goto('/MASTG/tests/');
    const iosCheckbox = page.locator('label:has-text("iOS") input').first();
    await iosCheckbox.check();
    await expect(page).toHaveURL(/ios/);
    await expect(iosCheckbox).toBeChecked();
  });

  test('should filter by profile (L1, L2, R, P)', async ({ page }) => {
    await page.goto('/MASTG/tests/');
    const l2Checkbox = page.locator('label:has-text("L2") input').first();
    await l2Checkbox.check();
    await expect(page).toHaveURL(/l2/);
    await expect(l2Checkbox).toBeChecked();
  });

  test('should filter by status (Show Deprecated)', async ({ page }) => {
    await page.goto('/MASTG/tests/');
    const deprecatedCheckbox = page.locator('label:has-text("Show Deprecated") input').first();
    await deprecatedCheckbox.check();
    await expect(page).toHaveURL(/deprecated/);
    await expect(deprecatedCheckbox).toBeChecked();
  });

  test('should combine filters and search', async ({ page }) => {
    await page.goto('/MASTG/tests/');
    const iosCheckbox = page.locator('label:has-text("iOS") input').first();
    await iosCheckbox.check();
    const searchInput = page.locator('input[id*="search"]').last();
    await searchInput.fill('crypto');
    await searchInput.dispatchEvent('keyup');
    await expect(page).toHaveURL(/ios/);
    await expect(page).toHaveURL(/q:crypto/);
  });
});
