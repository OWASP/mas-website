import { test, expect } from '@playwright/test';

// These tests guard the maswe: [...] tag rendering on MASTG test pages.
// A weakness tag is styled via a placeholder mechanism (see
// docs/hooks/add-tags.py): if the placeholder used for a given weakness
// isn't registered with the right icon "type", the tag silently falls back
// to the default "#" icon and grey background instead of the MASWE shield.
test.describe('MASWE Tags on MASTG Test Pages', () => {
  test('should style the MASWE tag correctly on a test with a single weakness', async ({ page }) => {
    // Known to have one MASWE weakness: maswe: [MASWE-0018]
    await page.goto('/MASTG/tests/android/MASVS-PLATFORM/MASTG-TEST-0357/');

    const tag = page.locator('.md-tags a', { hasText: 'MASWE-0018' });
    await expect(tag).toBeVisible();
    await expect(tag).toHaveClass(/\bmd-tag--maswe\b/);
    await expect(tag).toHaveAttribute('href', /MASWE-0018$/);
  });

  test('should style every MASWE tag correctly on a test with multiple weaknesses', async ({ page }) => {
    // Known to have multiple MASWE weaknesses: maswe: [MASWE-0036, MASWE-0040]
    await page.goto('/MASTG/tests/android/MASVS-PLATFORM/MASTG-TEST-0316/');

    for (const id of ['MASWE-0036', 'MASWE-0040']) {
      const tag = page.locator('.md-tags a', { hasText: id });
      await expect(tag).toBeVisible();
      await expect(tag).toHaveClass(/\bmd-tag--maswe\b/);
      await expect(tag).toHaveAttribute('href', new RegExp(`${id}$`));
    }

    // Regression guard: with multiple weaknesses, each gets its own
    // placeholder swapped out individually - none should ever leak into
    // the rendered page.
    await expect(page.locator('body')).not.toContainText('placeholder-tag-maswe');
  });
});
