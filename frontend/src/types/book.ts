export interface Book {
  id: number | null;
  external_id: string | null;
  title: string;
  author: string;
  description?: string | null;
  page_count?: number | null;
  published_date?: string | null;
  publisher?: string | null;
  isbn?: string | null;
  image_url?: string | null;
  language?: string | null;
  genres?: string[] | null;
}

export interface BookWithRating extends Book {
  averageRating: string | null;
}

export interface ExternalBook {
  external_id: string;
  title: string;
  authors?: string[];
  publishedDate?: string;
  description?: string;
  thumbnail?: string;
  pageCount?: number;
  categories?: string[];
  language?: string;
  publisher?: string;
  isbn?: string;
}

export interface UserBook {
  id: number;
  user_id: number;
  book_id: number | null;
  external_book_id: string | null;
  status: BookStatus;
  created_at: string;
  updated_at: string;
  book: Book | null;
}

export interface CreateBookRequest {
  title: string;
  author: string;
  description?: string;
  page_count?: number;
  published_date?: string;
  publisher?: string;
  isbn?: string;
  image_url?: string;
  language?: string;
  genres?: string[];
}

export interface UpdateBookRequest extends Partial<CreateBookRequest> {
  id: number;
}

export interface BookSearchParams {
  q?: string;
  page?: number;
  page_size?: number;
  author?: string;
  genre?: string;
  language?: string;
}

export interface ExternalBookSearchParams {
  q: string;
  page?: number;
  max_results?: number;
}

export type BookStatus = 'want_to_read' | 'currently_reading' | 'read';