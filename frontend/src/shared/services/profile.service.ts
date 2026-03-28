import { api } from './api';
import type { PostListDto, ProfileDto } from '../types/profile';

export const profileService = {
  getMe(): Promise<ProfileDto> {
    return api.get('/users/me/') as Promise<ProfileDto>;
  },

  getByUsername(username: string): Promise<ProfileDto> {
    return api.get(
      `/users/by-username/${encodeURIComponent(username)}/`
    ) as Promise<ProfileDto>;
  },

  getPostsByAuthor(authorId: string): Promise<PostListDto[]> {
    return api.get('/posts/', { params: { author: authorId } }) as Promise<PostListDto[]>;
  },

  getBookmarks(): Promise<PostListDto[]> {
    return api.get('/posts/bookmarks/') as Promise<PostListDto[]>;
  },

  updateProfile(data: Partial<{
    display_name: string;
    bio: string;
    avatar_url: string;
    website: string;
    location: string;
    is_private: boolean;
  }>): Promise<ProfileDto> {
    return api.patch('/profiles/update_profile/', data) as Promise<ProfileDto>;
  },

  follow(userId: string): Promise<unknown> {
    return api.post('/social/follow/follow/', { user_id: userId });
  },

  unfollow(userId: string): Promise<unknown> {
    return api.post('/social/follow/unfollow/', { user_id: userId });
  },

  changePassword(old_password: string, new_password: string): Promise<unknown> {
    return api.post('/users/change_password/', { old_password, new_password });
  },

  getBlockedAccounts(): Promise<
    { id: string; username: string; followers_count: number; is_following: boolean; is_blocked: boolean }[]
  > {
    return api.get('/users/blocked_accounts/') as Promise<
      { id: string; username: string; followers_count: number; is_following: boolean; is_blocked: boolean }[]
    >;
  },

  unblock(userId: string): Promise<unknown> {
    return api.post('/social/follow/unblock/', { user_id: userId });
  },
};
