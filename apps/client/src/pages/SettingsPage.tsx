import { useState } from 'react';
import { motion } from 'framer-motion';
import { User, Bell, Brain, Shield, Palette, Eye, EyeOff, Loader2, Check } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { useAuthStore } from '@/stores/authStore';
import { useUIStore } from '@/stores/uiStore';
import api from '@/lib/api';
import { useToast } from '@/hooks/useToast';

const tabs = [
  { id: 'profile',       label: 'Profile',       icon: User    },
  { id: 'notifications', label: 'Notifications',  icon: Bell    },
  { id: 'ai',            label: 'AI Settings',    icon: Brain   },
  { id: 'appearance',    label: 'Appearance',     icon: Palette },
  { id: 'security',      label: 'Security',       icon: Shield  },
];

// ── Reusable toggle row ───────────────────────────────────────────────────────
function ToggleRow({
  label, desc, checked, onChange, disabled,
}: {
  label: string; desc?: string; checked: boolean;
  onChange: (v: boolean) => void; disabled?: boolean;
}) {
  return (
    <div className="flex items-center justify-between p-3 rounded-lg bg-muted/30">
      <div>
        <p className="text-sm font-medium">{label}</p>
        {desc && <p className="text-xs text-muted-foreground">{desc}</p>}
      </div>
      <Switch checked={checked} onCheckedChange={onChange} disabled={disabled} />
    </div>
  );
}

