/**
 * MAS dynamic table filters (generic)
 *
 * Purpose
 * -------
 * This script adds a consistent, configurable filter bar above the dynamic
 * index tables rendered across the site (Tests, MASWE, Knowledge, Techniques,
 * Tools, Demos, Apps, Best Practices, Checklists). It replaces the built-in
 * DataTables search box with a richer UI that supports:
 *   - Status: Show Deprecated
 *   - Platform: Android, iOS, Network, Generic
 *   - Profile: L1, L2, R, P
 *   - Search: free-text search across ID/Title (+ a few optional columns)
 *
 * Pages targeted
 * --------------
 * Activation is limited to the following index page path prefixes (substring
 * matches against window.location.pathname):
 *   - /MASTG/tests/
 *   - /MASWE/
 *   - /MASTG/knowledge/
 *   - /MASTG/techniques/
 *   - /MASTG/tools/
 *   - /MASTG/demos/
 *   - /MASTG/apps/
 *   - /MASTG/best-practices/
 *   - /checklists/
 *
 * You can override/extend this mapping at runtime by defining
 * window.MAS_TABLE_FILTERS before this script loads, e.g.:
 *   window.MAS_TABLE_FILTERS = {
 *     '/MASTG/apps/': ['platform', 'search'],
 *     '/MASTG/tools/': ['platform', 'search']
 *   };
 *
 * Required HTML markers (rendered by mkdocs hooks)
 * -----------------------------------------------
 * The script relies on invisible tokens inserted into table cells:
 *   - Platform icons include a hidden <span> with e.g. 'platform:android'
 *   - Profile dots (L1/L2/R/P) include a hidden <span> with e.g. 'profile:L1'
 *     and visible colored dot classes:
 *       L1 -> mas-dot-blue, L2 -> mas-dot-green, R -> mas-dot-orange,
 *       P -> mas-dot-purple
 *   - Status cells include hidden markers like 'status:deprecated'
 * These are produced by helpers in docs/hooks/create_dynamic_tables.py.
 *
 * Column auto-detection
 * ---------------------
 * The script detects relevant columns by reading table headers (thead th):
 *   - ID (id), Title/Name (title/name), Platform (platform), Status (status)
 *   - Profile columns: exact headers 'L1', 'L2', 'R', 'P'
 *   - Optional: masvs id, mastg-test-id (to widen search coverage)
 * Only filter groups whose columns are present on a page are shown.
 *
 * Bookmarkable filters (URL hash)
 * -------------------------------
 * Selected filters are encoded in the hash and restored on load:
 *   - Platforms: android;ios;network;generic
 *   - Profiles: l1;l2;r;p
 *   - Status: deprecated
 *   - Search: q:your+query (URL encoded)
 * Examples:
 *   /MASTG/tests/#android;l2
 *   /MASWE/#ios;l1;q:crypto
 *   /MASTG/tools/#network
 *
 * DataTables integration
 * ----------------------
 * - For most pages, DataTables is initialized by docs/javascripts/datatables.js.
 *   This script waits for the 'init.dt' event before attaching filters.
 * - The Tests index table is excluded from that generic initializer; this
 *   script initializes it and then attaches filters.
 * - The default DataTables search box is removed per-table once our UI is
 *   injected.
 * - Each table gets a scoped custom filter function checked via
 *   settings.nTable === table to avoid cross-table interference.
 * - To avoid stacking filters across SPA navigations (navigation.instant),
 *   we remove previously registered custom filters marked with _masCustomFilter
 *   on each activation.
 *
 * SPA/instantiation timing
 * ------------------------
 * MkDocs Material navigation can render content asynchronously. We use a short
 * retry loop (up to ~1.5s total) to wait for the tables to appear before
 * binding. This keeps the UI stable on fast route changes.
 *
 * Matching rules
 * --------------
 * - Status: deprecated rows are hidden unless 'Show Deprecated' is checked.
 * - Platform: match on hidden 'platform:xxx' tokens in the Platform cell.
 * - Profile: match on hidden 'profile:XX' tokens or the color dot class mapped
 *   to the profile. If there are no profile columns, the profile filter is a
 *   no-op for that page.
 * - Search: case-insensitive substring across detected ID/Title/Control/
 *   MASVS/MASTG-Test-ID columns.
 *
 * Extensibility
 * -------------
 * - Add a new page: include its path prefix in DEFAULT_PAGE_CONFIG.
 * - Add a new group: extend UI creation and update the filtering predicate.
 * - Add a new platform: ensure the generator inserts 'platform:newvalue' into
 *   the Platform cell; add a checkbox in the Platform group.
 *
 * Maintenance notes
 * -----------------
 * - Be careful with header detection for single-letter columns (R, P) — we use
 *   exact matches to avoid clashes with 'platform'.
 * - If a future generator change moves hidden tokens, the profile fallback
 *   also searches all row cells to remain robust.
 * - The Tests page can change its wrapper id; detection checks #table_tests and
 *   related variants.
 */

