import { Outlet, useLocation } from 'react-router-dom';
import { useEffect } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { AIAssistantPanel } from '@/components/ai/AIAssistantPanel';
import { CommandPalette } from '@/components/common/CommandPalette';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';
import { useUIStore } from '@/stores/uiStore';
import { Toaster } from '@/components/ui/toaster';
import { useAuthStore } from '@/stores/authStore';
import { useNotificationStore } from '@/stores/notificationStore';
import { useSocket } from '@/hooks/useSocket';
import { useToast } from '@/hooks/useToast';

const pageTitles: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/calendar': 'Calendar',
  '/tasks': 'Tasks',
  '/habits': 'Habits',
  '/analytics': 'Analytics',
  '/focus': 'Focus Mode',
  '/team': 'Team',
  '/notifications': 'Notifications',
  '/settings': 'Settings',
  '/ai': 'AI Assistant',
};

// ── Listens for real-time socket notifications and shows toast popups ─────────
function NotificationListener() {
  const socket = useSocket();
  const { addNotification, fetchUnreadCount } = useNotificationStore();
  const { toast } = useToast();

  useEffect(() => {
    if (!socket) return;

    const handleNew = (notification: {
      _id: string; type: string; title: string;
      message: string; read: boolean; createdAt: string; actionUrl?: string;
    }) => {
      // Add to store
      addNotification(notification);
      fetchUnreadCount();

      // Show toast popup
      toast({
        title: notification.title,
        description: notification.message,
        duration: 5000,
      });

      // Browser notification if permitted
      if ('Notification' in window && window.Notification.permission === 'granted') {
        new window.Notification(notification.title, {
          body: notification.message,
          icon: '/favicon.svg',
        });
      }
    };

    socket.on('notification:new', handleNew);
    return () => { socket.off('notification:new', handleNew); };
  }, [socket, addNotification, fetchUnreadCount, toast]);

  return null;
}

export function AppLayout() {
  const location = useLocation();
  const { theme, aiPanelOpen, commandPaletteOpen, sidebarOpen, setSidebarOpen, toggleCommandPalette, toggleAIPanel } = useUIStore();
  const { fetchMe } = useAuthStore();

  const title = pageTitles[location.pathname] ||
    Object.entries(pageTitles).find(([path]) => location.pathname.startsWith(path))?.[1] || '';

  useEffect(() => {
    fetchMe();
  }, [fetchMe]);

  // Global keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd/Ctrl + K → Command palette
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        toggleCommandPalette();
      }
      // Cmd/Ctrl + / → AI panel
      if ((e.metaKey || e.ctrlKey) && e.key === '/') {
        e.preventDefault();
        toggleAIPanel();
      }
      // Escape → close panels
      if (e.key === 'Escape') {
        if (commandPaletteOpen) toggleCommandPalette();
        else if (aiPanelOpen) toggleAIPanel();
        else if (sidebarOpen) setSidebarOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [commandPaletteOpen, aiPanelOpen, sidebarOpen, toggleCommandPalette, toggleAIPanel, setSidebarOpen]);

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else if (theme === 'light') {
      root.classList.remove('dark');
    } else {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.classList.toggle('dark', prefersDark);
    }
  }, [theme]);

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <NotificationListener />

      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header title={title} />

        <main className="flex-1 overflow-y-auto">
          <div className="p-6">
            <ErrorBoundary>
              <Outlet />
            </ErrorBoundary>
          </div>
        </main>
      </div>

      {/* AI Panel */}
      {aiPanelOpen && <AIAssistantPanel />}

      {/* Command Palette */}
      {commandPaletteOpen && <CommandPalette />}

      <Toaster />
    </div>
  );
}
