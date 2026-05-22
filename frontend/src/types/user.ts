export interface User {
  id: number;
  name: string;
  email: string;
  profile_picture?: string;
  is_admin: boolean;
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