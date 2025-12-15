console.log('Script loaded');
let table;

// Check if Tabulator is available
if (typeof Tabulator === 'undefined') {
  console.error('Tabulator not loaded!');
  alert('Tabulator library failed to load. Check network tab.');
} else {
  console.log('Tabulator available');
}

// Initialize Tabulator
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM loaded, initializing table...');

  // Load saved theme first
  loadSavedTheme();

  try {
    table = new Tabulator("#grid", {
      layout: "fitColumns",
      layoutColumnsOnNewData: true,
      height: "100%",
      pagination: true,
      paginationSize: 50,
      paginationSizeSelector: [25, 50, 100, 250],
      movableColumns: true,
      resizableColumnFit: true,
      selectable: true,
      selectableRollingSelection: false,
      columns: [
        {
          title: "Name",
          field: "Name",
          visible: true,
          headerFilter: "input",
          width: 120
        },
        {
          title: "Short Description",
          field: "Description",
          headerFilter: "input",
          widthGrow: 2,
          formatter: "html"
        },
        {
          title: "Stabilized Orientation",
          field: "StabilizedOrientation",
          visible: false,
          headerFilter: "input"
        },
        {
          title: "Individual Genotype",
          field: "Genotype",
          visible: false,
          headerFilter: "input",
          formatter: "html"
        },
        {
          title: "Genotype variations",
          field: "Variations",
          headerFilter: "input",
          widthGrow: 1,
          formatter: "html"
        },
        {
          title: "Interesting genotype",
          field: "IsInteresting",
          visible: false,
          headerFilter: "list",
          headerFilterParams: {
            values: {
              "": "All",
              "Yes": "Yes",
              "No": "No"
            },
            clearable: true,
            placeholder: "Filter..."
          }
        },
        {
          title: "Uncommon genotype",
          field: "IsUncommon",
          visible: false,
          headerFilter: "list",
          headerFilterParams: {
            values: {
              "": "All",
              "Yes": "Yes",
              "No": "No"
            },
            clearable: true,
            placeholder: "Filter..."
          }
        }
      ],
      initialSort: [
        { column: "IsUncommon", dir: "desc" }
      ],
      cellClick: function(e, cell) {
        console.log('Cell clicked!');
        const row = cell.getRow();
        console.log('Row data:', row.getData());
        // Deselect all rows first, then select clicked row
        table.deselectRow();
        row.select();
        console.log('Row selected, isSelected:', row.isSelected());
        console.log('Selected rows:', table.getSelectedRows().length);
      },
      rowDblClick: function(e, row) {
        console.log('Row double-clicked!');
        const rowData = row.getData();
        const rsid = rowData.Name;
        if (rsid) {
          console.log('Looking up RSid:', rsid);
          const url = 'https://snpedia.com/index.php/' + rsid;
          window.open(url, '_blank');
        }
      },
      rowSelectionChanged: function(data, rows) {
        console.log('Selection changed:', rows.length, 'rows selected');
      }
    });

    console.log('Table initialized');

    // Show loading spinner
    const spinner = document.getElementById('loadingSpinner');
    spinner.classList.remove('hidden');

    // Load data
    fetch('/api/rsids')
      .then(response => {
        console.log('Response status:', response.status);
        return response.json();
      })
      .then(data => {
        console.log('Data received:', data.results ? data.results.length + ' rows' : 'no results');
        // Hide loading spinner
        spinner.classList.add('hidden');

        if (data.results && data.results.length > 0) {
          table.setData(data.results);
          console.log('Data loaded into table');

          // Set up filter change listeners
          table.on("headerFilterChanged", function(field, value) {
            console.log('Filter changed:', field, value);
            updateFilterButtonState();
          });

          // Initial filter button state check
          setTimeout(function() {
            updateFilterButtonState();
          }, 100);

          // Add a test to verify selectable is working
          setTimeout(function() {
            console.log('Table selectable config:', table.options.selectable);
            console.log('Total rows:', table.getRows().length);

            // Add direct DOM listener to handle row selection
            const gridElement = document.getElementById('grid');
            let clickTimeout;
            
            gridElement.addEventListener('click', function(e) {
              // Clear any existing timeout to prevent single click action on double click
              clearTimeout(clickTimeout);
              
              clickTimeout = setTimeout(function() {
                console.log('Single click detected!', e.target.className);

                // Find the row element
                let rowElement = e.target;
                while (rowElement && !rowElement.classList.contains('tabulator-row')) {
                  rowElement = rowElement.parentElement;
                }

                if (rowElement && rowElement.classList.contains('tabulator-row')) {
                  console.log('Row element found!');
                  // Get the row component from Tabulator
                  const rows = table.getRows();
                  for (let i = 0; i < rows.length; i++) {
                    if (rows[i].getElement() === rowElement) {
                      console.log('Matching row found, selecting...');
                      table.deselectRow();
                      rows[i].select();
                      console.log('Row selected!');
                      break;
                    }
                  }
                }
              }, 250); // Delay to allow double-click detection
            });

            // Add double-click handler
            gridElement.addEventListener('dblclick', function(e) {
              // Clear the single click timeout
              clearTimeout(clickTimeout);
              
              console.log('Double click detected!', e.target.className);

              // Find the row element
              let rowElement = e.target;
              while (rowElement && !rowElement.classList.contains('tabulator-row')) {
                rowElement = rowElement.parentElement;
              }

              if (rowElement && rowElement.classList.contains('tabulator-row')) {
                console.log('Row element found for double-click!');
                // Get the row component from Tabulator
                const rows = table.getRows();
                for (let i = 0; i < rows.length; i++) {
                  if (rows[i].getElement() === rowElement) {
                    const rowData = rows[i].getData();
                    const rsid = rowData.Name;
                    if (rsid) {
                      console.log('Looking up RSid:', rsid);
                      const url = 'https://snpedia.com/index.php/' + rsid;
                      window.open(url, '_blank');
                    }
                    break;
                  }
                }
              }
            });
          }, 1000);
        } else {
          console.warn('No data to display');
        }
      })
      .catch(error => {
        // Hide loading spinner on error
        spinner.classList.add('hidden');
        console.error('Error loading data:', error);
        alert('Error loading data: ' + error.message);
      });
  } catch (error) {
    console.error('Error initializing table:', error);
    alert('Error initializing table: ' + error.message);
  }
});

