import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { CategoryBreakdownItem } from '../services/api';

interface CategoryBarChartProps {
  data: CategoryBreakdownItem[];
}

const COLORS = ['#0284c7', '#0d9488', '#6366f1', '#f59e0b', '#ec4899'];

export const CategoryBarChart: React.FC<CategoryBarChartProps> = ({ data }) => {
  const chartData = data.map((item) => ({
    ...item,
    revenue_num: parseFloat(item.revenue),
  }));

  return (
    <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-slate-900">Revenue by Category</h3>
          <p className="text-xs text-slate-500">Total completed merchandise sales</p>
        </div>
      </div>

      <div className="h-72 w-full">
        {data.length === 0 ? (
          <div className="h-full flex items-center justify-center text-sm text-slate-400">
            No category data available
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{ top: 5, right: 20, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
              <XAxis
                type="number"
                stroke="#94a3b8"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                tickFormatter={(val) => `$${(val / 1000).toFixed(0)}k`}
              />
              <YAxis
                type="category"
                dataKey="category"
                stroke="#475569"
                fontSize={12}
                tickLine={false}
                axisLine={{ stroke: '#e2e8f0' }}
                width={100}
              />
              <Tooltip
                formatter={(val: any, _name: any, item: any) => [
                  `$${Number(val).toLocaleString()} (${item.payload.percentage_of_total}%)`,
                  'Revenue',
                ]}
                contentStyle={{
                  backgroundColor: '#0f172a',
                  border: 'none',
                  borderRadius: '8px',
                  color: '#fff',
                  fontSize: '12px',
                }}
              />
              <Bar dataKey="revenue_num" radius={[0, 4, 4, 0]}>
                {chartData.map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};
