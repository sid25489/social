import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface User {
  id: string;
  username: string;
  avatar?: string;
  bio?: string;
  displayName?: string;
  followersCount: number;
  followingCount: number;
  postsCount?: number;
  isPrivate?: boolean;
}

interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  setTokens: (access: string, refresh: string) => void;
  setAuth: (user: User | null, token: string, refresh?: string | null) => void;
  setUser: (user: User) => void;
  updateUser: (data: Partial<User>) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      setTokens: (access, refresh) =>
        set({ token: access, refreshToken: refresh, isAuthenticated: true }),
      setAuth: (user, token, refresh) =>
        set({
          user,
          token,
          refreshToken: refresh ?? null,
          isAuthenticated: !!token,
        }),
      setUser: (user) => set({ user, isAuthenticated: true }),
      updateUser: (data) =>
        set((state) => ({ user: state.user ? { ...state.user, ...data } : null })),
      logout: () =>
        set({
          user: null,
          token: null,
          refreshToken: null,
          isAuthenticated: false,
        }),
    }),
    {
      name: 'connectsphere-auth',
      partialize: (s) => ({
        user: s.user,
        token: s.token,
        refreshToken: s.refreshToken,
        isAuthenticated: s.isAuthenticated,
      }),
    }
  )
);
