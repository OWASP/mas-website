import { test, expect } from '@playwright/test';

test.describe('Multi-ID Search Functionality', () => {
  test('should support comma-separated ID search on techniques page', async ({ page }) => {
    // Navigate with multiple IDs in the search query
    await page.goto('/MASTG/techniques/#q:mastg-tech-0118,mastg-tech-0082');
    await page.waitForSelector('table', { timeout: 10000 });
    await page.waitForTimeout(2000);
    
    // Check that search input contains the query
    const searchInput = await page.locator('input[id*="search"]').last();
    const searchValue = await searchInput.inputValue();
    expect(searchValue).toContain('mastg-tech-0118,mastg-tech-0082');
    
    // Check that filtered results are shown
    const visibleRows = await page.locator('tbody tr:visible').count();
    expect(visibleRows).toBeGreaterThan(0);
    expect(visibleRows).toBeLessThanOrEqual(2);
  });

  test('should support comma-separated ID search on tests page', async ({ page }) => {
    await page.goto('/MASTG/tests/#q:mastg-test-0300,mastg-test-0297');
    await page.waitForSelector('table', { timeout: 10000 });
    await page.waitForTimeout(2000);
    
    const searchInput = await page.locator('input[id*="search"]').last();
    const searchValue = await searchInput.inputValue();
    expect(searchValue).toContain('mastg-test-0300,mastg-test-0297');
  });

  test('should support comma-separated ID search on demos page', async ({ page }) => {
    await page.goto('/MASTG/demos/#q:mastg-demo-0086,mastg-demo-0085');
    await page.waitForSelector('table', { timeout: 10000 });
    await page.waitForTimeout(2000);
    
    const searchInput = await page.locator('input[id*="search"]').last();
    const searchValue = await searchInput.inputValue();
    expect(searchValue).toContain('mastg-demo-0086,mastg-demo-0085');
  });

  test('should match any ID in comma-separated list', async ({ page }) => {
    // Search for two specific techniques
    await page.goto('/MASTG/techniques/#q:mastg-tech-0118,mastg-tech-0082');
    await page.waitForSelector('table', { timeout: 10000 });
    await page.waitForTimeout(2000);
    
    // Check that at least one of the techniques is visible
    const tech118Visible = await page.locator('tr:has-text("MASTG-TECH-0118")').count();
    const tech082Visible = await page.locator('tr:has-text("MASTG-TECH-0082")').count();
    
    expect(tech118Visible + tech082Visible).toBeGreaterThan(0);
  });

  test('should update search from clicking "Used in" links', async ({ page }) => {
    // Start at tools page
    await page.goto('/MASTG/tools/');
    await page.waitForSelector('table', { timeout: 10000 });
    await page.waitForTimeout(2000);
    
    // Search for a tool with references
    const searchInput = await page.locator('input[id*="search"]').last();
    await searchInput.fill('0073');
    await page.waitForTimeout(1000);
    
    // Click on a "Used in" link (MASTG-TECH)
    const toolRow = await page.locator('tr:has-text("MASTG-TOOL-0073")').first();
    const usedInCell = await toolRow.locator('td').nth(3);
    const techLink = await usedInCell.locator('a:has-text("MASTG-TECH")').first();
    
    if (await techLink.isVisible()) {
      await techLink.click();
      await page.waitForTimeout(2000);
      
      // Should navigate to techniques page with search query
      expect(page.url()).toContain('/MASTG/techniques/');
      expect(page.url()).toContain('#q:');
      
      // Search input should contain comma-separated IDs
      const newSearchInput = await page.locator('input[id*="search"]').last();
      const newSearchValue = await newSearchInput.inputValue();
      expect(newSearchValue).toContain(',');
    }
  });

  test('should clear search when hash is removed', async ({ page }) => {
    // Navigate with search query
    await page.goto('/MASTG/techniques/#q:mastg-tech-0118');
    await page.waitForSelector('table', { timeout: 10000 });
    await page.waitForTimeout(2000);
    
    // Navigate to page without hash
    await page.goto('/MASTG/techniques/');
    await page.waitForTimeout(2000);
    
    // Search input should be empty
    const searchInput = await page.locator('input[id*="search"]').last();
    const searchValue = await searchInput.inputValue();
    expect(searchValue).toBe('');
  });
});
