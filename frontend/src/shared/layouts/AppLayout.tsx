import { useState } from 'react';
import { Outlet, Link, useLocation, Navigate } from 'react-router-dom';
import { Home, Search, PlusSquare, Heart, MessageCircle, User, Instagram, Moon, Sun, Menu } from 'lucide-react';
import { cn } from '../utils/cn';
import { useTheme } from '../../providers/ThemeProvider';
import { useAuthStore } from '../../store/useAuthStore';
import { OpenSettingsContext } from '../contexts/SettingsDrawerContext';
import SettingsModal from '../../features/settings/components/SettingsModal';

const BottomNav = () => {
  const { pathname } = useLocation();
  const user = useAuthStore((s) => s.user);

  const navItems = [
    { icon: <Home className="w-6 h-6" />, path: '/' },
    { icon: <Search className="w-6 h-6" />, path: '/search' },
    { icon: <PlusSquare className="w-6 h-6" />, path: '/post/create' },
    { icon: <MessageCircle className="w-6 h-6" />, path: '/messages' },
    {
      icon: <User className="w-6 h-6" />,
      path: user ? `/profile/${user.username}` : '/profile/me',
    },
  ];

  return (
    <nav className="fixed bottom-4 left-4 right-4 bg-background/85 backdrop-blur-xl border border-border/50 shadow-2xl rounded-2xl p-2 flex justify-around items-center md:hidden z-50 transition-all duration-300">
      {navItems.map((item, idx) => {
        const profilePath = item.path.startsWith('/profile');
        const isActive = profilePath
          ? pathname.startsWith('/profile')
          : pathname === item.path || (item.path !== '/' && pathname.startsWith(item.path));
        return (
          <Link
            key={idx}
            to={item.path}
            className={cn(
              'p-3 rounded-xl transition-all duration-300 active:scale-90 relative group',
              isActive ? 'text-primary' : 'text-muted-foreground hover:text-foreground'
            )}
          >
            {isActive && (
              <span className="absolute inset-0 bg-primary/10 rounded-xl -z-10 animate-in fade-in zoom-in duration-300" />
            )}
            <div className={cn("transition-transform duration-300", isActive && "scale-110")}>
              {item.icon}
            </div>
          </Link>
        );
      })}
    </nav>
  );
};

const Sidebar = ({ onOpenSettings }: { onOpenSettings: () => void }) => {
  const { pathname } = useLocation();
  const { theme, setTheme } = useTheme();
  const user = useAuthStore((s) => s.user);

  const profilePath = user ? `/profile/${user.username}` : '/profile/me';

  const navItems = [
    { label: 'Home', icon: <Home className="w-6 h-6" />, path: '/' },
    { label: 'Search', icon: <Search className="w-6 h-6" />, path: '/search' },
    { label: 'Messages', icon: <MessageCircle className="w-6 h-6" />, path: '/messages' },
    { label: 'Notifications', icon: <Heart className="w-6 h-6" />, path: '/notifications' },
    { label: 'Create', icon: <PlusSquare className="w-6 h-6" />, path: '/post/create' },
    { label: 'Profile', icon: <User className="w-6 h-6" />, path: profilePath },
  ];

  return (
    <aside className="hidden md:flex flex-col w-[72px] xl:w-[244px] h-screen fixed left-0 top-0 border-r border-border/50 bg-background/95 backdrop-blur-xl py-6 px-2 xl:px-4 overflow-y-auto z-50 transition-all duration-300">
      <Link
        to="/"
        className="flex items-center gap-4 mb-8 px-2 xl:px-4 h-[60px] cursor-pointer group hover:bg-accent/50 rounded-xl w-fit xl:w-full transition-colors"
      >
        <div className="text-foreground transition-transform duration-300 group-hover:scale-105">
          <Instagram className="w-7 h-7 block xl:hidden" />
          <span
            className="hidden xl:block text-2xl font-black tracking-tight"
            style={{ fontFamily: 'var(--font-instagram, sans-serif)' }}
          >
            ConnectSphere
          </span>
        </div>
      </Link>

      <nav className="flex-1 flex flex-col gap-2">
        {navItems.map((item, idx) => {
          const profileItem = item.path.startsWith('/profile');
          const isActive = profileItem
            ? pathname.startsWith('/profile')
            : pathname === item.path || (item.path !== '/' && pathname.startsWith(item.path));
          return (
            <Link
              key={idx}
              to={item.path}
              className={cn(
                'flex items-center gap-4 p-3 xl:px-4 xl:py-3.5 rounded-xl transition-all duration-300 group relative overflow-hidden',
                isActive ? 'font-bold text-foreground' : 'text-muted-foreground hover:text-foreground hover:bg-accent/40'
              )}
            >
              {isActive && (
                <span className="absolute inset-0 bg-accent/60 dark:bg-accent/40 rounded-xl -z-10 animate-in fade-in" />
              )}
              <div className={cn('transition-all duration-300 group-hover:scale-110', isActive && 'text-primary scale-110')}>
                {item.icon}
              </div>
              <span className="hidden xl:block text-[16px]">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto flex flex-col gap-2">
        <button
          type="button"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className="flex items-center gap-4 p-3 xl:px-4 xl:py-3 rounded-lg xl:rounded-xl text-foreground hover:bg-accent/50 transition-all duration-200 group w-full"
        >
          <div className="transition-transform duration-300 group-hover:scale-110 text-foreground">
            {theme === 'dark' ? <Sun className="w-6 h-6" /> : <Moon className="w-6 h-6" />}
          </div>
          <span className="hidden xl:block text-[16px]">Switch Appearance</span>
        </button>

        <button
          type="button"
          onClick={onOpenSettings}
          className="flex items-center gap-4 p-3 xl:px-4 xl:py-3 rounded-lg xl:rounded-xl text-foreground hover:bg-accent/50 transition-all duration-200 group w-full"
        >
          <Menu className="w-6 h-6 transition-transform duration-300 group-hover:scale-110" />
          <span className="hidden xl:block text-[16px]">More</span>
        </button>
      </div>
    </aside>
  );
};

export default function AppLayout() {
  const [settingsOpen, setSettingsOpen] = useState(false);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated && !!s.token);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <OpenSettingsContext.Provider value={() => setSettingsOpen(true)}>
      <div className="min-h-screen bg-background text-foreground flex">
        <Sidebar onOpenSettings={() => setSettingsOpen(true)} />
        <main className="flex-1 md:ml-[72px] xl:ml-[244px] w-full max-w-[600px] mx-auto min-h-screen pb-24 md:pb-0 relative border-x border-border/20 lg:border-none transition-all duration-300">
          <Outlet />
        </main>
        <BottomNav />
        <SettingsModal open={settingsOpen} onClose={() => setSettingsOpen(false)} />
      </div>
    </OpenSettingsContext.Provider>
  );
}