// ── Change Password Modal ─────────────────────────────────────────────────────
function ChangePasswordForm({ onDone }: { onDone: () => void }) {
  const { toast } = useToast();
  const [current, setCurrent]   = useState('');
  const [newPwd, setNewPwd]     = useState('');
  const [confirm, setConfirm]   = useState('');
  const [showCur, setShowCur]   = useState(false);
  const [showNew, setShowNew]   = useState(false);
  const [saving, setSaving]     = useState(false);

  const rules = [
    { label: '8+ characters',    ok: newPwd.length >= 8 },
    { label: 'Uppercase',        ok: /[A-Z]/.test(newPwd) },
    { label: 'Lowercase',        ok: /[a-z]/.test(newPwd) },
    { label: 'Number',           ok: /\d/.test(newPwd) },
    { label: 'Special character', ok: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(newPwd) },
  ];
  const allOk = rules.every(r => r.ok) && newPwd === confirm;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!allOk) return;
    setSaving(true);
    try {
      await api.patch('/auth/change-password', {
        currentPassword: current,
        newPassword: newPwd,
        confirmPassword: confirm,
      });
      toast({ title: 'Password changed successfully' });
      onDone();
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message || 'Failed to change password';
      toast({ title: msg, variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 mt-3">
      <div className="space-y-2">
        <Label>Current Password</Label>
        <div className="relative">
          <Input type={showCur ? 'text' : 'password'} value={current}
            onChange={e => setCurrent(e.target.value)} placeholder="••••••••" required />
          <button type="button" onClick={() => setShowCur(v => !v)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">
            {showCur ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>
      </div>
      <div className="space-y-2">
        <Label>New Password</Label>
        <div className="relative">
          <Input type={showNew ? 'text' : 'password'} value={newPwd}
            onChange={e => setNewPwd(e.target.value)} placeholder="••••••••" required />
          <button type="button" onClick={() => setShowNew(v => !v)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">
            {showNew ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>
        {newPwd && (
          <div className="grid grid-cols-2 gap-1">
            {rules.map(r => (
              <div key={r.label} className={`flex items-center gap-1 text-xs ${r.ok ? 'text-green-600' : 'text-muted-foreground'}`}>
                <Check className="w-3 h-3" /> {r.label}
              </div>
            ))}
          </div>
        )}
      </div>
      <div className="space-y-2">
        <Label>Confirm New Password</Label>
        <Input type="password" value={confirm} onChange={e => setConfirm(e.target.value)}
          placeholder="••••••••" required
          className={confirm && confirm !== newPwd ? 'border-red-400' : ''} />
        {confirm && confirm !== newPwd && <p className="text-xs text-red-500">Passwords do not match</p>}
      </div>
      <div className="flex gap-2">
        <Button type="submit" disabled={saving || !allOk}>
          {saving ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Saving...</> : 'Update Password'}
        </Button>
        <Button type="button" variant="outline" onClick={onDone}>Cancel</Button>
      </div>
    </form>
  );
}

// ── Main Settings Page ────────────────────────────────────────────────────────
export function SettingsPage() {
  const [activeTab, setActiveTab] = useState('profile');
  const { user, updateUser } = useAuthStore();
  const { theme, setTheme } = useUIStore();
  const { toast } = useToast();

  // Profile state
  const [name, setName]         = useState(user?.name || '');
  const [timezone, setTimezone] = useState(user?.timezone || 'UTC');
  const [isSaving, setIsSaving] = useState(false);

  // Security state
  const [showPasswordForm, setShowPasswordForm] = useState(false);

  // ── Save profile ──────────────────────────────────────────────────────────
  const handleSaveProfile = async () => {
    setIsSaving(true);
    try {
      const res = await api.patch('/auth/profile', { name, timezone });
      updateUser(res.data.data);
      toast({ title: 'Profile updated' });
    } catch {
      toast({ title: 'Failed to update profile', variant: 'destructive' });
    } finally {
      setIsSaving(false);
    }
  };

  // ── Toggle notification setting ───────────────────────────────────────────
  const handleNotifToggle = async (key: string, value: boolean) => {
    const updated = {
      notificationSettings: {
        email: true, push: true, inApp: true,
        reminderMinutes: [15, 60], deadlineAlerts: true, aiSuggestions: true,
        ...user?.notificationSettings,
        [key]: value,
      },
    };
    updateUser(updated);
    try {
      const res = await api.patch('/auth/profile', updated);
      updateUser(res.data.data);
    } catch {
      updateUser({
        notificationSettings: {
          email: true, push: true, inApp: true,
          reminderMinutes: [15, 60], deadlineAlerts: true, aiSuggestions: true,
          ...user?.notificationSettings,
          [key]: !value,
        },
      });
      toast({ title: 'Failed to save setting', variant: 'destructive' });
    }
  };

  // ── Toggle AI setting ─────────────────────────────────────────────────────
  const handleAiToggle = async (key: string, value: boolean) => {
    const updated = {
      aiSettings: {
        autoSchedule: true, autoReschedule: true,
        learningEnabled: true, suggestionFrequency: 'medium',
        ...user?.aiSettings,
        [key]: value,
      },
    };
    updateUser(updated);
    try {
      const res = await api.patch('/auth/profile', updated);
      updateUser(res.data.data);
    } catch {
      updateUser({
        aiSettings: {
          autoSchedule: true, autoReschedule: true,
          learningEnabled: true, suggestionFrequency: 'medium',
          ...user?.aiSettings,
          [key]: !value,
        },
      });
      toast({ title: 'Failed to save setting', variant: 'destructive' });
    }
  };

  const ns = user?.notificationSettings;
  const ai = user?.aiSettings;

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-4xl">
      <h2 className="text-xl font-semibold mb-6">Settings</h2>

      <div className="flex gap-6">
        {/* Sidebar */}
        <div className="w-48 flex-shrink-0">
          <nav className="space-y-1">
            {tabs.map((tab) => (
              <button key={tab.id} onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                }`}>
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1 space-y-4">

          {/* ── PROFILE ── */}
          {activeTab === 'profile' && (
            <Card>
              <CardHeader><CardTitle>Profile Settings</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Full Name</Label>
                  <Input value={name} onChange={e => setName(e.target.value)} />
                </div>
                <div className="space-y-2">
                  <Label>Email</Label>
                  <Input value={user?.email || ''} disabled className="opacity-60" />
                  <p className="text-xs text-muted-foreground">Email cannot be changed</p>
                </div>
                <div className="space-y-2">
                  <Label>Timezone</Label>
                  <select value={timezone} onChange={e => setTimezone(e.target.value)}
                    className="w-full px-3 py-2 rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring">
                    {['UTC','America/New_York','America/Chicago','America/Denver','America/Los_Angeles',
                      'Europe/London','Europe/Paris','Asia/Kolkata','Asia/Tokyo','Asia/Shanghai','Australia/Sydney'].map(tz => (
                      <option key={tz} value={tz}>{tz}</option>
                    ))}
                  </select>
                </div>
                <Button onClick={handleSaveProfile} disabled={isSaving}>
                  {isSaving ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Saving...</> : 'Save Changes'}
                </Button>
              </CardContent>
            </Card>
          )}

          {/* ── NOTIFICATIONS ── */}
          {activeTab === 'notifications' && (
            <Card>
              <CardHeader><CardTitle>Notification Preferences</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                <ToggleRow label="Email notifications"  checked={!!ns?.email}          onChange={v => handleNotifToggle('email', v)} />
                <ToggleRow label="Push notifications"   checked={!!ns?.push}           onChange={v => handleNotifToggle('push', v)} />
                <ToggleRow label="In-app notifications" checked={!!ns?.inApp}          onChange={v => handleNotifToggle('inApp', v)} />
                <ToggleRow label="Deadline alerts"      checked={!!ns?.deadlineAlerts} onChange={v => handleNotifToggle('deadlineAlerts', v)} />
                <ToggleRow label="AI suggestions"       checked={!!ns?.aiSuggestions}  onChange={v => handleNotifToggle('aiSuggestions', v)} />
              </CardContent>
            </Card>
          )}

          {/* ── AI SETTINGS ── */}
          {activeTab === 'ai' && (
            <Card>
              <CardHeader><CardTitle>AI Settings</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                <ToggleRow
                  label="Auto-schedule tasks"
                  desc="Let AI automatically schedule pending tasks"
                  checked={!!ai?.autoSchedule}
                  onChange={v => handleAiToggle('autoSchedule', v)}
                />
                <ToggleRow
                  label="Auto-reschedule"
                  desc="Automatically reschedule missed tasks"
                  checked={!!ai?.autoReschedule}
                  onChange={v => handleAiToggle('autoReschedule', v)}
                />
                <ToggleRow
                  label="Learning mode"
                  desc="AI learns from your scheduling patterns"
                  checked={!!ai?.learningEnabled}
                  onChange={v => handleAiToggle('learningEnabled', v)}
                />
                <div className="space-y-2 pt-2">
                  <Label>Suggestion Frequency</Label>
                  <select
                    value={ai?.suggestionFrequency || 'medium'}
                    onChange={async e => {
                      const updated = {
                        aiSettings: {
                          autoSchedule: true, autoReschedule: true,
                          learningEnabled: true, suggestionFrequency: 'medium',
                          ...ai,
                          suggestionFrequency: e.target.value,
                        },
                      };
                      updateUser(updated);
                      try {
                        const res = await api.patch('/auth/profile', updated);
                        updateUser(res.data.data);
                      } catch {
                        toast({ title: 'Failed to save', variant: 'destructive' });
                      }
                    }}
                    className="w-full px-3 py-2 rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring">
                    <option value="low">Low — Weekly summaries</option>
                    <option value="medium">Medium — Daily suggestions</option>
                    <option value="high">High — Real-time suggestions</option>
                  </select>
                </div>
              </CardContent>
            </Card>
          )}

          {/* ── APPEARANCE ── */}
          {activeTab === 'appearance' && (
            <Card>
              <CardHeader><CardTitle>Appearance</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label className="mb-3 block">Theme</Label>
                  <div className="grid grid-cols-3 gap-3">
                    {(['light', 'dark', 'system'] as const).map(t => (
                      <button key={t} onClick={() => setTheme(t)}
                        className={`p-4 rounded-xl border-2 transition-colors capitalize text-sm font-medium ${
                          theme === t ? 'border-primary bg-primary/5' : 'border-border hover:border-muted-foreground'
                        }`}>
                        {t === 'light' ? '☀️' : t === 'dark' ? '🌙' : '💻'} {t}
                      </button>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* ── SECURITY ── */}
          {activeTab === 'security' && (
            <Card>
              <CardHeader><CardTitle>Security</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <div className="p-4 rounded-lg bg-muted/30">
                  <p className="text-sm font-medium mb-1">Change Password</p>
                  <p className="text-xs text-muted-foreground mb-3">
                    Update your password to keep your account secure
                  </p>
                  {showPasswordForm ? (
                    <ChangePasswordForm onDone={() => setShowPasswordForm(false)} />
                  ) : (
                    <Button variant="outline" size="sm" onClick={() => setShowPasswordForm(true)}>
                      Change Password
                    </Button>
                  )}
                </div>
                <div className="p-4 rounded-lg bg-muted/30">
                  <p className="text-sm font-medium mb-1">Account Status</p>
                  <div className="flex items-center gap-2 mt-2">
                    <div className="w-2 h-2 rounded-full bg-green-500" />
                    <p className="text-sm text-muted-foreground">
                      Email verified · Account active
                    </p>
                  </div>
                </div>
                <div className="p-4 rounded-lg bg-muted/30">
                  <p className="text-sm font-medium mb-1">Active Sessions</p>
                  <p className="text-xs text-muted-foreground mb-3">
                    Sign out from all devices except this one
                  </p>
                  <Button variant="outline" size="sm" className="text-destructive border-destructive hover:bg-destructive/10"
                    onClick={async () => {
                      try {
                        await api.post('/auth/logout', {});
                        toast({ title: 'All other sessions signed out' });
                      } catch {
                        toast({ title: 'Failed to sign out sessions', variant: 'destructive' });
                      }
                    }}>
                    Sign Out All Devices
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

        </div>
      </div>
    </motion.div>
  );
}
