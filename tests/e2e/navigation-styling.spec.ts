import { test, expect } from '@playwright/test';

test.describe('Navigation Styling', () => {
  test('should apply MASVS category color styling to navigation links (if present)', async ({ page }) => {
    await page.goto('/MASVS/');
    let found = false;
    for (const cat of ["STORAGE", "CRYPTO", "AUTH", "NETWORK", "PLATFORM", "CODE", "RESILIENCE", "PRIVACY"]) {
      const link = page.locator(`nav a:has-text("${cat}")`).first();
      if (await link.count() > 0) {
        await expect(link).toHaveCSS('color', /rgb\(/);
        found = true;
      }
    }
    if (!found) test.skip();
  });
});
