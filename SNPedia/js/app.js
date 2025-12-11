console.log('Script loaded');
let table;

// Check if Tabulator is available
if (typeof Tabulator === 'undefined') {
  console.error('Tabulator not loaded!');
  alert('Tabulator library failed to load. Check network tab.');
} else {
  console.log('Tabulator available');
}

// Initialize Tabulator
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM loaded, initializing table...');

  // Load saved theme first
  loadSavedTheme();

  try {
    table = new Tabulator("#grid", {
      layout: "fitColumns",
      layoutColumnsOnNewData: true,
      height: "100%",
      pagination: true,
      paginationSize: 50,
      paginationSizeSelector: [25, 50, 100, 250],
      movableColumns: true,
      resizableColumnFit: true,
      selectable: true,
      selectableRollingSelection: false,
      columns: [
        {
          title: "Name",
          field: "Name",
          visible: true,
          headerFilter: "input",
          width: 120
        },
        {
          title: "Short Description",
          field: "Description",
          headerFilter: "input",
          widthGrow: 2,
          formatter: "html"
        },
        {
          title: "Stabilized Orientation",
          field: "StabilizedOrientation",
          visible: false,
          headerFilter: "input"
        },
        {
          title: "Individual Genotype",
          field: "Genotype",
          visible: false,
          headerFilter: "input",
          formatter: "html"
        },
        {
          title: "Genotype variations",
          field: "Variations",
          headerFilter: "input",
          widthGrow: 1,
          formatter: "html"
        },
        {
          title: "Interesting genotype",
          field: "IsInteresting",
          visible: false,
          headerFilter: "list",
          headerFilterParams: {
            values: {
              "": "All",
              "Yes": "Yes",
              "No": "No"
            },
            clearable: true,
            placeholder: "Filter..."
          }
        },
        {
          title: "Uncommon genotype",
          field: "IsUncommon",
          visible: false,
          headerFilter: "list",
          headerFilterParams: {
            values: {
              "": "All",
              "Yes": "Yes",
              "No": "No"
            },
            clearable: true,
            placeholder: "Filter..."
          }
        }
      ],
      initialSort: [
        { column: "IsUncommon", dir: "desc" }
      ],
      cellClick: function(e, cell) {
        console.log('Cell clicked!');
        const row = cell.getRow();
        console.log('Row data:', row.getData());
        // Deselect all rows first, then select clicked row
        table.deselectRow();
        row.select();
        console.log('Row selected, isSelected:', row.isSelected());
        console.log('Selected rows:', table.getSelectedRows().length);
      },
      rowSelectionChanged: function(data, rows) {
        console.log('Selection changed:', rows.length, 'rows selected');
      }
    });

    console.log('Table initialized');

    // Show loading spinner
    const spinner = document.getElementById('loadingSpinner');
    spinner.classList.remove('hidden');

    // Load data
    fetch('/api/rsids')
      .then(response => {
        console.log('Response status:', response.status);
        return response.json();
      })
      .then(data => {
        console.log('Data received:', data.results ? data.results.length + ' rows' : 'no results');
        // Hide loading spinner
        spinner.classList.add('hidden');

        if (data.results && data.results.length > 0) {
          table.setData(data.results);
          console.log('Data loaded into table');

          // Set up filter change listeners
          table.on("headerFilterChanged", function(field, value) {
            console.log('Filter changed:', field, value);
            updateFilterButtonState();
          });

          // Initial filter button state check
          setTimeout(function() {
            updateFilterButtonState();
          }, 100);

          // Add a test to verify selectable is working
          setTimeout(function() {
            console.log('Table selectable config:', table.options.selectable);
            console.log('Total rows:', table.getRows().length);

            // Add direct DOM listener to handle row selection
            const gridElement = document.getElementById('grid');
            gridElement.addEventListener('click', function(e) {
              console.log('Click detected!', e.target.className);

              // Find the row element
              let rowElement = e.target;
              while (rowElement && !rowElement.classList.contains('tabulator-row')) {
                rowElement = rowElement.parentElement;
              }

              if (rowElement && rowElement.classList.contains('tabulator-row')) {
                console.log('Row element found!');
                // Get the row component from Tabulator
                const rows = table.getRows();
                for (let i = 0; i < rows.length; i++) {
                  if (rows[i].getElement() === rowElement) {
                    console.log('Matching row found, selecting...');
                    table.deselectRow();
                    rows[i].select();
                    console.log('Row selected!');
                    break;
                  }
                }
              }
            });
          }, 1000);
        } else {
          console.warn('No data to display');
        }
      })
      .catch(error => {
        // Hide loading spinner on error
        spinner.classList.add('hidden');
        console.error('Error loading data:', error);
        alert('Error loading data: ' + error.message);
      });
  } catch (error) {
    console.error('Error initializing table:', error);
    alert('Error initializing table: ' + error.message);
  }
});

