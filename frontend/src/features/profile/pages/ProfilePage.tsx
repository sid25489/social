import { Grid3X3, PlaySquare, Bookmark, UserSquare } from 'lucide-react';
import { cn } from '../../../shared/utils/cn';

export default function ProfilePage() {
  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground pb-20 md:pb-0">
      {/* Header Info */}
      <div className="p-4 sm:p-8 flex items-start gap-4 sm:gap-10 sm:max-w-4xl sm:mx-auto w-full">
        {/* Avatar */}
        <div className="w-20 h-20 sm:w-36 sm:h-36 shrink-0 rounded-full bg-ig-gradient p-[3px]">
          <img 
            src="https://api.dicebear.com/7.x/avataaars/svg?seed=sid" 
            alt="Profile avatar" 
            className="w-full h-full object-cover rounded-full border-4 border-background bg-background"
          />
        </div>
        
        {/* Stats & Info */}
        <div className="flex flex-col flex-1 pl-2 sm:pl-0">
          <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-6 mb-4 sm:mb-6">
            <h1 className="text-xl sm:text-2xl font-medium truncate">s4i_sidharth</h1>
            <div className="flex gap-2">
              <button className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold px-5 py-1.5 rounded-lg text-sm transition-colors w-full sm:w-auto">
                Follow
              </button>
              <button className="bg-accent hover:bg-accent/80 text-foreground font-semibold px-5 py-1.5 rounded-lg text-sm transition-colors w-full sm:w-auto">
                Message
              </button>
            </div>
          </div>
          
          <div className="hidden sm:flex gap-10 font-medium mb-6 text-[15px]">
            <span><span className="font-bold">42</span> posts</span>
            <span className="cursor-pointer"><span className="font-bold">1.2M</span> followers</span>
            <span className="cursor-pointer"><span className="font-bold">120</span> following</span>
          </div>

          <div className="hidden sm:block text-[15px]">
            <span className="font-semibold block">Sidharth</span>
            <span className="text-muted-foreground block">Software Engineer & Designer</span>
            <a href="#" className="text-blue-500 font-medium hover:underline">linktr.ee/sidharth</a>
          </div>
        </div>
      </div>
      
      {/* Mobile Bio */}
      <div className="px-4 pb-4 sm:hidden text-[14px]">
        <span className="font-semibold block">Sidharth</span>
        <span className="text-muted-foreground block">Software Engineer & Designer</span>
        <a href="#" className="text-blue-500 font-medium hover:underline">linktr.ee/sidharth</a>
      </div>

      {/* Mobile Stats */}
      <div className="flex sm:hidden justify-around py-3 border-t border-border/50 text-center font-medium">
        <div className="flex flex-col">
          <span className="font-bold">42</span>
          <span className="text-muted-foreground text-sm">posts</span>
        </div>
        <div className="flex flex-col">
          <span className="font-bold">1.2M</span>
          <span className="text-muted-foreground text-sm">followers</span>
        </div>
        <div className="flex flex-col">
          <span className="font-bold">120</span>
          <span className="text-muted-foreground text-sm">following</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex justify-center border-t border-border/50">
        <div className="flex gap-12 sm:gap-16">
          {[
            { id: 'posts', icon: <Grid3X3 className="w-4 h-4" />, label: 'POSTS' },
            { id: 'reels', icon: <PlaySquare className="w-4 h-4" />, label: 'REELS' },
            { id: 'saved', icon: <Bookmark className="w-4 h-4" />, label: 'SAVED' },
            { id: 'tagged', icon: <UserSquare className="w-4 h-4" />, label: 'TAGGED' }
          ].map(tab => (
            <button key={tab.id} className={cn(
              "flex items-center gap-2 py-4 text-xs font-semibold tracking-widest border-t-2 sm:px-1 transition-colors",
              tab.id === 'posts' ? "border-foreground text-foreground" : "border-transparent text-muted-foreground hover:text-foreground"
            )}>
              {tab.icon}
              <span className="hidden sm:inline">{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-3 gap-0.5 sm:gap-1 w-full max-w-4xl mx-auto">
        {[1,2,3,4,5,6,7,8,9,10,11,12].map(i => (
          <div key={i} className="aspect-square bg-accent hover:opacity-90 cursor-pointer object-cover group relative overflow-hidden">
            <img 
              src={`https://source.unsplash.com/random/400x400?sig=${i}`} 
              alt={`Post ${i}`}
              className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
            />
          </div>
        ))}
      </div>
    </div>
  );
}
