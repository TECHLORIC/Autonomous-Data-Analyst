'use client';

import React, { useState } from 'react';
import { VisualizationSpec } from '@/lib/api';

const PALETTE = [
  '#2563eb', // Royal Blue
  '#059669', // Emerald
  '#d97706', // Amber
  '#7c3aed', // Violet
  '#db2777', // Pink
  '#0891b2', // Cyan
  '#475569', // Slate
  '#ea580c', // Orange
];

export default function ChartRenderer({ spec }: { spec: VisualizationSpec }) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  if (!spec || !spec.data || spec.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 bg-slate-50 border border-dashed border-slate-200 rounded-2xl text-slate-400 text-sm">
        <svg className="w-8 h-8 mb-2 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        No chart points available for this visualization.
      </div>
    );
  }

  const chartData = spec.data;
  const { 
    x_axis_key = 'category_or_date', 
    y_axis_key = 'value', 
    chart_type = 'bar', 
    title = 'Analysis Chart', 
    takeaway 
  } = spec;

  // 1. Dynamic Key Resolution Helpers
  const getYValue = (d: Record<string, unknown>): number => {
    if (!d || typeof d !== 'object') return 0;

    // Direct key match
    if (d[y_axis_key] !== undefined && d[y_axis_key] !== null) {
      const v = typeof d[y_axis_key] === 'number' 
        ? d[y_axis_key] 
        : Number(String(d[y_axis_key]).replace(/[^0-9.-]+/g, ''));
      if (Number.isFinite(v)) return v;
    }

    // Common metric key fallbacks
    const fallbacks = ['value', 'val', 'sales', 'total_sales', 'total', 'count', 'amount', 'revenue', 'y'];
    for (const fb of fallbacks) {
      if (d[fb] !== undefined && d[fb] !== null) {
        const v = typeof d[fb] === 'number' 
          ? d[fb] 
          : Number(String(d[fb]).replace(/[^0-9.-]+/g, ''));
        if (Number.isFinite(v)) return v;
      }
    }

    // Fallback: any numeric property in row
    for (const [k, v] of Object.entries(d)) {
      if (k !== 'id' && k !== 'chart_id') {
        const parsed = typeof v === 'number' ? v : Number(String(v).replace(/[^0-9.-]+/g, ''));
        if (Number.isFinite(parsed)) return parsed;
      }
    }

    return 0;
  };

  const getXLabel = (d: Record<string, unknown>): string => {
    if (!d || typeof d !== 'object') return '';

    // Direct match
    if (d[x_axis_key] !== undefined && d[x_axis_key] !== null && String(d[x_axis_key]).trim() !== '') {
      return String(d[x_axis_key]);
    }

    // Common dimension/label key fallbacks
    const fallbacks = ['category_or_date', 'category', 'date', 'month', 'label', 'name', 'x', 'dimension', 'productline', 'country'];
    for (const fb of fallbacks) {
      if (d[fb] !== undefined && d[fb] !== null && String(d[fb]).trim() !== '') {
        return String(d[fb]);
      }
    }

    // Fallback: first non-numeric string property
    for (const v of Object.values(d)) {
      if (typeof v === 'string' && isNaN(Number(v)) && v.trim() !== '') {
        return v;
      }
    }

    return '';
  };

  const width = 760;
  const height = 360;
  const paddingLeft = 70;
  const paddingRight = 35;
  const paddingTop = 40;
  const paddingBottom = 75;

  const graphWidth = width - paddingLeft - paddingRight;
  const graphHeight = height - paddingTop - paddingBottom;

  const yValues = chartData.map((d) => getYValue(d as Record<string, unknown>));

  const rawMaxY = Math.max(...yValues, 0);
  const rawMinY = Math.min(...yValues, 0);
  const maxY = rawMaxY > 0 ? rawMaxY * 1.08 : 1;
  const minY = Math.min(rawMinY, 0);
  const rangeY = maxY - minY || 1;

  const scaleY = (val: number) => {
    return paddingTop + graphHeight - ((val - minY) / rangeY) * graphHeight;
  };

  const scaleX = (index: number) => {
    const step = graphWidth / Math.max(chartData.length, 1);
    return paddingLeft + index * step + step / 2;
  };

  const barWidth = Math.min(48, Math.max(14, (graphWidth / Math.max(chartData.length, 1)) * 0.65));

  const formatTick = (val: number) => {
    if (Math.abs(val) >= 1_000_000) return `${(val / 1_000_000).toFixed(1)}M`;
    if (Math.abs(val) >= 1_000) return `${(val / 1_000).toFixed(1)}k`;
    return val.toLocaleString(undefined, { maximumFractionDigits: 1 });
  };

  const formatValueLabel = (val: number) => {
    if (val >= 1_000_000) return `$${(val / 1_000_000).toFixed(2)}M`;
    if (val >= 1_000) return `$${val.toLocaleString()}`;
    return val.toLocaleString();
  };

  // Render Horizontal Gridlines & Y-Axis Labels
  const renderGrid = () => {
    const ticks = 4;
    return Array.from({ length: ticks + 1 }).map((_, i) => {
      const val = minY + (rangeY * i) / ticks;
      const y = scaleY(val);
      return (
        <g key={i}>
          <line
            x1={paddingLeft}
            y1={y}
            x2={width - paddingRight}
            y2={y}
            stroke="#f1f5f9"
            strokeDasharray="4 4"
            strokeWidth="1.5"
          />
          <text
            x={paddingLeft - 12}
            y={y + 4}
            fontSize="11"
            fill="#64748b"
            textAnchor="end"
            fontFamily="monospace"
            className="select-none"
          >
            {formatTick(val)}
          </text>
        </g>
      );
    });
  };

  // Render X-Axis Labels (adaptive step so labels never collide)
  const renderXAxis = () => {
    const stride = chartData.length > 14 ? Math.ceil(chartData.length / 10) : 1;

    return chartData.map((d, i) => {
      const x = scaleX(i);
      const rawLabel = getXLabel(d as Record<string, unknown>);
      const label = rawLabel.length > 14 ? `${rawLabel.substring(0, 13)}…` : rawLabel;
      const isHovered = hoveredIndex === i;

      // Stride skipping for dense datasets (e.g. 29 monthly points), but always show hovered or last
      if (stride > 1 && i % stride !== 0 && i !== chartData.length - 1 && !isHovered) {
        return null;
      }

      return (
        <g key={i}>
          <text
            x={x}
            y={height - paddingBottom + 24}
            fontSize="11"
            fill={isHovered ? '#1e293b' : '#64748b'}
            fontWeight={isHovered ? '700' : '500'}
            textAnchor="end"
            transform={`rotate(-35 ${x} ${height - paddingBottom + 24})`}
            className="select-none transition-colors"
          >
            {label}
          </text>
        </g>
      );
    });
  };

  // 1. BAR CHART
  const renderBarChart = () => {
    return chartData.map((d, i) => {
      const val = getYValue(d as Record<string, unknown>);
      const label = getXLabel(d as Record<string, unknown>);
      const x = scaleX(i) - barWidth / 2;
      const yZero = scaleY(0);
      const yVal = scaleY(val);
      const barTop = Math.min(yZero, yVal);
      const barH = Math.max(Math.abs(yZero - yVal), 2);
      const isHovered = hoveredIndex === i;

      return (
        <g 
          key={i} 
          onMouseEnter={() => setHoveredIndex(i)} 
          onMouseLeave={() => setHoveredIndex(null)}
          className="cursor-pointer"
        >
          <rect
            x={x}
            y={barTop}
            width={barWidth}
            height={barH}
            rx={barWidth > 18 ? 6 : 3}
            fill={isHovered ? '#1d4ed8' : '#3b82f6'}
            className="transition-all duration-150"
          />
          {isHovered && (
            <g>
              <rect
                x={x + barWidth / 2 - 48}
                y={barTop - 42}
                width={96}
                height={34}
                rx={6}
                fill="#0f172a"
                className="drop-shadow-lg"
              />
              <text
                x={x + barWidth / 2}
                y={barTop - 26}
                fontSize="10"
                fill="#94a3b8"
                textAnchor="middle"
                fontWeight="500"
              >
                {label}
              </text>
              <text
                x={x + barWidth / 2}
                y={barTop - 13}
                fontSize="11"
                fill="#ffffff"
                textAnchor="middle"
                fontWeight="700"
                fontFamily="monospace"
              >
                {formatValueLabel(val)}
              </text>
            </g>
          )}
        </g>
      );
    });
  };

  // 2. LINE CHART
  const renderLineChart = () => {
    const points = chartData.map((d, i) => `${scaleX(i)},${scaleY(getYValue(d as Record<string, unknown>))}`).join(' ');

    return (
      <g>
        <polyline
          points={points}
          fill="none"
          stroke="#2563eb"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {chartData.map((d, i) => {
          const val = getYValue(d as Record<string, unknown>);
          const label = getXLabel(d as Record<string, unknown>);
          const cx = scaleX(i);
          const cy = scaleY(val);
          const isHovered = hoveredIndex === i;

          return (
            <g
              key={i}
              onMouseEnter={() => setHoveredIndex(i)}
              onMouseLeave={() => setHoveredIndex(null)}
              className="cursor-pointer"
            >
              <circle
                cx={cx}
                cy={cy}
                r={isHovered ? 7 : 4}
                fill="#ffffff"
                stroke="#2563eb"
                strokeWidth={isHovered ? 3 : 2}
                className="transition-all duration-150"
              />
              {isHovered && (
                <g>
                  <rect
                    x={cx - 50}
                    y={cy - 44}
                    width={100}
                    height={36}
                    rx={6}
                    fill="#0f172a"
                    className="drop-shadow-lg"
                  />
                  <text
                    x={cx}
                    y={cy - 28}
                    fontSize="10"
                    fill="#94a3b8"
                    textAnchor="middle"
                    fontWeight="500"
                  >
                    {label}
                  </text>
                  <text
                    x={cx}
                    y={cy - 14}
                    fontSize="11"
                    fill="#ffffff"
                    textAnchor="middle"
                    fontWeight="700"
                    fontFamily="monospace"
                  >
                    {formatValueLabel(val)}
                  </text>
                </g>
              )}
            </g>
          );
        })}
      </g>
    );
  };

  // 3. AREA CHART
  const renderAreaChart = () => {
    const polyPoints = chartData.map((d, i) => `${scaleX(i)},${scaleY(getYValue(d as Record<string, unknown>))}`);
    const lineString = polyPoints.join(' ');
    
    // Close polygon at baseline
    const firstX = scaleX(0);
    const lastX = scaleX(chartData.length - 1);
    const baseY = scaleY(minY);
    const areaString = `${firstX},${baseY} ${lineString} ${lastX},${baseY}`;

    return (
      <g>
        <defs>
          <linearGradient id={`areaGrad-${spec.chart_id}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.38" />
            <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.02" />
          </linearGradient>
        </defs>
        <polygon points={areaString} fill={`url(#areaGrad-${spec.chart_id})`} />
        <polyline
          points={lineString}
          fill="none"
          stroke="#2563eb"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {chartData.map((d, i) => {
          const val = getYValue(d as Record<string, unknown>);
          const label = getXLabel(d as Record<string, unknown>);
          const cx = scaleX(i);
          const cy = scaleY(val);
          const isHovered = hoveredIndex === i;

          return (
            <g
              key={i}
              onMouseEnter={() => setHoveredIndex(i)}
              onMouseLeave={() => setHoveredIndex(null)}
              className="cursor-pointer"
            >
              <circle
                cx={cx}
                cy={cy}
                r={isHovered ? 6 : 3.5}
                fill="#ffffff"
                stroke="#2563eb"
                strokeWidth="2"
              />
              {isHovered && (
                <g>
                  <rect
                    x={cx - 50}
                    y={cy - 44}
                    width={100}
                    height={36}
                    rx={6}
                    fill="#0f172a"
                    className="drop-shadow-lg"
                  />
                  <text
                    x={cx}
                    y={cy - 28}
                    fontSize="10"
                    fill="#94a3b8"
                    textAnchor="middle"
                    fontWeight="500"
                  >
                    {label}
                  </text>
                  <text
                    x={cx}
                    y={cy - 14}
                    fontSize="11"
                    fill="#ffffff"
                    textAnchor="middle"
                    fontWeight="700"
                    fontFamily="monospace"
                  >
                    {formatValueLabel(val)}
                  </text>
                </g>
              )}
            </g>
          );
        })}
      </g>
    );
  };

  // 4. DONUT CHART
  const renderDonutChart = () => {
    const total = yValues.reduce((acc, curr) => acc + Math.max(curr, 0), 0) || 1;
    const centerX = 200;
    const centerY = height / 2;
    const radiusOuter = 105;
    const radiusInner = 68;

    let accumulatedAngle = -Math.PI / 2;

    const slices = chartData.map((d, i) => {
      const val = Math.max(getYValue(d as Record<string, unknown>), 0);
      const label = getXLabel(d as Record<string, unknown>);
      const sliceAngle = (val / total) * 2 * Math.PI;
      const startAngle = accumulatedAngle;
      const endAngle = accumulatedAngle + sliceAngle;
      accumulatedAngle += sliceAngle;

      const x1 = centerX + radiusOuter * Math.cos(startAngle);
      const y1 = centerY + radiusOuter * Math.sin(startAngle);
      const x2 = centerX + radiusOuter * Math.cos(endAngle);
      const y2 = centerY + radiusOuter * Math.sin(endAngle);

      const x3 = centerX + radiusInner * Math.cos(endAngle);
      const y3 = centerY + radiusInner * Math.sin(endAngle);
      const x4 = centerX + radiusInner * Math.cos(startAngle);
      const y4 = centerY + radiusInner * Math.sin(startAngle);

      const largeArcFlag = sliceAngle > Math.PI ? 1 : 0;
      const pathData = `M ${x1} ${y1} A ${radiusOuter} ${radiusOuter} 0 ${largeArcFlag} 1 ${x2} ${y2} L ${x3} ${y3} A ${radiusInner} ${radiusInner} 0 ${largeArcFlag} 0 ${x4} ${y4} Z`;

      return {
        pathData,
        color: PALETTE[i % PALETTE.length],
        label,
        val,
        percentage: ((val / total) * 100).toFixed(1),
      };
    });

    return (
      <g>
        {slices.map((slice, i) => {
          const isHovered = hoveredIndex === i;
          return (
            <path
              key={i}
              d={slice.pathData}
              fill={slice.color}
              stroke="#ffffff"
              strokeWidth={isHovered ? 4 : 2.5}
              opacity={isHovered ? 1 : hoveredIndex !== null ? 0.5 : 1}
              className="cursor-pointer transition-all duration-150"
              onMouseEnter={() => setHoveredIndex(i)}
              onMouseLeave={() => setHoveredIndex(null)}
            />
          );
        })}
        {/* Center label */}
        <text
          x={centerX}
          y={centerY - 6}
          fontSize="11"
          fontWeight="600"
          fill="#64748b"
          textAnchor="middle"
          className="uppercase tracking-wider select-none"
        >
          Total
        </text>
        <text
          x={centerX}
          y={centerY + 16}
          fontSize="17"
          fontWeight="700"
          fill="#0f172a"
          textAnchor="middle"
          fontFamily="monospace"
        >
          {formatTick(total)}
        </text>

        {/* Legend */}
        <g transform={`translate(${centerX + radiusOuter + 50}, 50)`}>
          {slices.map((slice, i) => {
            const isHovered = hoveredIndex === i;
            return (
              <g
                key={i}
                transform={`translate(0, ${i * 26})`}
                className="cursor-pointer select-none"
                onMouseEnter={() => setHoveredIndex(i)}
                onMouseLeave={() => setHoveredIndex(null)}
              >
                <circle cx="6" cy="6" r="5" fill={slice.color} />
                <text
                  x="20"
                  y="10"
                  fontSize="12"
                  fill={isHovered ? '#0f172a' : '#475569'}
                  fontWeight={isHovered ? '700' : '400'}
                >
                  {slice.label.length > 18 ? `${slice.label.substring(0, 17)}…` : slice.label}
                </text>
                <text
                  x="240"
                  y="10"
                  fontSize="12"
                  fill="#64748b"
                  textAnchor="end"
                  fontFamily="monospace"
                >
                  {slice.percentage}%
                </text>
              </g>
            );
          })}
        </g>
      </g>
    );
  };

  const isDonut = chart_type.toLowerCase() === 'donut';

  return (
    <div className="flex flex-col bg-white border border-slate-200/90 rounded-2xl shadow-sm hover:shadow-md transition-shadow p-5 relative overflow-hidden">
      {/* Top Header Badge */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-2">
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-blue-600 animate-pulse" />
          <h4 className="font-semibold text-slate-900 text-base tracking-tight">{title}</h4>
        </div>
        <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 bg-slate-100 px-2.5 py-1 rounded-md">
          {chart_type}
        </span>
      </div>

      {/* SVG Canvas */}
      <div className="w-full overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto min-w-[540px]">
          {!isDonut && renderGrid()}
          {!isDonut && renderXAxis()}

          {chart_type === 'bar' && renderBarChart()}
          {chart_type === 'line' && renderLineChart()}
          {chart_type === 'area' && renderAreaChart()}
          {isDonut && renderDonutChart()}
        </svg>
      </div>

      {/* LLM Analytical Takeaway */}
      {takeaway && (
        <div className="mt-4 flex items-start gap-2.5 p-3.5 bg-gradient-to-r from-blue-50/70 to-indigo-50/40 border border-blue-100 rounded-xl text-blue-950 text-sm leading-relaxed">
          <span className="text-base leading-none select-none">💡</span>
          <div>
            <strong className="font-semibold text-blue-900">Key Takeaway: </strong>
            <span className="text-blue-950/90">{takeaway}</span>
          </div>
        </div>
      )}
    </div>
  );
}
