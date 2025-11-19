// src/utils/exportExcel.js
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'

export function exportToExcel(data, fileName = 'report.xlsx') {
  // Convert JSON data to worksheet
  const ws = XLSX.utils.json_to_sheet(data)
  // Create a new workbook and append the worksheet
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Sheet1')
  // Write workbook to array buffer
  const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
  // Trigger file download
  saveAs(new Blob([wbout], { type: 'application/octet-stream' }), fileName)
}
