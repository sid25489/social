import { useEffect, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  ChevronLeft,
  ChevronRight,
  X,
  Bell,
  Lock,
  UserCircle,
  Ban,
  Activity,
  Archive,
  Bookmark,
  Users,
  Shield,
  BadgeCheck,
  Baby,
  Briefcase,
  UserCog,
  Eye,
  HelpCircle,
  Flag,
  LogOut,
  Trash2,
} from 'lucide-react';
import { profileService } from '../../../shared/services/profile.service';
import { useAuthStore } from '../../../store/useAuthStore';
import { useNavigate, Link } from 'react-router-dom';
import type { ProfileDto } from '../../../shared/types/profile';
import { cn } from '../../../shared/utils/cn';

const LS_KEY = 'connectsphere-local-settings';

type LocalSettings = {
  pushNotif: boolean;
  emailNotif: boolean;
  smsNotif: boolean;
  liveNotif: boolean;
  storyReplies: boolean;
  mentionNotif: boolean;
  likeNotif: boolean;
  commentNotif: boolean;
  sensitiveContent: boolean;
};

const defaultLocal: LocalSettings = {
  pushNotif: true,
  emailNotif: true,
  smsNotif: false,
  liveNotif: true,
  storyReplies: true,
  mentionNotif: true,
  likeNotif: true,
  commentNotif: true,
  sensitiveContent: false,
};

function loadLocal(): LocalSettings {
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (!raw) return { ...defaultLocal };
    return { ...defaultLocal, ...JSON.parse(raw) };
  } catch {
    return { ...defaultLocal };
  }
}

function saveLocal(s: LocalSettings) {
  localStorage.setItem(LS_KEY, JSON.stringify(s));
}

type SubView =
  | 'main'
  | 'notifications'
  | 'messages_prefs'
  | 'tags_mentions'
  | 'blocked'
  | 'edit'
  | 'password'
  | 'activity'
  | 'archiving'
  | 'saved'
  | 'close_friends'
  | 'supervision'
  | 'family'
  | 'verified'
  | 'professionals'
  | 'account_tools'
  | 'account_status'
  | 'help'
  | 'report'
  | 'content_prefs';

type RowProps = {
  icon: React.ReactNode;
  label: string;
  onClick?: () => void;
  to?: string;
  danger?: boolean;
};

function InfoPanel({
  title,
  body,
  onBack,
}: {
  title: string;
  body: string;
  onBack: () => void;
}) {
  return (
    <div className="flex flex-col h-full min-h-0">
      <header className="flex items-center gap-3 px-4 py-3 border-b border-border shrink-0">
        <button
          type="button"
          onClick={onBack}
          className="p-2 rounded-lg hover:bg-accent -ml-2"
          aria-label="Back"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>
        <h2 className="font-semibold text-base">{title}</h2>
      </header>
      <p className="p-4 text-sm text-muted-foreground leading-relaxed">{body}</p>
    </div>
  );
}