// Export to Excel
function exportToExcel() {
  if (table) {
    table.download("xlsx", "SNP Report.xlsx", {
      sheetName: "SNP Data"
    });
  }
}

// Check PDF libraries (for debugging)
function checkPDFLibraries() {
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

// Export to PDF with charts
function exportToPDF() {
  console.log('PDF export started...');
  
  if (!table) {
    console.error('Table not available');
    alert('Table not available for export');
    return;
  }

  // Simple check for jsPDF
  if (typeof window.jspdf === 'undefined' && typeof window.jsPDF === 'undefined') {
    console.error('jsPDF library not loaded');
    alert('PDF library not loaded. Please refresh the page and try again.');
    return;
  }

  try {
    // Try different ways to access jsPDF
    let jsPDF;
    if (window.jspdf && window.jspdf.jsPDF) {
      jsPDF = window.jspdf.jsPDF;
    } else if (window.jsPDF) {
      jsPDF = window.jsPDF;
    } else {
      throw new Error('jsPDF constructor not found');
    }

    const doc = new jsPDF();
    console.log('jsPDF initialized successfully');
    
    // Get all table data for statistics, filter uncommon for export
    const allData = table.getData();
    const uncommonData = allData.filter(row => row.IsUncommon === 'Yes');
    console.log('All data:', allData.length, 'rows');
    console.log('Uncommon RSIDs for export:', uncommonData.length, 'rows');
    
    // Title
    doc.setFontSize(20);
    doc.text('Uncommon SNPs Report', 20, 20);
    
    // Date
    doc.setFontSize(12);
    doc.text(`Generated: ${new Date().toLocaleDateString()}`, 20, 35);
    
    // Calculate statistics from all data for pie chart
    const totalSNPs = allData.length;
    const interestingSNPs = allData.filter(row => row.IsInteresting === 'Yes').length;
    const uncommonSNPs = allData.filter(row => row.IsUncommon === 'Yes').length;
    const regularSNPs = totalSNPs - uncommonSNPs - interestingSNPs;
    
    // Statistics for display
    const totalUncommonSNPs = uncommonData.length;
    const interestingUncommonSNPs = uncommonData.filter(row => row.IsInteresting === 'Yes').length;
    
    doc.setFontSize(14);
    doc.text('Summary Statistics:', 20, 55);
    doc.setFontSize(12);
    doc.text(`Total SNPs: ${totalSNPs}`, 30, 70);
    doc.text(`Interesting SNPs: ${interestingSNPs}`, 30, 80);
    doc.text(`Uncommon SNPs: ${uncommonSNPs}`, 30, 90);
    doc.text(`Regular SNPs: ${regularSNPs}`, 30, 100);
    
    doc.setFontSize(10);
    doc.text(`Note: Table below shows only uncommon SNPs (${totalUncommonSNPs} entries)`, 30, 115);
    
    // Check if Chart.js is available for charts
    if (typeof Chart !== 'undefined') {
      console.log('Chart.js available, adding pie chart to PDF...');
      // Add some space for charts
      doc.text('Overall Distribution:', 20, 130);
      addPieChartToPDF(doc, uncommonData, interestingSNPs, uncommonSNPs, regularSNPs, totalSNPs);
    } else {
      console.warn('Chart.js not available, creating simple pie chart manually');
      // Create simple pie chart without Chart.js
      addSimplePieChartToPDF(doc, uncommonData, interestingSNPs, uncommonSNPs, regularSNPs, totalSNPs);
    }
    
  } catch (error) {
    console.error('Error creating PDF:', error);
    alert('Error creating PDF: ' + error.message);
  }
}

// Add pie chart to PDF (Chart.js version)
function addPieChartToPDF(doc, uncommonData, interestingSNPs, uncommonSNPs, regularSNPs, totalSNPs) {
  try {
    console.log('Creating charts for PDF...');
    console.log('Chart.js version:', Chart.version);
    
    // Create a temporary canvas for charts
    const canvas = document.createElement('canvas');
    canvas.width = 600;
    canvas.height = 400;
    canvas.style.position = 'absolute';
    canvas.style.left = '-9999px';
    canvas.style.top = '-9999px';
    document.body.appendChild(canvas);
    const ctx = canvas.getContext('2d');
    
    // Calculate chart data for all SNP categories
    const chartData = [interestingSNPs, uncommonSNPs, regularSNPs];
    
    console.log('All SNPs chart data:', { 
      interestingSNPs, 
      uncommonSNPs, 
      regularSNPs, 
      totalSNPs,
      chartData 
    });
    
    // Test canvas
    ctx.fillStyle = 'red';
    ctx.fillRect(0, 0, 50, 50);
    const testImage = canvas.toDataURL('image/png');
    console.log('Canvas test image length:', testImage.length);
    
    // Clear test
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Create pie chart for all SNP categories
    const pieChart = new Chart(ctx, {
      type: 'pie',
      data: {
        labels: ['Interesting', 'Uncommon', 'Regular'],
        datasets: [{
          data: chartData,
          backgroundColor: [
            '#FF6384',
            '#36A2EB',
            '#FFCE56'
          ],
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: false,
        maintainAspectRatio: false,
        animation: {
          duration: 0
        },
        plugins: {
          title: {
            display: true,
            text: 'SNP Categories Distribution',
            font: { 
              size: 20,
              weight: 'bold'
            },
            padding: 20
          },
          legend: {
            position: 'bottom',
            labels: {
              font: {
                size: 14
              },
              padding: 15
            }
          }
        }
      }
    });

    console.log('Pie chart created, waiting for render...');

    // Wait longer for chart to render and force update
    setTimeout(() => {
      try {
        // Force chart update
        pieChart.update('none');
        
        console.log('Capturing pie chart...');
        
        // Get image data
        const pieImageData = canvas.toDataURL('image/png');
        console.log('Pie chart image data length:', pieImageData.length);
        
        if (pieImageData.length > 1000) {
          // Add pie chart to PDF (centered)
          doc.addImage(pieImageData, 'PNG', 70, 145, 80, 60);
          console.log('Pie chart added to PDF successfully');
        } else {
          console.warn('Pie chart image seems empty');
        }
        
        // Clean up pie chart
        pieChart.destroy();
        canvas.remove();
        
        // Add table data (uncommon SNPs only)
        addTableToPDF(doc, uncommonData);
        
        // Save PDF
        doc.save('Uncommon_SNPs_Report.pdf');
        console.log('PDF saved successfully with pie chart');
        
      } catch (error) {
        console.error('Error processing pie chart:', error);
        // Fallback: save without charts
        canvas.remove();
        addTableToPDF(doc, data);
        doc.save('SNP_Analysis_Report.pdf');
      }
    }, 2000);
    
  } catch (error) {
    console.error('Error in addChartsToPDF:', error);
    // Fallback: create PDF without charts
    addTableToPDF(doc, data);
    doc.save('SNP_Analysis_Report.pdf');
  }
}

// Create bar chart for genotype variations
function createBarChart(doc, canvas, ctx, data) {
  try {
    console.log('Creating bar chart...');
    
    // Count genotype variations
    const variationCounts = {};
    let totalVariations = 0;
    
    data.forEach(row => {
      if (row.Variations) {
        const variations = row.Variations.replace(/<[^>]*>/g, '').split(',');
        variations.forEach(variation => {
          const trimmed = variation.trim();
          if (trimmed && trimmed.length > 0) {
            variationCounts[trimmed] = (variationCounts[trimmed] || 0) + 1;
            totalVariations++;
          }
        });
      }
    });
    
    console.log('Total variations found:', totalVariations);
    console.log('Unique variations:', Object.keys(variationCounts).length);
    
    // Get top 6 variations (fewer for better readability)
    const sortedVariations = Object.entries(variationCounts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 6);
    
    console.log('Top variations for chart:', sortedVariations);
    
    if (sortedVariations.length > 0) {
      const barChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: sortedVariations.map(([variation]) => 
            variation.length > 6 ? variation.substring(0, 6) + '...' : variation
          ),
          datasets: [{
            label: 'Frequency',
            data: sortedVariations.map(([, count]) => count),
            backgroundColor: '#36A2EB',
            borderColor: '#2E86AB',
            borderWidth: 1
          }]
        },
        options: {
          responsive: false,
          maintainAspectRatio: false,
          animation: {
            duration: 0
          },
          plugins: {
            title: {
              display: true,
              text: 'Top Genotype Variations',
              font: { 
                size: 20,
                weight: 'bold'
              },
              padding: 20
            },
            legend: {
              display: false
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                font: {
                  size: 12
                }
              }
            },
            x: {
              ticks: {
                font: {
                  size: 12
                }
              }
            }
          }
        }
      });

      console.log('Bar chart created, waiting for render...');

      setTimeout(() => {
        try {
          // Force chart update
          barChart.update('none');
          
          console.log('Capturing bar chart...');
          
          // Get image data
          const barImageData = canvas.toDataURL('image/png');
          console.log('Bar chart image data length:', barImageData.length);
          
          if (barImageData.length > 1000) {
            // Add bar chart to PDF
            doc.addImage(barImageData, 'PNG', 110, 125, 80, 60);
            console.log('Bar chart added to PDF successfully');
          } else {
            console.warn('Bar chart image seems empty');
          }
          
          // Clean up
          barChart.destroy();
          canvas.remove();
          
          // Add table data
          addTableToPDF(doc, data);
          
          // Save PDF
          doc.save('SNP_Analysis_Report.pdf');
          console.log('PDF saved successfully with charts');
          
        } catch (error) {
          console.error('Error processing bar chart:', error);
          // Fallback: save without bar chart
          canvas.remove();
          addTableToPDF(doc, data);
          doc.save('SNP_Analysis_Report.pdf');
        }
      }, 2000);
    } else {
      console.log('No variations found, creating simple summary chart');
      // Create a simple summary chart instead
      createSummaryChart(doc, canvas, ctx, data);
    }
    
  } catch (error) {
    console.error('Error creating bar chart:', error);
    // Fallback: save without bar chart
    canvas.remove();
    addTableToPDF(doc, data);
    doc.save('SNP_Analysis_Report.pdf');
  }
}

