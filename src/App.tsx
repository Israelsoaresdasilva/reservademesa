import { useState } from "react";
import HomePage, { MenuChat } from "./Pages/homepage";
import Reservas from "./Pages/reservas/reservas";
import Avaliacoes from "./Pages/avaliacoes";
import {
  NotificationCenter,
  NotificationProvider,
} from "./features/notifications";

type ModalType = "cardapio" | "reserva" | "avaliacoes";

function App() {
  const [activeModal, setActiveModal] = useState<ModalType | null>(null);

  return (
    <NotificationProvider>
      <div className="app-one-page">
        <HomePage onOpenModal={setActiveModal} />

        {/* Floating cardápio closed state: the panel header (bottom-right, non blocking) */}
        <button
          type="button"
          className={`menu-chat-trigger${activeModal === "cardapio" ? " menu-chat-trigger--hidden" : ""}`}
          onClick={() => setActiveModal("cardapio")}
          aria-haspopup="dialog"
          aria-expanded={activeModal === "cardapio"}
          aria-label="Abrir cardápio"
        >
          <span className="menu-chat-trigger-avatar" aria-hidden="true">
            🍽️
          </span>
          <span className="menu-chat-trigger-copy">
            <strong>Ocean Blue</strong>
            <span>Cardápio Fechado</span>
          </span>
          <span className="menu-chat-trigger-caret" aria-hidden="true">
            ^
          </span>
        </button>

        {/* Menu panel: works side by side with the rest of the site */}
        {activeModal === "cardapio" && (
          <MenuChat
            onClose={() => setActiveModal(null)}
            onOpenReserva={() => setActiveModal("reserva")}
          />
        )}

        {(activeModal === "reserva" || activeModal === "avaliacoes") && (
          <div
            className="popup-overlay"
            onClick={() => setActiveModal(null)}
            aria-modal="true"
            role="dialog"
          >
            {activeModal === "reserva" && (
              <div
                className="popup-shell popup-shell--full"
                onClick={(event) => event.stopPropagation()}
              >
                <button
                  type="button"
                  className="popup-close popup-close--light"
                  onClick={() => setActiveModal(null)}
                  aria-label="Fechar reserva"
                >
                  ✕
                </button>
                <Reservas />
              </div>
            )}

            {activeModal === "avaliacoes" && (
              <div
                className="popup-shell popup-shell--scrollable"
                onClick={(event) => event.stopPropagation()}
              >
                <button
                  type="button"
                  className="popup-close"
                  onClick={() => setActiveModal(null)}
                  aria-label="Fechar avaliações"
                >
                  ✕
                </button>
                <Avaliacoes />
              </div>
            )}
          </div>
        )}

        <NotificationCenter />
      </div>
    </NotificationProvider>
  );
}

export default App;
