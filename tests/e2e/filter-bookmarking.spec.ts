import { test, expect } from '@playwright/test';

test.describe('Filter Bookmarking via URL Hash', () => {
  test('should support platform filter in URL hash', async ({ page }) => {
    await page.goto('/MASTG/tools/#ios');
    await page.waitForSelector('table', { timeout: 10000 });
    await page.waitForTimeout(2000);
    
    // iOS checkbox should be checked
    const iosCheckbox = await page.locator('label:has-text("iOS") input').first();
    await expect(iosCheckbox).toBeChecked();
  });

  test('should support multiple filters in URL hash', async ({ page }) => {
    await page.goto('/MASTG/tools/#ios;unused');
    await page.waitForSelector('table', { timeout: 10000 });
    await page.waitForTimeout(2000);
    
    // Both checkboxes should be checked
    const iosCheckbox = await page.locator('label:has-text("iOS") input').first();
    await expect(iosCheckbox).toBeChecked();
    
    const unusedCheckbox = await page.locator('label:has-text("Show Unused") input').first();
    await expect(unusedCheckbox).toBeChecked();
  });

  test('should update URL hash when filters are changed', async ({ page }) => {
    await page.goto('/MASTG/tools/');
    await page.waitForSelector('table', { timeout: 10000 });
    await page.waitForTimeout(2000);
    
    // Check iOS filter
    const iosCheckbox = await page.locator('label:has-text("iOS") input').first();
    await iosCheckbox.check();
    await page.waitForTimeout(500);
    
    // URL should contain ios
    expect(page.url()).toContain('ios');
  });

  test('should support search query in URL hash', async ({ page }) => {
    await page.goto('/MASTG/tools/#q:frida');
    await page.waitForSelector('table', { timeout: 10000 });
    await page.waitForTimeout(2000);
    
    // Search input should contain "frida"
    const searchInput = await page.locator('input[id*="search"]').last();
    const searchValue = await searchInput.inputValue();
    expect(searchValue).toBe('frida');
  });

  test('should combine filters and search in URL hash', async ({ page }) => {
    await page.goto('/MASTG/tools/#ios;q:frida');
    await page.waitForSelector('table', { timeout: 10000 });
    await page.waitForTimeout(2000);
    
    // iOS checkbox should be checked
    const iosCheckbox = await page.locator('label:has-text("iOS") input').first();
    await expect(iosCheckbox).toBeChecked();
    
    // Search should be populated
    const searchInput = await page.locator('input[id*="search"]').last();
    const searchValue = await searchInput.inputValue();
    expect(searchValue).toBe('frida');
  });

  test('should clear all filters button work correctly', async ({ page }) => {
    await page.goto('/MASTG/tools/#ios;unused');
    await page.waitForSelector('table', { timeout: 10000 });
    await page.waitForTimeout(2000);
    
    // Click "Clear All Filters" button
    const clearButton = await page.locator('button:has-text("Clear All Filters")').first();
    await clearButton.click();
    await page.waitForTimeout(500);
    
    // All checkboxes should be unchecked
    const iosCheckbox = await page.locator('label:has-text("iOS") input').first();
    await expect(iosCheckbox).not.toBeChecked();
    
    const unusedCheckbox = await page.locator('label:has-text("Show Unused") input').first();
    await expect(unusedCheckbox).not.toBeChecked();
    
    // URL hash should be cleared
    expect(page.url()).not.toContain('ios');
    expect(page.url()).not.toContain('unused');
  });
});
