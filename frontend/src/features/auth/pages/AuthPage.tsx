import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAuthStore } from '../../../store/useAuthStore';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

const loginSchema = z.object({
  username: z.string().min(3, "Username must be at least 3 characters").max(30),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const { setAuth } = useAuthStore();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormValues) => {
    // Implement API call logic here
    console.log(data);
    
    // Simulate API Auth Request
    await new Promise((resolve) => setTimeout(resolve, 800));

    // For demonstration
    setAuth({
      id: '1',
      username: data.username,
      followersCount: 1540,
      followingCount: 420
    }, 'mock-jwt-token-123.abcd.efghi');

    navigate('/');
  };

  const toggleMode = () => {
    setIsLogin((prev) => !prev);
    reset();
  };

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
            {isLogin ? "Welcome back!" : "Join the sphere today."}
          </p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-semibold text-foreground">Username</label>
            <input
              {...register('username')}
              type="text"
              placeholder="Enter your username"
              className="w-full bg-accent/30 border border-input rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
            />
            {errors.username && (
              <p className="text-destructive text-sm font-medium">{errors.username.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <label className="text-sm font-semibold text-foreground">Password</label>
            <input
              {...register('password')}
              type="password"
              placeholder="Enter your password"
              className="w-full bg-accent/30 border border-input rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
            />
            {errors.password && (
              <p className="text-destructive text-sm font-medium">{errors.password.message}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-primary text-primary-foreground font-semibold py-3 rounded-xl shadow-lg shadow-primary/30 hover:shadow-primary/50 hover:bg-primary/90 transition-all disabled:opacity-70 disabled:pointer-events-none active:scale-[0.98] relative overflow-hidden group"
          >
            <span className={isSubmitting ? "opacity-0" : "opacity-100"}>
              {isLogin ? 'Sign In' : 'Create Account'}
            </span>
            {isSubmitting && (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-5 h-5 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
              </div>
            )}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-muted-foreground font-medium">
          {isLogin ? "Don't have an account?" : "Already have an account?"}{" "}
          <button 
            type="button" 
            onClick={toggleMode}
            className="text-primary font-semibold hover:underline"
          >
            {isLogin ? 'Sign up' : 'Log in'}
          </button>
        </div>
      </motion.div>
    </div>
  );
}
