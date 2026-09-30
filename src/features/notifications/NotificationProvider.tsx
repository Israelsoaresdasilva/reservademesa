import { useCallback, useMemo, useState, type ReactNode } from "react";
import {
  NotificationContext,
  type NotificationContextValue,
  type NotificationItem,
  type NotifyInput,
} from "./useNotifications";

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
    [notifications],
  );

  const value = useMemo<NotificationContextValue>(
    () => ({
      notifications,
      unreadCount,
      notify,
      removeNotification,
      clearNotifications,
      markAllAsRead,
    }),
    [notifications, unreadCount, notify, removeNotification, clearNotifications, markAllAsRead],
  );

  return <NotificationContext.Provider value={value}>{children}</NotificationContext.Provider>;
}
