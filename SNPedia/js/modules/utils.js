/**
 * Utility Functions Module
 * Common utility functions used across the application
 */

export class Utils {
  // Check if PDF libraries are available (for debugging)
  static checkPDFLibraries() {
    console.log('Checking PDF libraries...');
    console.log('window.jspdf:', typeof window.jspdf);
    console.log('window.jsPDF:', typeof window.jsPDF);
    console.log('window.Chart:', typeof window.Chart);

    if (window.jspdf) {
      console.log('jspdf object:', Object.keys(window.jspdf));
    }

    // Try to create a simple PDF
    try {
      let jsPDF;
      if (window.jspdf && window.jspdf.jsPDF) {
        jsPDF = window.jspdf.jsPDF;
      } else if (window.jsPDF) {
        jsPDF = window.jsPDF;
      }

      if (jsPDF) {
        const testDoc = new jsPDF();
        testDoc.text('Test', 10, 10);
        console.log('jsPDF test successful');
        return true;
      }
    } catch (error) {
      console.error('jsPDF test failed:', error);
    }

    return false;
  }

  // Clean HTML tags from text
  static stripHtmlTags(html) {
    if (!html) return '';
    return html.replace(/<[^>]*>/g, '');
  }

  // Truncate text to specified length
  static truncateText(text, maxLength, suffix = '...') {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + suffix;
  }

  // Format date for display
  static formatDate(date = new Date()) {
    return date.toLocaleDateString();
  }

  // Debounce function for performance optimization
  static debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  // Throttle function for performance optimization
  static throttle(func, limit) {
    let inThrottle;
    return function() {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }

  // Check if element is visible in viewport
  static isElementInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
      rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
  }

  // Local storage helpers with error handling
  static setLocalStorage(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      console.error('Error saving to localStorage:', error);
      return false;
    }
  }

  static getLocalStorage(key, defaultValue = null) {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.error('Error reading from localStorage:', error);
      return defaultValue;
    }
  }

  static removeLocalStorage(key) {
    try {
      localStorage.removeItem(key);
      return true;
    } catch (error) {
      console.error('Error removing from localStorage:', error);
      return false;
    }
  }

  // Simple event emitter for inter-module communication
  static createEventEmitter() {
    const events = {};

    return {
      on(event, callback) {
        if (!events[event]) {
          events[event] = [];
        }
        events[event].push(callback);
      },

      off(event, callback) {
        if (events[event]) {
          events[event] = events[event].filter(cb => cb !== callback);
        }
      },

      emit(event, data) {
        if (events[event]) {
          events[event].forEach(callback => callback(data));
        }
      }
    };
  }

  // Performance measurement helper
  static measurePerformance(name, fn) {
    const start = performance.now();
    const result = fn();
    const end = performance.now();
    console.log(`${name} took ${end - start} milliseconds`);
    return result;
  }

  // Async version of measurePerformance
  static async measurePerformanceAsync(name, fn) {
    const start = performance.now();
    const result = await fn();
    const end = performance.now();
    console.log(`${name} took ${end - start} milliseconds`);
    return result;
  }
}
