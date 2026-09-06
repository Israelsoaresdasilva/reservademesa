import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";

export type NotificationType = "success" | "error" | "info";

export interface NotificationItem {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  createdAt: string;
  read: boolean;
}

interface NotifyInput {
  title: string;
  message: string;
  type?: NotificationType;
}

interface NotificationContextValue {
  notifications: NotificationItem[];
  unreadCount: number;
  notify: (input: NotifyInput) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  markAllAsRead: () => void;
}

const NotificationContext = createContext<NotificationContextValue | null>(null);

function createNotification(input: NotifyInput): NotificationItem {
  const now = new Date();
  return {
    id: `${now.getTime()}-${Math.random().toString(16).slice(2)}`,
    type: input.type ?? "info",
    title: input.title,
    message: input.message,
    createdAt: now.toISOString(),
    read: false,
  };
}

export function NotificationProvider({ children }: { children: ReactNode }) {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);

  const notify = useCallback((input: NotifyInput) => {
    const next = createNotification(input);
    setNotifications((prev) => [next, ...prev].slice(0, 20));
  }, []);

  const removeNotification = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((item) => item.id !== id));
  }, []);

  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications((prev) => prev.map((item) => ({ ...item, read: true })));
  }, []);

  const unreadCount = useMemo(
    () => notifications.filter((item) => !item.read).length,
    [notifications]
  );

  const value = useMemo(
    () => ({
      notifications,
      unreadCount,
      notify,
      removeNotification,
      clearNotifications,
      markAllAsRead,
    }),
    [notifications, unreadCount, notify, removeNotification, clearNotifications, markAllAsRead]
  );

  return <NotificationContext.Provider value={value}>{children}</NotificationContext.Provider>;
}

export function useNotifications() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error("useNotifications precisa ser usado dentro de NotificationProvider.");
  }
  return context;
}
