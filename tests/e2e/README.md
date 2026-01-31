# End-to-End Tests

This directory contains Playwright end-to-end tests for the MAS website features.

## Test Coverage

### Tools Cross-References (`tools-cross-references.spec.ts`)

Tests for the "Used in" column functionality on the tools page:

- Verifies the "Used in" column is displayed
- Checks cross-reference counts for tools with references
- Validates "Unused" labels for tools without references
- Tests clickable links in the "Used in" column
- Verifies proper icon display for different reference types

### Show Unused Filter (`tools-show-unused-filter.spec.ts`)

Tests for the "Show Unused" filter functionality:

- Verifies the "Show Unused" checkbox exists
- Tests that unused tools are hidden by default
- Validates URL hash updates when filter is toggled
- Tests filter state restoration from URL hash
- Checks filter information display

### Multi-ID Search (`multi-id-search.spec.ts`)

Tests for comma-separated ID search functionality:

- Tests multi-ID search on techniques, tests, and demos pages
- Validates matching behavior for comma-separated IDs
- Tests navigation from "Used in" links
- Verifies search clearing when hash is removed

### Filter Bookmarking (`filter-bookmarking.spec.ts`)

Tests for URL hash-based filter bookmarking:

- Tests single and multiple filter bookmarking
- Validates filter restoration from URL hash
- Tests search query bookmarking
- Tests combination of filters and search in URL hash
- Validates "Clear All Filters" button functionality

## Running Tests

### Prerequisites

```bash
# Install dependencies
npm install
```

### Run all tests

```bash
npm test
```

### Run tests in UI mode

```bash
npm run test:ui
```

### Run tests in headed mode (see browser)

```bash
npm run test:headed
```

### Debug tests

```bash
npm run test:debug
```

## CI/CD Integration

Tests run automatically in GitHub Actions on:

- Push to main/master branches
- Pull requests to main/master branches

See `.github/workflows/playwright.yml` for the workflow configuration.
