'use client';

import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import type { NutrientRadarData } from '@/lib/api';

interface NutrientRadarChartProps {
  data: NutrientRadarData[];
  description: string;
}

export default function NutrientRadarChart({ data, description }: NutrientRadarChartProps) {
  if (!data || data.length === 0) {
    return null;
  }

  // Custom tooltip to show more information
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="bg-white border border-slate-200 rounded-lg p-3 shadow-lg">
          <p className="text-sm font-semibold text-slate-900">{item.category}</p>
          <p className="text-xs text-slate-600 mt-1">
            Need Score: <span className="font-medium text-blue-600">{item.score}</span>/100
          </p>
          <p className="text-xs text-slate-500">
            Based on {item.findings_count} genetic {item.findings_count === 1 ? 'variant' : 'variants'}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6">
      <div className="mb-6">
        <h3 className="text-2xl font-bold text-slate-900 mb-2">Nutrient Need Analysis</h3>
        <p className="text-sm text-slate-600">{description}</p>
        <div className="mt-3 flex items-center gap-6 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span className="text-slate-600">0-30: Low Priority</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
            <span className="text-slate-600">31-60: Moderate</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <span className="text-slate-600">61-100: High Priority</span>
          </div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <RadarChart data={data}>
          <PolarGrid stroke="#e2e8f0" />
          <PolarAngleAxis
            dataKey="category"
            tick={{ fill: '#475569', fontSize: 12 }}
            stroke="#94a3b8"
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fill: '#64748b', fontSize: 10 }}
            stroke="#cbd5e1"
          />
          <Radar
            name="Nutrient Need"
            dataKey="score"
            stroke="#2563eb"
            fill="#2563eb"
            fillOpacity={0.3}
            strokeWidth={2}
          />
          <Tooltip content={<CustomTooltip />} />
        </RadarChart>
      </ResponsiveContainer>

      <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-xs text-blue-900">
          <strong>How to read this chart:</strong> Higher scores indicate nutrients that require more attention based on your genetic profile.
          Focus on categories with scores above 60 for targeted dietary changes or supplementation.
        </p>
      </div>
    </div>
  );
}
