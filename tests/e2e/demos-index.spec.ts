import { test, expect } from '@playwright/test';

test.describe('MASTG Demos Index', () => {
  test('should filter by platform', async ({ page }) => {
    await page.goto('/MASTG/demos/');
    const androidCheckbox = page.locator('label:has-text("Android") input').first();
    await androidCheckbox.check();
    await expect(page).toHaveURL(/android/);
    await expect(androidCheckbox).toBeChecked();
  });

  test('should filter by status (Show Deprecated)', async ({ page }) => {
    await page.goto('/MASTG/demos/');
    const deprecatedCheckbox = page.locator('label:has-text("Show Deprecated") input').first();
    await deprecatedCheckbox.check();
    await expect(page).toHaveURL(/deprecated/);
    await expect(deprecatedCheckbox).toBeChecked();
  });
});
