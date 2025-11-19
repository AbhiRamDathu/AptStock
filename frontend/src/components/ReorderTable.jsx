import { exportToExcel } from '../utils/exportExcel'

export default function ReorderTable({ sku, store, data }) {
  const calculateReorderQuantity = (predicted, safetyStock = 10) =>
    Math.max(0, Math.round(predicted + safetyStock))

  const handleExport = () => {
    const rows = data.map(d => ({
      Date: d.date,
      Predicted: Math.round(d.predicted_units),
      LowerCI: Math.round(d.lower_ci || 0),
      UpperCI: Math.round(d.upper_ci || 0),
      Reorder: calculateReorderQuantity(d.predicted_units)
    }))
    exportToExcel(rows, `reorder-${sku}-${store}.xlsx`)
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md mb-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Reorder Recommendations</h3>
        <button
          onClick={handleExport}
          className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
        >
          Export Excel
        </button>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Predicted
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Reorder
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.map((d, i) => (
              <tr key={i}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {d.date}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {Math.round(d.predicted_units)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {calculateReorderQuantity(d.predicted_units)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