// Create simple summary chart if no variations found
function createSummaryChart(doc, canvas, ctx, data) {
  try {
    console.log('Creating summary chart...');
    
    // Simple data summary
    const hasGenotype = data.filter(row => row.Genotype && row.Genotype.trim()).length;
    const hasVariations = data.filter(row => row.Variations && row.Variations.trim()).length;
    const hasDescription = data.filter(row => row.Description && row.Description.trim()).length;
    
    const summaryChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Has Genotype', 'Has Variations', 'Has Description'],
        datasets: [{
          label: 'Count',
          data: [hasGenotype, hasVariations, hasDescription],
          backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56'],
          borderWidth: 1
        }]
      },
      options: {
        responsive: false,
        maintainAspectRatio: false,
        animation: { duration: 0 },
        plugins: {
          title: {
            display: true,
            text: 'Data Completeness',
            font: { size: 20, weight: 'bold' },
            padding: 20
          },
          legend: { display: false }
        },
        scales: {
          y: { beginAtZero: true }
        }
      }
    });

    setTimeout(() => {
      try {
        summaryChart.update('none');
        const summaryImageData = canvas.toDataURL('image/png');
        
        if (summaryImageData.length > 1000) {
          doc.addImage(summaryImageData, 'PNG', 110, 125, 80, 60);
          console.log('Summary chart added to PDF');
        }
        
        summaryChart.destroy();
        canvas.remove();
        addTableToPDF(doc, data);
        doc.save('SNP_Analysis_Report.pdf');
        console.log('PDF saved with summary chart');
        
      } catch (error) {
        console.error('Error with summary chart:', error);
        canvas.remove();
        addTableToPDF(doc, data);
        doc.save('SNP_Analysis_Report.pdf');
      }
    }, 2000);
    
  } catch (error) {
    console.error('Error creating summary chart:', error);
    canvas.remove();
    addTableToPDF(doc, data);
    doc.save('SNP_Analysis_Report.pdf');
  }
}

