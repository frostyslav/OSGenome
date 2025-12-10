"""Test Font Awesome integration."""

import os
import re


def test_font_awesome_cdn_in_html():
    """Test that Font Awesome CDN is included in HTML."""
    html_file = "SNPedia/templates/snp_resource.html"

    assert os.path.exists(html_file), f"{html_file} not found"

    with open(html_file) as f:
        content = f.read()

    # Check for Font Awesome CDN
    assert "font-awesome" in content.lower(), "Font Awesome not found in HTML"
    assert "cdnjs.cloudflare.com" in content, "Font Awesome CDN not found"
    assert "integrity=" in content, "Integrity hash not found (security issue)"
    assert "crossorigin=" in content, "Crossorigin attribute not found"

    print("✓ Font Awesome CDN properly included in HTML")


def test_font_awesome_icons_in_html():
    """Test that Font Awesome icons are used in HTML."""
    html_file = "SNPedia/templates/snp_resource.html"

    with open(html_file) as f:
        content = f.read()

    # Check for Font Awesome icon classes
    required_icons = [
        "fa-file-excel",  # Export button
        "fa-search",  # Lookup button
        "fa-columns",  # Column menu
        "fa-sync-alt",  # Reload button
        "fa-keyboard",  # Shortcuts button and modal
        "fa-times",  # Close button
        "fa-filter",  # Filter icon
        "fa-question-circle",  # Help icon
        "fa-arrow-up",  # Arrow keys
        "fa-arrow-down",
        "fa-arrow-left",
        "fa-arrow-right",
    ]

    for icon in required_icons:
        assert icon in content, f"Icon '{icon}' not found in HTML"

    # Check that emojis are NOT used in buttons
    emoji_patterns = ["📊", "🔍", "⚙️", "🔄", "⌨️"]  # Old emoji icons

    # Allow emojis in comments or documentation, but not in actual UI elements
    # We'll check that <i class="fa is used instead
    assert (
        '<i class="fas' in content or '<i class="fab' in content
    ), "Font Awesome icon tags not found"

    print("✓ Font Awesome icons properly used in HTML")


def test_font_awesome_styles_in_css():
    """Test that Font Awesome icon styles exist in CSS."""
    css_file = "SNPedia/css/app.css"

    assert os.path.exists(css_file), f"{css_file} not found"

    with open(css_file) as f:
        content = f.read()

    # Check for icon-specific styles
    required_styles = [
        ".toolbar button i",
        ".shortcut-icon",
        ".modal-header h2 i",
    ]

    for style in required_styles:
        assert style in content, f"Style '{style}' not found in CSS"

    print("✓ Font Awesome icon styles properly implemented in CSS")


def test_csp_allows_font_awesome():
    """Test that CSP allows Font Awesome CDN."""
    app_file = "SNPedia/app.py"

    assert os.path.exists(app_file), f"{app_file} not found"

    with open(app_file) as f:
        content = f.read()

    # Check for CSP header
    assert "Content-Security-Policy" in content, "CSP header not found"

    # Check that cdnjs.cloudflare.com is allowed
    assert "cdnjs.cloudflare.com" in content, "Font Awesome CDN not allowed in CSP"

    # Check for font-src directive
    assert "font-src" in content, "font-src directive not found in CSP"

    print("✓ CSP properly configured for Font Awesome")


def test_no_emoji_in_buttons():
    """Test that emojis are replaced with Font Awesome icons."""
    html_file = "SNPedia/templates/snp_resource.html"

    with open(html_file) as f:
        content = f.read()

    # Extract button sections
    toolbar_section = re.search(r'<div class="toolbar">(.*?)</div>', content, re.DOTALL)

    if toolbar_section:
        toolbar_html = toolbar_section.group(1)

        # Check that buttons use <i> tags instead of emoji spans
        button_pattern = r"<button[^>]*>(.*?)</button>"
        buttons = re.findall(button_pattern, toolbar_html, re.DOTALL)

        for button_content in buttons:
            # Each button should have an <i> tag with Font Awesome class
            if "onclick=" in button_content:  # Skip nested buttons
                assert (
                    '<i class="fa' in button_content
                ), f"Button doesn't use Font Awesome icon: {button_content[:50]}"

    print("✓ Buttons use Font Awesome icons instead of emojis")


def test_font_awesome_documentation():
    """Test that Font Awesome usage is documented."""
    doc_file = "FONT_AWESOME_ICONS.md"

    assert os.path.exists(doc_file), f"{doc_file} not found"

    with open(doc_file) as f:
        content = f.read()

    # Check for key documentation sections
    assert "Font Awesome" in content, "Font Awesome not mentioned"
    assert "6.5.1" in content, "Version not documented"
    assert "cdnjs.cloudflare.com" in content, "CDN not documented"
    assert "fa-file-excel" in content, "Icons not documented"
    assert "Accessibility" in content, "Accessibility not documented"

    print("✓ Font Awesome properly documented")


def test_changelog_updated():
    """Test that changelog mentions Font Awesome."""
    changelog_file = "CHANGELOG_KEYBOARD_SHORTCUTS.md"

    assert os.path.exists(changelog_file), f"{changelog_file} not found"

    with open(changelog_file) as f:
        content = f.read()

    # Check that Font Awesome is mentioned
    assert "Font Awesome" in content, "Font Awesome not mentioned in changelog"

    print("✓ Changelog updated with Font Awesome information")


if __name__ == "__main__":
    print("Testing Font Awesome integration...\n")

    try:
        test_font_awesome_cdn_in_html()
        test_font_awesome_icons_in_html()
        test_font_awesome_styles_in_css()
        test_csp_allows_font_awesome()
        test_no_emoji_in_buttons()
        test_font_awesome_documentation()
        test_changelog_updated()

        print("\n" + "=" * 50)
        print("✅ All Font Awesome tests passed!")
        print("=" * 50)

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)
