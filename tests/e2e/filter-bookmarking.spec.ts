import { test, expect } from '@playwright/test';

test.describe('Filter Bookmarking via URL Hash', () => {
  test('should support platform filter in URL hash', async ({ page }) => {
    await page.goto('/MASTG/tools/#ios');
    await page.waitForSelector('table', { timeout: 10000 });
    
    // iOS checkbox should be checked
    const iosCheckbox = page.locator('label:has-text("iOS") input').first();
    await expect(iosCheckbox).toBeChecked({ timeout: 5000 });
  });

  test('should support multiple filters in URL hash', async ({ page }) => {
    await page.goto('/MASTG/tools/#ios;unused');
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Both checkboxes should be checked
    const iosCheckbox = page.locator('label:has-text("iOS") input').first();
    await expect(iosCheckbox).toBeChecked({ timeout: 5000 });
    
    const unusedCheckbox = page.locator('label:has-text("Show Unused") input').first();
    await expect(unusedCheckbox).toBeChecked({ timeout: 5000 });
  });

  test('should update URL hash when filters are changed', async ({ page }) => {
    await page.goto('/MASTG/tools/');
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Check iOS filter
    const iosCheckbox = page.locator('label:has-text("iOS") input').first();
    await iosCheckbox.check();
    
    // URL should contain ios
    await expect(page).toHaveURL(/ios/, { timeout: 5000 });
  });

  test('should support search query in URL hash', async ({ page }) => {
    await page.goto('/MASTG/tools/#q:frida');
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Search input should contain "frida"
    const searchInput = page.locator('input[id*="search"]').last();
    await expect(searchInput).toHaveValue('frida', { timeout: 5000 });
  });

  test('should combine filters and search in URL hash', async ({ page }) => {
    await page.goto('/MASTG/tools/#ios;q:frida');
    await page.waitForSelector('table', { timeout: 10000 });
    
    // iOS checkbox should be checked
    const iosCheckbox = page.locator('label:has-text("iOS") input').first();
    await expect(iosCheckbox).toBeChecked({ timeout: 5000 });
    
    // Search should be populated
    const searchInput = page.locator('input[id*="search"]').last();
    await expect(searchInput).toHaveValue('frida', { timeout: 5000 });
  });

  test('should clear all filters button work correctly', async ({ page }) => {
    await page.goto('/MASTG/tools/#ios;unused');
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Wait for filters to be applied
    const iosCheckbox = page.locator('label:has-text("iOS") input').first();
    await expect(iosCheckbox).toBeChecked({ timeout: 5000 });
    
    // Click "Clear All Filters" button
    const clearButton = page.locator('button:has-text("Clear All Filters")').first();
    await clearButton.click();
    
    // All checkboxes should be unchecked
    await expect(iosCheckbox).not.toBeChecked({ timeout: 5000 });
    
    const unusedCheckbox = page.locator('label:has-text("Show Unused") input').first();
    await expect(unusedCheckbox).not.toBeChecked({ timeout: 5000 });
    
    // URL hash should be cleared
    await expect(page).not.toHaveURL(/ios/);
    await expect(page).not.toHaveURL(/unused/);
  });
});
