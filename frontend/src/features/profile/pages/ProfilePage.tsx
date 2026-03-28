import { useState } from 'react';
import { useParams, Link, Navigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { Grid3X3, PlaySquare, Bookmark, UserSquare, Settings } from 'lucide-react';
import { cn } from '../../../shared/utils/cn';
import { profileService } from '../../../shared/services/profile.service';
import { useAuthStore } from '../../../store/useAuthStore';
import { useOpenSettings } from '../../../shared/contexts/SettingsDrawerContext';
import type { PostListDto, ProfileDto } from '../../../shared/types/profile';

type TabId = 'posts' | 'reels' | 'saved' | 'tagged';

export default function ProfilePage() {
  const { username } = useParams<{ username: string }>();
  const currentUser = useAuthStore((s) => s.user);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated && !!s.token);
  const openSettings = useOpenSettings();
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<TabId>('posts');

  const isSelf = username === 'me' || (!!currentUser && username === currentUser.username);

  const profileQuery = useQuery({
    queryKey: ['profile', username],
    queryFn: async (): Promise<ProfileDto> => {
      if (!username) throw new Error('No username');
      if (username === 'me') {
        return profileService.getMe();
      }
      return profileService.getByUsername(username);
    },
    enabled: !!username && isAuthenticated,
  });

  const postsQuery = useQuery({
    queryKey: ['profile-posts', profileQuery.data?.user_id],
    queryFn: () => profileService.getPostsByAuthor(profileQuery.data!.user_id),
    enabled: !!profileQuery.data?.user_id && tab === 'posts',
  });

  const bookmarksQuery = useQuery({
    queryKey: ['profile-bookmarks'],
    queryFn: () => profileService.getBookmarks(),
    enabled: isSelf && tab === 'saved' && isAuthenticated,
  });

  const followMutation = useMutation({
    mutationFn: () => {
      const id = profileQuery.data!.user_id;
      if (profileQuery.data!.is_following) {
        return profileService.unfollow(id);
      }
      return profileService.follow(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile', username] });
      queryClient.invalidateQueries({ queryKey: ['profile-posts'] });
    },
  });

  if (!username) {
    return <Navigate to="/" replace />;
  }

  if (!isAuthenticated) {
    return (
      <Navigate to="/login" state={{ from: `/profile/${username}` }} replace />
    );
  }

  if (profileQuery.isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-3">
        <div className="w-10 h-10 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        <p className="text-sm text-muted-foreground">Loading profile…</p>
      </div>
    );
  }

  if (profileQuery.isError) {
    const status = axios.isAxiosError(profileQuery.error) ? profileQuery.error.response?.status : null;
    const msg =
      status === 403 || status === 404
        ? 'This account is private or unavailable.'
        : 'Could not load this profile.';
    return (
      <div className="p-8 text-center">
        <p className="text-muted-foreground">{msg}</p>
        <Link to="/" className="text-primary font-semibold text-sm mt-4 inline-block">
          Back home
        </Link>
      </div>
    );
  }

  const p = profileQuery.data!;
  const displayName = p.display_name || p.username;
  const avatarSrc =
    p.avatar_url ||
    `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(p.username)}`;

  const gridPosts: PostListDto[] =
    tab === 'saved' && isSelf ? bookmarksQuery.data ?? [] : postsQuery.data ?? [];

  const tabs: { id: TabId; icon: React.ReactNode; label: string }[] = [
    { id: 'posts', icon: <Grid3X3 className="w-4 h-4" />, label: 'POSTS' },
    { id: 'reels', icon: <PlaySquare className="w-4 h-4" />, label: 'REELS' },
    { id: 'saved', icon: <Bookmark className="w-4 h-4" />, label: 'SAVED' },
    { id: 'tagged', icon: <UserSquare className="w-4 h-4" />, label: 'TAGGED' },
  ];

  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground pb-20 md:pb-0">
      <div className="p-4 sm:p-8 flex items-start gap-4 sm:gap-10 sm:max-w-4xl sm:mx-auto w-full relative">
        {isSelf && (
          <button
            type="button"
            onClick={openSettings}
            className="absolute right-2 top-2 sm:right-4 sm:top-4 p-2 rounded-xl hover:bg-accent text-muted-foreground hover:text-foreground md:hidden"
            aria-label="Settings"
          >
            <Settings className="w-5 h-5" />
          </button>
        )}
        <div className="w-20 h-20 sm:w-36 sm:h-36 shrink-0 rounded-full bg-ig-gradient p-[3px] group relative hover:scale-[1.02] transition-transform duration-300 shadow-md">
          <img
            src={avatarSrc}
            alt=""
            className="w-full h-full object-cover rounded-full border-4 border-background bg-background shadow-inner"
          />
        </div>

        <div className="flex flex-col flex-1 pl-2 sm:pl-0 min-w-0">
          <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-6 mb-4 sm:mb-6">
            <h1 className="text-xl sm:text-2xl font-medium truncate pr-10 md:pr-0">@{p.username}</h1>
            <div className="flex gap-2 flex-wrap">
              {isSelf ? (
                <button
                  type="button"
                  onClick={openSettings}
                  className="bg-accent hover:bg-accent/80 text-foreground font-semibold px-5 py-1.5 rounded-xl text-sm transition-all duration-300 active:scale-95 hover:shadow-sm inline-flex items-center justify-center gap-2"
                >
                  <Settings className="w-4 h-4 hidden sm:inline" />
                  Edit profile
                </button>
              ) : (
                <>
                  {!p.is_blocked && (
                    <button
                      type="button"
                      disabled={followMutation.isPending || !!p.pending_follow_request}
                      onClick={() => followMutation.mutate()}
                      className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold px-5 py-1.5 rounded-xl text-sm transition-all duration-300 active:scale-95 hover:shadow-md disabled:opacity-60"
                    >
                      {p.pending_follow_request
                        ? 'Requested'
                        : p.is_following
                          ? 'Following'
                          : 'Follow'}
                    </button>
                  )}
                  {p.can_message && (
                    <Link
                      to={`/messages/${p.user_id}`}
                      className="bg-accent hover:bg-accent/80 text-foreground font-semibold px-5 py-1.5 rounded-xl text-sm transition-all duration-300 active:scale-95 hover:shadow-sm inline-flex items-center justify-center"
                    >
                      Message
                    </Link>
                  )}
                </>
              )}
            </div>
          </div>

          <div className="hidden sm:flex gap-10 font-medium mb-6 text-[15px]">
            <span>
              <span className="font-bold">{p.posts_count}</span> posts
            </span>
            <span>
              <span className="font-bold">{p.followers_count}</span> followers
            </span>
            <span>
              <span className="font-bold">{p.following_count}</span> following
            </span>
          </div>

          <div className="hidden sm:block text-[15px]">
            <span className="font-semibold block">{displayName}</span>
            {p.bio ? <span className="text-muted-foreground block whitespace-pre-wrap">{p.bio}</span> : null}
            {p.website ? (
              <a
                href={p.website.startsWith('http') ? p.website : `https://${p.website}`}
                target="_blank"
                rel="noreferrer"
                className="text-blue-500 font-medium hover:underline break-all"
              >
                {p.website}
              </a>
            ) : null}
            {p.location ? <span className="text-muted-foreground block text-sm mt-1">{p.location}</span> : null}
          </div>
        </div>
      </div>

      <div className="px-4 pb-4 sm:hidden text-[14px]">
        <span className="font-semibold block">{displayName}</span>
        {p.bio ? <span className="text-muted-foreground block whitespace-pre-wrap">{p.bio}</span> : null}
        {p.website ? (
          <a
            href={p.website.startsWith('http') ? p.website : `https://${p.website}`}
            target="_blank"
            rel="noreferrer"
            className="text-blue-500 font-medium hover:underline break-all"
          >
            {p.website}
          </a>
        ) : null}
      </div>

      <div className="flex sm:hidden justify-around py-3 border-t border-border/50 text-center font-medium">
        <div className="flex flex-col">
          <span className="font-bold">{p.posts_count}</span>
          <span className="text-muted-foreground text-sm">posts</span>
        </div>
        <div className="flex flex-col">
          <span className="font-bold">{p.followers_count}</span>
          <span className="text-muted-foreground text-sm">followers</span>
        </div>
        <div className="flex flex-col">
          <span className="font-bold">{p.following_count}</span>
          <span className="text-muted-foreground text-sm">following</span>
        </div>
      </div>

      <div className="flex justify-center border-t border-border/50">
        <div className="flex gap-12 sm:gap-16">
          {tabs.map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => {
                if (t.id === 'saved' && !isSelf) return;
                setTab(t.id);
              }}
              disabled={t.id === 'saved' && !isSelf}
              className={cn(
                'flex items-center gap-2 py-4 text-xs font-semibold tracking-widest border-t-2 sm:px-1 transition-all duration-300',
                t.id === 'saved' && !isSelf && 'opacity-40 cursor-not-allowed',
                tab === t.id
                  ? 'border-foreground text-foreground'
                  : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'
              )}
            >
              {t.icon}
              <span className="hidden sm:inline">{t.label}</span>
            </button>
          ))}
        </div>
      </div>

      {tab === 'reels' && (
        <p className="text-center text-sm text-muted-foreground py-12">No reels yet.</p>
      )}
      {tab === 'tagged' && (
        <p className="text-center text-sm text-muted-foreground py-12">No tagged posts yet.</p>
      )}

      {(tab === 'posts' || tab === 'saved') && (
        <div className="grid grid-cols-3 gap-0.5 sm:gap-1 w-full max-w-4xl mx-auto">
          {tab === 'saved' && isSelf && bookmarksQuery.isLoading ? (
            <div className="col-span-3 flex justify-center py-12">
              <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            </div>
          ) : gridPosts.length === 0 ? (
            <div className="col-span-3 text-center text-sm text-muted-foreground py-12">
              {tab === 'saved' ? 'Save posts to see them here.' : 'No posts yet.'}
            </div>
          ) : (
            gridPosts.map((post) => {
              const thumb = post.image_urls?.[0];
              return (
                <Link
                  key={post.id}
                  to={`/post/${post.id}`}
                  className="aspect-square bg-accent/30 cursor-pointer group relative overflow-hidden block transition-opacity duration-300 hover:opacity-90"
                >
                  {thumb ? (
                    <img src={thumb} alt="" className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center p-2 text-[10px] text-center text-muted-foreground line-clamp-4 transition-transform duration-500 group-hover:scale-105">
                      {post.content}
                    </div>
                  )}
                  {/* Subtle hover overlay for desktop */}
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors duration-300 z-10 pointer-events-none hidden sm:block" />
                </Link>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}
