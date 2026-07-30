import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Zap, Loader2, Eye, EyeOff, Check, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import api from '@/lib/api';
import { useToast } from '@/hooks/useToast';

const rules = [
  { key: 'len',     label: '8+ characters',    test: (p: string) => p.length >= 8 },
  { key: 'upper',   label: 'Uppercase letter',  test: (p: string) => /[A-Z]/.test(p) },
  { key: 'lower',   label: 'Lowercase letter',  test: (p: string) => /[a-z]/.test(p) },
  { key: 'number',  label: 'Number',            test: (p: string) => /\d/.test(p) },
  { key: 'special', label: 'Special character', test: (p: string) => /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(p) },
];

export function ResetPasswordPage() {
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { toast } = useToast();

  const token = searchParams.get('token');
  const email = searchParams.get('email') || '';

  const passed = rules.filter((r) => r.test(password));
  const allPassed = passed.length === rules.length;

  if (!token || !email) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-2">
          <p className="text-muted-foreground">Invalid or missing reset link.</p>
          <Link to="/forgot-password" className="text-primary hover:underline block">Request a new one</Link>
        </div>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!allPassed) {
      toast({ title: 'Password does not meet all requirements', variant: 'destructive' });
      return;
    }
    if (password !== confirm) {
      toast({ title: 'Passwords do not match', variant: 'destructive' });
      return;
    }
    setIsLoading(true);
    try {
      await api.post('/auth/reset-password', { email, token, password, confirmPassword: confirm });
      toast({ title: 'Password reset successfully! Please log in.' });
      navigate('/login', { replace: true });
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message || 'Reset failed';
      toast({ title: msg, variant: 'destructive' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-background to-primary/5 p-4">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-2xl font-bold">FlowTime</span>
          </Link>
        </div>

        <div className="bg-card rounded-2xl border border-border shadow-lg p-8">
          <div className="mb-6">
            <h2 className="text-xl font-semibold">Set new password</h2>
            <p className="text-muted-foreground text-sm mt-1">
              Resetting password for <strong>{decodeURIComponent(email)}</strong>
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* New Password */}
            <div className="space-y-2">
              <Label>New Password</Label>
              <div className="relative">
                <Input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  autoComplete="new-password"
                />
                <button type="button" onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>

              {password && (
                <div className="grid grid-cols-2 gap-1 mt-1">
                  {rules.map((r) => {
                    const ok = r.test(password);
                    return (
                      <div key={r.key} className={`flex items-center gap-1 text-xs ${ok ? 'text-green-600 dark:text-green-400' : 'text-muted-foreground'}`}>
                        {ok ? <Check className="w-3 h-3" /> : <X className="w-3 h-3" />}
                        {r.label}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Confirm Password */}
            <div className="space-y-2">
              <Label>Confirm Password</Label>
              <div className="relative">
                <Input
                  type={showConfirm ? 'text' : 'password'}
                  value={confirm}
                  onChange={(e) => setConfirm(e.target.value)}
                  placeholder="••••••••"
                  required
                  autoComplete="new-password"
                  className={confirm && confirm !== password ? 'border-red-400 focus-visible:ring-red-400' : ''}
                />
                <button type="button" onClick={() => setShowConfirm(!showConfirm)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
                  {showConfirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {confirm && confirm !== password && (
                <p className="text-xs text-red-500">Passwords do not match</p>
              )}
            </div>

            <Button type="submit" className="w-full" disabled={isLoading || !allPassed || password !== confirm}>
              {isLoading ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Resetting...</>
              ) : (
                'Reset password'
              )}
            </Button>
          </form>
        </div>
      </motion.div>
    </div>
  );
}
