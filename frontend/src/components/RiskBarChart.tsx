'use client';

import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, registerables } from 'chart.js';
import { WardProperties } from '@/app/types/flood.types';
import { getRiskColor } from '@/app/utils/riskHelpers';

ChartJS.register(...registerables);

interface RiskBarChartProps {
  wards: WardProperties[];
}

export default function RiskBarChart({ wards }: RiskBarChartProps) {
  const sortedWards = [...wards].sort((a, b) => b.flood_risk - a.flood_risk).slice(0, 10);

  const data = {
    labels: sortedWards.map(w => w.ward_name),
    datasets: [
      {
        data: sortedWards.map(w => w.flood_risk),
        backgroundColor: sortedWards.map(w => getRiskColor(w.flood_risk)),
        borderRadius: 4,
        barThickness: 10,
      },
    ],
  };

  const options = {
    indexAxis: 'y' as const,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#0F1E35',
        titleFont: { family: 'Inter', size: 12 },
        bodyFont: { family: 'IBM Plex Mono', size: 12 },
        borderColor: '#1E3A5F',
        borderWidth: 1,
        padding: 10,
        displayColors: false,
      },
    },
    scales: {
      x: {
        min: 0,
        max: 1,
        grid: { color: '#1A2E4A' },
        ticks: { 
          color: '#6B8EB3', 
          font: { family: 'IBM Plex Mono', size: 10 },
          callback: (value: any) => (value * 100).toFixed(0) + '%'
        },
      },
      y: {
        grid: { display: false },
        ticks: { color: '#E8F0FE', font: { family: 'Inter', size: 11 } },
      },
    },
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 1500,
      easing: 'easeOutQuart' as const
    }
  };

  return (
    <div className="h-64 w-full">
      <Bar data={data} options={options} />
    </div>
  );
}
