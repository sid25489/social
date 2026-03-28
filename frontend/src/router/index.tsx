import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import AppLayout from '../shared/layouts/AppLayout';

const FeedPage = lazy(() => import('../features/feed/pages/FeedPage'));
const PostPage = lazy(() => import('../features/post/pages/PostPage'));
const ProfilePage = lazy(() => import('../features/profile/pages/ProfilePage'));
const MessagingPage = lazy(() => import('../features/messaging/pages/MessagingPage'));
const NotificationsPage = lazy(() => import('../features/notifications/pages/NotificationsPage'));
const SearchPage = lazy(() => import('../features/search/pages/SearchPage'));
const AuthPage = lazy(() => import('../features/auth/pages/AuthPage'));

const FallbackLoader = () => (
  <div className="flex items-center justify-center p-4 min-h-[40vh]">
    <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary" />
  </div>
);

const router = createBrowserRouter([
  {
    path: '/login',
    element: (
      <Suspense fallback={<FallbackLoader />}>
        <AuthPage />
      </Suspense>
    ),
  },
  {
    path: '/',
    element: <AppLayout />,
    children: [
      {
        index: true,
        element: (
          <Suspense fallback={<FallbackLoader />}>
            <FeedPage />
          </Suspense>
        ),
      },
      {
        path: 'post/:id',
        element: (
          <Suspense fallback={<FallbackLoader />}>
            <PostPage />
          </Suspense>
        ),
      },
      {
        path: 'profile/:username',
        element: (
          <Suspense fallback={<FallbackLoader />}>
            <ProfilePage />
          </Suspense>
        ),
      },
      {
        path: 'messages',
        element: (
          <Suspense fallback={<FallbackLoader />}>
            <MessagingPage />
          </Suspense>
        ),
      },
      {
        path: 'messages/:userId',
        element: (
          <Suspense fallback={<FallbackLoader />}>
            <MessagingPage />
          </Suspense>
        ),
      },
      {
        path: 'notifications',
        element: (
          <Suspense fallback={<FallbackLoader />}>
            <NotificationsPage />
          </Suspense>
        ),
      },
      {
        path: 'search',
        element: (
          <Suspense fallback={<FallbackLoader />}>
            <SearchPage />
          </Suspense>
        ),
      },
    ],
  },
  {
    path: '*',
    element: (
      <div className="text-center p-8 text-xl font-bold bg-background text-foreground min-h-screen">
        404 Not Found
      </div>
    ),
  },
]);

export function AppRouter() {
  return <RouterProvider router={router} />;
}
