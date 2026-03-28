import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';

// Centralised query client instance
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // Data remains fresh for 5 mins
      retry: (failureCount, error: any) => {
        // Retry networking errors exponentially up to 3 times
        if (error.status === 404 || error.status === 401 || error.status === 403) return false;
        return failureCount < 3;
      },
    },
  },
});

export const QueryProvider = ({ children }: { children: ReactNode }) => {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};
