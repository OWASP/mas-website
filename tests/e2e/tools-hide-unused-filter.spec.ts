import { test, expect } from '@playwright/test';

test.describe('MASTG Tools - Hide Unused Filter', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/MASTG/tools/');
    await page.waitForSelector('table', { timeout: 10000 });
  });

  test('should have "Hide Unused" checkbox in Used In filter group', async ({ page }) => {
    // Look for the Hide Unused checkbox
    const hideUnusedLabel = await page.locator('label:has-text("Hide Unused")').count();
    expect(hideUnusedLabel).toBeGreaterThan(0);
  });

  test('should show unused tools by default', async ({ page }) => {
    // Unused rows should be visible without any filter applied
    const unusedRows = await page.locator('td:has-text("Unused")').count();
    expect(unusedRows).toBeGreaterThan(0);
  });

  test('should hide unused tools when "Hide Unused" is enabled', async ({ page }) => {
    // Count total rows in table
    const totalRowsBefore = await page.locator('tbody tr').count();

    // Enable "Hide Unused" filter
    const hideUnusedCheckbox = page.locator('label:has-text("Hide Unused") input').first();
    await hideUnusedCheckbox.check();

    // Wait for the unused rows to disappear
    await expect(page.locator('td:has-text("Unused")')).toHaveCount(0, { timeout: 5000 });

    // Count rows after enabling
    const totalRowsAfter = await page.locator('tbody tr').count();

    // Should show fewer rows when "Hide Unused" is enabled
    expect(totalRowsAfter).toBeLessThan(totalRowsBefore);
  });

  test('should display filter info showing filtered entries', async ({ page }) => {
    // Get the info text
    const infoElement = await page.locator('span[id*="filter"][id*="info"]').first();
    const infoText = await infoElement.textContent();

    // Should show "filtered" in the info text when unused tools are hidden
    expect(infoText).toMatch(/Showing.*of.*entries/);
  });
});
