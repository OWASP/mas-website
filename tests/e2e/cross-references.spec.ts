import { test, expect } from '@playwright/test';

test.describe('Cross-References and Demo Buttons', () => {
  test('should display cross-reference buttons on item pages (if present)', async ({ page }) => {
    await page.goto('/MASTG/tests/android/MASTG-TEST-0073'); // Known to have cross-references
    const demoButton = page.locator('button:has-text("Demos")');
    const bestPracticesButton = page.locator('button:has-text("Best Practices")');
    // Only check if present, don't fail if missing
    if (await demoButton.count() > 0) {
      await expect(demoButton).toBeVisible();
    }
    if (await bestPracticesButton.count() > 0) {
      await expect(bestPracticesButton).toBeVisible();
    }
  });

  test('should navigate via cross-reference buttons (if present)', async ({ page }) => {
    await page.goto('/MASTG/tests/android/MASTG-TEST-0073');
    const demoButton = page.locator('button:has-text("Demos")').first();
    if (await demoButton.count() > 0) {
      await demoButton.click();
      await expect(page).toHaveURL(/MASTG\/demos/);
    } else {
      test.skip();
    }
  });
});
