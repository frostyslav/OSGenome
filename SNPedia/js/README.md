# SNPedia JavaScript Application - Modular Structure

This document describes the refactored modular structure of the SNPedia JavaScript application.

## Overview

The original `app.js` file (1425 lines) has been split into multiple focused modules for better maintainability, testability, and code organization.

## File Structure

```
SNPedia/js/
├── app.js                    # Original monolithic file (kept for reference)
├── app-modular.js           # New main application entry point
├── README.md                # This documentation
└── modules/
    ├── tableConfig.js       # Table configuration and column definitions
    ├── dataManager.js       # Data loading and API interactions
    ├── exportManager.js     # Excel and PDF export functionality
    ├── uiManager.js         # UI interactions and keyboard shortcuts
    ├── filterManager.js     # Table filtering functionality
    ├── themeManager.js      # Dark/light theme management
    ├── columnManager.js     # Column visibility and persistence
    ├── tableEventHandler.js # Table-specific event handling
    └── utils.js             # Common utility functions
```

## Module Descriptions

### 1. TableConfig (`tableConfig.js`)
- **Purpose**: Defines table structure and configuration
- **Key Features**:
  - Column definitions with filters and formatting
  - Table initialization options
  - Centralized table configuration management

### 2. DataManager (`dataManager.js`)
- **Purpose**: Handles all data-related operations
- **Key Features**:
  - API data loading with error handling
  - Data reloading functionality
  - Loading spinner management

### 3. ExportManager (`exportManager.js`)
- **Purpose**: Manages export functionality
- **Key Features**:
  - Excel export using Tabulator's built-in functionality
  - PDF export with charts and statistics
  - Chart generation (both Chart.js and fallback manual charts)
  - Table data formatting for PDF

### 4. UIManager (`uiManager.js`)
- **Purpose**: Handles UI interactions and keyboard shortcuts
- **Key Features**:
  - Keyboard shortcut handling
  - Modal management
  - Menu interactions
  - User notifications

### 5. FilterManager (`filterManager.js`)
- **Purpose**: Manages table filtering
- **Key Features**:
  - Filter state management
  - Clear all filters functionality
  - Filter button state updates
  - Filter notifications

### 6. ThemeManager (`themeManager.js`)
- **Purpose**: Handles theme switching
- **Key Features**:
  - Dark/light mode toggle
  - Theme persistence in localStorage
  - System preference detection

### 7. ColumnManager (`columnManager.js`)
- **Purpose**: Manages column visibility
- **Key Features**:
  - Column show/hide functionality
  - Visibility state persistence
  - Checkbox synchronization

### 8. TableEventHandler (`tableEventHandler.js`)
- **Purpose**: Handles table-specific events
- **Key Features**:
  - Cell click handling
  - Row selection management
  - Double-click for SNPedia lookup
  - DOM event handling for better reliability

### 9. Utils (`utils.js`)
- **Purpose**: Common utility functions
- **Key Features**:
  - PDF library checking
  - Text processing utilities
  - Performance measurement
  - LocalStorage helpers
  - Event emitter for inter-module communication

## Main Application (`app-modular.js`)

The main application file coordinates all modules and provides:
- Application initialization
- Manager coordination
- Backward compatibility with existing HTML
- Global function exposure
- Error handling

## Migration Guide

### To use the new modular version:

1. **Update HTML template**: Change the script reference from:
   ```html
   <script src="/static/js/app.js"></script>
   ```
   to:
   ```html
   <script type="module" src="/static/js/app-modular.js"></script>
   ```

2. **Backward Compatibility**: All existing global functions are preserved, so no HTML changes are required for button onclick handlers.

3. **Testing**: The new modular version maintains the same API and functionality as the original.

## Benefits of Modular Structure

1. **Maintainability**: Each module has a single responsibility
2. **Testability**: Individual modules can be tested in isolation
3. **Reusability**: Modules can be reused in other parts of the application
4. **Debugging**: Easier to locate and fix issues in specific functionality
5. **Performance**: Modules can be lazy-loaded if needed
6. **Team Development**: Multiple developers can work on different modules simultaneously

## Development Workflow

### Adding New Features:
1. Identify which module the feature belongs to
2. If it doesn't fit existing modules, create a new one
3. Update the main application to initialize the new module
4. Add any necessary global functions for backward compatibility

### Debugging:
1. Check browser console for module-specific logs
2. Use the browser's Network tab to ensure all modules load correctly
3. Access individual managers via `window.SNPediaApp.getManager('managerName')`

## Browser Compatibility

The modular version uses ES6 modules, which requires:
- Modern browsers (Chrome 61+, Firefox 60+, Safari 10.1+, Edge 16+)
- Server must serve JavaScript files with correct MIME type
- No additional build step required

## Performance Considerations

- Modules are loaded asynchronously
- Each module is cached by the browser
- No significant performance impact compared to the monolithic version
- Potential for future optimizations like lazy loading

## Future Enhancements

Potential improvements for the modular structure:
1. **TypeScript**: Add type definitions for better development experience
2. **Testing**: Add unit tests for each module
3. **Lazy Loading**: Load modules only when needed
4. **Service Workers**: Cache modules for offline functionality
5. **Build Process**: Optional bundling for production
