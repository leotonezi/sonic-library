export interface Book {
  id: number;
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