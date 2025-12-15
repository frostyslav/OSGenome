/**
 * Export Manager Module
 * Handles Excel and PDF export functionality
 */

export class ExportManager {
  constructor(table) {
    this.table = table;
  }

  exportToExcel() {
    if (this.table) {
      this.table.download("xlsx", "SNP Report.xlsx", {
        sheetName: "SNP Data"
      });
    }
  }

  exportToPDF() {
    console.log('PDF export started...');
    
    if (!this.table) {
      console.error('Table not available');
      alert('Table not available for export');
      return;
    }

    // Check for jsPDF library
    if (typeof window.jspdf === 'undefined' && typeof window.jsPDF === 'undefined') {
      console.error('jsPDF library not loaded');
      alert('PDF library not loaded. Please refresh the page and try again.');
      return;
    }

    try {
      // Get jsPDF constructor
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
      
      // Get table data
      const allData = this.table.getData();
      const uncommonData = allData.filter(row => row.IsUncommon === 'Yes');
      console.log('All data:', allData.length, 'rows');
      console.log('Uncommon RSIDs for export:', uncommonData.length, 'rows');
      
      this._createPDFContent(doc, allData, uncommonData);
      
    } catch (error) {
      console.error('Error creating PDF:', error);
      alert('Error creating PDF: ' + error.message);
    }
  }

