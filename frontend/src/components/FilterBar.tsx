import React from 'react';
import { Filter, RefreshCw } from 'lucide-react';

interface FilterBarProps {
  selectedRegion: string;
  onSelectRegion: (region: string) => void;
  onRefresh: () => void;
  isLoading: boolean;
}

const REGIONS = ['All', 'North America', 'Europe', 'Asia-Pacific', 'Latin America'];

export const FilterBar: React.FC<FilterBarProps> = ({
  selectedRegion,
  onSelectRegion,
  onRefresh,
  isLoading,
}) => {
  return (
    <div className="bg-white rounded-xl border border-slate-200/80 p-4 shadow-sm flex flex-wrap items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-slate-500">
          <Filter className="w-3.5 h-3.5" />
          <span>Region Filter:</span>
        </div>

        <div className="flex flex-wrap gap-1.5">
          {REGIONS.map((r) => {
            const isSelected = selectedRegion === r;
            return (
              <button
                key={r}
                onClick={() => onSelectRegion(r)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  isSelected
                    ? 'bg-brand-600 text-white shadow-sm'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200/70'
                }`}
              >
                {r}
              </button>
            );
          })}
        </div>
      </div>

      <button
        onClick={onRefresh}
        disabled={isLoading}
        className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg transition-colors"
      >
        <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
        <span>Refresh Data</span>
      </button>
    </div>
  );
};
