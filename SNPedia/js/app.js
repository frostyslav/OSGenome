/**
 * Main Application Module
 * Coordinates all the different managers and handles application initialization
 */

import { TableConfig } from './modules/tableConfig.js';
import { DataManager } from './modules/dataManager.js';
import { ExportManager } from './modules/exportManager.js';
import { UIManager } from './modules/uiManager.js';
import { FilterManager } from './modules/filterManager.js';
import { ThemeManager } from './modules/themeManager.js';
import { ColumnManager } from './modules/columnManager.js';
import { TableEventHandler } from './modules/tableEventHandler.js';

class SNPediaApp {
  constructor() {
    this.table = null;
    this.managers = {};

    console.log('SNPedia App initializing...');
    this.init();
  }

  async init() {
    // Check if Tabulator is available
    if (typeof Tabulator === 'undefined') {
      console.error('Tabulator not loaded!');
      alert('Tabulator library failed to load. Check network tab.');
      return;
    }

    console.log('Tabulator available');

    // Initialize theme first
    this.managers.theme = new ThemeManager();

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.initializeApp());
    } else {
      this.initializeApp();
    }
  }

  async initializeApp() {
    console.log('DOM loaded, initializing application...');

    try {
      // Initialize Tabulator table and wait for it to be ready
      await this.initializeTable();

      // Initialize all managers
      this.initializeManagers();

      // Load data
      await this.loadInitialData();

      // Setup global functions for backward compatibility
      this.setupGlobalFunctions();

      console.log('Application initialized successfully');

    } catch (error) {
      console.error('Error initializing application:', error);
      alert('Error initializing application: ' + error.message);
    }
  }

  async initializeTable() {
    const tableOptions = TableConfig.getTableOptions();

    this.table = new Tabulator("#grid", tableOptions);
    console.log('Table initialized');

    // Wait for table to be fully ready
    return new Promise((resolve) => {
      this.table.on("tableBuilt", () => {
        console.log('Table built and ready');
        resolve();
      });
    });
  }

  initializeManagers() {
    // Initialize all managers
    this.managers.data = new DataManager(this.table);
    this.managers.export = new ExportManager(this.table);
    this.managers.filter = new FilterManager(this.table);
    this.managers.column = new ColumnManager(this.table);
    this.managers.tableEvents = new TableEventHandler(this.table);

    // Initialize UI manager and connect it to other managers
    this.managers.ui = new UIManager(this.table);
    this.connectUIToManagers();

    console.log('All managers initialized');
  }

  connectUIToManagers() {
    // Override UI manager methods to use actual managers
    this.managers.ui.exportToExcel = () => this.managers.export.exportToExcel();
    this.managers.ui.exportToPDF = () => this.managers.export.exportToPDF();
    this.managers.ui.clearAllFilters = () => this.managers.filter.clearAllFilters();
    this.managers.ui.reloadData = () => this.reloadData();
    this.managers.ui.toggleDarkMode = () => this.managers.theme.toggleDarkMode();
  }

  async loadInitialData() {
    try {
      // Wait for backend to be ready
      await this.waitForBackend();

      // Give a small additional delay to ensure everything is fully initialized
      await new Promise(resolve => setTimeout(resolve, 100));

      const data = await this.managers.data.loadData();

      if (data && data.length > 0) {
        // Initialize filter state after data is loaded
        this.managers.filter.initializeFilterState();
        console.log('Initial data loaded successfully');
      }
    } catch (error) {
      console.error('Error loading initial data:', error);
      alert('Error loading data: ' + error.message);
    }
  }

  async waitForBackend(maxAttempts = 10) {
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        console.log(`Checking backend readiness... (attempt ${attempt})`);

        // First check if we can reach the server at all
        const healthResponse = await fetch('/api/health', {
          method: 'GET',
          cache: 'no-cache',
          headers: {
            'Cache-Control': 'no-cache'
          }
        });

        if (healthResponse.ok) {
          const health = await healthResponse.json();
          if (health.status === 'healthy') {
            console.log('Backend health check passed');

            // Also test the actual data endpoint
            const dataResponse = await fetch('/api/rsids', {
              method: 'GET',
              cache: 'no-cache',
              headers: {
                'Cache-Control': 'no-cache'
              }
            });

            if (dataResponse.ok) {
              const testData = await dataResponse.json();
              if (testData.results && testData.results.length > 0) {
                console.log('Backend is ready with data');
                return;
              } else {
                console.log('Backend ready but no data available');
                return;
              }
            }
          }
        }
      } catch (error) {
        console.log(`Backend not ready yet (attempt ${attempt}):`, error.message);
      }

      // Wait before next attempt (exponential backoff, but cap at 2 seconds)
      if (attempt < maxAttempts) {
        const delay = Math.min(attempt * 200, 2000);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }

    console.warn('Backend readiness check timed out, proceeding anyway');
  }

  async reloadData() {
    try {
      const data = await this.managers.data.reloadData();

      if (data && data.length > 0) {
        // Update filter button state after reload
        this.managers.filter.initializeFilterState();
        console.log('Data reloaded successfully');
      }
    } catch (error) {
      console.error('Error reloading data:', error);
      alert('Error reloading data: ' + error.message);
    }
  }

  // Setup global functions for backward compatibility with existing HTML
  setupGlobalFunctions() {
    // Export functions
    window.exportToExcel = () => this.managers.export.exportToExcel();
    window.exportToPDF = () => this.managers.export.exportToPDF();

    // UI functions
    window.lookupSNPedia = () => this.managers.ui.lookupSNPedia();
    window.showKeyboardShortcuts = () => {
      console.log('showKeyboardShortcuts called');
      this.managers.ui.showKeyboardShortcuts();
    };

    // Debug function for testing
    window.testModal = () => {
      const modal = document.getElementById('shortcutsModal');
      console.log('Modal element:', modal);
      if (modal) {
        console.log('Modal classes before:', modal.className);
        modal.classList.add('show');
        console.log('Modal classes after:', modal.className);
        console.log('Modal computed style display:', getComputedStyle(modal).display);
      }
    };

    // Debug function for theme testing
    window.testTheme = () => {
      const html = document.documentElement;
      const currentTheme = html.getAttribute('data-theme');
      const toolbar = document.querySelector('.toolbar');

      console.log('Current theme:', currentTheme);
      console.log('HTML data-theme attribute:', html.getAttribute('data-theme'));
      console.log('Toolbar element:', toolbar);

      if (toolbar) {
        const computedStyle = getComputedStyle(toolbar);
        console.log('Toolbar background:', computedStyle.background);
        console.log('Toolbar background-image:', computedStyle.backgroundImage);
      }

      return {
        theme: currentTheme,
        toolbarExists: !!toolbar
      };
    };
    window.hideKeyboardShortcuts = () => this.managers.ui.hideKeyboardShortcuts();
    window.focusSearch = () => this.managers.ui.focusSearch();
    window.toggleColumnMenu = () => this.managers.ui.toggleColumnMenu();

    // Filter functions
    window.clearAllFilters = () => this.managers.filter.clearAllFilters();

    // Data functions
    window.reloadData = () => this.reloadData();

    // Theme functions
    window.toggleDarkMode = () => this.managers.theme.toggleDarkMode();

    // Column functions
    window.toggleColumn = (columnName) => this.managers.column.toggleColumn(columnName);

    console.log('Global functions setup complete');
  }

  // Public API methods
  getTable() {
    return this.table;
  }

  getManager(name) {
    return this.managers[name];
  }

  getAllManagers() {
    return this.managers;
  }
}

// Initialize the application
console.log('Script loaded');
const app = new SNPediaApp();

// Export for potential external use
window.SNPediaApp = app;
