import React from 'react';

const InventoryRecommendations = ({ forecastData, historicalData }) => {
  const recs = forecastData.map(item => {
    const avgForecast = item.forecast.reduce((acc, f) => acc + f.predicted_units, 0) / item.forecast.length;
    return {
      sku: item.sku,
      recommendedStock: Math.ceil(avgForecast * 1.2),
      safetyStock: Math.ceil(avgForecast * 0.15),
      reorderPoint: Math.ceil(avgForecast * 0.7)
    };
  });

  return (
    <div className="mt-8 bg-white p-6 rounded shadow">
      <h3 className="font-semibold text-xl mb-4">Inventory Recommendations</h3>
      <table className="w-full border-collapse border border-gray-300">
        <thead>
          <tr className="bg-gray-100">
            <th className="border border-gray-300 p-2">SKU</th>
            <th className="border border-gray-300 p-2">Recommended Stock</th>
            <th className="border border-gray-300 p-2">Safety Stock</th>
            <th className="border border-gray-300 p-2">Reorder Point</th>
          </tr>
        </thead>
        <tbody>
          {recs.map((rec, i) => (
            <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
              <td className="border border-gray-300 p-2">{rec.sku}</td>
              <td className="border border-gray-300 p-2">{rec.recommendedStock}</td>
              <td className="border border-gray-300 p-2">{rec.safetyStock}</td>
              <td className="border border-gray-300 p-2">{rec.reorderPoint}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default InventoryRecommendations;
