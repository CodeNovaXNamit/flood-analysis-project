
'use client';

import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { WardProperties } from '@/app/types/flood.types';
import { getRiskColor } from '@/app/utils/riskHelpers';

ChartJS.register(ArcElement, Tooltip, Legend, ChartDataLabels);

interface RiskPieChartProps {
  wards: WardProperties[];
}

export default function RiskPieChart({ wards }: RiskPieChartProps) {
  // To keep it elegant and readable, we focus on the top 12 most critical sensed locations
  const sortedWards = [...wards]
    .sort((a, b) => b.flood_risk - a.flood_risk)
    .slice(0, 12);

  const data = {
    labels: sortedWards.map(w => w.ward_name),
    datasets: [
      {
        data: sortedWards.map(w => w.flood_risk),
        backgroundColor: sortedWards.map(w => getRiskColor(w.flood_risk)),
        borderColor: 'rgba(6, 13, 26, 0.8)',
        borderWidth: 2,
        hoverOffset: 20,
      },
    ],
  };

  const options = {
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: '#0F1E35',
        titleFont: { family: 'Inter', size: 12, weight: 'bold' as const },
        bodyFont: { family: 'IBM Plex Mono', size: 12 },
        borderColor: '#3B82F6',
        borderWidth: 1,
        padding: 12,
        displayColors: true,
        cornerRadius: 8,
        callbacks: {
          label: (context: any) => {
            const val = context.raw;
            return ` Risk Index: ${(val * 100).toFixed(1)}%`;
          }
        }
      },
      datalabels: {
        color: '#000',
        font: {
          family: 'IBM Plex Mono',
          weight: 'bold' as const,
          size: 10,
        },
        formatter: (value: number) => {
          return `${(value * 100).toFixed(0)}%`;
        },
        display: (context: any) => {
          // Only show labels for segments large enough to hold them
          return context.dataset.data[context.dataIndex] > 0.15;
        },
      },
    },
    responsive: true,
    maintainAspectRatio: false,
    layout: {
      padding: 20
    },
    animation: {
      animateRotate: true,
      animateScale: true,
      duration: 1500,
      easing: 'easeOutQuart' as const
    }
  };

  return (
    <div className="h-72 w-full relative flex items-center justify-center">
      <Pie data={data} options={options} />
      <div className="absolute bottom-[-10px] left-0 right-0 text-center">
        <p className="text-[9px] text-[var(--text-muted)] font-mono uppercase tracking-widest">
          Sensed Critical Wards
        </p>
      </div>
    </div>
  );
}
