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
  status: string;
  created_at: string;
  updated_at: string;
}
