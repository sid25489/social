import { Outlet, Link, useLocation } from 'react-router-dom';
import { Home, Search, PlusSquare, Heart, MessageCircle, User, Instagram, Moon, Sun, Menu } from 'lucide-react';
import { cn } from '../utils/cn';
import { useTheme } from '../../providers/ThemeProvider';

const BottomNav = () => {
  const { pathname } = useLocation();

  const navItems = [
    { icon: <Home className="w-6 h-6" />, path: '/' },
    { icon: <Search className="w-6 h-6" />, path: '/search' },
    { icon: <PlusSquare className="w-6 h-6" />, path: '/post/create' },
    { icon: <MessageCircle className="w-6 h-6" />, path: '/messages' },
    { icon: <User className="w-6 h-6" />, path: '/profile/me' },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-background border-t border-border p-2 flex justify-around items-center md:hidden z-50">
      {navItems.map((item, idx) => {
        const isActive = pathname === item.path || (item.path !== '/' && pathname.startsWith(item.path));
        return (
          <Link
            key={idx}
            to={item.path}
            className={cn(
              "p-3 rounded-xl transition-all duration-200 active:scale-95",
              isActive ? "text-primary" : "text-foreground hover:bg-accent hover:text-accent-foreground dark:text-gray-300"
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
  const { theme, setTheme } = useTheme();

  const navItems = [
    { label: 'Home', icon: <Home className="w-6 h-6" />, path: '/' },
    { label: 'Search', icon: <Search className="w-6 h-6" />, path: '/search' },
    { label: 'Messages', icon: <MessageCircle className="w-6 h-6" />, path: '/messages' },
    { label: 'Notifications', icon: <Heart className="w-6 h-6" />, path: '/notifications' },
    { label: 'Create', icon: <PlusSquare className="w-6 h-6" />, path: '/post/create' },
    { label: 'Profile', icon: <User className="w-6 h-6" />, path: '/profile/me' },
  ];

  return (
    <aside className="hidden md:flex flex-col w-[72px] xl:w-[244px] h-screen fixed left-0 top-0 border-r border-border py-4 px-2 xl:px-4 overflow-y-auto bg-background z-50 transition-all duration-300">
      <Link to="/" className="flex items-center gap-4 mb-8 px-2 xl:px-4 h-[60px] cursor-pointer group hover:bg-accent/50 rounded-xl w-fit xl:w-full transition-colors">
        <div className="text-foreground transition-transform duration-300 group-hover:scale-105">
          <Instagram className="w-7 h-7 block xl:hidden" />
          <span className="hidden xl:block text-2xl font-black tracking-tight" style={{ fontFamily: 'var(--font-instagram, sans-serif)' }}>
            ConnectSphere
          </span>
        </div>
      </Link>
      
      <nav className="flex-1 flex flex-col gap-2">
        {navItems.map((item, idx) => {
          const isActive = pathname === item.path || (item.path !== '/' && pathname.startsWith(item.path));
          return (
            <Link
              key={idx}
              to={item.path}
              className={cn(
                "flex items-center gap-4 p-3 xl:px-4 xl:py-3 rounded-lg xl:rounded-xl transition-all duration-200 group relative",
                isActive 
                  ? "font-bold text-foreground" 
                  : "text-foreground hover:bg-accent/50 dark:text-gray-200"
              )}
            >
              <div className={cn(
                "transition-transform duration-300 group-hover:scale-110",
                isActive && "text-primary"
              )}>
                {item.icon}
              </div>
              <span className="hidden xl:block text-[16px]">{item.label}</span>
            </Link>
          );
        })}
      </nav>
      
      <div className="mt-auto flex flex-col gap-2">
        <button
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className="flex items-center gap-4 p-3 xl:px-4 xl:py-3 rounded-lg xl:rounded-xl text-foreground hover:bg-accent/50 transition-all duration-200 group w-full"
        >
          <div className="transition-transform duration-300 group-hover:scale-110 text-foreground">
            {theme === 'dark' ? <Sun className="w-6 h-6" /> : <Moon className="w-6 h-6" />}
          </div>
          <span className="hidden xl:block text-[16px]">Switch Appearance</span>
        </button>

        <button className="flex items-center gap-4 p-3 xl:px-4 xl:py-3 rounded-lg xl:rounded-xl text-foreground hover:bg-accent/50 transition-all duration-200 group w-full">
          <Menu className="w-6 h-6 transition-transform duration-300 group-hover:scale-110" />
          <span className="hidden xl:block text-[16px]">More</span>
        </button>
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
      <main className="flex-1 md:ml-[72px] xl:ml-[244px] w-full max-w-[600px] mx-auto min-h-screen pb-20 md:pb-0 relative border-x border-border/20 lg:border-none">
        <Outlet />
      </main>
      
      {/* Mobile Bottom Navigation */}
      <BottomNav />
    </div>
  );
}
