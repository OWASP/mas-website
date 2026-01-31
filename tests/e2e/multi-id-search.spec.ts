import { test, expect } from '@playwright/test';

test.describe('Multi-ID Search Functionality', () => {
  test('should support comma-separated ID search on techniques page', async ({ page }) => {
    // Navigate with multiple IDs in the search query
    await page.goto('/MASTG/techniques/#q:mastg-tech-0118,mastg-tech-0082');
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Wait for search input to be populated by JavaScript
    const searchInput = page.locator('input[id*="search"]').last();
    await expect(searchInput).toHaveValue(/mastg-tech-0118,mastg-tech-0082/, { timeout: 5000 });
    
    // Check that filtered results are shown
    const visibleRows = await page.locator('tbody tr:visible').count();
    expect(visibleRows).toBeGreaterThan(0);
    expect(visibleRows).toBeLessThanOrEqual(2);
  });

  test('should support comma-separated ID search on tests page', async ({ page }) => {
    await page.goto('/MASTG/tests/#q:mastg-test-0300,mastg-test-0297');
    await page.waitForSelector('table', { timeout: 10000 });
    
    const searchInput = page.locator('input[id*="search"]').last();
    await expect(searchInput).toHaveValue(/mastg-test-0300,mastg-test-0297/, { timeout: 5000 });
  });

  test('should support comma-separated ID search on demos page', async ({ page }) => {
    await page.goto('/MASTG/demos/#q:mastg-demo-0086,mastg-demo-0085');
    await page.waitForSelector('table', { timeout: 10000 });
    
    const searchInput = page.locator('input[id*="search"]').last();
    await expect(searchInput).toHaveValue(/mastg-demo-0086,mastg-demo-0085/, { timeout: 5000 });
  });

  test('should match any ID in comma-separated list', async ({ page }) => {
    // Search for two specific techniques
    await page.goto('/MASTG/techniques/#q:mastg-tech-0118,mastg-tech-0082');
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Wait for table filtering to complete
    const searchInput = page.locator('input[id*="search"]').last();
    await expect(searchInput).toHaveValue(/mastg-tech/, { timeout: 5000 });
    
    // Check that at least one of the techniques is visible
    const tech118Visible = await page.locator('tr:has-text("MASTG-TECH-0118")').count();
    const tech082Visible = await page.locator('tr:has-text("MASTG-TECH-0082")').count();
    
    expect(tech118Visible + tech082Visible).toBeGreaterThan(0);
  });

  test('should update search from clicking "Used in" links', async ({ page }) => {
    // Start at tools page
    await page.goto('/MASTG/tools/');
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Search for a tool with references
    const searchInput = page.locator('input[id*="search"]').last();
    await searchInput.fill('0073');
    
    // Wait for the tool row to appear
    const toolRow = page.locator('tr:has-text("MASTG-TOOL-0073")').first();
    await expect(toolRow).toBeVisible({ timeout: 5000 });
    
    // Click on a "Used in" link (MASTG-TECH)
    const usedInCell = toolRow.locator('td').nth(3);
    const techLink = usedInCell.locator('a:has-text("MASTG-TECH")').first();
    
    if (await techLink.isVisible()) {
      // Get the href to verify it has the hash
      const href = await techLink.getAttribute('href');
      expect(href).toContain('#q:');
      
      // Click and wait for navigation
      await Promise.all([
        page.waitForNavigation({ timeout: 5000 }),
        techLink.click()
      ]);
      
      // Should navigate to techniques page with search query
      // URL format is #[filters;]q:ids - filters like "unused" may be present
      expect(page.url()).toContain('/MASTG/techniques/');
      expect(page.url()).toMatch(/[#;]q:/);
      
      await page.waitForSelector('table', { timeout: 10000 });
      
      // Search input should contain comma-separated IDs
      const newSearchInput = page.locator('input[id*="search"]').last();
      await expect(newSearchInput).toHaveValue(/,/, { timeout: 5000 });
    }
  });

  test('should clear search when hash is removed', async ({ page }) => {
    // Navigate with search query
    await page.goto('/MASTG/techniques/#q:mastg-tech-0118');
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Wait for search to be populated
    const searchInput = page.locator('input[id*="search"]').last();
    await expect(searchInput).toHaveValue(/mastg-tech-0118/, { timeout: 5000 });
    
    // Navigate to page without hash
    await page.goto('/MASTG/techniques/');
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Search input should be empty
    await expect(searchInput).toHaveValue('', { timeout: 5000 });
  });
});
