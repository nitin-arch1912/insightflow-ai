import React, { useEffect, useState } from 'react';
import {
  DollarSign,
  ShoppingBag,
  TrendingUp,
  AlertCircle,
  Activity,
  Layers,
} from 'lucide-react';
import {
  fetchOverview,
  fetchCategoryBreakdown,
  fetchRegionBreakdown,
  fetchTrends,
  AnalyticsOverview,
  CategoryBreakdownItem,
  RegionBreakdownItem,
  TrendItem,
  ApiError,
} from './services/api';
import { MetricCard } from './components/MetricCard';
import { RevenueTrendChart } from './components/RevenueTrendChart';
import { CategoryBarChart } from './components/CategoryBarChart';
import { RegionBreakdownList } from './components/RegionBreakdownList';
import { FilterBar } from './components/FilterBar';

export const App: React.FC = () => {
  const [selectedRegion, setSelectedRegion] = useState('All');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);

  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [categories, setCategories] = useState<CategoryBreakdownItem[]>([]);
  const [regions, setRegions] = useState<RegionBreakdownItem[]>([]);
  const [trends, setTrends] = useState<TrendItem[]>([]);

  const loadData = async (region: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const [overviewData, categoryData, regionData, trendData] = await Promise.all([
        fetchOverview({ region }),
        fetchCategoryBreakdown(),
        fetchRegionBreakdown(),
        fetchTrends({ interval: 'daily' }),
      ]);

      setOverview(overviewData);
      setCategories(categoryData.items);
      setRegions(regionData.items);
      setTrends(trendData.items);
    } catch (err: any) {
      setError(err as ApiError);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData(selectedRegion);
  }, [selectedRegion]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 pb-12">
      {/* Top Navbar */}
      <header className="bg-white border-b border-slate-200/80 sticky top-0 z-30 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-brand-600 flex items-center justify-center text-white shadow-sm shadow-brand-500/20">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-bold text-lg text-slate-900 leading-none">InsightFlow AI</h1>
                <span className="text-[10px] uppercase font-bold tracking-wider bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded border border-slate-200">
                  v0.1.0
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">Enterprise Intelligence Platform</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              API Connected
            </span>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 space-y-6">
        {/* Error Alert */}
        {error && (
          <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 flex items-start gap-3 text-rose-800">
            <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
            <div className="text-sm">
              <p className="font-semibold">{error.message || 'Failed to load analytics'}</p>
              {error.request_id && (
                <p className="text-xs text-rose-600 font-mono mt-1">Trace ID: {error.request_id}</p>
              )}
            </div>
          </div>
        )}

        {/* Filters */}
        <FilterBar
          selectedRegion={selectedRegion}
          onSelectRegion={setSelectedRegion}
          onRefresh={() => loadData(selectedRegion)}
          isLoading={isLoading}
        />

        {/* KPI Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="Net Revenue"
            value={overview ? `$${parseFloat(overview.net_revenue).toLocaleString(undefined, { minimumFractionDigits: 2 })}` : '—'}
            subtitle={overview ? `Gross: $${parseFloat(overview.gross_revenue).toLocaleString()} (Discounts: -$${parseFloat(overview.discount_amount).toLocaleString()})` : undefined}
            icon={<DollarSign className="w-4 h-4" />}
            badge="Healthy"
            badgeColor="green"
          />
          <MetricCard
            title="Total Orders"
            value={overview ? overview.total_orders.toLocaleString() : '—'}
            subtitle={overview ? `${overview.completed_orders} completed (${overview.total_orders - overview.completed_orders} pending/cancelled)` : undefined}
            icon={<ShoppingBag className="w-4 h-4" />}
            badge={`${overview ? overview.active_customers : 0} Buyers`}
            badgeColor="blue"
          />
          <MetricCard
            title="Average Order Value"
            value={overview ? `$${parseFloat(overview.average_order_value).toLocaleString(undefined, { minimumFractionDigits: 2 })}` : '—'}
            subtitle="Net revenue per completed order"
            icon={<TrendingUp className="w-4 h-4" />}
          />
          <MetricCard
            title="Refund Rate"
            value={overview ? `${overview.refund_rate_percentage}%` : '—'}
            subtitle="Calculated over total order placements"
            icon={<Layers className="w-4 h-4" />}
            badge={overview && overview.refund_rate_percentage < 5 ? 'Low' : 'Caution'}
            badgeColor={overview && overview.refund_rate_percentage < 5 ? 'green' : 'yellow'}
          />
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <RevenueTrendChart data={trends} />
          </div>
          <div>
            <RegionBreakdownList
              data={regions}
              totalRevenue={overview?.net_revenue || '0.00'}
            />
          </div>
        </div>

        {/* Category Breakdown Bar Chart */}
        <div>
          <CategoryBarChart data={categories} />
        </div>
      </main>
    </div>
  );
};
