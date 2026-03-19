import { useEffect, useMemo, useState, type CSSProperties } from "react";
import { useLocation } from "react-router-dom";
import { useNotifications, type NotificationItem } from "./NotificationProvider";
import "./notifications.css";

function formatTime(value: string) {
  try {
    return new Intl.DateTimeFormat("pt-BR", {
      hour: "2-digit",
      minute: "2-digit",
      day: "2-digit",
      month: "2-digit",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

function NotificationCard({
  item,
  onRemove,
}: {
  item: NotificationItem;
  onRemove: (id: string) => void;
}) {
  return (
    <article className={`notification-card notification-card--${item.type}`}>
      <div className="notification-card__header">
        <strong>{item.title}</strong>
        <button
          type="button"
          className="notification-card__close"
          aria-label="Remover notificacao"
          onClick={() => onRemove(item.id)}
        >
          x
        </button>
      </div>
      <p>{item.message}</p>
      <span className="notification-card__time">{formatTime(item.createdAt)}</span>
    </article>
  );
}

export function NotificationCenter() {
  const [open, setOpen] = useState(false);
  const { pathname } = useLocation();
  const isHome = pathname === "/";
  const [homeStyle, setHomeStyle] = useState<CSSProperties>({});
  const {
    notifications,
    unreadCount,
    removeNotification,
    clearNotifications,
    markAllAsRead,
  } = useNotifications();

  useEffect(() => {
    if (open) {
      markAllAsRead();
    }
  }, [open, markAllAsRead]);

  useEffect(() => {
    if (!isHome) return;

    const triggerSize = 46;
    const gap = 10;

    const updatePosition = () => {
      const reserveButton = document.querySelector(".reserve-button") as HTMLElement | null;

      if (!reserveButton) {
        setHomeStyle({});
        return;
      }

      const rect = reserveButton.getBoundingClientRect();
      const right = window.innerWidth - rect.left + gap;
      const top = rect.top + rect.height / 2 - triggerSize / 2;

      setHomeStyle({
        top: `${Math.max(8, top)}px`,
        right: `${Math.max(8, right)}px`,
      });
    };

    updatePosition();
    window.addEventListener("resize", updatePosition);
    window.addEventListener("scroll", updatePosition, true);

    return () => {
      window.removeEventListener("resize", updatePosition);
      window.removeEventListener("scroll", updatePosition, true);
    };
  }, [isHome]);

  const sectionStyle = useMemo(
    () => (isHome ? homeStyle : undefined),
    [isHome, homeStyle]
  );

  return (
    <section
      className={`notification-center${isHome ? " notification-center--home" : ""}`}
      style={sectionStyle}
    >
      <button
        type="button"
        className="notification-center__trigger"
        aria-label="Abrir notificacoes"
        onClick={() => setOpen((prev) => !prev)}
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 2a6 6 0 0 0-6 6v3.6l-1.5 3a1 1 0 0 0 .9 1.4h13.2a1 1 0 0 0 .9-1.4l-1.5-3V8a6 6 0 0 0-6-6Zm0 20a3 3 0 0 0 2.8-2h-5.6A3 3 0 0 0 12 22Z" />
        </svg>
        {unreadCount > 0 && <span className="notification-center__badge">{unreadCount}</span>}
      </button>

      {open && (
        <div className="notification-center__panel" role="dialog" aria-label="Lista de notificacoes">
          <header className="notification-center__header">
            <strong>Notificacoes</strong>
            <button
              type="button"
              onClick={clearNotifications}
              disabled={notifications.length === 0}
            >
              Limpar
            </button>
          </header>

          <div className="notification-center__list">
            {notifications.length === 0 ? (
              <p className="notification-center__empty">Nenhuma notificacao por enquanto.</p>
            ) : (
              notifications.map((item) => (
                <NotificationCard key={item.id} item={item} onRemove={removeNotification} />
              ))
            )}
          </div>
        </div>
      )}
    </section>
  );
}
