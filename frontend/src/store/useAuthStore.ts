import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  username: string;
  avatar?: string;
  bio?: string;
  followersCount: number;
  followingCount: number;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  setAuth: (user: User, token: string) => void;
  updateUser: (data: Partial<User>) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      setAuth: (user, token) => set({ user, token, isAuthenticated: true }),
      updateUser: (data) =>
        set((state) => ({ user: state.user ? { ...state.user, ...data } : null })),
      logout: () => set({ user: null, token: null, isAuthenticated: false }),
    }),
    {
      name: 'connectsphere-auth',
    }
  )
);
