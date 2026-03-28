import { api } from './api';
import { useAuthStore } from '../../store/useAuthStore';
import type { ProfileDto } from '../types/profile';

function mapProfileToUser(p: ProfileDto) {
  return {
    id: p.user_id,
    username: p.username,
    displayName: p.display_name || '',
    bio: p.bio || '',
    avatar: p.avatar_url || undefined,
    followersCount: p.followers_count,
    followingCount: p.following_count,
    postsCount: p.posts_count,
    isPrivate: p.is_private,
  };
}

export const authService = {
  async syncUserFromApi(): Promise<void> {
    const profile = (await api.get('/users/me/')) as ProfileDto;
    useAuthStore.getState().setUser(mapProfileToUser(profile));
  },

  async login(username: string, password: string): Promise<void> {
    const data = (await api.post('/auth/token/', { username, password })) as {
      access: string;
      refresh: string;
    };
    useAuthStore.getState().setTokens(data.access, data.refresh);
    await authService.syncUserFromApi();
  },

  async register(body: {
    email: string;
    username: string;
    password: string;
    password2: string;
  }): Promise<void> {
    const res = (await api.post('/auth/register/register/', body)) as {
      tokens: { access: string; refresh: string };
    };
    useAuthStore.getState().setTokens(res.tokens.access, res.tokens.refresh);
    await authService.syncUserFromApi();
  },
};
