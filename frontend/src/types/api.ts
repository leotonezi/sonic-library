export interface ApiResponse<T> {
  data: T;
  message: string;
  status: string;
}

export interface ApiError {
  message: string;
  status: number;
  details?: string;
}

export interface PaginationMetadata {
  current_page: number;
  total_pages: number;
  total_count: number;
  page_size: number;
  has_next: boolean;
  has_previous: boolean;
  start_index: number;
  end_index: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: PaginationMetadata;
  message: string;
  status: string;
}