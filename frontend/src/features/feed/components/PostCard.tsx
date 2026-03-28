import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Heart, MessageCircle, Share2, MoreHorizontal, Bookmark } from 'lucide-react';
import { feedService, type Post } from '../services/feed.service';
import { cn } from '../../../shared/utils/cn';
import { useMutation, useQueryClient } from '@tanstack/react-query';

interface PostCardProps {
  post: Post;
  queryTypeKey?: string[]; // E.g. ['feed'] or ['profile', 'user_id']
  // This helps React Virtual with dynamic heights
  registerRef?: (node: HTMLDivElement | null) => void;
}

export const PostCard = React.forwardRef<HTMLDivElement, PostCardProps>(({ post, queryTypeKey = ['feed'], registerRef }, ref) => {
  const queryClient = useQueryClient();
  const [doubleClicked, setDoubleClicked] = useState(false);

  // Optimistic Heart Animation Update
  const mutation = useMutation({
    mutationFn: (isLiked: boolean) => 
      isLiked ? feedService.unlikePost(post.id) : feedService.likePost(post.id),
    onMutate: async (isLiked) => {
      await queryClient.cancelQueries({ queryKey: queryTypeKey });
      const previousFeed = queryClient.getQueryData(queryTypeKey);

      // Optimistically update the cache safely for paginated or single responses
      queryClient.setQueryData(queryTypeKey, (old: any) => {
        if (!old) return old;
        return {
          ...old,
          pages: old.pages.map((page: any) => ({
            ...page,
            results: page.results.map((p: Post) => {
              if (p.id === post.id) {
                return {
                  ...p,
                  isLikedByMe: !isLiked,
                  likesCount: !isLiked ? p.likesCount + 1 : p.likesCount - 1
                };
              }
              return p;
            })
          }))
        };
      });
      return { previousFeed };
    },
    onError: (_err, _variables, context) => {
      queryClient.setQueryData(queryTypeKey, context?.previousFeed);
    },
    onSettled: () => {
      // We don't indiscriminately invalidate the query because if it's an infinite query with 10 pages,
      // invalidating it will cause 10 parallel HTTP requests to re-fetch every single page!
      // Since it's a simple boolean like/unlike action, the optimistic cache is completely reliable.
      // queryClient.invalidateQueries({ queryKey: queryTypeKey });
    }
  });

  const handleLike = () => {
    mutation.mutate(post.isLikedByMe);
  };

  const handleDoubleClick = () => {
    if (!post.isLikedByMe) {
      handleLike();
    }
    setDoubleClicked(true);
    setTimeout(() => setDoubleClicked(false), 800);
  };

  return (
    <div 
      ref={(node) => {
        if (typeof ref === 'function') ref(node);
        else if (ref) ref.current = node;
        if (registerRef) registerRef(node);
      }}
      className="bg-card border-b border-border/50 sm:border sm:border-border/60 sm:rounded-2xl mb-2 sm:mb-8 overflow-hidden text-card-foreground shadow-sm hover:shadow-lg hover:border-border/80 transition-all duration-300"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-3 sm:p-4">
        <div className="flex items-center gap-3 cursor-pointer group">
          <div className="h-10 w-10 rounded-full bg-ig-gradient p-[2px] transition-transform duration-300 group-hover:scale-105 group-hover:shadow-md">
            <img 
              src={post.author.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${post.author.username}`} 
              alt={post.author.username}
              className="h-full w-full rounded-full border-2 border-background object-cover bg-background"
            />
          </div>
          <div>
            <h4 className="font-semibold text-sm hover:text-muted-foreground">{post.author.username}</h4>
            <span className="text-xs text-muted-foreground">{new Date(post.createdAt).toLocaleDateString()}</span>
          </div>
        </div>
        <button className="text-muted-foreground hover:text-foreground transition-all duration-300 hover:rotate-90 p-1 rounded-full hover:bg-accent/50">
          <MoreHorizontal className="h-5 w-5" />
        </button>
      </div>

      {/* Media / Content */}
      <div 
        className="w-full relative bg-accent/10 cursor-pointer overflow-hidden min-h-[300px] flex items-center justify-center border-y border-border/20 sm:border-none"
        onDoubleClick={handleDoubleClick}
      >
        {post.mediaUrl ? (
          <img 
            src={post.mediaUrl} 
            alt="Post content" 
            className="w-full max-h-[600px] object-cover bg-background"
            style={{ aspectRatio: "4/5" }}
            loading="lazy"
          />
        ) : (
          <div className="p-8 text-xl sm:text-2xl font-medium leading-relaxed break-words w-full text-center">
            {post.content}
          </div>
        )}
        
        {/* Double click heart animation overlay */}
        <AnimatePresence>
          {doubleClicked && (
            <motion.div
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1.5, opacity: 0.9 }}
              exit={{ scale: 0, opacity: 0 }}
              transition={{ duration: 0.3, type: 'spring' }}
              className="absolute inset-0 flex items-center justify-center pointer-events-none z-10"
            >
              <Heart className="w-24 h-24 text-white drop-shadow-2xl fill-white" />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Actions */}
      <div className="p-3 sm:p-4 flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button 
              onClick={handleLike}
              className="transition-all active:scale-75 hover:scale-110 disabled:opacity-50 group flex items-center duration-300"
              disabled={mutation.isPending}
            >
              <motion.div
                whileTap={{ scale: 0.8 }}
                transition={{ type: "spring", stiffness: 400, damping: 17 }}
              >
                <Heart 
                  strokeWidth={post.isLikedByMe ? 0 : 1.5}
                  className={cn(
                    "w-[26px] h-[26px] transition-colors", 
                    post.isLikedByMe ? "fill-destructive text-destructive" : "text-foreground group-hover:text-muted-foreground"
                  )} 
                />
              </motion.div>
            </button>
            <button className="transition-all active:scale-90 hover:scale-110 duration-300 group flex items-center text-foreground hover:text-muted-foreground">
              <MessageCircle strokeWidth={1.5} className="w-[26px] h-[26px]" />
            </button>
            <button className="transition-all active:scale-90 hover:scale-110 duration-300 group text-foreground hover:text-muted-foreground mr-1">
              <Share2 strokeWidth={1.5} className="w-[26px] h-[26px]" />
            </button>
          </div>
          <button className="transition-all active:scale-90 hover:scale-110 duration-300 text-foreground">
            <Bookmark strokeWidth={1.5} className="w-[26px] h-[26px]" />
          </button>
        </div>
        
        <div className="font-semibold text-sm px-1 py-1">
          {post.likesCount.toLocaleString()} {post.likesCount === 1 ? 'like' : 'likes'}
        </div>

        {/* Caption */}
        {post.mediaUrl && (
          <div className="text-sm px-1">
            <span className="font-semibold mr-2">{post.author.username}</span>
            <span>{post.content}</span>
          </div>
        )}
        
        {/* Comments count */}
        {post.commentsCount > 0 && (
          <button className="text-muted-foreground text-sm font-medium self-start hover:text-foreground px-1 py-1 transition-colors duration-200">
            View all {post.commentsCount} comments
          </button>
        )}
      </div>
    </div>
  );
});

PostCard.displayName = 'PostCard';
