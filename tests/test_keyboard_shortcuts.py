"""Test keyboard shortcuts functionality."""

import os
import re


def test_keyboard_shortcuts_in_js():
    """Test that keyboard shortcuts are properly implemented in JavaScript."""
    js_file = "SNPedia/js/app.js"

    assert os.path.exists(js_file), f"{js_file} not found"

    with open(js_file) as f:
        content = f.read()

    # Check for keyboard event listener
    assert "addEventListener('keydown'" in content, "Keyboard event listener not found"

    # Check for all expected shortcuts
    shortcuts = [
        ("e", "exportToExcel"),
        ("l", "lookupSNPedia"),
        ("f", "focusSearch"),
        ("k", "toggleColumnMenu"),
        ("r", "reloadData"),
        ("/", "showKeyboardShortcuts"),
    ]

    for key, function in shortcuts:
        assert f"e.key === '{key}'" in content, f"Shortcut for key '{key}' not found"
        assert function in content, f"Function '{function}' not found"

    # Check for Escape key handler
    assert "e.key === 'Escape'" in content, "Escape key handler not found"

    # Check for modifier key detection (Ctrl/Cmd)
    assert "e.ctrlKey || e.metaKey" in content, "Modifier key detection not found"

    print("✓ All keyboard shortcuts properly implemented in JavaScript")


def test_keyboard_shortcuts_modal_in_html():
    """Test that keyboard shortcuts modal exists in HTML."""
    html_file = "SNPedia/templates/snp_resource.html"

    assert os.path.exists(html_file), f"{html_file} not found"

    with open(html_file) as f:
        content = f.read()

    # Check for modal structure
    assert 'id="shortcutsModal"' in content, "Shortcuts modal not found"
    assert "modal-overlay" in content, "Modal overlay class not found"
    assert "modal-content" in content, "Modal content class not found"

    # Check for shortcuts button in toolbar
    assert "showKeyboardShortcuts()" in content, "Show shortcuts button not found"
    assert "Shortcuts" in content, "Shortcuts button text not found"

    # Check for key shortcuts listed in modal
    expected_keys = ["Ctrl", "Escape", "Enter"]
    for key in expected_keys:
        assert key in content, f"Key '{key}' not found in modal"

    print("✓ Keyboard shortcuts modal properly implemented in HTML")


def test_keyboard_shortcuts_styles_in_css():
    """Test that keyboard shortcuts styles exist in CSS."""
    css_file = "SNPedia/css/app.css"

    assert os.path.exists(css_file), f"{css_file} not found"

    with open(css_file) as f:
        content = f.read()

    # Check for modal styles
    required_classes = [
        ".modal-overlay",
        ".modal-content",
        ".modal-header",
        ".modal-close",
        ".shortcuts-list",
        ".shortcut-item",
        ".shortcut-keys",
        ".key",
        ".shortcut-description",
    ]

    for css_class in required_classes:
        assert css_class in content, f"CSS class '{css_class}' not found"

    # Check for animations
    assert "@keyframes fadeIn" in content, "fadeIn animation not found"
    assert "@keyframes slideUp" in content, "slideUp animation not found"

    # Check for icon styles (Font Awesome)
    assert ".shortcut-icon" in content, "Shortcut icon styles not found"
    assert ".toolbar button i" in content, "Toolbar icon styles not found"

    print("✓ Keyboard shortcuts styles properly implemented in CSS")


def test_keyboard_shortcuts_documented():
    """Test that keyboard shortcuts are documented in README."""
    readme_file = "README.md"

    assert os.path.exists(readme_file), f"{readme_file} not found"

    with open(readme_file) as f:
        content = f.read()

    # Check for keyboard shortcuts section
    assert (
        "Keyboard Shortcuts" in content
    ), "Keyboard shortcuts section not found in README"
    assert (
        "⌨️" in content or "keyboard" in content.lower()
    ), "Keyboard emoji or mention not found"

    # Check for documented shortcuts
    shortcuts = ["E", "L", "F", "K", "R", "Escape"]
    for shortcut in shortcuts:
        # Look for the key mentioned in context of Ctrl/Cmd
        if shortcut == "Escape":
            assert "Escape" in content, f"Shortcut '{shortcut}' not documented"
        else:
            # Check for patterns like "Ctrl/Cmd + E" or "Ctrl+E"
            pattern = f"(Ctrl|Cmd)[/\\s+]+{shortcut}"
            assert re.search(
                pattern, content, re.IGNORECASE
            ), f"Shortcut key '{shortcut}' not documented"

    print("✓ Keyboard shortcuts properly documented in README")


def test_all_functions_exist():
    """Test that all required functions exist in JavaScript."""
    js_file = "SNPedia/js/app.js"

    with open(js_file) as f:
        content = f.read()

    required_functions = [
        "showKeyboardShortcuts",
        "hideKeyboardShortcuts",
        "reloadData",
        "focusSearch",
        "clearSelectionAndMenus",
        "exportToExcel",
        "lookupSNPedia",
        "toggleColumnMenu",
    ]

    for func in required_functions:
        assert f"function {func}(" in content, f"Function '{func}' not found"

    print("✓ All required functions exist in JavaScript")


if __name__ == "__main__":
    print("Testing keyboard shortcuts implementation...\n")

    try:
        test_keyboard_shortcuts_in_js()
        test_keyboard_shortcuts_modal_in_html()
        test_keyboard_shortcuts_styles_in_css()
        test_keyboard_shortcuts_documented()
        test_all_functions_exist()

        print("\n" + "=" * 50)
        print("✅ All keyboard shortcuts tests passed!")
        print("=" * 50)

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)
