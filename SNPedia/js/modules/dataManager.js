/**
 * Data Manager Module
 * Handles data loading, reloading, and API interactions
 */

export class DataManager {
  constructor(table) {
    this.table = table;
  }

  async loadData(retryCount = 0, maxRetries = 3) {
    const spinner = document.getElementById('loadingSpinner');
    spinner.classList.remove('hidden');

    try {
      console.log(`Loading data... (attempt ${retryCount + 1})`);
      console.log('Table state:', this.table ? 'initialized' : 'not initialized');
      console.log('Spinner element:', spinner ? 'found' : 'not found');
      console.log('Fetch timestamp:', new Date().toISOString());
      
      const fetchStart = performance.now();
      const response = await fetch('/api/rsids');
      const fetchEnd = performance.now();
      console.log(`Fetch completed in ${fetchEnd - fetchStart}ms`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Data received:', data.results ? data.results.length + ' rows' : 'no results');
      console.log('Full response:', data);

      spinner.classList.add('hidden');

      if (data.results && data.results.length > 0) {
        console.log('About to set data on table:', this.table);
        
        // Ensure table is properly initialized
        if (!this.table) {
          throw new Error('Table not initialized');
        }
        
        // Check if table element exists in DOM
        const tableElement = document.getElementById('grid');
        if (!tableElement) {
          throw new Error('Table element not found in DOM');
        }
        
        // Use a more reliable way to set data
        try {
          this.table.setData(data.results);
        } catch (tableError) {
          console.warn('Direct setData failed, waiting for table to be ready:', tableError);
          // If direct setData fails, wait for table to be built and try again
          await new Promise(resolve => {
            if (this.table.initialized) {
              resolve();
            } else {
              this.table.on("tableBuilt", resolve);
            }
          });
          this.table.setData(data.results);
        }
        console.log('Data loaded into table successfully');
        return data.results;
      } else if (retryCount < maxRetries) {
        // If no data and we haven't exceeded retries, wait and try again
        console.warn(`No data received, retrying in ${(retryCount + 1) * 1000}ms...`);
        spinner.classList.remove('hidden');
        await new Promise(resolve => setTimeout(resolve, (retryCount + 1) * 1000));
        return this.loadData(retryCount + 1, maxRetries);
      } else {
        console.warn('No data to display after all retries');
        this.showNoDataMessage();
        return [];
      }
    } catch (error) {
      spinner.classList.add('hidden');
      
      if (retryCount < maxRetries) {
        console.warn(`Error loading data, retrying in ${(retryCount + 1) * 1000}ms...`, error);
        spinner.classList.remove('hidden');
        await new Promise(resolve => setTimeout(resolve, (retryCount + 1) * 1000));
        return this.loadData(retryCount + 1, maxRetries);
      } else {
        console.error('Error loading data after all retries:', error);
        throw error;
      }
    }
  }

  async reloadData() {
    if (!this.table) return;

    // Use the same retry logic as loadData
    return this.loadData();
  }

  showNoDataMessage() {
    // Create a helpful message for users when no data is available
    const gridElement = document.getElementById('grid');
    if (gridElement) {
      gridElement.innerHTML = `
        <div style="text-align: center; padding: 40px; color: #666; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
          <div style="font-size: 48px; margin-bottom: 20px;">📊</div>
          <h3 style="color: #333; margin-bottom: 16px;">No Genetic Data Available</h3>
          <p style="margin-bottom: 20px; color: #666;">No processed genetic data was found. This could mean:</p>
          
          <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin: 20px auto; max-width: 500px; text-align: left;">
            <h4 style="margin-top: 0; color: #495057;">To get started:</h4>
            <ol style="margin: 0; padding-left: 20px; line-height: 1.6;">
              <li><strong>Import</strong> your genome data file (23andMe, AncestryDNA, etc.)</li>
              <li><strong>Crawl</strong> SNPedia for reference information</li>
              <li><strong>Process</strong> the results to generate the display data</li>
            </ol>
          </div>

          <div style="background: #e3f2fd; border-radius: 8px; padding: 15px; margin: 20px auto; max-width: 500px;">
            <strong>CLI Command:</strong><br>
            <code style="background: #fff; padding: 4px 8px; border-radius: 4px; font-family: monospace;">
              python -m SNPedia.cli pipeline -f your_genome_file.txt
            </code>
          </div>

          <button onclick="reloadData()" style="margin-top: 20px; padding: 12px 24px; background: #007bff; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 500;">
            🔄 Try Again
          </button>
          
          <p style="margin-top: 20px; font-size: 12px; color: #999;">
            See the <code>data/README.md</code> file for detailed instructions
          </p>
        </div>
      `;
    }
  }
}