// Create charts for PDF
function createChartsForPDF(doc, data, interestingSNPs, uncommonSNPs, totalSNPs) {
  try {
    console.log('Creating charts for PDF...');
    
    // Create a temporary canvas for charts
    const canvas = document.createElement('canvas');
    canvas.width = 400;
    canvas.height = 300;
    canvas.style.display = 'none'; // Hide from view
    document.body.appendChild(canvas); // Add to DOM for rendering
    const ctx = canvas.getContext('2d');
    
    // Calculate chart data
    const regularSNPs = totalSNPs - uncommonSNPs;
    const chartData = [interestingSNPs, uncommonSNPs - interestingSNPs, regularSNPs];
    
    console.log('Chart data:', { interestingSNPs, uncommonSNPs, regularSNPs, totalSNPs });
    
    // Chart 1: SNP Categories Pie Chart
    const pieChart = new Chart(ctx, {
      type: 'pie',
      data: {
        labels: ['Interesting', 'Uncommon Only', 'Regular'],
        datasets: [{
          data: chartData,
          backgroundColor: [
            '#FF6384',
            '#36A2EB', 
            '#FFCE56'
          ]
        }]
      },
      options: {
        responsive: false,
        animation: false,
        plugins: {
          title: {
            display: true,
            text: 'SNP Categories Distribution'
          },
          legend: {
            position: 'bottom'
          }
        }
      }
    });

    // Wait for chart to render, then add to PDF
    setTimeout(() => {
      try {
        console.log('Adding pie chart to PDF...');
        
        // Add pie chart to PDF
        const pieImageData = canvas.toDataURL('image/png');
        doc.addImage(pieImageData, 'PNG', 20, 110, 80, 60);
        
        // Destroy pie chart and create bar chart
        pieChart.destroy();
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Count genotype variations for bar chart
        const variationCounts = {};
        data.forEach(row => {
          if (row.Variations) {
            const variations = row.Variations.replace(/<[^>]*>/g, '').split(',');
            variations.forEach(variation => {
              const trimmed = variation.trim();
              if (trimmed && trimmed.length > 0) {
                variationCounts[trimmed] = (variationCounts[trimmed] || 0) + 1;
              }
            });
          }
        });
        
        // Get top 8 variations (fewer for better readability)
        const sortedVariations = Object.entries(variationCounts)
          .sort(([,a], [,b]) => b - a)
          .slice(0, 8);
        
        console.log('Top variations:', sortedVariations);
        
        if (sortedVariations.length > 0) {
          const barChart = new Chart(ctx, {
            type: 'bar',
            data: {
              labels: sortedVariations.map(([variation]) => 
                variation.length > 8 ? variation.substring(0, 8) + '...' : variation
              ),
              datasets: [{
                label: 'Count',
                data: sortedVariations.map(([, count]) => count),
                backgroundColor: '#36A2EB'
              }]
            },
            options: {
              responsive: false,
              animation: false,
              plugins: {
                title: {
                  display: true,
                  text: 'Top Genotype Variations'
                }
              },
              scales: {
                y: {
                  beginAtZero: true
                }
              }
            }
          });

          setTimeout(() => {
            try {
              console.log('Adding bar chart to PDF...');
              
              // Add bar chart to PDF
              const barImageData = canvas.toDataURL('image/png');
              doc.addImage(barImageData, 'PNG', 110, 110, 80, 60);
              
              // Add table data
              addTableToPDF(doc, data);
              
              // Clean up
              barChart.destroy();
              canvas.remove();
              
              // Save PDF
              doc.save('SNP_Analysis_Report.pdf');
              console.log('PDF saved successfully with charts');
              
            } catch (error) {
              console.error('Error adding bar chart:', error);
              // Fallback: save without bar chart
              canvas.remove();
              addTableToPDF(doc, data);
              doc.save('SNP_Analysis_Report.pdf');
            }
          }, 800);
        } else {
          console.log('No variations found, skipping bar chart');
          // Add table data without bar chart
          addTableToPDF(doc, data);
          canvas.remove();
          doc.save('SNP_Analysis_Report.pdf');
        }
        
      } catch (error) {
        console.error('Error creating charts:', error);
        // Fallback: save PDF without charts
        canvas.remove();
        addTableToPDF(doc, data);
        doc.save('SNP_Analysis_Report.pdf');
      }
    }, 1000);
    
  } catch (error) {
    console.error('Error in createChartsForPDF:', error);
    // Fallback: create PDF without charts
    addTableToPDF(doc, data);
    doc.save('SNP_Analysis_Report.pdf');
  }
}

