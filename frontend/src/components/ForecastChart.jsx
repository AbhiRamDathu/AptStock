import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

const ForecastChart = ({ forecastData, confidenceIntervals = [] }) => {
  if (!forecastData || forecastData.length === 0) {
    return <p className="text-center py-4 text-gray-500">No forecast data to display</p>;
  }

  const datasets = [];
  forecastData.forEach((item, idx) => {
    const color = `hsl(${(idx * 60) % 360}, 75%, 50%)`;

    datasets.push({
      label: `SKU: ${item.sku}`,
      data: item.forecast.map(f => ({ x: f.date, y: f.predicted_units })),
      borderColor: color,
      backgroundColor: color,
      fill: false,
      tension: 0.3,
      borderWidth: 3,
      pointRadius: 4
    });

    if (confidenceIntervals.length > 0) {
      const ci = confidenceIntervals.find(ci => ci.sku === item.sku);
      if (ci) {
        datasets.push({
          label: `${item.sku} CI Upper`,
          data: ci.confidence.map(c => ({ x: c.date, y: c.upper })),
          borderColor: 'transparent',
          backgroundColor: `${color}33`,
          fill: '+1',
          pointRadius: 0,
          borderWidth: 0
        });
        datasets.push({
          label: `${item.sku} CI Lower`,
          data: ci.confidence.map(c => ({ x: c.date, y: c.lower })),
          borderColor: 'transparent',
          backgroundColor: `${color}33`,
          fill: '-1',
          pointRadius: 0,
          borderWidth: 0
        });
      }
    }
  });

  const allDates = Array.from(new Set(forecastData.flatMap(i => i.forecast.map(f => f.date)))).sort();

  const data = {
    labels: allDates,
    datasets
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {position: 'top'},
      title: {display: true, text: 'Sales Forecast'},
      tooltip: {mode: 'index', intersect: false}
    },
    scales: {
      x: {
        type: 'category',
        title: { display: true, text: 'Date'}
      },
      y: {
        beginAtZero: true,
        title: { display: true, text: 'Predicted Units Sold'}
      }
    }
  };

  return <div style={{height: '400px'}}><Line data={data} options={options} /></div>;
};

export default ForecastChart;
