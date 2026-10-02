'use client';

import React from 'react';

export default function ChartRenderer({ spec, rawResults }: { spec: any, rawResults: any[] }) {
  if (!spec || !rawResults || rawResults.length === 0) return null;

  // Find the data array that matches the chart specification
  let chartData: any[] = [];
  for (const res of rawResults) {
    const data = res.results;
    if (Array.isArray(data) && data.length > 0) {
      const firstRow = data[0];
      if (spec.x_axis && spec.y_axis && firstRow.hasOwnProperty(spec.x_axis) && firstRow.hasOwnProperty(spec.y_axis)) {
        chartData = data;
        break;
      }
    }
  }

  if (chartData.length === 0) {
    return (
      <div className="text-gray-500 text-sm text-center p-4 border border-dashed rounded bg-gray-50">
        Could not find matching data for the chart specification.
      </div>
    );
  }

  const { x_axis, y_axis, chart_type } = spec;

  // Dimensions
  const width = 800;
  const height = 400;
  const padding = 60;
  const bottomPadding = 120; // Extra room for angled text

  const graphWidth = width - padding * 2;
  const graphHeight = height - padding - bottomPadding;

  // Find min and max for Y axis
  const yValues = chartData.map(d => Number(d[y_axis]) || 0);
  const maxY = Math.max(...yValues, 0);
  const minY = Math.min(...yValues, 0);
  const rangeY = maxY - minY || 1; // avoid division by zero

  // Scaling functions
  const scaleY = (val: number) => padding + graphHeight - ((val - minY) / rangeY) * graphHeight;
  const scaleX = (index: number) => padding + (index * (graphWidth / (chartData.length || 1))) + (graphWidth / (chartData.length || 1)) / 2;
  const barWidth = Math.max(10, (graphWidth / (chartData.length || 1)) * 0.8);

  const renderYAxis = () => {
    const ticks = 5;
    return Array.from({ length: ticks + 1 }).map((_, i) => {
      const val = minY + (rangeY * i) / ticks;
      const y = scaleY(val);
      return (
        <g key={i}>
          <line x1={padding} y1={y} x2={width - padding} y2={y} stroke="#e5e7eb" strokeDasharray="4 4" />
          <text x={padding - 10} y={y + 4} fontSize="12" fill="#6b7280" textAnchor="end">
            {val.toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </text>
        </g>
      );
    });
  };

  const renderXAxis = () => {
    return chartData.map((d, i) => {
      const x = scaleX(i);
      const label = String(d[x_axis]);
      return (
        <g key={i}>
          <text 
            x={x} 
            y={height - bottomPadding + 20} 
            fontSize="12" 
            fill="#6b7280" 
            textAnchor="end"
            transform={`rotate(-45 ${x} ${height - bottomPadding + 20})`}
          >
            {label.length > 20 ? label.substring(0, 20) + '...' : label}
          </text>
        </g>
      );
    });
  };

  const renderBarChart = () => {
    return chartData.map((d, i) => {
      const x = scaleX(i) - barWidth / 2;
      const y = scaleY(Math.max(0, Number(d[y_axis])));
      const h = Math.abs(scaleY(0) - scaleY(Number(d[y_axis])));
      return (
        <g key={i} className="group">
          <rect 
            x={x} 
            y={y} 
            width={barWidth} 
            height={h} 
            fill="#3b82f6" 
            rx="4" 
            ry="4"
            className="hover:fill-blue-600 transition-colors cursor-pointer"
          />
          {/* Simple Tooltip on Hover */}
          <title>{`${d[x_axis]}: ${d[y_axis]}`}</title>
        </g>
      );
    });
  };

  const renderLineChart = () => {
    const points = chartData.map((d, i) => `${scaleX(i)},${scaleY(Number(d[y_axis]))}`).join(' ');
    return (
      <g>
        <polyline 
          points={points} 
          fill="none" 
          stroke="#3b82f6" 
          strokeWidth="3" 
          strokeLinejoin="round" 
        />
        {chartData.map((d, i) => (
          <circle 
            key={i} 
            cx={scaleX(i)} 
            cy={scaleY(Number(d[y_axis]))} 
            r="5" 
            fill="#ffffff" 
            stroke="#3b82f6" 
            strokeWidth="2"
          >
            <title>{`${d[x_axis]}: ${d[y_axis]}`}</title>
          </circle>
        ))}
      </g>
    );
  };

  return (
    <div className="w-full flex flex-col items-center bg-white p-4 rounded-xl border border-gray-100 shadow-sm mt-4">
      <h4 className="text-center font-bold text-gray-800 mb-6">{spec.title}</h4>
      <div className="w-full overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto min-w-[600px]">
          {/* Axes */}
          <line x1={padding} y1={padding} x2={padding} y2={height - bottomPadding} stroke="#9ca3af" strokeWidth="2" />
          <line x1={padding} y1={height - bottomPadding} x2={width - padding} y2={height - bottomPadding} stroke="#9ca3af" strokeWidth="2" />
          
          {renderYAxis()}
          {renderXAxis()}
          
          {/* Data */}
          {chart_type === 'bar' ? renderBarChart() : renderLineChart()}
        </svg>
      </div>
    </div>
  );
}
