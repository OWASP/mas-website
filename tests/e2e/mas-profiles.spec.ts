import { test, expect } from '@playwright/test';

// Covers the "MAS Profiles" section added to the top nav: docs/Profiles/*.md,
// its own nav entry (docs/hooks: no dedicated hook, wired directly in
// mkdocs.yml), the "## Requirements" table injected by
// docs/hooks/create_dynamic_tables.py (get_weaknesses_for_profile /
// PROFILE_PAGES), and the redirect from the old MASTG/0x03b-Testing-Profiles
// location (docs/hooks/add_redirects.py).

test.describe('MAS Profiles Navigation', () => {
  test('should have a top-level "MAS Profiles" nav entry linking to /Profiles/', async ({ page }) => {
    await page.goto('/');
    const link = page.locator('nav a:has-text("MAS Profiles")').first();
    await expect(link).toBeVisible();
    await expect(link).toHaveAttribute('href', /\/Profiles\//);
  });

  test('old MASTG/0x03b-Testing-Profiles URL should redirect to /Profiles/', async ({ page }) => {
    await page.goto('/MASTG/0x03b-Testing-Profiles/');
    await expect(page).toHaveURL(/\/Profiles\/$/);
  });
});

test.describe('MAS Profiles Index Page', () => {
  test('should load with the intro content and link to every sub-page', async ({ page }) => {
    await page.goto('/Profiles/');
    await expect(page).toHaveTitle(/MAS Testing Profiles/);
    await expect(page.locator('h1', { hasText: 'MAS Testing Profiles' })).toBeVisible();

    for (const [text, href] of [
      ['MAS-L1', /MAS-L1/],
      ['MAS-L2', /MAS-L2/],
      ['MAS-R', /MAS-R/],
      ['MAS-P', /MAS-P/],
      ['Using MAS Profiles', /Using-MAS-Profiles/],
    ] as const) {
      const link = page.locator(`a:has-text("${text}")`).first();
      await expect(link).toBeVisible();
      await expect(link).toHaveAttribute('href', href);
    }
  });

  test('should render the profile examples image', async ({ page }) => {
    await page.goto('/Profiles/');
    const img = page.locator('img[src*="example_apps_profiles"]');
    await expect(img).toBeVisible();
  });

  test('should show the attacker capabilities summary table', async ({ page }) => {
    await page.goto('/Profiles/');

    await expect(page.locator('h3', { hasText: 'Attacker capabilities at a glance' })).toBeVisible();

    const summaryTable = page.locator('table').filter({ hasText: 'Brief attacker model' }).first();
    await expect(summaryTable).toBeVisible();

    for (const expectedText of [
      'MAS-L1',
      'Other applications installed on the device are adversaries.',
      'MAS-L2',
      'The operating system cannot be trusted, and attackers may have physical access to the device.',
      'MAS-R',
      'The user of the device is an attacker, including reverse engineers and cheaters.',
      'MAS-P',
      "Not attacker-centric; focuses on protecting users' personal data and responsible data handling.",
    ]) {
      await expect(summaryTable).toContainText(expectedText);
    }
  });
});

test.describe('Using MAS Profiles Page', () => {
  test('should load and link to MAS-L1 and MAS-L2', async ({ page }) => {
    await page.goto('/Profiles/Using-MAS-Profiles/');
    await expect(page.locator('h1', { hasText: 'Using MAS Profiles' })).toBeVisible();
    await expect(page.locator('h2:has-text("References")')).toBeVisible();

    const l1Link = page.locator('a:has-text("MAS-L1")').first();
    const l2Link = page.locator('a:has-text("MAS-L2")').first();
    await expect(l1Link).toHaveAttribute('href', /MAS-L1/);
    await expect(l2Link).toHaveAttribute('href', /MAS-L2/);
  });
});

// One test.describe block per profile page, each checking:
// - the page loads with the right title
// - the "## Requirements" table is present with the expected columns
// - it has at least one row, and MASWE ID links point at /MASWE/
const profiles: { slug: string; titleFragment: string; expectedMinRows: number }[] = [
  { slug: 'MAS-L1', titleFragment: 'MAS-L1 - Essential Security', expectedMinRows: 20 },
  { slug: 'MAS-L2', titleFragment: 'MAS-L2 - Advanced Security', expectedMinRows: 40 },
  { slug: 'MAS-R', titleFragment: 'MAS-R - Resilient Security', expectedMinRows: 10 },
  { slug: 'MAS-P', titleFragment: 'MAS-P - Baseline Privacy', expectedMinRows: 10 },
];

for (const { slug, titleFragment, expectedMinRows } of profiles) {
  test.describe(`${slug} Page`, () => {
    test(`should load and show a "Requirements" section with a MASWE table`, async ({ page }) => {
      await page.goto(`/Profiles/${slug}/`);
      await expect(page).toHaveTitle(new RegExp(titleFragment.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));

      const heading = page.locator('h2:has-text("Requirements")');
      await expect(heading).toBeVisible();

      const table = page.locator('table').first();
      await expect(table).toBeVisible();

      const headerCells = table.locator('thead tr th');
      const headerTexts = await headerCells.allTextContents();
      for (const col of ['Requirement', 'MASWE ID', 'Platform', 'MASVS ID', 'Tests', 'Status']) {
        expect(headerTexts).toContain(col);
      }

      const rows = table.locator('tbody tr');
      const rowCount = await rows.count();
      expect(rowCount).toBeGreaterThanOrEqual(expectedMinRows);

      // First row's MASWE ID cell should link into /MASWE/
      const maswIdColIndex = headerTexts.indexOf('MASWE ID');
      const firstRowLink = rows.first().locator('td').nth(maswIdColIndex).locator('a').first();
      await expect(firstRowLink).toHaveAttribute('href', /\/MASWE\//);
      // Link text follows the "MASWE-000N: Title" convention
      await expect(firstRowLink).toHaveText(/^MASWE-\d{4}: .+/);
    });
  });
}

test.describe('MAS Profile Cross-References', () => {
  test('MAS-R should link to MAS-L1 and MAS-L2', async ({ page }) => {
    await page.goto('/Profiles/MAS-R/');
    const l1Link = page.locator('a:has-text("MAS-L1")').first();
    const l2Link = page.locator('a:has-text("MAS-L2")').first();
    await expect(l1Link).toHaveAttribute('href', /MAS-L1/);
    await expect(l2Link).toHaveAttribute('href', /MAS-L2/);
  });

  test('MAS-P should link to MAS-L1 and MAS-L2', async ({ page }) => {
    await page.goto('/Profiles/MAS-P/');
    const l1Link = page.locator('a:has-text("MAS-L1")').first();
    const l2Link = page.locator('a:has-text("MAS-L2")').first();
    await expect(l1Link).toHaveAttribute('href', /MAS-L1/);
    await expect(l2Link).toHaveAttribute('href', /MAS-L2/);
  });

  test('MAS-L2 should link to MAS-L1', async ({ page }) => {
    await page.goto('/Profiles/MAS-L2/');
    const l1Link = page.locator('a:has-text("MAS-L1")').first();
    await expect(l1Link).toHaveAttribute('href', /MAS-L1/);
  });
});
