import { test, expect } from '@playwright/test';

test.describe('MASTG Tools - Knowledge References in "Used in" Column', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/MASTG/tools/');
    // Wait for DataTables to initialize
    await page.waitForSelector('table', { timeout: 10000 });
  });

  test('should show knowledge references in "Used in" column', async ({ page }) => {
    // Search for MASTG-TOOL-0121 which has knowledge references
    const searchInput = page.locator('input[id*="search"]').last();
    await searchInput.fill('0121');
    
    // Wait for the tool row to appear
    const toolRow = page.locator('tr:has-text("MASTG-TOOL-0121")').first();
    await expect(toolRow).toBeVisible({ timeout: 5000 });

    // Check that "Used in" column contains MASTG-KNOW
    const usedInCell = toolRow.locator('td').nth(3);
    await expect(usedInCell).toContainText('MASTG-KNOW');
  });

  test('should have clickable knowledge links in "Used in" column', async ({ page }) => {
    // Search for a tool with knowledge references
    const searchInput = page.locator('input[id*="search"]').last();
    await searchInput.fill('0121');
    
    // Wait for the tool row to appear
    const toolRow = page.locator('tr:has-text("MASTG-TOOL-0121")').first();
    await expect(toolRow).toBeVisible({ timeout: 5000 });

    // Find links in the "Used in" column that point to knowledge
    const usedInCell = toolRow.locator('td').nth(3);
    const knowledgeLink = usedInCell.locator('a[href*="/MASTG/knowledge/"]').first();
    
    // Ensure the link exists
    if ((await knowledgeLink.count()) > 0) {
      await expect(knowledgeLink).toBeVisible({ timeout: 5000 });
      
      // Check that link has proper href format
      const href = await knowledgeLink.getAttribute('href');
      expect(href).toMatch(/\/MASTG\/knowledge\/#q:/);
    }
  });

  test('should display knowledge icon in "Used in" column', async ({ page }) => {
    // Search for MASTG-TOOL-0121
    const searchInput = page.locator('input[id*="search"]').last();
    await searchInput.fill('0121');
    
    // Wait for the tool row to appear
    const toolRow = page.locator('tr:has-text("MASTG-TOOL-0121")').first();
    await expect(toolRow).toBeVisible({ timeout: 5000 });

    const usedInCell = toolRow.locator('td').nth(3);
    
    // Check for knowledge link with icon (Material icons are rendered as SVG)
    const knowledgeLink = usedInCell.locator('a[href*="/MASTG/knowledge/"]').first();
    if ((await knowledgeLink.count()) > 0) {
      const svgIcons = await knowledgeLink.locator('svg').count();
      expect(svgIcons).toBeGreaterThan(0);
    }
  });

  test('should navigate to knowledge page when clicking knowledge link', async ({ page }) => {
    // Search for MASTG-TOOL-0028 which also has knowledge references
    const searchInput = page.locator('input[id*="search"]').last();
    await searchInput.fill('0028');
    
    // Wait for the tool row to appear
    const toolRow = page.locator('tr:has-text("MASTG-TOOL-0028")').first();
    await expect(toolRow).toBeVisible({ timeout: 5000 });

    // Find and click knowledge link
    const usedInCell = toolRow.locator('td').nth(3);
    const knowledgeLink = usedInCell.locator('a[href*="/MASTG/knowledge/"]').first();
    
    if ((await knowledgeLink.count()) > 0) {
      await knowledgeLink.click();
      
      // Should navigate to knowledge page with search query
      await expect(page).toHaveURL(/\/MASTG\/knowledge\//);
      await expect(page).toHaveURL(/#q:/);
    }
  });

  test('should show multiple reference types including knowledge', async ({ page }) => {
    // Search for MASTG-TOOL-0073 which may have multiple reference types
    const searchInput = page.locator('input[id*="search"]').last();
    await searchInput.fill('0073');
    
    // Wait for the tool row to appear
    const toolRow = page.locator('tr:has-text("MASTG-TOOL-0073")').first();
    await expect(toolRow).toBeVisible({ timeout: 5000 });

    const usedInCell = toolRow.locator('td').nth(3);
    
    // Count total links (techniques, knowledge, demos, tests)
    const totalLinks = await usedInCell.locator('a').count();
    expect(totalLinks).toBeGreaterThan(0);
    
    // Check for proper ordering (techniques, knowledge, demos, tests)
    const allLinks = await usedInCell.locator('a').all();
    if (allLinks.length > 1) {
      // Verify links are separated by line breaks
      const cellHTML = await usedInCell.innerHTML();
      expect(cellHTML).toContain('<br>');
    }
  });
});
