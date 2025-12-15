/**
 * UI Manager Module
 * Handles UI interactions, modals, menus, and keyboard shortcuts
 */

export class UIManager {
  constructor(table) {
    this.table = table;
    this.setupEventListeners();
  }

  setupEventListeners() {
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));
    
    // Modal close handlers
    document.addEventListener('click', (e) => this.handleModalClicks(e));
    
    // Column menu handler
    window.onclick = (event) => this.handleColumnMenuClicks(event);
  }

  handleKeyboardShortcuts(e) {
    const modifier = e.ctrlKey || e.metaKey;

    if (modifier && e.key === 'e') {
      e.preventDefault();
      this.exportToExcel();
      return;
    }

    if (modifier && e.key === 'p') {
      e.preventDefault();
      this.exportToPDF();
      return;
    }

    if (modifier && e.key === 'l') {
      e.preventDefault();
      this.lookupSNPedia();
      return;
    }

    if (modifier && e.key === 'f') {
      e.preventDefault();
      this.focusSearch();
      return;
    }

    if (modifier && e.key === 'k') {
      e.preventDefault();
      this.toggleColumnMenu();
      return;
    }

    if (modifier && e.key === 'x') {
      e.preventDefault();
      this.clearAllFilters();
      return;
    }

    if (modifier && e.key === 'r') {
      e.preventDefault();
      this.reloadData();
      return;
    }

    if (modifier && e.key === '/') {
      e.preventDefault();
      this.showKeyboardShortcuts();
      return;
    }

    if (modifier && e.key === 'd') {
      e.preventDefault();
      this.toggleDarkMode();
      return;
    }

    if (e.key === 'Escape') {
      const modal = document.getElementById('shortcutsModal');
      if (modal && modal.classList.contains('show')) {
        this.hideKeyboardShortcuts();
      } else {
        this.clearSelectionAndMenus();
      }
      return;
    }
  }

  handleModalClicks(e) {
    const modal = document.getElementById('shortcutsModal');
    if (e.target === modal) {
      this.hideKeyboardShortcuts();
    }
  }

  handleColumnMenuClicks(event) {
    if (!event.target.matches('.column-menu button')) {
      const menu = document.getElementById('columnMenu');
      if (menu.classList.contains('show')) {
        menu.classList.remove('show');
      }
    }
  }

  // UI Action Methods
  focusSearch() {
    const firstFilter = document.querySelector('.tabulator-header-filter input');
    if (firstFilter) {
      firstFilter.focus();
    }
  }

  showKeyboardShortcuts() {
    const modal = document.getElementById('shortcutsModal');
    modal.classList.add('show');
  }

  hideKeyboardShortcuts() {
    const modal = document.getElementById('shortcutsModal');
    modal.classList.remove('show');
  }

  toggleColumnMenu() {
    const menu = document.getElementById('columnMenu');
    menu.classList.toggle('show');
  }

  clearSelectionAndMenus() {
    if (this.table) {
      this.table.deselectRow();
    }

    const menu = document.getElementById('columnMenu');
    if (menu && menu.classList.contains('show')) {
      menu.classList.remove('show');
    }
  }

  lookupSNPedia() {
    if (!this.table) return;

    let selectedRows = this.table.getSelectedData();

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

  showFilterNotification(message) {
    let notification = document.getElementById('filterNotification');
    if (!notification) {
      notification = document.createElement('div');
      notification.id = 'filterNotification';
      notification.className = 'filter-notification';
      document.body.appendChild(notification);
    }

    notification.textContent = message;
    notification.classList.add('show');

    setTimeout(() => {
      notification.classList.remove('show');
    }, 2000);
  }

  // Placeholder methods that will be implemented by the main app
  exportToExcel() {
    // Will be handled by ExportManager
    console.log('Export to Excel triggered from UI');
  }

  exportToPDF() {
    // Will be handled by ExportManager
    console.log('Export to PDF triggered from UI');
  }

  clearAllFilters() {
    // Will be handled by FilterManager
    console.log('Clear all filters triggered from UI');
  }

  reloadData() {
    // Will be handled by DataManager
    console.log('Reload data triggered from UI');
  }

  toggleDarkMode() {
    // Will be handled by ThemeManager
    console.log('Toggle dark mode triggered from UI');
  }
}