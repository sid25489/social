import React, { useRef, useEffect } from 'react';
import { useInfiniteQuery } from '@tanstack/react-query';
import { useVirtualizer } from '@tanstack/react-virtual';
import { PostCard } from '../components/PostCard';
import { feedService, type Post } from '../services/feed.service';

export default function FeedPage() {
  const containerRef = useRef<HTMLDivElement>(null);
  
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    status
  } = useInfiniteQuery({
    queryKey: ['feed'],
    queryFn: ({ pageParam = 1 }) => feedService.getFeed(pageParam),
    initialPageParam: 1,
    getNextPageParam: (lastPage, allPages) => {
      // DRF style: lastPage.next might be a URL. Extract page param or return allPages.length + 1
      return lastPage.next ? allPages.length + 1 : undefined;
    },
    // Adding stale time so feed feels instant on back navigation
    staleTime: 60000,
  });

  const flatPosts = React.useMemo(() => {
    return data?.pages.flatMap((page) => page.results) ?? [];
  }, [data]);

  // The virtualizer calculates the items heights
  const rowVirtualizer = useVirtualizer({
    count: hasNextPage ? flatPosts.length + 1 : flatPosts.length,
    getScrollElement: () => containerRef.current,
    estimateSize: () => 500, // estimated height of PostCard
    overscan: 3, // rendered outside of viewport
  });

  const virtualItems = rowVirtualizer.getVirtualItems();

  useEffect(() => {
    const [lastItem] = [...virtualItems].reverse();
    if (!lastItem) return;

    if (
      lastItem.index >= flatPosts.length - 1 &&
      hasNextPage &&
      !isFetchingNextPage
    ) {
      fetchNextPage();
    }
  }, [hasNextPage, fetchNextPage, flatPosts.length, isFetchingNextPage, virtualItems]);

  if (status === 'pending') {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="flex flex-col h-screen items-center justify-center p-4 text-center space-y-4">
        <h2 className="text-xl font-bold">Failed to load feed</h2>
        <button 
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div 
      ref={containerRef}
      className="h-screen overflow-y-auto no-scrollbar pb-20 md:pb-0"
    >
      <div className="md:pt-4 max-w-[600px] mx-auto">
        <div
          style={{
            height: `${rowVirtualizer.getTotalSize()}px`,
            width: '100%',
            position: 'relative',
          }}
        >
          {virtualItems.map((virtualRow) => {
            const isLoaderRow = virtualRow.index > flatPosts.length - 1;
            const post = flatPosts[virtualRow.index];

            return (
              <div
                key={virtualRow.index}
                data-index={virtualRow.index}
                ref={rowVirtualizer.measureElement}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  transform: `translateY(${virtualRow.start}px)`,
                }}
              >
                {isLoaderRow ? (
                  hasNextPage ? (
                    <div className="py-4 text-center text-muted-foreground w-full flex justify-center pointer-events-none">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                    </div>
                  ) : (
                    <div className="py-6 text-center text-muted-foreground font-medium">
                      You've caught up!
                    </div>
                  )
                ) : (
                  <PostCard post={post as Post} />
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
