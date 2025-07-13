export interface User {
  id: number;
  name: string;
  email: string;
  profile_picture?: string;
}

export interface UserProfile extends User {
  created_at?: string;
  updated_at?: string;
}

export interface UpdateUserRequest {
  name?: string;
  email?: string;
  profile_picture?: string;
}