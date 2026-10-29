import React from 'react';
import { RegionBreakdownItem } from '../services/api';
import { Globe, Users, ShoppingBag } from 'lucide-react';

interface RegionBreakdownListProps {
  data: RegionBreakdownItem[];
  totalRevenue: string;
}

export const RegionBreakdownList: React.FC<RegionBreakdownListProps> = ({
  data,
  totalRevenue,
}) => {
  const totalNum = parseFloat(totalRevenue) || 1;

  return (
    <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-slate-900">Regional Performance</h3>
          <p className="text-xs text-slate-500">Distribution across active global territories</p>
        </div>
        <Globe className="w-4 h-4 text-slate-400" />
      </div>

      <div className="space-y-4">
        {data.map((item) => {
          const revNum = parseFloat(item.revenue);
          const pct = Math.min(100, Math.round((revNum / totalNum) * 100));

          return (
            <div key={item.region} className="p-3 rounded-lg border border-slate-100 bg-slate-50/50">
              <div className="flex justify-between items-center mb-1.5">
                <span className="font-medium text-sm text-slate-800">{item.region}</span>
                <span className="font-semibold text-sm text-slate-900">
                  ${revNum.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </span>
              </div>

              {/* Progress bar */}
              <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden mb-2">
                <div
                  className="bg-brand-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${pct}%` }}
                />
              </div>

              <div className="flex justify-between text-xs text-slate-500">
                <span className="flex items-center gap-1">
                  <ShoppingBag className="w-3.5 h-3.5 text-slate-400" />
                  {item.order_count} orders
                </span>
                <span className="flex items-center gap-1">
                  <Users className="w-3.5 h-3.5 text-slate-400" />
                  {item.customer_count} customers
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