// Export to Excel
function exportToExcel() {
  if (table) {
    table.download("xlsx", "SNP Report.xlsx", {
      sheetName: "SNP Data"
    });
  }
}

// Lookup selected SNP on SNPedia
function lookupSNPedia() {
  if (!table) return;

  // Try to get selected rows first
  let selectedRows = table.getSelectedData();

  // If no selection, prompt user to enter RSid
  if (selectedRows.length === 0) {
    const rsid = prompt('Enter RSid (e.g., rs3131972) or click a row first:');
    if (rsid && rsid.trim()) {
      const url = 'https://snpedia.com/index.php/' + rsid.trim();
      window.open(url, '_blank');
    }
    return;
  }

  const rsid = selectedRows[0].Name;
  const url = 'https://snpedia.com/index.php/' + rsid;
  window.open(url, '_blank');
}

// Show keyboard shortcuts help
function showKeyboardShortcuts() {
  const modal = document.getElementById('shortcutsModal');
  modal.classList.add('show');
}

// Hide keyboard shortcuts modal
function hideKeyboardShortcuts() {
  const modal = document.getElementById('shortcutsModal');
  modal.classList.remove('show');
}

// Close modal when clicking outside
document.addEventListener('click', function(e) {
  const modal = document.getElementById('shortcutsModal');
  if (e.target === modal) {
    hideKeyboardShortcuts();
  }
});

// Reload table data
function reloadData() {
  if (!table) return;

  const spinner = document.getElementById('loadingSpinner');
  spinner.classList.remove('hidden');

  fetch('/api/rsids')
    .then(response => response.json())
    .then(data => {
      spinner.classList.add('hidden');
      if (data.results && data.results.length > 0) {
        table.setData(data.results);
        console.log('Data reloaded');
        // Update filter button state after reload
        setTimeout(function() {
          updateFilterButtonState();
        }, 100);
      }
    })
    .catch(error => {
      spinner.classList.add('hidden');
      console.error('Error reloading data:', error);
      alert('Error reloading data: ' + error.message);
    });
}

// Focus first header filter input
function focusSearch() {
  const firstFilter = document.querySelector('.tabulator-header-filter input');
  if (firstFilter) {
    firstFilter.focus();
  }
}

// Clear all filters
function clearAllFilters() {
  if (!table) return;

  console.log('Clearing all filters...');

  // Check if there were any active filters before clearing
  const hadActiveFilters = table.getHeaderFilters().some(filter =>
    filter.value !== undefined && filter.value !== null && filter.value !== ""
  );

  // Clear all header filters
  table.clearHeaderFilter();

  // Update filter button state
  updateFilterButtonState();

  // Show feedback if filters were actually cleared
  if (hadActiveFilters) {
    showFilterNotification('All filters cleared');
  } else {
    showFilterNotification('No active filters to clear');
  }

  console.log('All filters cleared');
}

// Show a brief notification about filter actions
function showFilterNotification(message) {
  // Create or get existing notification element
  let notification = document.getElementById('filterNotification');
  if (!notification) {
    notification = document.createElement('div');
    notification.id = 'filterNotification';
    notification.className = 'filter-notification';
    document.body.appendChild(notification);
  }

  notification.textContent = message;
  notification.classList.add('show');

  // Hide after 2 seconds
  setTimeout(function() {
    notification.classList.remove('show');
  }, 2000);
}

// Check if any filters are active and update button state
function updateFilterButtonState() {
  if (!table) return;

  const clearButton = document.querySelector('button[onclick="clearAllFilters()"]');
  if (!clearButton) return;

  // Check if any header filters have values
  const hasActiveFilters = table.getHeaderFilters().some(filter =>
    filter.value !== undefined && filter.value !== null && filter.value !== ""
  );

  if (hasActiveFilters) {
    clearButton.classList.add('filters-active');
    clearButton.title = 'Clear All Filters (Ctrl+X) - Filters Active';
  } else {
    clearButton.classList.remove('filters-active');
    clearButton.title = 'Clear All Filters (Ctrl+X)';
  }
}

// Clear selection and close menus
function clearSelectionAndMenus() {
  if (table) {
    table.deselectRow();
  }

  const menu = document.getElementById('columnMenu');
  if (menu && menu.classList.contains('show')) {
    menu.classList.remove('show');
  }
}

// Dark mode toggle functionality
function toggleDarkMode() {
  const html = document.documentElement;
  const currentTheme = html.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

  html.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);

  console.log('Theme switched to:', newTheme);
}

