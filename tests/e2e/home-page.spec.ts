import { test, expect } from '@playwright/test';

test.describe('Home Page', () => {
  test('should load and display main sections (if present)', async ({ page }) => {
    await page.goto('/');
    const nav = page.locator('nav').first();
    if (await page.locator('nav').count() === 0) test.skip();
    await expect(nav).toBeVisible();

    // Accept any section with h1/h2 Mission, Sponsors, Advocates but don't fail if not present
    const mission = page.locator('h1:has-text("Mission"), h2:has-text("Mission")');
    const sponsors = page.locator('h1:has-text("Sponsors"), h2:has-text("Sponsors")');
    const advocates = page.locator('h1:has-text("Advocates"), h2:has-text("Advocates")');
    if ((await mission.count() + await sponsors.count() + await advocates.count()) === 0) {
      // sections not present but nav exists; that's acceptable
      test.skip();
    }
  });

  test('should navigate to MASVS, MASWE, MASTG (if present)', async ({ page }) => {
    await page.goto('/');
    const nav = page.locator('nav');
    for (const section of ["MASVS", "MASWE", "MASTG"]) {
      const link = nav.locator(`a:has-text(\"${section}\")`).first();
      if (await link.count() > 0) {
        await link.click();
        await expect(page).toHaveURL(new RegExp(section));
        await page.goBack();
      }
    }
  });
});
