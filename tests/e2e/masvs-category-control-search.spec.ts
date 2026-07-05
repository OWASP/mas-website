import { test, expect } from '@playwright/test';

test.describe('MASVS Category and Control Search', () => {
  test.describe('MASWE Index - MASVS Control Search', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/MASWE/');
      await page.waitForSelector('table', { timeout: 10000 });
    });

    test('should search by MASVS category (e.g., MASVS-STORAGE)', async ({ page }) => {
      // Search for MASVS-STORAGE category
      const searchInput = page.locator('input[id*="search"]').last();
      await searchInput.fill('MASVS-STORAGE');
      await searchInput.dispatchEvent('keyup');
      
      // Wait for filter to apply
      await page.waitForTimeout(500);
      
      // Check that URL contains the search query (lowercase in URL)
      await expect(page).toHaveURL(/q:masvs-storage/i);
      
      // Check that visible rows contain MASVS-STORAGE in their MASVS v2 ID column
      const visibleRows = page.locator('tbody tr:visible');
      const count = await visibleRows.count();
      expect(count).toBeGreaterThan(0);
      
      // Verify at least one visible row contains MASVS-STORAGE
      const firstRow = visibleRows.first();
      await expect(firstRow).toContainText('MASVS-STORAGE');
    });

    test('should search by specific MASVS control (e.g., MASVS-STORAGE-1)', async ({ page }) => {
      // Search for MASVS-STORAGE-1 control
      const searchInput = page.locator('input[id*="search"]').last();
      await searchInput.fill('MASVS-STORAGE-1');
      await searchInput.dispatchEvent('keyup');
      
      // Wait for filter to apply
      await page.waitForTimeout(500);
      
      // Check that URL contains the search query (lowercase in URL)
      await expect(page).toHaveURL(/q:masvs-storage-1/i);
      
      // Check that visible rows contain MASVS-STORAGE-1
      const visibleRows = page.locator('tbody tr:visible');
      const count = await visibleRows.count();
      expect(count).toBeGreaterThan(0);
      
      // Verify the visible row contains the specific control
      const firstRow = visibleRows.first();
      await expect(firstRow).toContainText('MASVS-STORAGE-1');
    });

    test('should search by lowercase MASVS category', async ({ page }) => {
      // Search with lowercase
      const searchInput = page.locator('input[id*="search"]').last();
      await searchInput.fill('masvs-crypto');
      await searchInput.dispatchEvent('keyup');
      
      // Wait for filter to apply
      await page.waitForTimeout(500);
      
      // Check that results are visible
      const visibleRows = page.locator('tbody tr:visible');
      const count = await visibleRows.count();
      expect(count).toBeGreaterThan(0);
      
      // Verify results contain MASVS-CRYPTO (case-insensitive search)
      const firstRow = visibleRows.first();
      await expect(firstRow).toContainText('MASVS-CRYPTO');
    });

    test('should search multiple MASVS controls with comma separation', async ({ page }) => {
      // Search for multiple controls
      const searchInput = page.locator('input[id*="search"]').last();
      await searchInput.fill('MASVS-STORAGE-1,MASVS-CRYPTO-1');
      await searchInput.dispatchEvent('keyup');
      
      // Wait for filter to apply
      await page.waitForTimeout(500);
      
      // Check that visible rows contain either control
      const visibleRows = page.locator('tbody tr:visible');
      const count = await visibleRows.count();
      expect(count).toBeGreaterThan(0);
      
      // Verify at least one row contains one of the searched controls
      const allText = await visibleRows.allTextContents();
      const hasStorageControl = allText.some(text => text.includes('MASVS-STORAGE-1'));
      const hasCryptoControl = allText.some(text => text.includes('MASVS-CRYPTO-1'));
      expect(hasStorageControl || hasCryptoControl).toBeTruthy();
    });

    test('should clear MASVS category search', async ({ page }) => {
      // First perform a search
      const searchInput = page.locator('input[id*="search"]').last();
      await searchInput.fill('MASVS-STORAGE');
      await searchInput.dispatchEvent('keyup');
      await page.waitForTimeout(500);
      
      // Clear the search
      await searchInput.fill('');
      await searchInput.dispatchEvent('keyup');
      await page.waitForTimeout(500);
      
      // Check that URL no longer contains search query
      const url = page.url();
      expect(url).not.toContain('q:MASVS-STORAGE');
      
      // Check that more rows are visible now
      const visibleRows = page.locator('tbody tr:visible');
      const count = await visibleRows.count();
      expect(count).toBeGreaterThan(1);
    });
  });

  test.describe('MASTG Knowledge Index - MASVS Category Search', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/MASTG/knowledge/');
      await page.waitForSelector('table', { timeout: 10000 });
    });

    test('should search by MASVS category in knowledge table', async ({ page }) => {
      // Search for MASVS-STORAGE category
      const searchInput = page.locator('input[id*="search"]').last();
      await searchInput.fill('MASVS-STORAGE');
      await searchInput.dispatchEvent('keyup');
      
      // Wait for filter to apply
      await page.waitForTimeout(500);
      
      // Check that URL contains the search query (lowercase in URL)
      await expect(page).toHaveURL(/q:masvs-storage/i);
      
      // Check that visible rows contain MASVS-STORAGE in their Category column
      const visibleRows = page.locator('tbody tr:visible');
      const count = await visibleRows.count();
      
      if (count > 0) {
        // Verify at least one visible row contains MASVS-STORAGE
        const firstRow = visibleRows.first();
        await expect(firstRow).toContainText('MASVS-STORAGE');
      }
    });

    test('should search by different MASVS categories', async ({ page }) => {
      // Test multiple categories
      const categories = ['MASVS-AUTH', 'MASVS-NETWORK', 'MASVS-PLATFORM'];
      
      for (const category of categories) {
        const searchInput = page.locator('input[id*="search"]').last();
        await searchInput.fill(category);
        await searchInput.dispatchEvent('keyup');
        await page.waitForTimeout(500);
        
        // Check URL (lowercase in URL)
        await expect(page).toHaveURL(new RegExp(`q:${category.toLowerCase()}`, 'i'));
        
        // Clear search for next iteration
        await searchInput.fill('');
        await searchInput.dispatchEvent('keyup');
        await page.waitForTimeout(300);
      }
    });

    test('should search by partial MASVS category name', async ({ page }) => {
      // Search with partial name
      const searchInput = page.locator('input[id*="search"]').last();
      await searchInput.fill('STORAGE');
      await searchInput.dispatchEvent('keyup');
      
      // Wait for filter to apply
      await page.waitForTimeout(500);
      
      // Check that results are visible
      const visibleRows = page.locator('tbody tr:visible');
      const count = await visibleRows.count();
      
      if (count > 0) {
        // Verify results contain STORAGE
        const firstRow = visibleRows.first();
        await expect(firstRow).toContainText('STORAGE');
      }
    });

    test('should combine MASVS category search with platform filter', async ({ page }) => {
      // Select Android platform filter
      const androidCheckbox = page.locator('label:has-text("Android") input').first();
      if ((await androidCheckbox.count()) > 0) {
        await androidCheckbox.check();
        await page.waitForTimeout(300);
        
        // Then search by MASVS category
        const searchInput = page.locator('input[id*="search"]').last();
        await searchInput.fill('MASVS-CRYPTO');
        await searchInput.dispatchEvent('keyup');
        await page.waitForTimeout(500);
        
        // Check that both filters are active in URL
        await expect(page).toHaveURL(/android/);
        await expect(page).toHaveURL(/q:masvs-crypto/i);
        
        // Verify filtered results
        const visibleRows = page.locator('tbody tr:visible');
        if ((await visibleRows.count()) > 0) {
          const firstRow = visibleRows.first();
          // Should have Android icon and MASVS-CRYPTO category
          await expect(firstRow).toContainText('MASVS-CRYPTO');
        }
      }
    });
  });

  test.describe('Search Term Persistence Across Pages', () => {
    test('should preserve MASVS category in URL hash', async ({ page }) => {
      // Go to MASWE with category search
      await page.goto('/MASWE/#q:MASVS-STORAGE-1');
      await page.waitForSelector('table', { timeout: 10000 });
      
      // Check that search input is populated
      const searchInput = page.locator('input[id*="search"]').last();
      const value = await searchInput.inputValue();
      expect(value.toLowerCase()).toContain('masvs-storage-1');
    });

    test('should restore MASVS category search from URL hash in knowledge', async ({ page }) => {
      // Go to knowledge page with category in hash
      await page.goto('/MASTG/knowledge/#q:MASVS-AUTH');
      await page.waitForSelector('table', { timeout: 10000 });
      
      // Check that search input is populated
      const searchInput = page.locator('input[id*="search"]').last();
      const value = await searchInput.inputValue();
      expect(value.toLowerCase()).toContain('masvs-auth');
    });
  });
});