  _createPDFContent(doc, allData, uncommonData) {
    // Title and header
    doc.setFontSize(20);
    doc.text('Uncommon SNPs Report', 20, 20);
    
    doc.setFontSize(12);
    doc.text(`Generated: ${new Date().toLocaleDateString()}`, 20, 35);
    
    // Calculate statistics
    const totalSNPs = allData.length;
    const interestingSNPs = allData.filter(row => row.IsInteresting === 'Yes').length;
    const uncommonSNPs = allData.filter(row => row.IsUncommon === 'Yes').length;
    const regularSNPs = totalSNPs - uncommonSNPs - interestingSNPs;
    
    // Add statistics
    doc.setFontSize(14);
    doc.text('Summary Statistics:', 20, 55);
    doc.setFontSize(12);
    doc.text(`Total SNPs: ${totalSNPs}`, 30, 70);
    doc.text(`Interesting SNPs: ${interestingSNPs}`, 30, 80);
    doc.text(`Uncommon SNPs: ${uncommonSNPs}`, 30, 90);
    doc.text(`Regular SNPs: ${regularSNPs}`, 30, 100);
    
    doc.setFontSize(10);
    doc.text(`Note: Table below shows only uncommon SNPs (${uncommonData.length} entries)`, 30, 115);
    
    // Add charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
      console.log('Chart.js available, adding charts...');
      this._addChartsToPDF(doc, uncommonData, interestingSNPs, uncommonSNPs, regularSNPs, totalSNPs);
    } else {
      console.warn('Chart.js not available, creating simple charts');
      this._addSimpleChartsToPDF(doc, uncommonData, interestingSNPs, uncommonSNPs, regularSNPs, totalSNPs);
    }
  }

  _addChartsToPDF(doc, uncommonData, interestingSNPs, uncommonSNPs, regularSNPs, totalSNPs) {
    try {
      // Create temporary canvas
      const canvas = document.createElement('canvas');
      canvas.width = 600;
      canvas.height = 400;
      canvas.style.position = 'absolute';
      canvas.style.left = '-9999px';
      canvas.style.top = '-9999px';
      document.body.appendChild(canvas);
      const ctx = canvas.getContext('2d');
      
      // Create pie chart
      const pieChart = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: ['Interesting', 'Uncommon', 'Regular'],
          datasets: [{
            data: [interestingSNPs, uncommonSNPs, regularSNPs],
            backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56'],
            borderWidth: 2,
            borderColor: '#ffffff'
          }]
        },
        options: {
          responsive: false,
          maintainAspectRatio: false,
          animation: { duration: 0 },
          plugins: {
            title: {
              display: true,
              text: 'SNP Categories Distribution',
              font: { size: 20, weight: 'bold' },
              padding: 20
            },
            legend: {
              position: 'bottom',
              labels: { font: { size: 14 }, padding: 15 }
            }
          }
        }
      });

      setTimeout(() => {
        try {
          pieChart.update('none');
          const pieImageData = canvas.toDataURL('image/png');
          
          if (pieImageData.length > 1000) {
            doc.addImage(pieImageData, 'PNG', 70, 145, 80, 60);
            console.log('Pie chart added to PDF successfully');
          }
          
          pieChart.destroy();
          canvas.remove();
          
          this._addTableToPDF(doc, uncommonData);
          doc.save('Uncommon_SNPs_Report.pdf');
          console.log('PDF saved successfully');
          
        } catch (error) {
          console.error('Error processing chart:', error);
          canvas.remove();
          this._addTableToPDF(doc, uncommonData);
          doc.save('Uncommon_SNPs_Report.pdf');
        }
      }, 2000);
      
    } catch (error) {
      console.error('Error creating charts:', error);
      this._addTableToPDF(doc, uncommonData);
      doc.save('Uncommon_SNPs_Report.pdf');
    }
  }

  _addSimpleChartsToPDF(doc, uncommonData, interestingSNPs, uncommonSNPs, regularSNPs, totalSNPs) {
    try {
      const canvas = document.createElement('canvas');
      canvas.width = 300;
      canvas.height = 200;
      canvas.style.position = 'absolute';
      canvas.style.left = '-9999px';
      document.body.appendChild(canvas);
      const ctx = canvas.getContext('2d');
      
      this._drawSimplePieChart(ctx, canvas.width, canvas.height, [
        { label: 'Interesting', value: interestingSNPs, color: '#FF6384' },
        { label: 'Uncommon', value: uncommonSNPs, color: '#36A2EB' },
        { label: 'Regular', value: regularSNPs, color: '#FFCE56' }
      ]);
      
      const pieImageData = canvas.toDataURL('image/png');
      doc.addImage(pieImageData, 'PNG', 70, 145, 60, 40);
      
      canvas.remove();
      this._addTableToPDF(doc, uncommonData);
      doc.save('Uncommon_SNPs_Report.pdf');
      console.log('PDF saved with simple chart');
      
    } catch (error) {
      console.error('Error creating simple charts:', error);
      this._addTableToPDF(doc, uncommonData);
      doc.save('Uncommon_SNPs_Report.pdf');
    }
  }

  _drawSimplePieChart(ctx, width, height, data) {
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 3;
    
    const total = data.reduce((sum, item) => sum + item.value, 0);
    if (total === 0) return;
    
    let currentAngle = -Math.PI / 2;
    
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
    
    // Add title and legend
    ctx.fillStyle = '#000000';
    ctx.font = 'bold 16px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('SNP Categories', centerX, 20);
    
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

  _addTableToPDF(doc, data) {
    doc.addPage();
    
    doc.setFontSize(16);
    doc.text('SNP Data Table', 20, 20);
    
    const headers = ['Name', 'Description', 'Variations', 'Interesting', 'Uncommon'];
    let yPos = 40;
    
    // Header row
    doc.setFontSize(10);
    doc.setFont(undefined, 'bold');
    headers.forEach((header, index) => {
      doc.text(header, 20 + (index * 35), yPos);
    });
    
    // Data rows
    doc.setFont(undefined, 'normal');
    yPos += 10;
    
    const maxRows = Math.min(30, data.length);
    for (let i = 0; i < maxRows; i++) {
      const row = data[i];
      yPos += 8;
      
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
    
    if (data.length > 30) {
      yPos += 15;
      doc.setFontSize(8);
      doc.text(`Note: Showing first 30 of ${data.length} total SNPs. Export to Excel for complete data.`, 20, yPos);
    }
  }
}