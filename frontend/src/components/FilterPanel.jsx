import React from 'react';

const FilterPanel = ({
  skus,
  selectedSKUs,
  setSelectedSKUs,
  store,
  setStore,
  fromDate,
  toDate,
  setFromDate,
  setToDate,
  chartType,
  setChartType,
  showConfidenceBands,
  setShowConfidenceBands,
  onRefresh,
}) => {
  const toggleSKU = (sku) => {
    if (selectedSKUs.includes(sku)) {
      setSelectedSKUs(selectedSKUs.filter((s) => s !== sku));
    } else {
      setSelectedSKUs([...selectedSKUs, sku]);
    }
  };

  const toggleAllSKUs = () => {
    if (selectedSKUs.length === skus.length) {
      setSelectedSKUs([]);
    } else {
      setSelectedSKUs(skus);
    }
  };

  return (
    <div className="bg-gray-50 rounded-lg p-4 mb-6 shadow-sm">
      <h3 className="text-lg font-semibold mb-2">Filters</h3>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="col-span-1">
          <label className="block font-medium">Store</label>
          <select
            value={store}
            onChange={(e) => setStore(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300"
          >
            <option>StoreA</option>
            <option>StoreB</option>
          </select>
        </div>

        <div className="col-span-1">
          <label className="block font-medium">From Date</label>
          <input
            type="date"
            value={fromDate}
            onChange={(e) => setFromDate(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300"
          />
        </div>

        <div className="col-span-1">
          <label className="block font-medium">To Date</label>
          <input
            type="date"
            value={toDate}
            onChange={(e) => setToDate(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300"
          />
        </div>

        <div className="col-span-1 space-y-2">
          <div>
            <button
              className="text-sm text-blue-600 underline"
              onClick={toggleAllSKUs}
            >
              {selectedSKUs.length === skus.length
                ? "Deselect All SKUs"
                : "Select All SKUs"}
            </button>
          </div>
          <div className="overflow-auto max-h-40 border rounded p-3">
            {skus.map((sku) => (
              <div key={sku} className="flex items-center">
                <input
                  type="checkbox"
                  checked={selectedSKUs.includes(sku)}
                  onChange={() => toggleSKU(sku)}
                  className="mr-2"
                />
                <label>{sku}</label>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
        <div>
          <label className="block font-medium">Chart Type</label>
          <select
            value={chartType}
            onChange={(e) => setChartType(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300"
          >
            <option value="historical">Historical Only</option>
            <option value="forecast">Forecast Only</option>
            <option value="combined">Combined</option>
          </select>
        </div>

        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={showConfidenceBands}
            onChange={(e) => setShowConfidenceBands(e.target.checked)}
            id="confidence"
            className="rounded"
          />
          <label htmlFor="confidence" className="font-medium">
            Show Confidence Intervals
          </label>
        </div>

        <div>
          <button
            onClick={onRefresh}
            className="px-6 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors"
          >
            Refresh Data
          </button>
        </div>
      </div>
    </div>
  );
};

export default FilterPanel;
