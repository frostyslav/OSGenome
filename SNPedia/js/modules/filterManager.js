/**
 * Filter Manager Module
 * Handles table filtering functionality
 */

export class FilterManager {
  constructor(table) {
    this.table = table;
    this.setupFilterListeners();
  }

  setupFilterListeners() {
    if (this.table) {
      this.table.on("headerFilterChanged", (field, value) => {
        console.log('Filter changed:', field, value);
        this.updateFilterButtonState();
      });
    }
  }

  clearAllFilters() {
    if (!this.table) return;

    console.log('Clearing all filters...');

    // Check if there were any active filters before clearing
    const hadActiveFilters = this.table.getHeaderFilters().some(filter =>
      filter.value !== undefined && filter.value !== null && filter.value !== ""
    );

    // Clear all header filters
    this.table.clearHeaderFilter();

    // Update filter button state
    this.updateFilterButtonState();

    // Show feedback if filters were actually cleared
    if (hadActiveFilters) {
      this.showFilterNotification('All filters cleared');
    } else {
      this.showFilterNotification('No active filters to clear');
    }

    console.log('All filters cleared');
  }

  updateFilterButtonState() {
    if (!this.table) return;

    const clearButton = document.querySelector('button[onclick="clearAllFilters()"]');
    if (!clearButton) return;

    // Check if any header filters have values
    const hasActiveFilters = this.table.getHeaderFilters().some(filter =>
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

  showFilterNotification(message) {
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
    setTimeout(() => {
      notification.classList.remove('show');
    }, 2000);
  }

  // Initialize filter button state after data load
  initializeFilterState() {
    setTimeout(() => {
      this.updateFilterButtonState();
    }, 100);
  }
}
