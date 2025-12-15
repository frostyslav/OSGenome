/**
 * Data Manager Module
 * Handles data loading, reloading, and API interactions
 */

export class DataManager {
  constructor(table) {
    this.table = table;
  }

  async loadData() {
    const spinner = document.getElementById('loadingSpinner');
    spinner.classList.remove('hidden');

    try {
      console.log('Loading data...');
      const response = await fetch('/api/rsids');

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Data received:', data.results ? data.results.length + ' rows' : 'no results');

      spinner.classList.add('hidden');

      if (data.results && data.results.length > 0) {
        this.table.setData(data.results);
        console.log('Data loaded into table');
        return data.results;
      } else {
        console.warn('No data to display');
        return [];
      }
    } catch (error) {
      spinner.classList.add('hidden');
      console.error('Error loading data:', error);
      throw error;
    }
  }

  async reloadData() {
    if (!this.table) return;

    const spinner = document.getElementById('loadingSpinner');
    spinner.classList.remove('hidden');

    try {
      const response = await fetch('/api/rsids');
      const data = await response.json();

      spinner.classList.add('hidden');

      if (data.results && data.results.length > 0) {
        this.table.setData(data.results);
        console.log('Data reloaded');
        return data.results;
      }
    } catch (error) {
      spinner.classList.add('hidden');
      console.error('Error reloading data:', error);
      throw error;
    }
  }
}
