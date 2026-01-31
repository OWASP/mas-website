import { test, expect } from '@playwright/test';

test.describe('Basic Site Functionality', () => {
  test('should load the tools page', async ({ page }) => {
    await page.goto('/MASTG/tools/');
    await expect(page).toHaveTitle(/Testing Tools/);
  });

  test('should have a table on tools page', async ({ page }) => {
    await page.goto('/MASTG/tools/');
    await page.waitForSelector('table', { timeout: 10000 });
    const table = await page.locator('table').first();
    await expect(table).toBeVisible();
  });
});