export default function SettingsModal({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const [sub, setSub] = useState<SubView>('main');
  const [local, setLocal] = useState<LocalSettings>(loadLocal);
  const [reportText, setReportText] = useState('');
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const logout = useAuthStore((s) => s.logout);
  const user = useAuthStore((s) => s.user);
  const updateUser = useAuthStore((s) => s.updateUser);

  const { data: me, isLoading: meLoading } = useQuery({
    queryKey: ['profile', 'me'],
    queryFn: () => profileService.getMe(),
    enabled: open && sub === 'edit',
  });

  const [editForm, setEditForm] = useState({
    display_name: '',
    bio: '',
    avatar_url: '',
    website: '',
    location: '',
  });

  useEffect(() => {
    if (me) {
      setEditForm({
        display_name: me.display_name || '',
        bio: me.bio || '',
        avatar_url: me.avatar_url || '',
        website: me.website || '',
        location: me.location || '',
      });
    }
  }, [me]);

  const updateMutation = useMutation({
    mutationFn: (data: Partial<typeof editForm> & { is_private?: boolean }) =>
      profileService.updateProfile(data),
    onSuccess: (p: ProfileDto) => {
      updateUser({
        displayName: p.display_name || '',
        bio: p.bio || '',
        avatar: p.avatar_url || undefined,
        isPrivate: p.is_private,
      });
      queryClient.invalidateQueries({ queryKey: ['profile'] });
      setSub('main');
    },
  });

  const privateMutation = useMutation({
    mutationFn: (is_private: boolean) => profileService.updateProfile({ is_private }),
    onSuccess: (p: ProfileDto) => {
      updateUser({ isPrivate: p.is_private });
      queryClient.invalidateQueries({ queryKey: ['profile'] });
    },
  });

  const passwordMutation = useMutation({
    mutationFn: ({ old_password, new_password }: { old_password: string; new_password: string }) =>
      profileService.changePassword(old_password, new_password),
    onSuccess: () => {
      setSub('main');
      alert('Password updated successfully.');
    },
  });

  const { data: blocked = [], refetch: refetchBlocked } = useQuery({
    queryKey: ['blocked-accounts'],
    queryFn: () => profileService.getBlockedAccounts(),
    enabled: open && sub === 'blocked',
  });

  const unblockMutation = useMutation({
    mutationFn: (userId: string) => profileService.unblock(userId),
    onSuccess: () => refetchBlocked(),
  });

  useEffect(() => {
    if (!open) {
      setSub('main');
      setReportText('');
    }
  }, [open]);

  useEffect(() => {
    saveLocal(local);
  }, [local]);

  const setLocalField = <K extends keyof LocalSettings>(key: K, value: LocalSettings[K]) => {
    setLocal((prev) => ({ ...prev, [key]: value }));
  };

  const handleLogout = () => {
    logout();
    onClose();
    navigate('/login');
  };

  const Row = ({ icon, label, onClick, to, danger }: RowProps) => {
    const inner = (
      <>
        <span className="text-foreground shrink-0">{icon}</span>
        <span className={cn('flex-1 text-left text-sm', danger && 'text-destructive')}>{label}</span>
        {to ? <ChevronRight className="w-4 h-4 text-muted-foreground" /> : null}
        {!to && onClick ? <ChevronRight className="w-4 h-4 text-muted-foreground" /> : null}
      </>
    );
    const className =
      'flex items-center gap-3 w-full px-4 py-3.5 hover:bg-accent/60 transition-colors text-left border-b border-border/40';
    if (to) {
      return (
        <Link to={to} className={className} onClick={onClose}>
          {inner}
        </Link>
      );
    }
    return (
      <button type="button" className={className} onClick={onClick!}>
        {inner}
      </button>
    );
  };

  const Toggle = ({
    label,
    checked,
    onChange,
  }: {
    label: string;
    checked: boolean;
    onChange: (v: boolean) => void;
  }) => (
    <label className="flex items-center justify-between px-4 py-3.5 border-b border-border/40 gap-4">
      <span className="text-sm">{label}</span>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={cn(
          'w-11 h-6 rounded-full transition-colors relative shrink-0',
          checked ? 'bg-primary' : 'bg-muted'
        )}
      >
        <span
          className={cn(
            'absolute top-1 w-4 h-4 rounded-full bg-background shadow transition-transform',
            checked ? 'left-6' : 'left-1'
          )}
        />
      </button>
    </label>
  );

  if (!open) return null;

  const infoScreens: Partial<Record<SubView, { title: string; body: string }>> = {
    archiving: {
      title: 'Archiving and downloading',
      body:
        'Download a copy of your data or archive posts. Full export is processed on our servers; in this demo, use your account data request flow in production.',
    },
    saved: {
      title: 'Saved',
      body: 'Posts you save appear in the Saved tab on your profile. Open your profile and tap Saved to view them.',
    },
    close_friends: {
      title: 'Close Friends',
      body: 'Share stories and posts with a smaller group. List management will connect to the social graph in a future update.',
    },
    supervision: {
      title: 'Supervision',
      body: 'Parental supervision tools help families support teens using ConnectSphere. Configuration is not enabled in this build.',
    },
    family: {
      title: 'Family Center',
      body: 'Monitor time spent, requests, and safety settings across linked accounts. Coming soon.',
    },
    verified: {
      title: 'Meta Verified',
      body: 'Subscription badges and support are not available in this demo.',
    },
    professionals: {
      title: 'Account type and professional tools',
      body: 'Switch to a professional account to access insights, contact buttons, and promotions when those APIs are enabled.',
    },
    account_tools: {
      title: 'Meta Accounts Center',
      body: 'Central place for accounts, passwords, and security across Meta experiences. Placeholder for this standalone app.',
    },
    account_status: {
      title: 'Account status',
      body:
        'To delete your account permanently, contact support. You can log out below to end this session on this device.',
    },
    help: {
      title: 'Help',
      body: 'Visit the help center for common questions about profiles, privacy, and safety.',
    },
  };

  const info = infoScreens[sub];
  if (info) {
    return (
      <div
        className="fixed inset-0 z-[100] flex items-end md:items-center justify-center bg-black/50 backdrop-blur-sm"
        role="dialog"
        aria-modal="true"
        aria-label="Settings"
      >
        <div
          className="bg-background w-full md:max-w-md md:rounded-2xl border border-border shadow-2xl max-h-[90vh] flex flex-col rounded-t-3xl overflow-hidden animate-in slide-in-from-bottom-4 duration-200"
          onClick={(e) => e.stopPropagation()}
        >
          <InfoPanel title={info.title} body={info.body} onBack={() => setSub('main')} />
          <div className="p-4 border-t border-border">
            <button
              type="button"
              onClick={onClose}
              className="w-full py-3 rounded-xl bg-primary text-primary-foreground font-semibold text-sm"
            >
              Done
            </button>
          </div>
        </div>
        <button type="button" className="absolute inset-0 -z-10" aria-label="Close" onClick={onClose} />
      </div>
    );
  }

  return (
    <div
      className="fixed inset-0 z-[100] flex items-end md:items-center justify-center bg-black/50 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-label="Settings"
      onClick={onClose}
    >
      <div
        className="bg-background w-full md:max-w-md md:rounded-2xl border border-border shadow-2xl max-h-[92vh] flex flex-col rounded-t-3xl overflow-hidden animate-in slide-in-from-bottom-4 duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="flex items-center justify-between px-3 py-2 border-b border-border shrink-0">
          {sub !== 'main' ? (
            <button
              type="button"
              onClick={() => setSub('main')}
              className="p-2 rounded-lg hover:bg-accent"
              aria-label="Back"
            >
              <ChevronLeft className="w-6 h-6" />
            </button>
          ) : (
            <span className="w-10" />
          )}
          <h1 className="font-bold text-base">
            {sub === 'main' && 'Settings'}
            {sub === 'notifications' && 'Notifications'}
            {sub === 'messages_prefs' && 'Messages and story replies'}
            {sub === 'tags_mentions' && 'Tags and mentions'}
            {sub === 'blocked' && 'Blocked accounts'}
            {sub === 'edit' && 'Edit profile'}
            {sub === 'password' && 'Change password'}
            {sub === 'activity' && 'Your activity'}
            {sub === 'content_prefs' && 'Sensitive content'}
            {sub === 'report' && 'Report a problem'}
          </h1>
          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-accent"
            aria-label="Close settings"
          >
            <X className="w-5 h-5" />
          </button>
        </header>

        <div className="flex-1 overflow-y-auto min-h-0">
          {sub === 'main' && (
            <div className="pb-4">
              <p className="px-4 pt-3 pb-2 text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                How you use ConnectSphere
              </p>
              <Row
                icon={<Bell className="w-5 h-5" />}
                label="Notifications"
                onClick={() => setSub('notifications')}
              />
              <Row
                icon={<Activity className="w-5 h-5" />}
                label="Your activity"
                onClick={() => setSub('activity')}
              />
              <Row
                icon={<Archive className="w-5 h-5" />}
                label="Archiving and downloading"
                onClick={() => setSub('archiving')}
              />
              <Row
                icon={<Bookmark className="w-5 h-5" />}
                label="Saved"
                onClick={() => setSub('saved')}
              />
              <Row
                icon={<Users className="w-5 h-5" />}
                label="Close Friends"
                onClick={() => setSub('close_friends')}
              />

              <p className="px-4 pt-4 pb-2 text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                Who can see your content
              </p>
              <Row
                icon={<Ban className="w-5 h-5" />}
                label="Blocked accounts"
                onClick={() => setSub('blocked')}
              />
              <Row
                icon={<Eye className="w-5 h-5" />}
                label="Sensitive content"
                onClick={() => setSub('content_prefs')}
              />

              <p className="px-4 pt-4 pb-2 text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                Account
              </p>
              <Row
                icon={<UserCircle className="w-5 h-5" />}
                label="Edit profile"
                onClick={() => setSub('edit')}
              />
              <Row
                icon={<Lock className="w-5 h-5" />}
                label="Password"
                onClick={() => setSub('password')}
              />
              <div className="px-4 py-3 border-b border-border/40 flex items-center justify-between gap-4">
                <div>
                  <p className="text-sm font-medium">Private account</p>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    Only approved followers see your posts
                  </p>
                </div>
                <button
                  type="button"
                  role="switch"
                  aria-checked={user?.isPrivate ?? false}
                  disabled={privateMutation.isPending}
                  onClick={() => privateMutation.mutate(!(user?.isPrivate ?? false))}
                  className={cn(
                    'w-11 h-6 rounded-full transition-colors relative shrink-0 disabled:opacity-50',
                    user?.isPrivate ? 'bg-primary' : 'bg-muted'
                  )}
                >
                  <span
                    className={cn(
                      'absolute top-1 w-4 h-4 rounded-full bg-background shadow transition-transform',
                      user?.isPrivate ? 'left-6' : 'left-1'
                    )}
                  />
                </button>
              </div>

              <p className="px-4 pt-4 pb-2 text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                For families & professionals
              </p>
              <Row
                icon={<Baby className="w-5 h-5" />}
                label="Supervision"
                onClick={() => setSub('supervision')}
              />
              <Row
                icon={<Shield className="w-5 h-5" />}
                label="Family Center"
                onClick={() => setSub('family')}
              />
              <Row
                icon={<BadgeCheck className="w-5 h-5" />}
                label="Meta Verified"
                onClick={() => setSub('verified')}
              />
              <Row
                icon={<Briefcase className="w-5 h-5" />}
                label="Account type and tools"
                onClick={() => setSub('professionals')}
              />
              <Row
                icon={<UserCog className="w-5 h-5" />}
                label="Accounts Center"
                onClick={() => setSub('account_tools')}
              />

              <p className="px-4 pt-4 pb-2 text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                More
              </p>
              <Row
                icon={<HelpCircle className="w-5 h-5" />}
                label="Help"
                onClick={() => setSub('help')}
              />
              <Row
                icon={<Flag className="w-5 h-5" />}
                label="Report a problem"
                onClick={() => setSub('report')}
              />
              <Row
                icon={<Trash2 className="w-5 h-5" />}
                label="Account status"
                onClick={() => setSub('account_status')}
              />
              <Row
                icon={<LogOut className="w-5 h-5" />}
                label="Log out"
                danger
                onClick={handleLogout}
              />
            </div>
          )}

          {sub === 'notifications' && (
            <div>
              <Toggle
                label="Push notifications"
                checked={local.pushNotif}
                onChange={(v) => setLocalField('pushNotif', v)}
              />
              <Toggle
                label="Email notifications"
                checked={local.emailNotif}
                onChange={(v) => setLocalField('emailNotif', v)}
              />
              <Toggle
                label="SMS notifications"
                checked={local.smsNotif}
                onChange={(v) => setLocalField('smsNotif', v)}
              />
              <Toggle
                label="Live notifications"
                checked={local.liveNotif}
                onChange={(v) => setLocalField('liveNotif', v)}
              />
              <Row
                icon={<span className="w-5" />}
                label="Messages and story replies"
                onClick={() => setSub('messages_prefs')}
              />
              <Row
                icon={<span className="w-5" />}
                label="Tags and mentions"
                onClick={() => setSub('tags_mentions')}
              />
            </div>
          )}

          {sub === 'messages_prefs' && (
            <div>
              <Toggle
                label="Message requests"
                checked={local.storyReplies}
                onChange={(v) => setLocalField('storyReplies', v)}
              />
              <p className="px-4 py-3 text-xs text-muted-foreground">
                Control alerts for message requests and story replies. Preferences are stored on this device.
              </p>
            </div>
          )}

          {sub === 'tags_mentions' && (
            <div>
              <Toggle
                label="Mentions in stories and posts"
                checked={local.mentionNotif}
                onChange={(v) => setLocalField('mentionNotif', v)}
              />
              <Toggle
                label="Likes"
                checked={local.likeNotif}
                onChange={(v) => setLocalField('likeNotif', v)}
              />
              <Toggle
                label="Comments"
                checked={local.commentNotif}
                onChange={(v) => setLocalField('commentNotif', v)}
              />
            </div>
          )}

          {sub === 'content_prefs' && (
            <div>
              <Toggle
                label="Allow sensitive content"
                checked={local.sensitiveContent}
                onChange={(v) => setLocalField('sensitiveContent', v)}
              />
              <p className="px-4 py-3 text-xs text-muted-foreground">
                This preference is saved locally and can drive ranking filters when enabled server-side.
              </p>
            </div>
          )}

          {sub === 'activity' && (
            <div className="p-4 space-y-3">
              <p className="text-sm text-muted-foreground">
                See interactions such as likes, comments, and follows.
              </p>
              <Link
                to="/notifications"
                onClick={onClose}
                className="inline-flex items-center gap-2 text-sm font-semibold text-primary"
              >
                Open notifications
                <ChevronRight className="w-4 h-4" />
              </Link>
            </div>
          )}

          {sub === 'blocked' && (
            <div className="pb-4">
              {blocked.length === 0 ? (
                <p className="p-6 text-center text-sm text-muted-foreground">No blocked accounts.</p>
              ) : (
                blocked.map((u) => (
                  <div
                    key={u.id}
                    className="flex items-center justify-between px-4 py-3 border-b border-border/40"
                  >
                    <span className="text-sm font-medium">@{u.username}</span>
                    <button
                      type="button"
                      className="text-xs font-semibold text-primary"
                      disabled={unblockMutation.isPending}
                      onClick={() => unblockMutation.mutate(u.id)}
                    >
                      Unblock
                    </button>
                  </div>
                ))
              )}
            </div>
          )}

          {sub === 'edit' && meLoading && (
            <div className="flex justify-center py-16">
              <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            </div>
          )}

          {sub === 'edit' && me && !meLoading && (
            <form
              className="p-4 space-y-4"
              onSubmit={(e) => {
                e.preventDefault();
                updateMutation.mutate({
                  display_name: editForm.display_name,
                  bio: editForm.bio,
                  avatar_url: editForm.avatar_url || undefined,
                  website: editForm.website || undefined,
                  location: editForm.location || undefined,
                });
              }}
            >
              <div className="space-y-1">
                <label className="text-xs font-semibold text-muted-foreground">Display name</label>
                <input
                  className="w-full rounded-xl border border-input bg-accent/30 px-3 py-2 text-sm"
                  value={editForm.display_name}
                  onChange={(e) => setEditForm((f) => ({ ...f, display_name: e.target.value }))}
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-semibold text-muted-foreground">Bio</label>
                <textarea
                  className="w-full rounded-xl border border-input bg-accent/30 px-3 py-2 text-sm min-h-[80px]"
                  value={editForm.bio}
                  onChange={(e) => setEditForm((f) => ({ ...f, bio: e.target.value }))}
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-semibold text-muted-foreground">Avatar URL</label>
                <input
                  className="w-full rounded-xl border border-input bg-accent/30 px-3 py-2 text-sm"
                  value={editForm.avatar_url}
                  onChange={(e) => setEditForm((f) => ({ ...f, avatar_url: e.target.value }))}
                  placeholder="https://..."
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-semibold text-muted-foreground">Website</label>
                <input
                  className="w-full rounded-xl border border-input bg-accent/30 px-3 py-2 text-sm"
                  value={editForm.website}
                  onChange={(e) => setEditForm((f) => ({ ...f, website: e.target.value }))}
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-semibold text-muted-foreground">Location</label>
                <input
                  className="w-full rounded-xl border border-input bg-accent/30 px-3 py-2 text-sm"
                  value={editForm.location}
                  onChange={(e) => setEditForm((f) => ({ ...f, location: e.target.value }))}
                />
              </div>
              {updateMutation.isError && (
                <p className="text-sm text-destructive">Could not save profile. Check your input.</p>
              )}
              <button
                type="submit"
                disabled={updateMutation.isPending}
                className="w-full py-3 rounded-xl bg-primary text-primary-foreground font-semibold text-sm disabled:opacity-60"
              >
                {updateMutation.isPending ? 'Saving…' : 'Submit'}
              </button>
            </form>
          )}

          {sub === 'password' && (
            <PasswordForm
              onCancel={() => setSub('main')}
              onSubmit={(old_password, new_password) => passwordMutation.mutate({ old_password, new_password })}
              isPending={passwordMutation.isPending}
              error={passwordMutation.error as Error | null}
            />
          )}

          {sub === 'report' && (
            <div className="p-4 space-y-3">
              <textarea
                className="w-full rounded-xl border border-input bg-accent/30 px-3 py-2 text-sm min-h-[120px]"
                placeholder="Describe what went wrong…"
                value={reportText}
                onChange={(e) => setReportText(e.target.value)}
              />
              <button
                type="button"
                className="w-full py-3 rounded-xl bg-primary text-primary-foreground font-semibold text-sm"
                onClick={() => {
                  alert('Thanks — your report was recorded locally for this demo.');
                  setReportText('');
                  setSub('main');
                }}
              >
                Send report
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function PasswordForm({
  onCancel,
  onSubmit,
  isPending,
  error,
}: {
  onCancel: () => void;
  onSubmit: (oldP: string, newP: string) => void;
  isPending: boolean;
  error: Error | null;
}) {
  const [old_password, setOld] = useState('');
  const [new_password, setNew] = useState('');
  const [confirm, setConfirm] = useState('');

  return (
    <form
      className="p-4 space-y-4"
      onSubmit={(e) => {
        e.preventDefault();
        if (new_password !== confirm) {
          alert('New passwords do not match.');
          return;
        }
        onSubmit(old_password, new_password);
      }}
    >
      <div className="space-y-1">
        <label className="text-xs font-semibold text-muted-foreground">Current password</label>
        <input
          type="password"
          className="w-full rounded-xl border border-input bg-accent/30 px-3 py-2 text-sm"
          value={old_password}
          onChange={(e) => setOld(e.target.value)}
          autoComplete="current-password"
        />
      </div>
      <div className="space-y-1">
        <label className="text-xs font-semibold text-muted-foreground">New password</label>
        <input
          type="password"
          className="w-full rounded-xl border border-input bg-accent/30 px-3 py-2 text-sm"
          value={new_password}
          onChange={(e) => setNew(e.target.value)}
          autoComplete="new-password"
        />
      </div>
      <div className="space-y-1">
        <label className="text-xs font-semibold text-muted-foreground">Confirm new password</label>
        <input
          type="password"
          className="w-full rounded-xl border border-input bg-accent/30 px-3 py-2 text-sm"
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
          autoComplete="new-password"
        />
      </div>
      {error && <p className="text-sm text-destructive">Could not update password.</p>}
      <div className="flex gap-2">
        <button
          type="button"
          onClick={onCancel}
          className="flex-1 py-3 rounded-xl border border-border font-semibold text-sm"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isPending}
          className="flex-1 py-3 rounded-xl bg-primary text-primary-foreground font-semibold text-sm disabled:opacity-60"
        >
          {isPending ? '…' : 'Update'}
        </button>
      </div>
    </form>
  );
}
