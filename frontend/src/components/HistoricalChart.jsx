import React, { useState } from 'react';
import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

const ExportMenu = ({ historicalData, forecastData }) => {
  const [open, setOpen] = useState(false);

  const flattenData = (data) => {
    const flat = [];
    data.forEach(item => {
      if (item.historical) {
        item.historical.forEach(h => {
          flat.push({sku: item.sku, store: item.store, date: h.date, type: 'historical', value: h.units_sold});
        });
      }
      if (item.forecast) {
        item.forecast.forEach(f => {
          flat.push({sku: item.sku, store: item.store, date: f.date, type: 'forecast', value: f.predicted_units});
        });
      }
    });
    return flat;
  };

  const exportCSV = () => {
    const flat = flattenData([...historicalData, ...forecastData]);
    const worksheet = XLSX.utils.json_to_sheet(flat);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Data');
    XLSX.writeFile(workbook, `forecast_data_${Date.now()}.csv`);
    setOpen(false);
  };

  const exportExcel = () => {
    const flat = flattenData([...historicalData, ...forecastData]);
    const worksheet = XLSX.utils.json_to_sheet(flat);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Data');
    XLSX.writeFile(workbook, `forecast_data_${Date.now()}.xlsx`);
    setOpen(false);
  };

  const exportPDF = () => {
    const chartDiv = document.querySelector('.space-y-8');
    if (!chartDiv) return;

    html2canvas(chartDiv).then(canvas => {
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF();
      const width = pdf.internal.pageSize.getWidth();
      const height = (canvas.height * width) / canvas.width;
      pdf.addImage(imgData, 'PNG', 0, 0, width, height);
      pdf.save(`forecast_charts_${Date.now()}.pdf`);
      setOpen(false);
    });
  };

  return (
    <div className="relative z-20">
      <button onClick={() => setOpen(!open)} className="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700">
        Export Data
      </button>
      {open && (
        <>
          <div onClick={() => setOpen(false)} className="fixed inset-0 bg-black opacity-30 z-10" />
          <div className="absolute right-0 mt-2 w-48 bg-white rounded border shadow-lg z-20">
            <button onClick={exportCSV} className="block w-full text-left px-4 py-2 hover:bg-gray-200">Export CSV</button>
            <button onClick={exportExcel} className="block w-full text-left px-4 py-2 hover:bg-gray-200">Export Excel</button>
            <button onClick={exportPDF} className="block w-full text-left px-4 py-2 hover:bg-gray-200">Export Charts PDF</button>
          </div>
        </>
      )}
    </div>
  );
};

export default ExportMenu;