// Add table data to PDF
function addTableToPDF(doc, data) {
  // Add new page for table
  doc.addPage();
  
  doc.setFontSize(16);
  doc.text('SNP Data Table', 20, 20);
  
  // Table headers
  const headers = ['Name', 'Description', 'Variations', 'Interesting', 'Uncommon'];
  let yPos = 40;
  
  // Header row
  doc.setFontSize(10);
  doc.setFont(undefined, 'bold');
  headers.forEach((header, index) => {
    doc.text(header, 20 + (index * 35), yPos);
  });
  
  // Data rows (limit to first 30 rows to fit on page)
  doc.setFont(undefined, 'normal');
  yPos += 10;
  
  const maxRows = Math.min(30, data.length);
  for (let i = 0; i < maxRows; i++) {
    const row = data[i];
    yPos += 8;
    
    // Check if we need a new page
    if (yPos > 270) {
      doc.addPage();
      yPos = 30;
      
      // Repeat headers
      doc.setFont(undefined, 'bold');
      headers.forEach((header, index) => {
        doc.text(header, 20 + (index * 35), yPos);
      });
      doc.setFont(undefined, 'normal');
      yPos += 10;
    }
    
    // Row data
    doc.text(row.Name || '', 20, yPos);
    doc.text((row.Description || '').replace(/<[^>]*>/g, '').substring(0, 20) + '...', 55, yPos);
    doc.text((row.Variations || '').replace(/<[^>]*>/g, '').substring(0, 15) + '...', 90, yPos);
    doc.text(row.IsInteresting || 'No', 125, yPos);
    doc.text(row.IsUncommon || 'No', 160, yPos);
  }
  
  // Add footer note if data was truncated
  if (data.length > 30) {
    yPos += 15;
    doc.setFontSize(8);
    doc.text(`Note: Showing first 30 of ${data.length} total SNPs. Export to Excel for complete data.`, 20, yPos);
  }
}

