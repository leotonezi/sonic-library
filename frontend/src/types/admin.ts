export interface AdminUser {
  id: number;
  name: string;
  email: string;
  is_active: boolean;
  profile_picture: string | null;
  books_count: number;
  reviews_count: number;
}

export interface AdminUserDetail extends AdminUser {
  books: Record<string, unknown>[];
  reviews: Record<string, unknown>[];
}

export interface AdminReview {
  id: number;
  user_id: number;
  user_name: string;
  book_id: number | null;
  external_book_id: string | null;
  book_title: string | null;
  content: string;
  rate: number;
  created_at: string;
}

import { BookStatus } from './book';

export interface AdminUserBook {
  id: number;
  user_id: number;
  user_name: string;
  book_id: number | null;
  external_book_id: string | null;
  book_title: string | null;
  status: BookStatus;
  created_at: string;
}

export interface AdminStats {
  total_users: number;
  total_active_users: number;
  total_books: number;
  total_reviews: number;
  total_user_books: number;
  avg_rating: number;
}

export interface PaginationResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
