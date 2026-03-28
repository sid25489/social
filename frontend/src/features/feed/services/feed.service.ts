import { api } from '../../../shared/services/api';

export interface User {
  id: string;
  username: string;
  avatar: string;
}

export interface Post {
  id: string;
  author: User;
  content: string;
  mediaUrl?: string;
  likesCount: number;
  commentsCount: number;
  isLikedByMe: boolean;
  createdAt: string;
}

export interface FeedResponse {
  results: Post[];
  next: string | null;
  previous: string | null;
}

export const feedService = {
  getFeed: async (pageParam = 1): Promise<FeedResponse> => {
    // This connects to the Django API. DRF uses pagination, so it could be limit/offset or page.
    return api.get(`/feed/?page=${pageParam}`);
  },
  
  likePost: async (postId: string) => {
    return api.post(`/posts/${postId}/like/`);
  },
  
  unlikePost: async (postId: string) => {
    return api.delete(`/posts/${postId}/like/`);
  }
};
