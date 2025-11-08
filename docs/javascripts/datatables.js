
document$.subscribe(function() {
    // Only apply DataTables on MASTG index pages (whitelist)
    var currentPath = window.location.pathname;

    var mastgFolders = [
        'apps',
        'best-practices',
        'demos',
        'knowledge',
        'techniques',
        'tests',
        'tools'
    ];

    var isIndexPage = false;
    for (var i = 0; i < mastgFolders.length; i++) {
        if (currentPath.endsWith('/' + mastgFolders[i] + '/')) {
            isIndexPage = true;
            break;
        }
    }

    if (isIndexPage) {
        // Add DataTable to all tables, but not the advanced tests table
        $('table').not("#table_tests table").DataTable({
            paging: false, // Disable pagination
            order: [], // Disable auto-sorting
            dom: '<"top"if>rt<"bottom"lp><"clear">'
        });
    }
});