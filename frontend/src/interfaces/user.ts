export default interface User {
  id: number;
  name: string;
  email: string;
  profile_picture?: string;
  is_admin: boolean;
}