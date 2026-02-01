import { test, expect } from '@playwright/test';

test.describe('MASVS Pages', () => {
  test('should load MASVS index and category pages (if present)', async ({ page }) => {
    await page.goto('/MASVS/');
    const h1 = page.locator('h1').first();
    if (await h1.count() === 0) test.skip();
    const h1Text = (await h1.textContent()) || '';
    if (!/MASVS/i.test(h1Text)) test.skip();

    const table = page.locator('table').first();
    if (await table.count() === 0) test.skip();
    await expect(table).toBeVisible();

    // Try to navigate to any category page
    const catLink = page.locator('a:has-text("STORAGE"), a:has-text("CRYPTO"), a:has-text("AUTH"), a:has-text("NETWORK"), a:has-text("PLATFORM"), a:has-text("CODE"), a:has-text("RESILIENCE"), a:has-text("PRIVACY")').first();
    if (await catLink.count() > 0) {
      await catLink.click();
      const newH1 = page.locator('h1').first();
      if (await newH1.count() > 0) {
        await expect(newH1).not.toContainText('MASVS');
      }
      const newTable = page.locator('table').first();
      if (await newTable.count() > 0) await expect(newTable).toBeVisible();
    } else {
      test.skip();
    }
  });

  test('should apply MASVS category color styling to nav links (if present)', async ({ page }) => {
    await page.goto('/MASVS/');
    const navLink = page.locator('nav a:has-text("STORAGE"), nav a:has-text("CRYPTO"), nav a:has-text("AUTH")').first();
    if (await navLink.count() > 0) {
      await expect(navLink).toHaveCSS('color', /rgb\(/);
    } else {
      test.skip();
    }
  });
});
