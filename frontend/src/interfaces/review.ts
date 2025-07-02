export default interface Review {
  id: number;
  content: string;
  rate: number;
  user_id: number;
  created_at?: string;
  user_name?: string;
  user_profile_picture?: string;
}
