import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate, Navigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import axios from 'axios';
import { authService } from '../../../shared/services/auth.service';
import { useAuthStore } from '../../../store/useAuthStore';

const loginSchema = z.object({
  username: z.string().min(1, 'Username is required').max(150),
  password: z.string().min(1, 'Password is required'),
});

const signupSchema = z
  .object({
    email: z.string().email('Enter a valid email'),
    username: z.string().min(3, 'At least 3 characters').max(150),
    password: z.string().min(8, 'At least 8 characters'),
    password2: z.string().min(8, 'Confirm your password'),
  })
  .refine((d) => d.password === d.password2, {
    message: "Passwords don't match",
    path: ['password2'],
  });

type LoginValues = z.infer<typeof loginSchema>;
type SignupValues = z.infer<typeof signupSchema>;

function formatApiError(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const data = err.response?.data;
    if (typeof data === 'string') return data;
    if (data && typeof data === 'object') {
      if ('detail' in data && typeof (data as { detail: unknown }).detail === 'string') {
        return (data as { detail: string }).detail;
      }
      const parts: string[] = [];
      for (const [, v] of Object.entries(data as Record<string, unknown>)) {
        if (Array.isArray(v)) parts.push(v.join(' '));
        else if (typeof v === 'string') parts.push(v);
      }
      if (parts.length) return parts.join(' ');
    }
    return err.message || 'Request failed';
  }
  return 'Something went wrong';
}

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [formError, setFormError] = useState<string | null>(null);
  const navigate = useNavigate();
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated && !!s.token);

  const loginForm = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { username: '', password: '' },
  });

  const signupForm = useForm<SignupValues>({
    resolver: zodResolver(signupSchema),
    defaultValues: { email: '', username: '', password: '', password2: '' },
  });

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const toggleMode = () => {
    setIsLogin((v) => !v);
    setFormError(null);
    loginForm.reset();
    signupForm.reset();
  };

  const onLogin = loginForm.handleSubmit(async (data) => {
    setFormError(null);
    try {
      await authService.login(data.username, data.password);
      navigate('/');
    } catch (e) {
      setFormError(formatApiError(e));
    }
  });

  const onSignup = signupForm.handleSubmit(async (data) => {
    setFormError(null);
    try {
      await authService.register({
        email: data.email,
        username: data.username,
        password: data.password,
        password2: data.password2,
      });
      navigate('/');
    } catch (e) {
      setFormError(formatApiError(e));
    }
  });

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4 selection:bg-primary/30">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="w-full max-w-md bg-card border border-border rounded-3xl p-8 shadow-xl"
      >
        <div className="text-center mb-8">
          <h1 className="text-3xl font-black bg-gradient-to-r from-primary to-accent-foreground bg-clip-text text-transparent">
            ConnectSphere
          </h1>
          <p className="text-muted-foreground mt-2 font-medium">
            {isLogin ? 'Welcome back!' : 'Create an account'}
          </p>
        </div>

        {formError && (
          <div
            role="alert"
            className="mb-4 rounded-xl border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive"
          >
            {formError}
          </div>
        )}

        {isLogin ? (
          <form onSubmit={onLogin} className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-semibold text-foreground">Username</label>
              <input
                {...loginForm.register('username')}
                type="text"
                autoComplete="username"
                className="w-full bg-accent/30 border border-input rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
              />
              {loginForm.formState.errors.username && (
                <p className="text-destructive text-sm font-medium">
                  {loginForm.formState.errors.username.message}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold text-foreground">Password</label>
              <input
                {...loginForm.register('password')}
                type="password"
                autoComplete="current-password"
                className="w-full bg-accent/30 border border-input rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
              />
              {loginForm.formState.errors.password && (
                <p className="text-destructive text-sm font-medium">
                  {loginForm.formState.errors.password.message}
                </p>
              )}
            </div>
            <SubmitButton pending={loginForm.formState.isSubmitting} label="Sign In" />
          </form>
        ) : (
          <form onSubmit={onSignup} className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-semibold text-foreground">Email</label>
              <input
                {...signupForm.register('email')}
                type="email"
                autoComplete="email"
                className="w-full bg-accent/30 border border-input rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
              />
              {signupForm.formState.errors.email && (
                <p className="text-destructive text-sm font-medium">
                  {signupForm.formState.errors.email.message}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold text-foreground">Username</label>
              <input
                {...signupForm.register('username')}
                type="text"
                autoComplete="username"
                className="w-full bg-accent/30 border border-input rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
              />
              {signupForm.formState.errors.username && (
                <p className="text-destructive text-sm font-medium">
                  {signupForm.formState.errors.username.message}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold text-foreground">Password</label>
              <input
                {...signupForm.register('password')}
                type="password"
                autoComplete="new-password"
                className="w-full bg-accent/30 border border-input rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
              />
              {signupForm.formState.errors.password && (
                <p className="text-destructive text-sm font-medium">
                  {signupForm.formState.errors.password.message}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold text-foreground">Confirm password</label>
              <input
                {...signupForm.register('password2')}
                type="password"
                autoComplete="new-password"
                className="w-full bg-accent/30 border border-input rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
              />
              {signupForm.formState.errors.password2 && (
                <p className="text-destructive text-sm font-medium">
                  {signupForm.formState.errors.password2.message}
                </p>
              )}
            </div>
            <SubmitButton pending={signupForm.formState.isSubmitting} label="Create account" />
          </form>
        )}

        <div className="mt-6 text-center text-sm text-muted-foreground font-medium">
          {isLogin ? "Don't have an account? " : 'Already have an account? '}
          <button type="button" onClick={toggleMode} className="text-primary font-semibold hover:underline">
            {isLogin ? 'Sign up' : 'Log in'}
          </button>
        </div>
      </motion.div>
    </div>
  );
}

function SubmitButton({ pending, label }: { pending: boolean; label: string }) {
  return (
    <button
      type="submit"
      disabled={pending}
      className="w-full bg-primary text-primary-foreground font-semibold py-3 rounded-xl shadow-lg shadow-primary/30 hover:shadow-primary/50 hover:bg-primary/90 transition-all disabled:opacity-70 disabled:pointer-events-none active:scale-[0.98] relative overflow-hidden group"
    >
      <span className={pending ? 'opacity-0' : 'opacity-100'}>{label}</span>
      {pending && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-5 h-5 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
        </div>
      )}
    </button>
  );
}