// Lookup selected SNP on SNPedia
function lookupSNPedia() {
  if (!table) return;

  // Try to get selected rows first
  let selectedRows = table.getSelectedData();

  // If no selection, prompt user to enter RSid
  if (selectedRows.length === 0) {
    const rsid = prompt('Enter RSid (e.g., rs3131972) or click a row first:');
    if (rsid && rsid.trim()) {
      const url = 'https://snpedia.com/index.php/' + rsid.trim();
      window.open(url, '_blank');
    }
    return;
  }

  const rsid = selectedRows[0].Name;
  const url = 'https://snpedia.com/index.php/' + rsid;
  window.open(url, '_blank');
}

// Show keyboard shortcuts help
function showKeyboardShortcuts() {
  const modal = document.getElementById('shortcutsModal');
  modal.classList.add('show');
}

// Hide keyboard shortcuts modal
function hideKeyboardShortcuts() {
  const modal = document.getElementById('shortcutsModal');
  modal.classList.remove('show');
}

// Close modal when clicking outside
document.addEventListener('click', function(e) {
  const modal = document.getElementById('shortcutsModal');
  if (e.target === modal) {
    hideKeyboardShortcuts();
  }
});

// Reload table data
function reloadData() {
  if (!table) return;

  const spinner = document.getElementById('loadingSpinner');
  spinner.classList.remove('hidden');

  fetch('/api/rsids')
    .then(response => response.json())
    .then(data => {
      spinner.classList.add('hidden');
      if (data.results && data.results.length > 0) {
        table.setData(data.results);
        console.log('Data reloaded');
        // Update filter button state after reload
        setTimeout(function() {
          updateFilterButtonState();
        }, 100);
      }
    })
    .catch(error => {
      spinner.classList.add('hidden');
      console.error('Error reloading data:', error);
      alert('Error reloading data: ' + error.message);
    });
}

// Focus first header filter input
function focusSearch() {
  const firstFilter = document.querySelector('.tabulator-header-filter input');
  if (firstFilter) {
    firstFilter.focus();
  }
}

// Clear all filters
function clearAllFilters() {
  if (!table) return;

  console.log('Clearing all filters...');

  // Check if there were any active filters before clearing
  const hadActiveFilters = table.getHeaderFilters().some(filter =>
    filter.value !== undefined && filter.value !== null && filter.value !== ""
  );

  // Clear all header filters
  table.clearHeaderFilter();

  // Update filter button state
  updateFilterButtonState();

  // Show feedback if filters were actually cleared
  if (hadActiveFilters) {
    showFilterNotification('All filters cleared');
  } else {
    showFilterNotification('No active filters to clear');
  }

  console.log('All filters cleared');
}

// Show a brief notification about filter actions
function showFilterNotification(message) {
  // Create or get existing notification element
  let notification = document.getElementById('filterNotification');
  if (!notification) {
    notification = document.createElement('div');
    notification.id = 'filterNotification';
    notification.className = 'filter-notification';
    document.body.appendChild(notification);
  }

  notification.textContent = message;
  notification.classList.add('show');

  // Hide after 2 seconds
  setTimeout(function() {
    notification.classList.remove('show');
  }, 2000);
}

// Check if any filters are active and update button state
function updateFilterButtonState() {
  if (!table) return;

  const clearButton = document.querySelector('button[onclick="clearAllFilters()"]');
  if (!clearButton) return;

  // Check if any header filters have values
  const hasActiveFilters = table.getHeaderFilters().some(filter =>
    filter.value !== undefined && filter.value !== null && filter.value !== ""
  );

  if (hasActiveFilters) {
    clearButton.classList.add('filters-active');
    clearButton.title = 'Clear All Filters (Ctrl+X) - Filters Active';
  } else {
    clearButton.classList.remove('filters-active');
    clearButton.title = 'Clear All Filters (Ctrl+X)';
  }
}

