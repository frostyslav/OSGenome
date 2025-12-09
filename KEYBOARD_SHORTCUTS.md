# Keyboard Shortcuts Guide

OSGenome includes comprehensive keyboard shortcuts to improve your workflow and make genetic data analysis faster and more efficient.

## Quick Reference

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl/Cmd + E` | Export to Excel | Download the current table view as an Excel file |
| `Ctrl/Cmd + L` | Lookup on SNPedia | Open the selected SNP on SNPedia in a new tab |
| `Ctrl/Cmd + F` | Focus Search | Jump to the search/filter field to quickly find SNPs |
| `Ctrl/Cmd + K` | Toggle Columns | Show or hide the column visibility menu |
| `Ctrl/Cmd + R` | Reload Data | Refresh the table data from the server |
| `Ctrl/Cmd + /` | Show Shortcuts | Display this keyboard shortcuts help dialog |
| `Escape` | Clear/Close | Clear selection and close open menus or dialogs |
| `Arrow Keys` | Navigate | Move between table rows and cells |
| `Enter` | Select Row | Select the currently focused row |

## Platform Notes

- **Windows/Linux**: Use `Ctrl` key
- **macOS**: Use `Cmd` (⌘) key

## Detailed Usage

### Export to Excel (Ctrl+E)
Quickly export your genetic data to an Excel spreadsheet. The export includes all visible columns and respects your current filters.

**Tip**: Configure which columns to export by toggling column visibility first.

### Lookup on SNPedia (Ctrl+L)
Opens the selected SNP's page on SNPedia in a new browser tab. If no row is selected, you'll be prompted to enter an RSid manually.

**Tip**: Click a row first to select it, then use this shortcut for quick lookups.

### Focus Search (Ctrl+F)
Jumps your cursor to the first filter input field in the table header, allowing you to immediately start typing to filter results.

**Note**: This overrides the browser's default find function when focused on the table.

### Toggle Columns (Ctrl+K)
Opens or closes the column visibility menu where you can show/hide different data columns like:
- Name
- Description
- Stabilized Orientation
- Individual Genotype
- Genotype Variations
- Interesting Genotype
- Uncommon Genotype

**Tip**: Your column preferences are saved in browser storage and persist between sessions.

### Reload Data (Ctrl+R)
Refreshes the table data from the server without reloading the entire page. Useful if you've updated your genetic data files.

**Note**: This overrides the browser's default page reload when focused on the table.

### Show Shortcuts (Ctrl+/)
Displays a beautiful modal dialog with all available keyboard shortcuts. The same information you're reading now!

### Clear/Close (Escape)
Multi-purpose shortcut that:
- Closes the keyboard shortcuts modal if open
- Closes the column visibility menu if open
- Clears any selected rows in the table

### Navigate (Arrow Keys)
Use arrow keys to move through the table:
- `↑` / `↓` - Move between rows
- `←` / `→` - Move between cells
- Works with Tabulator's built-in navigation

### Select Row (Enter)
When a row is focused (via arrow key navigation), press Enter to select it. This is useful for keyboard-only workflows.

## Accessibility

All keyboard shortcuts are designed to work without a mouse, making OSGenome fully accessible via keyboard navigation. This is particularly useful for:
- Users with mobility impairments
- Power users who prefer keyboard workflows
- Screen reader users
- Touch-typing enthusiasts

## Visual Indicators

- **Toolbar Buttons**: Hover over any toolbar button to see its keyboard shortcut in the tooltip
- **Button Icons**: Each button includes a Font Awesome icon for quick visual identification
- **Shortcuts Button**: The keyboard shortcuts button is always visible in the toolbar with a keyboard icon

## Tips for Power Users

1. **Workflow Optimization**: Memorize the most common shortcuts (Ctrl+E, Ctrl+L, Ctrl+F) for maximum efficiency
2. **Filter First**: Use Ctrl+F to filter, then Ctrl+E to export only relevant data
3. **Quick Lookup**: Select interesting SNPs with arrow keys and Enter, then Ctrl+L to research them
4. **Column Management**: Set up your preferred columns once with Ctrl+K - they'll be remembered
5. **Keyboard-Only Mode**: You can perform all major actions without touching the mouse

## Customization

Currently, keyboard shortcuts are fixed. If you'd like to customize them, you can modify the `SNPedia/js/app.js` file and look for the `keydown` event listener.

## Troubleshooting

**Shortcut not working?**
- Ensure the table area has focus (click on it first)
- Check if another browser extension is intercepting the shortcut
- Try clicking the corresponding toolbar button instead

**Ctrl+F opens browser find instead?**
- This is expected if focus is outside the table
- Click on the table first, then use Ctrl+F

**Shortcuts modal won't close?**
- Press Escape
- Click outside the modal
- Click the X button in the top-right corner

## Browser Compatibility

Keyboard shortcuts work in all modern browsers:
- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari
- ✅ Opera

## Future Enhancements

Planned keyboard shortcut features:
- Customizable key bindings
- Vim-style navigation mode
- Quick filter presets (1-9 keys)
- Batch selection with Shift+Arrow
- Copy selected rows with Ctrl+C

## Feedback

Found a keyboard shortcut that doesn't work or have suggestions for new ones? Please open an issue on the GitHub repository!

---

**Remember**: Press `Ctrl+/` anytime to see the shortcuts reference!
