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
            values: ["Yes", "No"],
            clearable: true
          }
        },
        {
          title: "Uncommon genotype",
          field: "IsUncommon",
          visible: false,
          headerFilter: "list",
          headerFilterParams: {
            values: ["Yes", "No"],
            clearable: true
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
    
    // Load data
    fetch('/api/rsids')
      .then(response => {
        console.log('Response status:', response.status);
        return response.json();
      })
      .then(data => {
        console.log('Data received:', data.results ? data.results.length + ' rows' : 'no results');
        if (data.results && data.results.length > 0) {
          table.setData(data.results);
          console.log('Data loaded into table');
          
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
