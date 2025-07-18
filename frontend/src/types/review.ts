export interface Review {
  id: number;
  content: string;
  rate: number;
  user_id: number;
  created_at?: string;
  user_name?: string;
  user_profile_picture?: string;
}

export interface CreateReviewRequest {
  content: string;
  rate: number;
  book_id?: number;
  external_book_id?: string;
}

export interface UpdateReviewRequest {
  id: number;
  content?: string;
  rate?: number;
}

export interface ReviewWithUser extends Review {
  user: {
    id: number;
    name: string;
    profile_picture?: string;
  };
}