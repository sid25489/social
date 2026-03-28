export interface ProfileDto {
  id: string;
  user_id: string;
  username: string;
  email?: string;
  display_name: string;
  bio: string;
  avatar_url: string | null;
  cover_image_url: string | null;
  website: string | null;
  location: string;
  is_private: boolean;
  followers_count: number;
  following_count: number;
  posts_count: number;
  is_following: boolean;
  is_blocked: boolean;
  can_message: boolean;
  pending_follow_request: string | null;
}

export interface PostListDto {
  id: string;
  author: {
    id: string;
    username: string;
    followers_count: number;
    is_following: boolean;
    is_blocked: boolean;
  };
  content: string;
  likes_count: number;
  comments_count: number;
  image_urls: string[];
  created_at: string;
}
