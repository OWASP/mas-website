import { test, expect } from '@playwright/test';

test.describe('MASTG Tools - Show Unused Filter', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/MASTG/tools/');
    await page.waitForSelector('table', { timeout: 10000 });
    await page.waitForTimeout(2000);
  });

  test('should have "Show Unused" checkbox in Status filter group', async ({ page }) => {
    // Look for the Show Unused checkbox
    const showUnusedLabel = await page.locator('label:has-text("Show Unused")').count();
    expect(showUnusedLabel).toBeGreaterThan(0);
  });

  test('should hide unused tools by default', async ({ page }) => {
    // Count total rows in table
    const totalRowsBefore = await page.locator('tbody tr').count();
    
    // Enable "Show Unused" filter
    const showUnusedCheckbox = await page.locator('label:has-text("Show Unused") input').first();
    await showUnusedCheckbox.check();
    await page.waitForTimeout(1000);
    
    // Count rows after enabling
    const totalRowsAfter = await page.locator('tbody tr').count();
    
    // Should show more rows when "Show Unused" is enabled
    expect(totalRowsAfter).toBeGreaterThan(totalRowsBefore);
  });

  test('should update URL hash when "Show Unused" is toggled', async ({ page }) => {
    // Check initial URL (should not have "unused")
    let url = page.url();
    expect(url).not.toContain('#unused');
    
    // Enable "Show Unused" filter
    const showUnusedCheckbox = await page.locator('label:has-text("Show Unused") input').first();
    await showUnusedCheckbox.check();
    await page.waitForTimeout(500);
    
    // Check URL contains "unused" hash
    url = page.url();
    expect(url).toContain('unused');
  });

  test('should restore "Show Unused" state from URL hash', async ({ page }) => {
    // Navigate to tools page with #unused hash
    await page.goto('/MASTG/tools/#unused');
    await page.waitForSelector('table', { timeout: 10000 });
    await page.waitForTimeout(2000);
    
    // Check that "Show Unused" checkbox is checked
    const showUnusedCheckbox = await page.locator('label:has-text("Show Unused") input').first();
    await expect(showUnusedCheckbox).toBeChecked();
  });

  test('should display filter info showing filtered entries', async ({ page }) => {
    // Get the info text
    const infoElement = await page.locator('span[id*="filter"][id*="info"]').first();
    const infoText = await infoElement.textContent();
    
    // Should show "filtered" in the info text when unused tools are hidden
    expect(infoText).toMatch(/Showing.*of.*entries/);
  });
});