// Load saved theme on page load
function loadSavedTheme() {
  const savedTheme = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const theme = savedTheme || (prefersDark ? 'dark' : 'light');

  document.documentElement.setAttribute('data-theme', theme);
  console.log('Theme loaded:', theme);
}

// Keyboard shortcuts handler
document.addEventListener('keydown', function(e) {
  // Check for Ctrl (Windows/Linux) or Cmd (Mac)
  const modifier = e.ctrlKey || e.metaKey;

  // Ctrl/Cmd + E: Export to Excel
  if (modifier && e.key === 'e') {
    e.preventDefault();
    exportToExcel();
    return;
  }

  // Ctrl/Cmd + L: Lookup on SNPedia
  if (modifier && e.key === 'l') {
    e.preventDefault();
    lookupSNPedia();
    return;
  }

  // Ctrl/Cmd + F: Focus search
  if (modifier && e.key === 'f') {
    e.preventDefault();
    focusSearch();
    return;
  }

  // Ctrl/Cmd + K: Toggle column menu
  if (modifier && e.key === 'k') {
    e.preventDefault();
    toggleColumnMenu();
    return;
  }

  // Ctrl/Cmd + X: Clear all filters
  if (modifier && e.key === 'x') {
    e.preventDefault();
    clearAllFilters();
    return;
  }

  // Ctrl/Cmd + R: Reload data
  if (modifier && e.key === 'r') {
    e.preventDefault();
    reloadData();
    return;
  }

  // Ctrl/Cmd + /: Show keyboard shortcuts
  if (modifier && e.key === '/') {
    e.preventDefault();
    showKeyboardShortcuts();
    return;
  }

  // Ctrl/Cmd + D: Toggle dark mode
  if (modifier && e.key === 'd') {
    e.preventDefault();
    toggleDarkMode();
    return;
  }

  // Escape: Clear selection and close menus/modals
  if (e.key === 'Escape') {
    const modal = document.getElementById('shortcutsModal');
    if (modal && modal.classList.contains('show')) {
      hideKeyboardShortcuts();
    } else {
      clearSelectionAndMenus();
    }
    return;
  }
});

// Toggle column visibility menu
function toggleColumnMenu() {
  const menu = document.getElementById('columnMenu');
  menu.classList.toggle('show');
}

// Close menu when clicking outside
window.onclick = function(event) {
  if (!event.target.matches('.column-menu button')) {
    const menu = document.getElementById('columnMenu');
    if (menu.classList.contains('show')) {
      menu.classList.remove('show');
    }
  }
}

// Load column visibility from localStorage
function loadColumnVisibility() {
  const saved = localStorage.getItem('columnVisibility');
  if (saved) {
    return JSON.parse(saved);
  }
  // Default visibility
  return {
    'Name': true,
    'Description': true,
    'StabilizedOrientation': false,
    'Genotype': false,
    'Variations': true,
    'IsInteresting': false,
    'IsUncommon': false
  };
}

// Save column visibility to localStorage
function saveColumnVisibility(columnName, visible) {
  const visibility = loadColumnVisibility();
  visibility[columnName] = visible;
  localStorage.setItem('columnVisibility', JSON.stringify(visibility));
}

// Handle column visibility changes
document.addEventListener('DOMContentLoaded', function() {
  // Wait for table to be initialized
  setTimeout(function() {
    // Load saved visibility state
    const visibility = loadColumnVisibility();

    // Update checkboxes and table columns based on saved state
    const checkboxes = document.querySelectorAll('#columnMenu input[type="checkbox"]');
    checkboxes.forEach(function(checkbox) {
      const columnName = checkbox.getAttribute('data-column');
      const isVisible = visibility[columnName];

      // Update checkbox state
      checkbox.checked = isVisible;

      // Update table column visibility
      if (table) {
        if (isVisible) {
          table.showColumn(columnName);
        } else {
          table.hideColumn(columnName);
        }
      }
    });

    // Redraw table after all columns are set to fix layout
    if (table) {
      table.redraw(true);
      console.log('Table redrawn after restoring column visibility');
    }

    // Add change listeners
    checkboxes.forEach(function(checkbox) {
      const columnName = checkbox.getAttribute('data-column');

      // Add change listener
      checkbox.addEventListener('change', function() {
        if (table) {
          if (this.checked) {
            table.showColumn(columnName);
            saveColumnVisibility(columnName, true);
          } else {
            table.hideColumn(columnName);
            saveColumnVisibility(columnName, false);
          }
          // Redraw table to adjust column widths
          table.redraw(true);
        }
      });
    });
  }, 500);
});
