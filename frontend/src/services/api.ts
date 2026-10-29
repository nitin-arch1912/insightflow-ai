export interface AnalyticsOverview {
  gross_revenue: string;
  discount_amount: string;
  net_revenue: string;
  total_orders: number;
  completed_orders: number;
  average_order_value: string;
  refund_rate_percentage: number;
  active_customers: number;
}

export interface CategoryBreakdownItem {
  category: string;
  revenue: string;
  units_sold: number;
  order_count: number;
  percentage_of_total: number;
}

export interface CategoryBreakdownResponse {
  items: CategoryBreakdownItem[];
  total_category_revenue: string;
}

export interface RegionBreakdownItem {
  region: string;
  revenue: string;
  order_count: number;
  customer_count: number;
}

export interface RegionBreakdownResponse {
  items: RegionBreakdownItem[];
  total_regional_revenue: string;
}

export interface TrendItem {
  date: string;
  gross_revenue: string;
  net_revenue: string;
  order_count: number;
}

export interface TrendResponse {
  interval: string;
  items: TrendItem[];
}

export interface ApiError {
  code: string;
  message: string;
  details?: any;
  request_id?: string;
}

const API_BASE = '/api/v1';

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    try {
      const errorJson = await response.json();
      if (errorJson.error) {
        throw errorJson.error as ApiError;
      }
    } catch (e: any) {
      if (e.code) throw e;
    }
    throw {
      code: 'HTTP_ERROR',
      message: `Request failed with status ${response.status}`,
    } as ApiError;
  }
  return response.json();
}

export async function fetchOverview(params?: {
  region?: string;
  startDate?: string;
  endDate?: string;
}): Promise<AnalyticsOverview> {
  const query = new URLSearchParams();
  if (params?.region && params.region !== 'All') query.append('region', params.region);
  if (params?.startDate) query.append('start_date', params.startDate);
  if (params?.endDate) query.append('end_date', params.endDate);

  const url = `${API_BASE}/analytics/overview${query.toString() ? `?${query.toString()}` : ''}`;
  const res = await fetch(url);
  return handleResponse<AnalyticsOverview>(res);
}

export async function fetchCategoryBreakdown(params?: {
  startDate?: string;
  endDate?: string;
}): Promise<CategoryBreakdownResponse> {
  const query = new URLSearchParams();
  if (params?.startDate) query.append('start_date', params.startDate);
  if (params?.endDate) query.append('end_date', params.endDate);

  const url = `${API_BASE}/analytics/by-category${query.toString() ? `?${query.toString()}` : ''}`;
  const res = await fetch(url);
  return handleResponse<CategoryBreakdownResponse>(res);
}

export async function fetchRegionBreakdown(params?: {
  startDate?: string;
  endDate?: string;
}): Promise<RegionBreakdownResponse> {
  const query = new URLSearchParams();
  if (params?.startDate) query.append('start_date', params.startDate);
  if (params?.endDate) query.append('end_date', params.endDate);

  const url = `${API_BASE}/analytics/by-region${query.toString() ? `?${query.toString()}` : ''}`;
  const res = await fetch(url);
  return handleResponse<RegionBreakdownResponse>(res);
}

export async function fetchTrends(params?: {
  interval?: 'daily' | 'weekly';
  startDate?: string;
  endDate?: string;
}): Promise<TrendResponse> {
  const query = new URLSearchParams();
  if (params?.interval) query.append('interval', params.interval);
  if (params?.startDate) query.append('start_date', params.startDate);
  if (params?.endDate) query.append('end_date', params.endDate);

  const url = `${API_BASE}/analytics/trends${query.toString() ? `?${query.toString()}` : ''}`;
  const res = await fetch(url);
  return handleResponse<TrendResponse>(res);
}