// Generic, auto-detecting filters for all dynamic tables (tests, weaknesses, techniques, tools, demos, apps, best practices, knowledge, checklists)
// Works with MkDocs Material navigation (document$) and jQuery DataTables.

(function () {
  const GLOBAL = window || {};

  // Optional page-specific configuration. If a page path matches a key (substring), the listed groups are enabled.
  // If not specified, groups are auto-enabled when their columns are present.
  const DEFAULT_PAGE_CONFIG = {
    '/MASTG/tests/': ['status', 'platform', 'profile', 'search'],
    '/MASWE/': ['status', 'platform', 'profile', 'search'],
    '/MASTG/knowledge/': ['platform', 'search'],
    '/MASTG/tools/': ['used_in', 'platform', 'search'],
    '/MASTG/techniques/': ['used_in', 'platform', 'search'],
    '/MASTG/demos/': ['status', 'platform', 'search'],
    '/MASTG/best-practices/': ['platform', 'search'],
    '/MASTG/apps/': ['platform', 'search'],
    '/checklists/': ['status', 'platform', 'profile', 'search']
  };

  // Allow runtime overrides via window.MAS_TABLE_FILTERS = { pathSubstring: ['group', ...] }
  const PAGE_CONFIG = Object.assign({}, DEFAULT_PAGE_CONFIG, GLOBAL.MAS_TABLE_FILTERS || {});

  // Tokens supported in URL hash, applied across pages
  const HASH_TOKENS = ['android', 'ios', 'network', 'generic', 'l1', 'l2', 'r', 'p', 'deprecated', 'unused'];

  // Utility: case-insensitive includes on HTML/text
  function cellIncludes(htmlOrText, token) {
    if (!htmlOrText) return false;
    const s = ('' + htmlOrText).toLowerCase();
    return s.includes(token.toLowerCase());
  }

  // Detect columns by header text
  function detectColumns(table) {
    const ths = table.querySelectorAll('thead th');
    const map = {};
    ths.forEach((th, idx) => {
      const label = (th.textContent || '').trim().toLowerCase();
      map[idx] = label;
    });

    function findExact(label) {
      for (const [idx, l] of Object.entries(map)) {
        if (l === label) return parseInt(idx, 10);
      }
      return null;
    }

    function findAnyEquals(labels) {
      const arr = Array.isArray(labels) ? labels : [labels];
      for (const lab of arr) {
        const idx = findExact(lab);
        if (idx != null) return idx;
      }
      return null;
    }

    function findIncludes(labels) {
      const arr = Array.isArray(labels) ? labels : [labels];
      for (const [idx, l] of Object.entries(map)) {
        if (arr.some(lbl => l.includes(lbl))) return parseInt(idx, 10);
      }
      return null;
    }

    return {
      id: findExact('id'),
      title: findAnyEquals(['title', 'name']),
      control: findIncludes(['control / mastg test']) ?? findExact('control'),
      platform: findExact('platform'),
      status: findExact('status'),
      used_in: findAnyEquals(['used in']),
      L1: findExact('l1'),
      L2: findExact('l2'),
      R: findExact('r'),
      P: findExact('p'),
      masvs: findAnyEquals(['masvs v2 id', 'masvs-id']) ?? findIncludes(['masvs']),
      mastgTestId: findAnyEquals(['mastg-test-id']) ?? findIncludes(['mastg test id']),
    };
  }

  // Build UI group helper
  function createGroup(labelText) {
    const groupContainer = document.createElement('div');
    groupContainer.className = 'filter-group';
    groupContainer.style.display = 'flex';
    groupContainer.style.alignItems = 'center';
    groupContainer.style.gap = '0.5rem';

    const groupLabel = document.createElement('span');
    groupLabel.textContent = labelText;
    groupLabel.style.fontWeight = 'bold';
    groupLabel.style.minWidth = '70px';
    groupLabel.style.color = 'var(--md-default-fg-color, rgba(0, 0, 0, 0.87))';
    groupContainer.appendChild(groupLabel);
    return { groupContainer };
  }

  function createCheckbox(id, label, dataset) {
    const toggleLabel = document.createElement('label');
    toggleLabel.className = 'md-toggle__label';
    toggleLabel.style.display = 'flex';
    toggleLabel.style.alignItems = 'center';
    toggleLabel.style.cursor = 'pointer';
    toggleLabel.style.marginRight = '0.5rem';
    toggleLabel.style.padding = '0.25rem 0.5rem';
    toggleLabel.style.border = '1px solid var(--md-default-fg-color--lightest, rgba(0, 0, 0, 0.1))';
    toggleLabel.style.borderRadius = '4px';
    toggleLabel.style.backgroundColor = 'var(--md-default-bg-color, white)';
    toggleLabel.style.transition = 'background-color 0.2s, border-color 0.2s';
    toggleLabel.style.color = 'var(--md-default-fg-color, rgba(0, 0, 0, 0.87))';

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = id;
    Object.assign(checkbox.dataset, dataset || {});
    checkbox.style.marginRight = '6px';

    toggleLabel.addEventListener('mouseover', function () {
      if (!checkbox.checked) {
        toggleLabel.style.backgroundColor = 'var(--md-default-fg-color--lightest, rgba(0, 0, 0, 0.05))';
      }
    });
    toggleLabel.addEventListener('mouseout', function () {
      if (!checkbox.checked) {
        toggleLabel.style.backgroundColor = 'var(--md-default-bg-color, white)';
      }
    });
    checkbox.addEventListener('change', function () {
      if (checkbox.checked) {
        toggleLabel.style.backgroundColor = 'var(--md-primary-fg-color--transparent, rgba(13, 110, 253, 0.1))';
        toggleLabel.style.borderColor = 'var(--md-primary-fg-color--light, rgba(13, 110, 253, 0.5))';
      } else {
        toggleLabel.style.backgroundColor = 'var(--md-default-bg-color, white)';
        toggleLabel.style.borderColor = 'var(--md-default-fg-color--lightest, rgba(0, 0, 0, 0.1))';
      }
    });

    const labelText = document.createTextNode(label);
    toggleLabel.appendChild(checkbox);
    toggleLabel.appendChild(labelText);
    return { toggleLabel, checkbox };
  }

  // Parse hash tokens
  function parseHash() {
    const raw = (window.location.hash || '').replace(/^#/, '').trim();
    if (!raw) return { tokens: [], query: '' };
    const parts = raw.split(';').filter(Boolean);
    let q = '';
    const tokens = [];
    parts.forEach(p => {
      if (p.startsWith('q:')) q = decodeURIComponent(p.substring(2));
      else tokens.push(p.toLowerCase());
    });
    return { tokens, query: q };
  }

  function updateHash(tokens, query) {
    const parts = [...new Set(tokens.filter(Boolean))];
    if (query && query.trim()) parts.push('q:' + encodeURIComponent(query.trim()))
    const value = parts.join(';');
    history.replaceState(null, null, value ? ('#' + value) : '#');
  }

  // Main initializer: find all candidate tables and enhance
  function configureDynamicTables() {
    // Clean previously registered custom filters (from prior SPA navigations)
    if ($.fn && $.fn.dataTable && $.fn.dataTable.ext && Array.isArray($.fn.dataTable.ext.search)) {
      $.fn.dataTable.ext.search = $.fn.dataTable.ext.search.filter(fn => !fn._masCustomFilter);
    }

    const { tokens: initialTokens, query: initialQuery } = parseHash();
    const path = window.location.pathname || '';
    // Activate only on specific index pages defined in PAGE_CONFIG
    let pageGroups = null;
    for (const [key, groups] of Object.entries(PAGE_CONFIG)) {
      if (path.indexOf(key) !== -1) { pageGroups = groups; break; }
    }
    if (!pageGroups) return;

    function attemptSetup(attempt) {
      const pageRoot = document.querySelector('main, article, body') || document.body;
      const allTables = Array.from(pageRoot.querySelectorAll('table'))
        .filter(t => !t.classList.contains('mas-filters-initialized'));
      if (!allTables.length) {
        if (attempt < 20) {
          setTimeout(() => attemptSetup(attempt + 1), 75);
        }
        return;
      }

      allTables.forEach((table, tIndex) => {
        const $table = $(table);
        const isTestsTable = $table.closest('#table_tests, div#table_tests, [id^="table_tests"]').length > 0;

        // Encapsulate setup that requires a ready DataTable instance
        function setup(dtApi) {
          // Detect columns early
          const cols = detectColumns(table);

          // Determine which groups to show (auto if not configured)
          const show = {
            status: !!cols.status,
            used_in: !!cols.used_in,
            platform: !!cols.platform,
            profile: !!(cols.L1 || cols.L2 || cols.R || cols.P),
            search: true
          };
          if (pageGroups) {
            Object.keys(show).forEach(k => show[k] = pageGroups.includes(k) && show[k]);
          }

          // If nothing applicable, skip this table
          if (!show.status && !show.used_in && !show.platform && !show.profile && !show.search) return;

          // Remove default search box next to this table only
          const wrapper = $table.closest('.dataTables_wrapper');
          if (wrapper.length) {
            const df = wrapper.find('.dataTables_filter');
            if (df.length) df.parent().remove();
          } else {
            // As a fallback, try removing any sibling default filters (unexpected structure)
            const globalDf = $table.parent().find('.dataTables_filter');
            if (globalDf.length) globalDf.parent().remove();
          }

          // Build container UI
          const container = document.createElement('div');
          container.className = 'mastg-filters-wrapper';
          container.style.padding = '1rem';
          container.style.marginBottom = '1.5rem';
          container.style.backgroundColor = 'var(--md-default-fg-color--lightest, rgba(0, 0, 0, 0.05))';
          container.style.borderRadius = '4px';
          container.style.color = 'var(--md-default-fg-color, rgba(0, 0, 0, 0.87))';

          const row = document.createElement('div');
          row.className = 'mastg-filters';
          row.style.display = 'flex';
          row.style.flexWrap = 'wrap';
          row.style.gap = '1rem';
          row.style.alignItems = 'center';
          row.style.width = '100%';
          // Add some vertical breathing room from the row below (info/clear)
          row.style.marginBottom = '0.75rem';

          container.appendChild(row);

          // Active state per table
          const state = {
            showDeprecated: false,
            showUnused: path.indexOf('/MASTG/techniques/') !== -1, // Default to true for techniques page
            platforms: [], // values: android, ios, network, generic
            profiles: [], // values: L1,L2,R,P
            search: ''
          };

          // Status group (Show Deprecated)
          if (show.status) {
            const { groupContainer } = createGroup('Status:');
            
            // Show Deprecated checkbox
            const { toggleLabel: deprecatedLabel, checkbox: deprecatedCheckbox } = createCheckbox(`mas-filter-${tIndex}-status-deprecated`, 'Show Deprecated', {
              type: 'status', token: 'deprecated'
            });
            deprecatedCheckbox.addEventListener('change', () => {
              state.showDeprecated = deprecatedCheckbox.checked;
              applyFilters();
            });
            groupContainer.appendChild(deprecatedLabel);
            
            row.appendChild(groupContainer);
          }

          // Used In group (Show Unused)
          if (show.used_in) {
            const { groupContainer } = createGroup('Used In:');
            
            // Show Unused checkbox
            const { toggleLabel: unusedLabel, checkbox: unusedCheckbox } = createCheckbox(`mas-filter-${tIndex}-used_in-unused`, 'Show Unused', {
              type: 'used_in', token: 'unused'
            });
            unusedCheckbox.addEventListener('change', () => {
              state.showUnused = unusedCheckbox.checked;
              applyFilters();
            });
            groupContainer.appendChild(unusedLabel);
            
            row.appendChild(groupContainer);
          }

          // Platform group (auto-detect platforms present)
          if (show.platform) {
            const { groupContainer } = createGroup('Platform:');
            const platforms = ['android', 'ios', 'network', 'generic'];
            const present = new Set();
            // Scan all rows for hidden platform:xxx tokens
            dtApi.rows().every(function () {
              const data = this.data();
              const html = (data[cols.platform] || '').toString().toLowerCase();
              platforms.forEach(p => { if (html.includes(`platform:${p}`)) present.add(p); });
            });
            platforms.filter(p => present.has(p)).forEach(p => {
              // Special-case formatting: display 'ios' as 'iOS' (not 'Ios')
              const label = p === 'ios' ? 'iOS' : (p.charAt(0).toUpperCase() + p.slice(1));
              const { toggleLabel, checkbox } = createCheckbox(`mas-filter-${tIndex}-platform-${p}`, label, {
                type: 'platform', value: p, token: p
              });
              checkbox.addEventListener('change', () => {
                const v = checkbox.dataset.value;
                if (checkbox.checked) {
                  if (!state.platforms.includes(v)) state.platforms.push(v);
                } else {
                  state.platforms = state.platforms.filter(x => x !== v);
                }
                applyFilters();
              });
              groupContainer.appendChild(toggleLabel);
            });
            row.appendChild(groupContainer);
          }

          // Profile group
          if (show.profile) {
            const { groupContainer } = createGroup('Profile:');
            const profiles = [
              cols.L1 != null ? 'L1' : null,
              cols.L2 != null ? 'L2' : null,
              cols.R != null ? 'R' : null,
              cols.P != null ? 'P' : null,
            ].filter(Boolean);
            profiles.forEach(p => {
              const { toggleLabel, checkbox } = createCheckbox(`mas-filter-${tIndex}-profile-${p.toLowerCase()}`, p, {
                type: 'profile', value: p, token: p.toLowerCase()
              });
              checkbox.addEventListener('change', () => {
                const v = checkbox.dataset.value;
                if (checkbox.checked) {
                  if (!state.profiles.includes(v)) state.profiles.push(v);
                } else {
                  state.profiles = state.profiles.filter(x => x !== v);
                }
                applyFilters();
              });
              groupContainer.appendChild(toggleLabel);
            });
            row.appendChild(groupContainer);
          }

          // Search group
          let searchInput = null;
          if (show.search) {
            const searchContainer = document.createElement('div');
            searchContainer.className = 'filter-group';
            searchContainer.style.display = 'flex';
            searchContainer.style.alignItems = 'center';
            searchContainer.style.gap = '0.5rem';
            // Keep the search controls docked to the right edge of the filters row
            searchContainer.style.marginLeft = 'auto';

            const searchLabel = document.createElement('span');
            searchLabel.textContent = 'Search:';
            searchLabel.style.fontWeight = 'bold';
            searchLabel.style.minWidth = '70px';
            searchLabel.style.color = 'var(--md-default-fg-color, rgba(0, 0, 0, 0.87))';

            searchInput = document.createElement('input');
            searchInput.type = 'text';
            searchInput.id = `mas-filter-${tIndex}-search`;
            searchInput.style.fontWeight = 'bold';
            searchInput.style.minWidth = '300px';
            searchInput.style.padding = '10px';
            searchInput.style.border = '1px solid #ccc';
            searchInput.style.borderRadius = '5px';
            searchInput.addEventListener('keyup', () => {
              state.search = (searchInput.value || '').toLowerCase();
              applyFilters();
            });

            searchContainer.appendChild(searchLabel);
            searchContainer.appendChild(searchInput);
            row.appendChild(searchContainer);
          }

          // Bottom row
          const bottomRow = document.createElement('div');
          bottomRow.style.display = 'flex';
          bottomRow.style.justifyContent = 'space-between';
          bottomRow.style.alignItems = 'center';
          bottomRow.style.width = '100%';
          // Extra separation from the filter controls above
          bottomRow.style.marginTop = '0.75rem';

          const infoSpan = document.createElement('span');
          infoSpan.id = `mas-filter-${tIndex}-info`;
          // Do not emphasize 'Showing' text
          infoSpan.style.fontWeight = 'normal';
          infoSpan.style.color = 'var(--md-default-fg-color, rgba(0, 0, 0, 0.87))';

          const clearButton = document.createElement('button');
          clearButton.textContent = 'Clear All Filters';
          clearButton.style.padding = '0.3rem 0.75rem';
          clearButton.style.border = '1px solid var(--md-default-fg-color--lightest, rgba(0, 0, 0, 0.1))';
          clearButton.style.borderRadius = '4px';
          clearButton.style.backgroundColor = 'var(--md-default-fg-color--lightest, #f8f8f8)';
          clearButton.style.color = 'var(--md-default-fg-color, rgba(0, 0, 0, 0.87))';
          clearButton.style.cursor = 'pointer';
          clearButton.style.transition = 'background-color 0.2s';
          clearButton.addEventListener('mouseover', function () {
            clearButton.style.backgroundColor = 'var(--md-accent-fg-color--transparent, #e9e9e9)';
          });
          clearButton.addEventListener('mouseout', function () {
            clearButton.style.backgroundColor = 'var(--md-default-fg-color--lightest, #f8f8f8)';
          });
          clearButton.addEventListener('click', function () {
            // Uncheck all inputs in this container
            container.querySelectorAll('input[type="checkbox"]').forEach(cb => { cb.checked = false; cb.dispatchEvent(new Event('change')); });
            if (searchInput) searchInput.value = '';
            state.showDeprecated = false;
            state.showUnused = false;
            state.platforms = [];
            state.profiles = [];
            state.search = '';
            applyFilters();
          });

          bottomRow.appendChild(infoSpan);
          bottomRow.appendChild(clearButton);
          container.appendChild(bottomRow);

          // Insert container before this table's wrapper
          const wrapperNode = wrapper.get(0);
          if (wrapperNode && wrapperNode.parentNode) {
            wrapperNode.parentNode.insertBefore(container, wrapperNode);
          } else if (table && table.parentNode) {
            // Fallback: insert right before the table element
            table.parentNode.insertBefore(container, table);
          }

          // DataTables custom filter for this specific table
          const customFilter = Object.assign(function (settings, rowData /*, dataIndex*/) {
            if (settings.nTable !== table) return true; // Only filter this table

            // Status: hide deprecated unless explicitly shown
            if (cols.status != null && !state.showDeprecated) {
              const statusHtml = (rowData[cols.status] || '').toString().toLowerCase();
              if (statusHtml.includes('status:deprecated')) return false;
            }

            // Status: hide unused unless explicitly shown (for tools page)
            if (cols.used_in != null && !state.showUnused) {
              const usedInHtml = (rowData[cols.used_in] || '').toString().toLowerCase();
              if (usedInHtml.includes('unused')) return false;
            }

            // Platform filter
            if (cols.platform != null && state.platforms.length > 0) {
              const platformHtml = (rowData[cols.platform] || '').toString().toLowerCase();
              const matched = state.platforms.some(p => platformHtml.includes(`platform:${p}`));
              if (!matched) return false;
            }

            // Profiles filter
            if (state.profiles.length > 0) {
              const colIndexByProfile = { L1: cols.L1, L2: cols.L2, R: cols.R, P: cols.P };
              // If none of the profile columns are present, don't filter by profile
              const anyProfileCol = Object.values(colIndexByProfile).some(v => v != null);
              if (!anyProfileCol) return true;
              const colorByProfile = { L1: 'blue', L2: 'green', R: 'orange', P: 'purple' };
              const matched = state.profiles.some(level => {
                const idx = colIndexByProfile[level];
                const token = `profile:${level.toLowerCase()}`;
                if (idx != null) {
                  const cell = (rowData[idx] || '').toString().toLowerCase();
                  if (cell.includes(token) || cell.includes(`mas-dot-${colorByProfile[level]}`)) return true;
                }
                // Fallback: search entire row string when a specific column index was not available or empty
                const wholeRow = rowData.map(c => (c || '').toString().toLowerCase()).join(' ');
                return wholeRow.includes(token);
              });
              if (!matched) return false;
            }

            // Search across common columns
            // Multi-ID Search Feature:
            // Supports both substring search and comma-separated ID list search.
            // Format: "#q:mastg-tech-0001,mastg-tech-0002,mastg-test-0100"
            // Behavior: Matches if ANY of the comma-separated IDs is found in ANY candidate field
            // (ID, Title, Control, MASVS ID, or MASTG-TEST-ID columns)
            if (state.search && state.search.length > 0) {
              const searchTerm = state.search.trim();
              const candidates = [cols.id, cols.title, cols.control, cols.masvs, cols.mastgTestId]
                .filter(idx => idx != null)
                .map(idx => (rowData[idx] || '').toString().toLowerCase());
              
              // Check if search contains commas (multi-ID search)
              if (searchTerm.includes(',')) {
                // Split by comma and check if any ID matches
                const ids = searchTerm.split(',').map(id => id.trim()).filter(id => id.length > 0);
                const ok = ids.some(searchId => candidates.some(text => text.includes(searchId)));
                if (!ok) return false;
              } else {
                // Regular substring search
                const ok = candidates.some(text => text.includes(searchTerm));
                if (!ok) return false;
              }
            }

            return true;
          }, { _masCustomFilter: true, _masTableIndex: tIndex });
          $.fn.dataTable.ext.search.push(customFilter);

          function updateInfo() {
            const infoNode = document.getElementById(`mas-filter-${tIndex}-info`);
            if (!infoNode) return;
            const filteredCount = dtApi.rows({ filter: 'applied' }).count();
            const totalCount = dtApi.rows().count();
            if (filteredCount < totalCount) {
              infoNode.textContent = `Showing ${filteredCount} of ${totalCount} entries (filtered)`;
            } else {
              infoNode.textContent = `Showing 1 to ${totalCount} of ${totalCount} entries`;
            }
          }

          function applyFilters() {
            // Update hash
            const tokens = [];
            if (state.showDeprecated) tokens.push('deprecated');
            if (state.showUnused) tokens.push('unused');
            state.platforms.forEach(p => tokens.push(p));
            state.profiles.forEach(p => tokens.push(p.toLowerCase()));
            updateHash(tokens, state.search);
            dtApi.draw();
            updateInfo();
          }

          // Apply initial hash tokens
          if (initialTokens.length) {
            if (show.status && initialTokens.includes('deprecated')) state.showDeprecated = true;
            if (show.used_in && initialTokens.includes('unused')) state.showUnused = true;
            if (show.platform) state.platforms = initialTokens.filter(t => ['android', 'ios', 'network', 'generic'].includes(t));
            if (show.profile) state.profiles = initialTokens.filter(t => ['l1', 'l2', 'r', 'p'].includes(t)).map(s => s.toUpperCase());
          }
          if (show.search && initialQuery) {
            state.search = initialQuery.toLowerCase();
            if (searchInput) searchInput.value = initialQuery;
          }

          // Reflect initial states in checkboxes
          container.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            const token = (cb.dataset.token || '').toLowerCase();
            if (!token) return;
            const shouldCheck = initialTokens.includes(token);
            if (shouldCheck) {
              cb.checked = true;
              cb.dispatchEvent(new Event('change'));
            }
          });

          // Initial draw/info
          applyFilters();

          // Mark initialized
          table.classList.add('mas-filters-initialized');
        }

        // Initialize or wait for DataTables
        if ($.fn.dataTable.isDataTable(table)) {
          setup($table.DataTable());
        } else if (isTestsTable) {
          // For the tests index, this table is excluded from the generic datatables init,
          // so we initialize it here and ensure setup runs after init. Bind the handler BEFORE init.
          $table.one('init.dt', function () { setup($table.DataTable()); });
          $table.DataTable({
            paging: false,
            order: [],
            dom: '<"top"if>rt<"bottom"lp><"clear">',
            info: false,
            search: true
          });
        } else {
          // Let datatables.js initialize it; then run setup
          $table.one('init.dt', function () {
            setup($table.DataTable());
          });
        }
      });
    }

    attemptSetup(0);
  }

  // Re-run on mkdocs page changes
  if (typeof document$ !== 'undefined' && document$.subscribe) {
    document$.subscribe(function () {
      configureDynamicTables();
    });
  } else {
    // Fallback for direct page load
    document.addEventListener('DOMContentLoaded', configureDynamicTables);
  }
})();
