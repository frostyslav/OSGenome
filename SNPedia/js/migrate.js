/**
 * Migration Helper Script
 * Helps transition from monolithic app.js to modular structure
 */

// This script can be used to verify that the modular version works correctly
// and provides debugging utilities during the migration process

class MigrationHelper {
  constructor() {
    this.originalFunctions = {};
    this.modularFunctions = {};
    this.testResults = [];
  }

  // Capture original global functions before loading modular version
  captureOriginalFunctions() {
    const functionsToCheck = [
      'exportToExcel',
      'exportToPDF',
      'lookupSNPedia',
      'showKeyboardShortcuts',
      'hideKeyboardShortcuts',
      'focusSearch',
      'toggleColumnMenu',
      'clearAllFilters',
      'reloadData',
      'toggleDarkMode'
    ];

    functionsToCheck.forEach(funcName => {
      if (typeof window[funcName] === 'function') {
        this.originalFunctions[funcName] = window[funcName];
      }
    });

    console.log('Captured original functions:', Object.keys(this.originalFunctions));
  }

  // Capture modular functions after loading modular version
  captureModularFunctions() {
    const functionsToCheck = [
      'exportToExcel',
      'exportToPDF',
      'lookupSNPedia',
      'showKeyboardShortcuts',
      'hideKeyboardShortcuts',
      'focusSearch',
      'toggleColumnMenu',
      'clearAllFilters',
      'reloadData',
      'toggleDarkMode'
    ];

    functionsToCheck.forEach(funcName => {
      if (typeof window[funcName] === 'function') {
        this.modularFunctions[funcName] = window[funcName];
      }
    });

    console.log('Captured modular functions:', Object.keys(this.modularFunctions));
  }

  // Compare function availability
  compareFunctions() {
    const originalKeys = Object.keys(this.originalFunctions);
    const modularKeys = Object.keys(this.modularFunctions);

    console.log('=== Function Comparison ===');
    console.log('Original functions:', originalKeys.length);
    console.log('Modular functions:', modularKeys.length);

    // Check for missing functions
    const missing = originalKeys.filter(key => !modularKeys.includes(key));
    const added = modularKeys.filter(key => !originalKeys.includes(key));

    if (missing.length > 0) {
      console.warn('Missing functions in modular version:', missing);
    }

    if (added.length > 0) {
      console.log('New functions in modular version:', added);
    }

    if (missing.length === 0 && originalKeys.length === modularKeys.length) {
      console.log('✅ All functions successfully migrated');
    }

    return { missing, added, originalCount: originalKeys.length, modularCount: modularKeys.length };
  }

  // Test basic functionality
  async testBasicFunctionality() {
    console.log('=== Testing Basic Functionality ===');

    const tests = [
      {
        name: 'SNPediaApp exists',
        test: () => typeof window.SNPediaApp !== 'undefined',
        expected: true
      },
      {
        name: 'Table initialized',
        test: () => window.SNPediaApp && window.SNPediaApp.getTable() !== null,
        expected: true
      },
      {
        name: 'Managers initialized',
        test: () => {
          const managers = window.SNPediaApp?.getAllManagers();
          return managers && Object.keys(managers).length > 0;
        },
        expected: true
      },
      {
        name: 'Theme manager works',
        test: () => {
          const themeManager = window.SNPediaApp?.getManager('theme');
          return themeManager && typeof themeManager.toggleDarkMode === 'function';
        },
        expected: true
      },
      {
        name: 'Export manager works',
        test: () => {
          const exportManager = window.SNPediaApp?.getManager('export');
          return exportManager && typeof exportManager.exportToExcel === 'function';
        },
        expected: true
      }
    ];

    tests.forEach(test => {
      try {
        const result = test.test();
        const passed = result === test.expected;

        this.testResults.push({
          name: test.name,
          passed,
          result,
          expected: test.expected
        });

        console.log(`${passed ? '✅' : '❌'} ${test.name}: ${result}`);
      } catch (error) {
        this.testResults.push({
          name: test.name,
          passed: false,
          error: error.message
        });
        console.log(`❌ ${test.name}: Error - ${error.message}`);
      }
    });

    const passedTests = this.testResults.filter(t => t.passed).length;
    console.log(`\n=== Test Summary ===`);
    console.log(`Passed: ${passedTests}/${tests.length}`);

    return this.testResults;
  }

  // Generate migration report
  generateReport() {
    const report = {
      timestamp: new Date().toISOString(),
      functions: this.compareFunctions(),
      tests: this.testResults,
      recommendations: []
    };

    // Add recommendations based on results
    if (report.functions.missing.length > 0) {
      report.recommendations.push('Some functions are missing in the modular version. Check the main app initialization.');
    }

    const failedTests = report.tests.filter(t => !t.passed);
    if (failedTests.length > 0) {
      report.recommendations.push(`${failedTests.length} tests failed. Check console for details.`);
    }

    if (report.functions.missing.length === 0 && failedTests.length === 0) {
      report.recommendations.push('Migration appears successful! You can safely switch to the modular version.');
    }

    console.log('\n=== Migration Report ===');
    console.log(JSON.stringify(report, null, 2));

    return report;
  }

  // Helper method to run full migration check
  async runFullCheck() {
    console.log('🔄 Running full migration check...');

    // Wait a bit for everything to initialize
    await new Promise(resolve => setTimeout(resolve, 1000));

    this.captureModularFunctions();
    await this.testBasicFunctionality();
    return this.generateReport();
  }
}

// Make available globally for manual testing
window.MigrationHelper = MigrationHelper;

// Auto-run check if modular app is detected
if (typeof window.SNPediaApp !== 'undefined') {
  const helper = new MigrationHelper();
  setTimeout(() => {
    helper.runFullCheck().then(report => {
      console.log('Migration check complete. See report above.');
    });
  }, 2000);
}

console.log('Migration helper loaded. Use new MigrationHelper() to run manual checks.');
