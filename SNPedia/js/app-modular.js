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
      // Initialize Tabulator table
      this.initializeTable();

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

  initializeTable() {
    const tableOptions = TableConfig.getTableOptions();

    this.table = new Tabulator("#grid", tableOptions);
    console.log('Table initialized');
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
    window.showKeyboardShortcuts = () => this.managers.ui.showKeyboardShortcuts();
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
