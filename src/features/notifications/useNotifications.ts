import { createContext, useContext } from "react";

export type NotificationType = "success" | "error" | "info";

export interface NotificationItem {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  createdAt: string;
  read: boolean;
}

export interface NotifyInput {
  title: string;
  message: string;
  type?: NotificationType;
}

export interface NotificationContextValue {
  notifications: NotificationItem[];
  unreadCount: number;
  notify: (input: NotifyInput) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  markAllAsRead: () => void;
}

export const NotificationContext = createContext<NotificationContextValue | null>(null);

export function useNotifications() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error("useNotifications precisa ser usado dentro de NotificationProvider.");
  }
  return context;
}
