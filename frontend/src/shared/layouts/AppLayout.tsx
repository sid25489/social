import { Outlet, Link, useLocation } from 'react-router-dom';
import { Home, Search, PlusSquare, Heart, MessageCircle, User } from 'lucide-react';
import { cn } from '../utils/cn';

const BottomNav = () => {
  const { pathname } = useLocation();

  const navItems = [
    { icon: <Home className="w-6 h-6" />, path: '/' },
    { icon: <Search className="w-6 h-6" />, path: '/search' },
    { icon: <PlusSquare className="w-6 h-6" />, path: '/post/create' }, // We'll make this open a modal in reality
    { icon: <Heart className="w-6 h-6" />, path: '/notifications' },
    { icon: <MessageCircle className="w-6 h-6" />, path: '/messages' },
    { icon: <User className="w-6 h-6" />, path: '/profile/me' },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-background/80 backdrop-blur-md border-t border-border p-3 flex justify-around items-center md:hidden z-50">
      {navItems.map((item, idx) => {
        const isActive = pathname === item.path || (item.path !== '/' && pathname.startsWith(item.path));
        return (
          <Link
            key={idx}
            to={item.path}
            className={cn(
              "p-2 rounded-xl transition-all duration-200 active:scale-95",
              isActive ? "text-primary bg-primary/10" : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
            )}
          >
            {item.icon}
          </Link>
        );
      })}
    </nav>
  );
};

const Sidebar = () => {
  const { pathname } = useLocation();

  const navItems = [
    { label: 'Home', icon: <Home className="w-6 h-6" />, path: '/' },
    { label: 'Search', icon: <Search className="w-6 h-6" />, path: '/search' },
    { label: 'Messages', icon: <MessageCircle className="w-6 h-6" />, path: '/messages' },
    { label: 'Notifications', icon: <Heart className="w-6 h-6" />, path: '/notifications' },
    { label: 'Create', icon: <PlusSquare className="w-6 h-6" />, path: '/post/create' },
    { label: 'Profile', icon: <User className="w-6 h-6" />, path: '/profile/me' },
  ];

  return (
    <aside className="hidden md:flex flex-col w-[280px] h-screen fixed left-0 top-0 border-r border-border p-4 overflow-y-auto">
      <div className="text-2xl font-black tracking-tight mb-8 px-4 text-foreground cursor-pointer">
        ConnectSphere
      </div>
      
      <nav className="flex-1 flex flex-col gap-2">
        {navItems.map((item, idx) => {
          const isActive = pathname === item.path || (item.path !== '/' && pathname.startsWith(item.path));
          return (
            <Link
              key={idx}
              to={item.path}
              className={cn(
                "flex items-center gap-4 px-4 py-3 rounded-2xl transition-all duration-200 group",
                isActive 
                  ? "bg-primary text-primary-foreground font-semibold" 
                  : "text-foreground hover:bg-accent/50 hover:text-accent-foreground"
              )}
            >
              <div className={cn(
                "transition-transform duration-300 group-hover:scale-110",
                isActive ? "text-primary-foreground" : "text-foreground"
              )}>
                {item.icon}
              </div>
              <span className="text-[17px]">{item.label}</span>
            </Link>
          );
        })}
      </nav>
      
      <div className="mt-auto px-4 cursor-pointer">
        {/* User Mini Profile Footer could go here */}
      </div>
    </aside>
  );
};

export default function AppLayout() {
  return (
    <div className="min-h-screen bg-background text-foreground flex">
      {/* Desktop Sidebar */}
      <Sidebar />
      
      {/* Main Content Area */}
      <main className="flex-1 md:ml-[280px] w-full max-w-[600px] mx-auto min-h-screen border-x border-border/50 pb-20 md:pb-0 relative">
        <Outlet />
      </main>
      
      {/* Mobile Bottom Navigation */}
      <BottomNav />
    </div>
  );
}
