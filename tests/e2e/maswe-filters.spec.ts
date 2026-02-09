import { test, expect } from '@playwright/test';

test.describe('MASWE Index Filters', () => {
  test('should have MASVS v2 ID column with styled category chips', async ({ page }) => {
    await page.goto('/MASWE/');
    const masvsCategoryHeader = page.locator('th:has-text("MASVS v2 ID")').first();
    await expect(masvsCategoryHeader).toBeVisible();
    
    // Check that MASVS v2 ID cells have category chips with full control IDs inside
    const categoryChip = page.locator('td span.md-tag:has-text("MASVS-")').first();
    if ((await categoryChip.count()) > 0) {
      await expect(categoryChip).toBeVisible();
      const chipText = await categoryChip.textContent();
      // Should contain full control ID (e.g., "MASVS-STORAGE-1", "MASVS-CRYPTO-2")
      expect(chipText).toMatch(/MASVS-\w+-\d+/);
      
      // Verify white text color
      const color = await categoryChip.evaluate(el => window.getComputedStyle(el).color);
      expect(color).toContain('rgb(255, 255, 255)'); // White color
      
      // Verify it has background color
      const bgColor = await categoryChip.evaluate(el => window.getComputedStyle(el).backgroundColor);
      expect(bgColor).not.toBe('rgba(0, 0, 0, 0)'); // Not transparent
    }
  });

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