// Clear selection and close menus
function clearSelectionAndMenus() {
  if (table) {
    table.deselectRow();
  }

  const menu = document.getElementById('columnMenu');
  if (menu && menu.classList.contains('show')) {
    menu.classList.remove('show');
  }
}

// Dark mode toggle functionality
function toggleDarkMode() {
  const html = document.documentElement;
  const currentTheme = html.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

  html.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);

  console.log('Theme switched to:', newTheme);
}

// Load saved theme on page load
function loadSavedTheme() {
  const savedTheme = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const theme = savedTheme || (prefersDark ? 'dark' : 'light');

  document.documentElement.setAttribute('data-theme', theme);
  console.log('Theme loaded:', theme);
}

// Keyboard shortcuts handler
document.addEventListener('keydown', function(e) {
  // Check for Ctrl (Windows/Linux) or Cmd (Mac)
  const modifier = e.ctrlKey || e.metaKey;

  // Ctrl/Cmd + E: Export to Excel
  if (modifier && e.key === 'e') {
    e.preventDefault();
    exportToExcel();
    return;
  }

  // Ctrl/Cmd + P: Export to PDF
  if (modifier && e.key === 'p') {
    e.preventDefault();
    exportToPDF();
    return;
  }

  // Ctrl/Cmd + L: Lookup on SNPedia
  if (modifier && e.key === 'l') {
    e.preventDefault();
    lookupSNPedia();
    return;
  }

  // Ctrl/Cmd + F: Focus search
  if (modifier && e.key === 'f') {
    e.preventDefault();
    focusSearch();
    return;
  }

  // Ctrl/Cmd + K: Toggle column menu
  if (modifier && e.key === 'k') {
    e.preventDefault();
    toggleColumnMenu();
    return;
  }

  // Ctrl/Cmd + X: Clear all filters
  if (modifier && e.key === 'x') {
    e.preventDefault();
    clearAllFilters();
    return;
  }

  // Ctrl/Cmd + R: Reload data
  if (modifier && e.key === 'r') {
    e.preventDefault();
    reloadData();
    return;
  }

  // Ctrl/Cmd + /: Show keyboard shortcuts
  if (modifier && e.key === '/') {
    e.preventDefault();
    showKeyboardShortcuts();
    return;
  }

  // Ctrl/Cmd + D: Toggle dark mode
  if (modifier && e.key === 'd') {
    e.preventDefault();
    toggleDarkMode();
    return;
  }

  // Escape: Clear selection and close menus/modals
  if (e.key === 'Escape') {
    const modal = document.getElementById('shortcutsModal');
    if (modal && modal.classList.contains('show')) {
      hideKeyboardShortcuts();
    } else {
      clearSelectionAndMenus();
    }
    return;
  }
});

// Toggle column visibility menu
function toggleColumnMenu() {
  const menu = document.getElementById('columnMenu');
  menu.classList.toggle('show');
}

// Close menu when clicking outside
window.onclick = function(event) {
  if (!event.target.matches('.column-menu button')) {
    const menu = document.getElementById('columnMenu');
    if (menu.classList.contains('show')) {
      menu.classList.remove('show');
    }
  }
}

// Load column visibility from localStorage
function loadColumnVisibility() {
  const saved = localStorage.getItem('columnVisibility');
  if (saved) {
    return JSON.parse(saved);
  }
  // Default visibility
  return {
    'Name': true,
    'Description': true,
    'StabilizedOrientation': false,
    'Genotype': false,
    'Variations': true,
    'IsInteresting': false,
    'IsUncommon': false
  };
}

// Save column visibility to localStorage
function saveColumnVisibility(columnName, visible) {
  const visibility = loadColumnVisibility();
  visibility[columnName] = visible;
  localStorage.setItem('columnVisibility', JSON.stringify(visibility));
}

// Handle column visibility changes
document.addEventListener('DOMContentLoaded', function() {
  // Wait for table to be initialized
  setTimeout(function() {
    // Load saved visibility state
    const visibility = loadColumnVisibility();

    // Update checkboxes and table columns based on saved state
    const checkboxes = document.querySelectorAll('#columnMenu input[type="checkbox"]');
    checkboxes.forEach(function(checkbox) {
      const columnName = checkbox.getAttribute('data-column');
      const isVisible = visibility[columnName];

      // Update checkbox state
      checkbox.checked = isVisible;

      // Update table column visibility
      if (table) {
        if (isVisible) {
          table.showColumn(columnName);
        } else {
          table.hideColumn(columnName);
        }
      }
    });

    // Redraw table after all columns are set to fix layout
    if (table) {
      table.redraw(true);
      console.log('Table redrawn after restoring column visibility');
    }

    // Add change listeners
    checkboxes.forEach(function(checkbox) {
      const columnName = checkbox.getAttribute('data-column');

      // Add change listener
      checkbox.addEventListener('change', function() {
        if (table) {
          if (this.checked) {
            table.showColumn(columnName);
            saveColumnVisibility(columnName, true);
          } else {
            table.hideColumn(columnName);
            saveColumnVisibility(columnName, false);
          }
          // Redraw table to adjust column widths
          table.redraw(true);
        }
      });
    });
  }, 500);
});

