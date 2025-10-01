import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface SearchRequest {
  location: string;
  check_in: string;
  check_out: string;
  guests: number;
  discount_types?: string[];
}

export interface SearchResponse {
  search_id: string;
  status: string;
  message: string;
}

export interface ResultItem {
  result_id: string;
  hotel_name: string;
  hotel_chain: string;
  discount_type: string;
  original_price: number | null;
  discounted_price: number | null;
  taxes: number;
  fees: number;
  total_price: number | null;
  currency: string;
  available: boolean;
  scraped_at: string;
}

export interface ResultsResponse {
  search_id: string;
  status: string;
  location: string;
  check_in: string;
  check_out: string;
  guests: number;
  result_count: number;
  results: ResultItem[];
}

export const searchApi = {
  // Create a new search
  createSearch: async (data: SearchRequest): Promise<SearchResponse> => {
    const response = await api.post<SearchResponse>('/api/search', data);
    return response.data;
  },

  // Get results for a search
  getResults: async (searchId: string): Promise<ResultsResponse> => {
    const response = await api.get<ResultsResponse>(`/api/results/${searchId}`);
    return response.data;
  },

  // Get results summary
  getResultsSummary: async (searchId: string) => {
    const response = await api.get(`/api/results/${searchId}/summary`);
    return response.data;
  },

  // List recent searches
  listSearches: async (limit: number = 10) => {
    const response = await api.get(`/api/searches?limit=${limit}`);
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
