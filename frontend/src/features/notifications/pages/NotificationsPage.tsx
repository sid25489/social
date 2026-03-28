import { Heart, UserPlus, MessageCircle } from 'lucide-react';

export default function NotificationsPage() {
  const notifications = [
    { type: 'like', text: 'liked your post.', time: '2h', icon: <Heart className="text-destructive fill-destructive w-5 h-5"/> },
    { type: 'follow', text: 'started following you.', time: '5h', icon: <UserPlus className="text-primary w-5 h-5"/> },
    { type: 'comment', text: 'commented: "This is fire 🔥"', time: '1d', icon: <MessageCircle className="text-muted-foreground w-5 h-5"/> },
  ];

  return (
    <div className="p-4 md:p-8">
      <h1 className="text-2xl font-bold mb-6">Notifications</h1>
      <div className="space-y-4">
        {notifications.map((n, i) => (
          <div key={i} className="flex items-center gap-4 p-3 hover:bg-accent/50 rounded-xl cursor-pointer transition-colors">
            <div className="p-2 bg-accent rounded-full">
              {n.icon}
            </div>
            <div className="flex-1 text-[15px]">
              <span className="font-bold mr-1">user_{i}</span>
              <span className="text-muted-foreground text-[15px]">{n.text}</span>
            </div>
            <span className="text-xs text-muted-foreground whitespace-nowrap">{n.time}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
