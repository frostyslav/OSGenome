# CSS Architecture

This directory contains the modular CSS architecture for the SNPedia application. The CSS has been broken down into logical modules for better maintainability and organization.

## File Structure

```
css/
├── app.css           # Main entry point - imports all modules
├── variables.css     # CSS custom properties and theme variables
├── base.css          # Base HTML/body styles and layout containers
├── toolbar.css       # Toolbar and button styles
├── components.css    # Reusable components (modals, spinners, notifications)
├── table.css         # Tabulator table-specific styles
├── responsive.css    # Media queries and responsive design
├── dark-mode.css     # Dark theme overrides
└── README.md         # This file
```

## Module Descriptions

### `variables.css`
- CSS custom properties for colors, spacing, shadows
- Light and dark theme variable definitions
- Centralized theming system

### `base.css`
- HTML and body base styles
- Container layout styles
- Grid container styles
- Font and basic typography

### `toolbar.css`
- Toolbar container and button styles
- Column menu dropdown styles
- Theme toggle button
- Clear filters button styling

### `components.css`
- Loading spinner component
- Filter notification component
- Modal overlay and content
- Keyboard shortcuts modal
- Reusable UI components

### `table.css`
- Tabulator table styling
- Row and cell styling
- Header and footer styles
- Selection and hover states
- Pagination styles

### `responsive.css`
- Mobile-first responsive design
- Media queries for different screen sizes
- Responsive table adjustments
- Mobile-specific component styles

### `dark-mode.css`
- Dark theme overrides for all components
- Tabulator dark mode styling
- Toolbar dark mode overrides
- Component dark mode adjustments

## Usage

The main `app.css` file imports all modules in the correct order:

```css
@import url('./variables.css');
@import url('./base.css');
@import url('./toolbar.css');
@import url('./components.css');
@import url('./table.css');
@import url('./responsive.css');
@import url('./dark-mode.css');
```

HTML templates should continue to reference `css/app.css` as before:

```html
<link href="css/app.css" rel="stylesheet">
```

## Benefits

1. **Maintainability**: Each module focuses on a specific concern
2. **Reusability**: Components can be easily identified and modified
3. **Performance**: Easier to identify unused styles
4. **Collaboration**: Multiple developers can work on different modules
5. **Debugging**: Easier to locate and fix style issues
6. **Scalability**: New features can add their own CSS modules

## Development Guidelines

- Keep modules focused on single responsibilities
- Use CSS custom properties from `variables.css` for consistency
- Add new components to `components.css` or create new module files
- Ensure responsive styles are added to `responsive.css`
- Dark mode overrides should go in `dark-mode.css`
- Import order in `app.css` matters - variables first, dark mode last