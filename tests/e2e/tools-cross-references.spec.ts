import { test, expect } from '@playwright/test';

test.describe('MASTG Tools - Cross-References and "Used in" Column', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/MASTG/tools/');
    // Wait for DataTables to initialize
    await page.waitForSelector('table', { timeout: 10000 });
    // Wait a bit more for filters to load
    await page.waitForTimeout(2000);
  });

  test('should display the "Used in" column in tools table', async ({ page }) => {
    // Check that the "Used in" column header exists
    const headers = await page.$$eval('thead th', ths => ths.map(th => th.textContent?.trim()));
    expect(headers).toContain('Used in');
  });

  test('should show cross-reference counts for tools with references', async ({ page }) => {
    // Search for MASTG-TOOL-0073 which has known references
    const searchInput = await page.locator('input[id*="search"]').last();
    await searchInput.fill('0073');
    await page.waitForTimeout(1000);

    // Check that the tool is displayed
    const toolRow = await page.locator('tr:has-text("MASTG-TOOL-0073")').first();
    await expect(toolRow).toBeVisible();

    // Check that "Used in" column contains MASTG-TECH
    const usedInCell = await toolRow.locator('td').nth(3);
    const usedInText = await usedInCell.textContent();
    expect(usedInText).toContain('MASTG-TECH');
  });

  test('should mark unused tools with "Unused" label', async ({ page }) => {
    // Show unused tools first - find checkbox via label
    const showUnusedLabel = await page.locator('label:has-text("Show Unused")').first();
    if (await showUnusedLabel.isVisible()) {
      // Click the label to check the checkbox
      await showUnusedLabel.click();
      await page.waitForTimeout(1000);
    }

    // Look for any unused tool in the table
    const unusedCells = await page.locator('td:has-text("Unused")').count();
    expect(unusedCells).toBeGreaterThan(0);
  });

  test('should have clickable links in "Used in" column', async ({ page }) => {
    // Search for a tool with references
    const searchInput = await page.locator('input[id*="search"]').last();
    await searchInput.fill('0073');
    await page.waitForTimeout(1000);

    // Find links in the "Used in" column
    const toolRow = await page.locator('tr:has-text("MASTG-TOOL-0073")').first();
    const usedInCell = await toolRow.locator('td').nth(3);
    const links = await usedInCell.locator('a').count();
    expect(links).toBeGreaterThan(0);

    // Check that links have proper href format
    const firstLink = await usedInCell.locator('a').first();
    const href = await firstLink.getAttribute('href');
    expect(href).toMatch(/\/MASTG\/(techniques|demos|tests)\/#q:/);
  });

  test('should display counts with proper icons', async ({ page }) => {
    // Search for MASTG-TOOL-0073
    const searchInput = await page.locator('input[id*="search"]').last();
    await searchInput.fill('0073');
    await page.waitForTimeout(1000);

    const toolRow = await page.locator('tr:has-text("MASTG-TOOL-0073")').first();
    const usedInCell = await toolRow.locator('td').nth(3);
    
    // Check for icon elements (Material icons are rendered as SVG)
    const svgIcons = await usedInCell.locator('svg').count();
    expect(svgIcons).toBeGreaterThan(0);
  });
});
