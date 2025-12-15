/**
 * Theme Manager Module
 * Handles dark/light theme functionality
 */

export class ThemeManager {
  constructor() {
    this.loadSavedTheme();
  }

  toggleDarkMode() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);

    console.log('Theme switched to:', newTheme);
  }

  loadSavedTheme() {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = savedTheme || (prefersDark ? 'dark' : 'light');

    document.documentElement.setAttribute('data-theme', theme);
    console.log('Theme loaded:', theme);
  }

  getCurrentTheme() {
    return document.documentElement.getAttribute('data-theme') || 'light';
  }

  setTheme(theme) {
    if (theme === 'dark' || theme === 'light') {
      document.documentElement.setAttribute('data-theme', theme);
      localStorage.setItem('theme', theme);
      console.log('Theme set to:', theme);
    }
  }
}
