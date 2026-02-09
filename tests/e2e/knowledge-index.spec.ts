import { test, expect } from '@playwright/test';

test.describe('MASTG Knowledge Index', () => {
  test('should have Category column with full MASVS names and white text', async ({ page }) => {
    await page.goto('/MASTG/knowledge/');
    const categoryHeader = page.locator('th:has-text("Category")').first();
    await expect(categoryHeader).toBeVisible();
    
    // Check that category chips display full MASVS names (e.g., "MASVS-STORAGE" not "STORAGE")
    const categoryCell = page.locator('td .md-tag').first();
    if ((await categoryCell.count()) > 0) {
      await expect(categoryCell).toBeVisible();
      const chipText = await categoryCell.textContent();
      // Should contain "MASVS-" prefix
      expect(chipText).toMatch(/MASVS-/);
      
      // Verify white text color
      const color = await categoryCell.evaluate(el => window.getComputedStyle(el).color);
      expect(color).toContain('rgb(255, 255, 255)'); // White color
      
      // Verify it has background color (indicating it's styled)
      const bgColor = await categoryCell.evaluate(el => window.getComputedStyle(el).backgroundColor);
      expect(bgColor).not.toBe('rgba(0, 0, 0, 0)'); // Not transparent
    }
  });

  test('should have Status column', async ({ page }) => {
    await page.goto('/MASTG/knowledge/');
    const statusHeader = page.locator('th:has-text("Status")').first();
    await expect(statusHeader).toBeVisible();
  });

  test('should filter by platform', async ({ page }) => {
    await page.goto('/MASTG/knowledge/');
    const androidCheckbox = page.locator('label:has-text("Android") input').first();
    if ((await androidCheckbox.count()) > 0) {
      await androidCheckbox.check();
      await expect(page).toHaveURL(/android/);
      await expect(androidCheckbox).toBeChecked();
    }
  });

  test('should filter by status (Show Deprecated)', async ({ page }) => {
    await page.goto('/MASTG/knowledge/');
    const deprecatedCheckbox = page.locator('label:has-text("Show Deprecated") input').first();
    await deprecatedCheckbox.check();
    await expect(page).toHaveURL(/deprecated/);
    await expect(deprecatedCheckbox).toBeChecked();
  });

  test('should search for knowledge articles', async ({ page }) => {
    await page.goto('/MASTG/knowledge/');
    const searchInput = page.locator('input[id*="search"]').last();
    await searchInput.fill('data');
    await searchInput.dispatchEvent('keyup');
    await expect(page).toHaveURL(/q:data/);
  });

  test('should clear all filters', async ({ page }) => {
    await page.goto('/MASTG/knowledge/#android;deprecated;q:test');
    const clearButton = page.locator('button:has-text("Clear All Filters")');
    await clearButton.click();
    await expect(page).toHaveURL(/^[^#]*#?$/); // URL should not have hash parameters
  });
});
