export interface Book {
  id: number;
  title: string;
  author: string;
  description?: string;
}

export interface BookWithRating extends Book {
  averageRating: string | null;
}