export interface SearchRequest {
  location: string;
  check_in: string;
  check_out: string;
  guests: number;
  discount_types?: string[];
}

export interface Result {
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

export interface SearchResults {
  search_id: string;
  status: string;
  location: string;
  check_in: string;
  check_out: string;
  guests: number;
  result_count: number;
  results: Result[];
}
