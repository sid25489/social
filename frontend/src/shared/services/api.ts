import axios, { AxiosError } from 'axios';
import { useAuthStore } from '../../store/useAuthStore';

// Define the baseURL for Axios based on environment
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: any) => void;
}> = [];

const processQueue = (error: AxiosError | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Request interceptor to attach JWT
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling and token refresh
api.interceptors.response.use(
  (response) => {
    // Return direct data if present, or whole response
    return response.data;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config;

    // Reject immediately if no config or not a 401
    if (!originalRequest || error.response?.status !== 401) {
      return Promise.reject(error);
    }

    // Prevent infinite loop if the refresh endpoint itself throws 401
    if (originalRequest.url?.includes('/auth/refresh')) {
      useAuthStore.getState().logout();
      window.location.href = '/login';
      return Promise.reject(error);
    }

    // @ts-ignore
    if (originalRequest._retry) {
      return Promise.reject(error);
    }

    if (isRefreshing) {
      // If we are already refreshing, push next requests to queue
      try {
        const token = await new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        });
        originalRequest.headers.Authorization = `Bearer ${token}`;
        return api(originalRequest);
      } catch (err) {
        return Promise.reject(err);
      }
    }

    // @ts-ignore
    originalRequest._retry = true;
    isRefreshing = true;

    try {
      // Implement silent refresh logic here
      // const { data } = await axios.post('/api/v1/auth/refresh');
      // const newToken = data.access_token;
      
      // For now, if 401 occurs and refresh is mocked to fail, we logout
      const newToken = null; // REPLACE WITH REAL REFRESH
      
      if (!newToken) {
        throw new Error('Refresh failed');
      }

      // useAuthStore.getState().setAuth(useAuthStore.getState().user!, newToken);
      // api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
      
      // processQueue(null, newToken);
      // return api(originalRequest);
    } catch (refreshError) {
      processQueue(refreshError as AxiosError, null);
      useAuthStore.getState().logout();
      window.location.href = '/login';
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);
