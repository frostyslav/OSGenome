/**
 * Column Manager Module
 * Handles column visibility and persistence
 */

export class ColumnManager {
  constructor(table) {
    this.table = table;
    this.setupColumnVisibility();
  }

  loadColumnVisibility() {
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

  saveColumnVisibility(columnName, visible) {
    const visibility = this.loadColumnVisibility();
    visibility[columnName] = visible;
    localStorage.setItem('columnVisibility', JSON.stringify(visibility));
  }

  setupColumnVisibility() {
    // Wait for table to be initialized
    setTimeout(() => {
      this.restoreColumnVisibility();
      this.setupColumnListeners();
    }, 500);
  }

  restoreColumnVisibility() {
    const visibility = this.loadColumnVisibility();

    // Update checkboxes and table columns based on saved state
    const checkboxes = document.querySelectorAll('#columnMenu input[type="checkbox"]');
    checkboxes.forEach((checkbox) => {
      const columnName = checkbox.getAttribute('data-column');
      const isVisible = visibility[columnName];

      // Update checkbox state
      checkbox.checked = isVisible;

      // Update table column visibility
      if (this.table) {
        if (isVisible) {
          this.table.showColumn(columnName);
        } else {
          this.table.hideColumn(columnName);
        }
      }
    });

    // Redraw table after all columns are set to fix layout
    if (this.table) {
      this.table.redraw(true);
      console.log('Table redrawn after restoring column visibility');
    }
  }

  setupColumnListeners() {
    const checkboxes = document.querySelectorAll('#columnMenu input[type="checkbox"]');
    checkboxes.forEach((checkbox) => {
      const columnName = checkbox.getAttribute('data-column');

      // Add change listener
      checkbox.addEventListener('change', () => {
        if (this.table) {
          if (checkbox.checked) {
            this.table.showColumn(columnName);
            this.saveColumnVisibility(columnName, true);
          } else {
            this.table.hideColumn(columnName);
            this.saveColumnVisibility(columnName, false);
          }
          // Redraw table to adjust column widths
          this.table.redraw(true);
        }
      });
    });
  }

  showColumn(columnName) {
    if (this.table) {
      this.table.showColumn(columnName);
      this.saveColumnVisibility(columnName, true);
      
      // Update checkbox if it exists
      const checkbox = document.querySelector(`#columnMenu input[data-column="${columnName}"]`);
      if (checkbox) {
        checkbox.checked = true;
      }
      
      this.table.redraw(true);
    }
  }

  hideColumn(columnName) {
    if (this.table) {
      this.table.hideColumn(columnName);
      this.saveColumnVisibility(columnName, false);
      
      // Update checkbox if it exists
      const checkbox = document.querySelector(`#columnMenu input[data-column="${columnName}"]`);
      if (checkbox) {
        checkbox.checked = false;
      }
      
      this.table.redraw(true);
    }
  }

  toggleColumn(columnName) {
    const visibility = this.loadColumnVisibility();
    const isVisible = visibility[columnName];
    
    if (isVisible) {
      this.hideColumn(columnName);
    } else {
      this.showColumn(columnName);
    }
  }
}