// Create simple pie chart without Chart.js library
function addSimplePieChartToPDF(doc, uncommonData, interestingSNPs, uncommonSNPs, regularSNPs, totalSNPs) {
  try {
    console.log('Creating simple charts without Chart.js...');
    
    // Create canvas for manual drawing
    const canvas = document.createElement('canvas');
    canvas.width = 300;
    canvas.height = 200;
    canvas.style.position = 'absolute';
    canvas.style.left = '-9999px';
    document.body.appendChild(canvas);
    const ctx = canvas.getContext('2d');
    
    // Draw simple pie chart for all SNP categories
    drawSimplePieChart(ctx, canvas.width, canvas.height, [
      { label: 'Interesting', value: interestingSNPs, color: '#FF6384' },
      { label: 'Uncommon', value: uncommonSNPs, color: '#36A2EB' },
      { label: 'Regular', value: regularSNPs, color: '#FFCE56' }
    ]);
    
    // Add pie chart to PDF (centered)
    const pieImageData = canvas.toDataURL('image/png');
    doc.addImage(pieImageData, 'PNG', 70, 145, 60, 40);
    
    // Clean up
    canvas.remove();
    
    // Add table data (uncommon SNPs only)
    addTableToPDF(doc, uncommonData);
    
    // Save PDF
    doc.save('Uncommon_SNPs_Report.pdf');
    console.log('PDF saved successfully with simple pie chart');
    
  } catch (error) {
    console.error('Error creating simple charts:', error);
    // Fallback: save without charts
    addTableToPDF(doc, uncommonData);
    doc.save('Uncommon_SNPs_Report.pdf');
  }
}

// Draw simple pie chart manually
function drawSimplePieChart(ctx, width, height, data) {
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(width, height) / 3;
  
  const total = data.reduce((sum, item) => sum + item.value, 0);
  if (total === 0) return;
  
  let currentAngle = -Math.PI / 2; // Start at top
  
  // Draw pie slices
  data.forEach(item => {
    if (item.value > 0) {
      const sliceAngle = (item.value / total) * 2 * Math.PI;
      
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
      ctx.closePath();
      ctx.fillStyle = item.color;
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2;
      ctx.stroke();
      
      currentAngle += sliceAngle;
    }
  });
  
  // Add title
  ctx.fillStyle = '#000000';
  ctx.font = 'bold 16px Arial';
  ctx.textAlign = 'center';
  ctx.fillText('SNP Categories', centerX, 20);
  
  // Add legend
  let legendY = height - 60;
  ctx.font = '12px Arial';
  ctx.textAlign = 'left';
  data.forEach((item, index) => {
    if (item.value > 0) {
      ctx.fillStyle = item.color;
      ctx.fillRect(10, legendY + (index * 15), 10, 10);
      ctx.fillStyle = '#000000';
      ctx.fillText(`${item.label}: ${item.value}`, 25, legendY + (index * 15) + 8);
    }
  });
}

// Draw simple bar chart manually
function drawSimpleBarChart(ctx, width, height, data) {
  if (data.length === 0) return;
  
  const margin = 40;
  const chartWidth = width - (margin * 2);
  const chartHeight = height - (margin * 2);
  const barWidth = chartWidth / data.length * 0.8;
  const maxValue = Math.max(...data.map(([, count]) => count));
  
  // Draw title
  ctx.fillStyle = '#000000';
  ctx.font = 'bold 16px Arial';
  ctx.textAlign = 'center';
  ctx.fillText('Top Variations', width / 2, 20);
  
  // Draw bars
  data.forEach(([variation, count], index) => {
    const barHeight = (count / maxValue) * chartHeight * 0.8;
    const x = margin + (index * (chartWidth / data.length)) + (chartWidth / data.length - barWidth) / 2;
    const y = height - margin - barHeight;
    
    // Draw bar
    ctx.fillStyle = '#36A2EB';
    ctx.fillRect(x, y, barWidth, barHeight);
    
    // Draw value on top
    ctx.fillStyle = '#000000';
    ctx.font = '10px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(count.toString(), x + barWidth / 2, y - 5);
    
    // Draw label
    ctx.save();
    ctx.translate(x + barWidth / 2, height - 10);
    ctx.rotate(-Math.PI / 4);
    ctx.textAlign = 'right';
    const label = variation.length > 8 ? variation.substring(0, 8) + '...' : variation;
    ctx.fillText(label, 0, 0);
    ctx.restore();
  });
}