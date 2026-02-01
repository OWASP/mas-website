import { test, expect } from '@playwright/test';

test.describe('MASWE Index Filters', () => {
  test('should filter by platform', async ({ page }) => {
    await page.goto('/MASWE/');
    const androidCheckbox = page.locator('label:has-text("Android") input').first();
    await androidCheckbox.check();
    await expect(page).toHaveURL(/android/);
    await expect(androidCheckbox).toBeChecked();
  });

  test('should filter by profile (L1, L2, R, P)', async ({ page }) => {
    await page.goto('/MASWE/');
    const l1Checkbox = page.locator('label:has-text("L1") input').first();
    await l1Checkbox.check();
    await expect(page).toHaveURL(/l1/);
    await expect(l1Checkbox).toBeChecked();
  });

  test('should filter by status (Show Deprecated)', async ({ page }) => {
    await page.goto('/MASWE/');
    const deprecatedCheckbox = page.locator('label:has-text("Show Deprecated") input').first();
    await deprecatedCheckbox.check();
    await expect(page).toHaveURL(/deprecated/);
    await expect(deprecatedCheckbox).toBeChecked();
  });

  test('should support URL hash bookmarking for filters', async ({ page }) => {
    await page.goto('/MASWE/#android;l1;deprecated');
    await expect(page.locator('label:has-text("Android") input')).toBeChecked();
    await expect(page.locator('label:has-text("L1") input')).toBeChecked();
    await expect(page.locator('label:has-text("Show Deprecated") input')).toBeChecked();
  });
});
