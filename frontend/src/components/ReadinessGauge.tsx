'use client';

import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

interface ReadinessGaugeProps {
  score: number;
}

export default function ReadinessGauge({ score }: ReadinessGaugeProps) {
  const getColor = (s: number) => {
    if (s >= 70) return '#22C55E';
    if (s >= 40) return '#F59E0B';
    return '#EF4444';
  };

  const getLabel = (s: number) => {
    if (s >= 70) return "Sufficient Capacity";
    if (s >= 40) return "Needs Attention";
    return "Critical Shortfall";
  };

  const data = {
    datasets: [
      {
        data: [score, 100 - score],
        backgroundColor: [getColor(score), '#1A2E4A'],
        borderWidth: 0,
        circumference: 180,
        rotation: 270,
        cutout: '80%',
      },
    ],
  };

  const options = {
    plugins: {
      tooltip: { enabled: false },
      legend: { display: false },
    },
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 1000,
      easing: 'easeOutQuart' as const
    }
  };

  return (
    <div className="relative h-40 w-full flex flex-col items-center justify-center">
      <div className="h-full w-full">
        <Doughnut data={data} options={options} />
      </div>
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 translate-y-2 flex flex-col items-center">
        <span className="text-4xl font-mono font-bold leading-none">{score}</span>
        <span className="text-[9px] text-[var(--text-muted)] uppercase tracking-widest font-bold mt-1">
          {getLabel(score)}
        </span>
      </div>
    </div>
  );
}
