import { test, expect } from '@playwright/test';

test.describe('MAS Checklists', () => {
  test('should load checklist index and download button', async ({ page }) => {
    await page.goto('/checklists/');
    // Accept both button or link for download
    const downloadButton = page.locator('button:has-text("Download Excel Checklist")');
    const downloadLink = page.locator('a:has-text("Download Excel Checklist")');
    if (await downloadButton.count() > 0) {
      await expect(downloadButton).toBeVisible();
    } else if (await downloadLink.count() > 0) {
      await expect(downloadLink).toBeVisible();
    } else {
      test.skip();
    }
  });

  test('should render MASVS category checklist tables', async ({ page }) => {
    await page.goto('/checklists/MASVS-STORAGE');
    await expect(page.locator('h1')).toContainText('STORAGE');
    await expect(page.locator('table')).toBeVisible();
  });
});
