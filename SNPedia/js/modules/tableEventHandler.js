/**
 * Table Event Handler Module
 * Handles table-specific events like clicks, selections, etc.
 */

export class TableEventHandler {
  constructor(table) {
    this.table = table;
    this.setupTableEvents();
  }

  setupTableEvents() {
    if (!this.table) return;

    // Set up table event handlers
    this.table.on("cellClick", (e, cell) => this.handleCellClick(e, cell));
    this.table.on("rowDblClick", (e, row) => this.handleRowDoubleClick(e, row));
    this.table.on("rowSelectionChanged", (data, rows) => this.handleSelectionChange(data, rows));

    // Set up DOM event handlers for better row selection
    this.setupDOMEventHandlers();
  }

  handleCellClick(e, cell) {
    console.log('Cell clicked!');
    const row = cell.getRow();
    console.log('Row data:', row.getData());

    // Deselect all rows first, then select clicked row
    this.table.deselectRow();
    row.select();
    console.log('Row selected, isSelected:', row.isSelected());
    console.log('Selected rows:', this.table.getSelectedRows().length);
  }

  handleRowDoubleClick(e, row) {
    console.log('Row double-clicked!');
    const rowData = row.getData();
    const rsid = rowData.Name;
    if (rsid) {
      console.log('Looking up RSid:', rsid);
      const url = 'https://snpedia.com/index.php/' + rsid;
      window.open(url, '_blank');
    }
  }

  handleSelectionChange(data, rows) {
    console.log('Selection changed:', rows.length, 'rows selected');
  }

  setupDOMEventHandlers() {
    // Add direct DOM listener to handle row selection more reliably
    setTimeout(() => {
      const gridElement = document.getElementById('grid');
      if (!gridElement) return;

      let clickTimeout;

      gridElement.addEventListener('click', (e) => {
        // Clear any existing timeout to prevent single click action on double click
        clearTimeout(clickTimeout);

        clickTimeout = setTimeout(() => {
          console.log('Single click detected!', e.target.className);

          // Find the row element
          let rowElement = e.target;
          while (rowElement && !rowElement.classList.contains('tabulator-row')) {
            rowElement = rowElement.parentElement;
          }

          if (rowElement && rowElement.classList.contains('tabulator-row')) {
            console.log('Row element found!');
            // Get the row component from Tabulator
            const rows = this.table.getRows();
            for (let i = 0; i < rows.length; i++) {
              if (rows[i].getElement() === rowElement) {
                console.log('Matching row found, selecting...');
                this.table.deselectRow();
                rows[i].select();
                console.log('Row selected!');
                break;
              }
            }
          }
        }, 250); // Delay to allow double-click detection
      });

      // Add double-click handler
      gridElement.addEventListener('dblclick', (e) => {
        // Clear the single click timeout
        clearTimeout(clickTimeout);

        console.log('Double click detected!', e.target.className);

        // Find the row element
        let rowElement = e.target;
        while (rowElement && !rowElement.classList.contains('tabulator-row')) {
          rowElement = rowElement.parentElement;
        }

        if (rowElement && rowElement.classList.contains('tabulator-row')) {
          console.log('Row element found for double-click!');
          // Get the row component from Tabulator
          const rows = this.table.getRows();
          for (let i = 0; i < rows.length; i++) {
            if (rows[i].getElement() === rowElement) {
              const rowData = rows[i].getData();
              const rsid = rowData.Name;
              if (rsid) {
                console.log('Looking up RSid:', rsid);
                const url = 'https://snpedia.com/index.php/' + rsid;
                window.open(url, '_blank');
              }
              break;
            }
          }
        }
      });
    }, 1000);
  }

  // Utility methods for external use
  getSelectedRows() {
    return this.table ? this.table.getSelectedRows() : [];
  }

  getSelectedData() {
    return this.table ? this.table.getSelectedData() : [];
  }

  deselectAll() {
    if (this.table) {
      this.table.deselectRow();
    }
  }

  selectRow(row) {
    if (this.table && row) {
      this.table.deselectRow();
      row.select();
    }
  }
}
