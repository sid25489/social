import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, History, TrendingUp, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
// import { api } from '../../../shared/services/api';

function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(timer);
    };
  }, [value, delay]);

  return debouncedValue;
}

export default function SearchPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState<'top' | 'accounts' | 'tags'>('top');
  const debouncedSearchTerm = useDebounce(searchTerm, 300);

  const { data, isLoading } = useQuery({
    queryKey: ['search', debouncedSearchTerm, activeTab],
    queryFn: async () => {
      if (!debouncedSearchTerm) return null;
      // return api.get(`/search/?q=${debouncedSearchTerm}&type=${activeTab}`);
      // Mocking for now:
      return new Promise((resolve) => 
        setTimeout(() => resolve([
          { id: 1, name: `Result for ${debouncedSearchTerm}` },
          { id: 2, name: `${activeTab} item match` }
        ]), 400)
      );
    },
    enabled: !!debouncedSearchTerm,
  });

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col p-4 md:pt-8 w-full">
      {/* Search Input */}
      <div className="relative group">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
        <input 
          autoFocus
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search ConnectSphere..."
          className="w-full bg-accent/40 rounded-full h-12 pl-12 pr-10 text-base font-medium focus:outline-none focus:ring-2 focus:ring-primary focus:bg-background transition-all shadow-sm"
        />
        <AnimatePresence>
          {searchTerm && (
            <motion.button 
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0, opacity: 0 }}
              onClick={() => setSearchTerm('')}
              className="absolute right-4 top-1/2 -translate-y-1/2 bg-muted-foreground/20 rounded-full p-1 hover:bg-muted-foreground/30 text-foreground"
            >
              <X className="h-4 w-4" />
            </motion.button>
          )}
        </AnimatePresence>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-6 mt-6 border-b border-border pb-1 overflow-x-auto no-scrollbar">
        {(['top', 'accounts', 'tags'] as const).map((tab) => (
          <button 
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`pb-3 font-semibold text-[15px] transition-colors relative whitespace-nowrap ${
              activeTab === tab ? 'text-foreground' : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
            {activeTab === tab && (
              <motion.div 
                layoutId="search-tab-indicator"
                className="absolute bottom-0 left-0 right-0 h-1 bg-primary rounded-t-full"
              />
            )}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto pt-4 no-scrollbar pb-20 md:pb-0">
        {!searchTerm ? (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <History className="h-5 w-5 text-muted-foreground" />
                Recent Searches
              </h3>
              <div className="flex flex-wrap gap-2">
                {['frontend dev', 'react 18 features', 'tailwind animations'].map(tag => (
                  <span key={tag} className="px-4 py-2 bg-accent/50 rounded-full text-sm font-medium cursor-pointer hover:bg-accent hover:shadow-sm transition-all border border-transparent hover:border-border">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-primary" />
                Trending Today
              </h3>
              <div className="space-y-4">
                {[1, 2, 3, 4].map(i => (
                  <div key={i} className="flex items-center justify-between group cursor-pointer">
                    <div className="flex flex-col">
                      <span className="text-xs text-muted-foreground font-semibold uppercase tracking-wider">Trending in Tech</span>
                      <span className="font-bold text-foreground group-hover:underline">#SystemDesign</span>
                      <span className="text-sm text-muted-foreground">12.5K posts</span>
                    </div>
                    <button className="text-muted-foreground hover:text-foreground rounded-full p-2 hover:bg-accent">
                      <MoreHorizontal className="h-5 w-5" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : isLoading ? (
          <div className="flex justify-center mt-12">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary"></div>
          </div>
        ) : (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
            {/* Render Search Results dynamically */}
            {data && Array.isArray(data) ? data.map((item: any) => (
              <div key={item.id} className="p-4 border-b border-border/50 hover:bg-accent/30 rounded-lg cursor-pointer transition-colors">
                <h4 className="font-semibold">{item.name}</h4>
                <p className="text-sm text-muted-foreground">Matches active query.</p>
              </div>
            )) : <p className="text-center text-muted-foreground mt-8 text-sm">No results found for "{searchTerm}"</p>}
          </div>
        )}
      </div>
    </div>
  );
}
// Required dummy fix for MoreHorizontal since it was implicitly used in UI
import { MoreHorizontal } from 'lucide-react';
