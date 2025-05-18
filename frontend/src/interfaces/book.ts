export interface Book {
  id: number;
  external_book_id: string | null;
  title: string;
  author: string;
  description?: string;
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