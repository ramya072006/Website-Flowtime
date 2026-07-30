import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Zap, Loader2, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import api from '@/lib/api';
import { useAuthStore } from '@/stores/authStore';
import { useToast } from '@/hooks/useToast';

export function VerifyOtpPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  const { setSession } = useAuthStore();

  // Email is passed via router state after registration
  const email: string = (location.state as { email?: string })?.email || '';

  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [isLoading, setIsLoading] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [countdown, setCountdown] = useState(60);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  // Redirect if no email in state
  useEffect(() => {
    if (!email) navigate('/register', { replace: true });
  }, [email, navigate]);

  // Countdown for resend button
  useEffect(() => {
    if (countdown <= 0) return;
    const t = setTimeout(() => setCountdown((c) => c - 1), 1000);
    return () => clearTimeout(t);
  }, [countdown]);

  const handleChange = (index: number, value: string) => {
    if (!/^\d*$/.test(value)) return; // digits only
    const next = [...otp];
    next[index] = value.slice(-1);
    setOtp(next);
    if (value && index < 5) inputRefs.current[index + 1]?.focus();
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
    if (pasted.length === 6) {
      setOtp(pasted.split(''));
      inputRefs.current[5]?.focus();
    }
    e.preventDefault();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const code = otp.join('');
    if (code.length !== 6) {
      toast({ title: 'Please enter the complete 6-digit code', variant: 'destructive' });
      return;
    }
    setIsLoading(true);
    try {
      const res = await api.post('/auth/verify-otp', { email, otp: code });
      const { user, tokens } = res.data.data;
      // Store session in auth store and go to dashboard
      setSession(user, tokens.accessToken, tokens.refreshToken);
      toast({ title: 'Email verified! Welcome to FlowTime 🎉' });
      navigate('/dashboard', { replace: true });
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message || 'Invalid code';
      toast({ title: msg, variant: 'destructive' });
      setOtp(['', '', '', '', '', '']);
      inputRefs.current[0]?.focus();
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    setIsResending(true);
    try {
      await api.post('/auth/resend-otp', { email });
      setCountdown(60);
      toast({ title: 'A new code has been sent to your email' });
    } catch {
      toast({ title: 'Failed to resend code. Please try again.', variant: 'destructive' });
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-background to-primary/5 p-4">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md">

        {/* Logo */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-2xl font-bold">FlowTime</span>
          </Link>
        </div>

        <div className="bg-card rounded-2xl border border-border shadow-lg p-8">
          <div className="text-center mb-6">
            <div className="w-14 h-14 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-3">
              <span className="text-2xl">📧</span>
            </div>
            <h2 className="text-xl font-semibold">Check your email</h2>
            <p className="text-muted-foreground text-sm mt-1">
              We sent a 6-digit code to <strong>{email}</strong>
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* OTP inputs */}
            <div className="flex justify-center gap-3">
              {otp.map((digit, i) => (
                <Input
                  key={i}
                  ref={(el) => { inputRefs.current[i] = el; }}
                  type="text"
                  inputMode="numeric"
                  maxLength={1}
                  value={digit}
                  onChange={(e) => handleChange(i, e.target.value)}
                  onKeyDown={(e) => handleKeyDown(i, e)}
                  onPaste={i === 0 ? handlePaste : undefined}
                  className="w-12 h-14 text-center text-xl font-bold"
                  autoFocus={i === 0}
                  autoComplete="one-time-code"
                />
              ))}
            </div>

            <Button type="submit" className="w-full" disabled={isLoading || otp.join('').length !== 6}>
              {isLoading ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Verifying...</>
              ) : (
                'Verify email'
              )}
            </Button>
          </form>

          <div className="mt-4 text-center">
            {countdown > 0 ? (
              <p className="text-sm text-muted-foreground">
                Resend code in <span className="font-medium text-foreground">{countdown}s</span>
              </p>
            ) : (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleResend}
                disabled={isResending}
                className="text-primary"
              >
                {isResending ? (
                  <><Loader2 className="w-3 h-3 mr-1 animate-spin" /> Sending...</>
                ) : (
                  <><RefreshCw className="w-3 h-3 mr-1" /> Resend code</>
                )}
              </Button>
            )}
          </div>

          <p className="text-center text-xs text-muted-foreground mt-4">
            Wrong email?{' '}
            <Link to="/register" className="text-primary hover:underline">Go back</Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
