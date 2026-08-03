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
    await page.goto('/MASTG/tools/#ios;hideunused');
    await page.waitForSelector('table', { timeout: 10000 });

    // Both checkboxes should be checked
    const iosCheckbox = page.locator('label:has-text("iOS") input').first();
    await expect(iosCheckbox).toBeChecked({ timeout: 5000 });

    const unusedCheckbox = page.locator('label:has-text("Hide Unused") input').first();
    await expect(unusedCheckbox).toBeChecked({ timeout: 5000 });
  });

  test('should support profile filter in URL hash (if present)', async ({ page }) => {
    await page.goto('/MASTG/tools/#l1');
    await page.waitForSelector('table', { timeout: 10000 });
    const l1Checkbox = page.locator('label:has-text("L1") input').first();
    if ((await l1Checkbox.count()) > 0) {
      await expect(l1Checkbox).toBeChecked({ timeout: 5000 });
    } else {
      test.skip();
    }
  });

  test('should support multiple profile filters in URL hash (if present)', async ({ page }) => {
    await page.goto('/MASTG/tools/#l1;l2;r;p');
    await page.waitForSelector('table', { timeout: 10000 });
    const l1Checkbox = page.locator('label:has-text("L1") input').first();
    const l2Checkbox = page.locator('label:has-text("L2") input').first();
    const rCheckbox = page.locator('label:has-text("R") input').first();
    const pCheckbox = page.locator('label:has-text("P") input').first();
    if (((await l1Checkbox.count()) > 0) && ((await l2Checkbox.count()) > 0) && ((await rCheckbox.count()) > 0) && ((await pCheckbox.count()) > 0)) {
      await expect(l1Checkbox).toBeChecked({ timeout: 5000 });
      await expect(l2Checkbox).toBeChecked({ timeout: 5000 });
      await expect(rCheckbox).toBeChecked({ timeout: 5000 });
      await expect(pCheckbox).toBeChecked({ timeout: 5000 });
    } else {
      test.skip();
    }
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

  test('should update URL hash when search term is typed', async ({ page }) => {
    await page.goto('/MASTG/tools/');
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Type in search box
    const searchInput = page.locator('input[id*="search"]').last();
    await searchInput.fill('frida');
    await searchInput.dispatchEvent('keyup'); 
    
    // URL should contain search query
    await expect(page).toHaveURL(/q:frida/, { timeout: 5000 });
  });

  test('should update URL hash when combining search with filters', async ({ page }) => {
    await page.goto('/MASTG/tools/');
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Check iOS filter
    const iosCheckbox = page.locator('label:has-text("iOS") input').first();
    await iosCheckbox.check();
    
    // Type in search box
    const searchInput = page.locator('input[id*="search"]').last();
    await searchInput.fill('frida');
    await searchInput.dispatchEvent('keyup'); 
    
    // URL should contain both filter and search query
    await expect(page).toHaveURL(/ios/, { timeout: 5000 });
    await expect(page).toHaveURL(/q:frida/, { timeout: 5000 });
  });

  test('should clear search term from URL when cleared', async ({ page }) => {
    await page.goto('/MASTG/tools/#q:frida');
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Clear the search box
    const searchInput = page.locator('input[id*="search"]').last();
    await searchInput.clear();
    
    // URL should not contain search query anymore
    await expect(page).not.toHaveURL(/q:frida/, { timeout: 5000 });
  });

  test('should clear all filters button work correctly', async ({ page }) => {
    await page.goto('/MASTG/tools/#ios;hideunused');
    await page.waitForSelector('table', { timeout: 10000 });

    // Wait for filters to be applied
    const iosCheckbox = page.locator('label:has-text("iOS") input').first();
    await expect(iosCheckbox).toBeChecked({ timeout: 5000 });

    // Click "Clear All Filters" button
    const clearButton = page.locator('button:has-text("Clear All Filters")').first();
    await clearButton.click();

    // All checkboxes should be unchecked
    await expect(iosCheckbox).not.toBeChecked({ timeout: 5000 });

    const unusedCheckbox = page.locator('label:has-text("Hide Unused") input').first();
    await expect(unusedCheckbox).not.toBeChecked({ timeout: 5000 });

    // URL hash should be cleared
    await expect(page).not.toHaveURL(/ios/);
    await expect(page).not.toHaveURL(/hideunused/);
  });

  test('should clear search term when clear all filters is clicked', async ({ page }) => {
    await page.goto('/MASTG/tools/#ios;q:frida');
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Click "Clear All Filters" button
    const clearButton = page.locator('button:has-text("Clear All Filters")').first();
    await clearButton.click();
    
    // URL should not contain search query
    await expect(page).not.toHaveURL(/q:frida/, { timeout: 5000 });
    
    // Search box should be empty
    const searchInput = page.locator('input[id*="search"]').last();
    await expect(searchInput).toHaveValue('', { timeout: 5000 });
  });
});
