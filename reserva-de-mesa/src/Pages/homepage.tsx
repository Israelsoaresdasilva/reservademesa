import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../App.css";
import { useNotifications } from "../features/notifications";

const seafoodHighlights = [
  {
    title: "OSTRAS FRESCAS",
    image:
      "https://images.unsplash.com/photo-1559737558-2f5a35f4523b?auto=format&fit=crop&w=1200&q=80",
  },
  {
    title: "RISOTO DE CAMARAO",
    image:
      "https://images.unsplash.com/photo-1476124369491-e7addf5db371?auto=format&fit=crop&w=1200&q=80",
  },
  {
    title: "PAELLA DO CHEF",
    image:
      "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=1200&q=80",
  },
];

function Sidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
  const navigate = useNavigate();
  return (
    <>
      <div
        className={`sidebar-backdrop${open ? " sidebar-backdrop--visible" : ""}`}
        onClick={onClose}
        aria-hidden="true"
      />
      <nav
        className={`sidebar${open ? " sidebar--open" : ""}`}
        aria-label="Menu principal"
        aria-hidden={!open}
      >
        <div className="sidebar-top">
          <button
            className="sidebar-close"
            onClick={onClose}
            aria-label="Fechar menu"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path
                d="M18 6 6 18M6 6l12 12"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
          </button>
          <div className="sidebar-header-info">
            <a
              className="phone-link"
              href="tel:+552420260003"
              aria-label="Ligar para o restaurante"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M6.7 10.8a15.2 15.2 0 0 0 6.5 6.5l2.2-2.2a1 1 0 0 1 1-.24 11 11 0 0 0 3.45.55 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17.8 17.8 0 0 1 3 4a1 1 0 0 1 1-1h3.6a1 1 0 0 1 1 1c0 1.2.18 2.36.55 3.45a1 1 0 0 1-.25 1.02L6.7 10.8Z" />
              </svg>
              <span>+55 21 99999-9999</span>
            </a>
          </div>
        </div>

        <div className="sidebar-logo">
          <img src="/logo.png" alt="Ocean Blue" />
        </div>

        <ul className="sidebar-nav">
          <li>
            <a
              href="#"
              onClick={() => {
                onClose();
                navigate("/");
              }}
            >
              OCEAN BLUE
            </a>
          </li>
          <li>
            <a
              href="#"
              onClick={() => {
                onClose();
                window.location.href = "/Cardápio.html";
              }}
            >
              CARDAPIO
            </a>
          </li>
          <li>
            <a
              href="#"
              onClick={() => {
                onClose();
                navigate("/reservas");
              }}
            >
              RESERVA
            </a>
          </li>
          <li>
            <a
              href="#"
              onClick={() => {
                onClose();
                navigate("/avaliacoes");
              }}
            >
              AVALIAÇÕES
            </a>
          </li>
        </ul>
      </nav>
    </>
  );
}

function EventoModal({
  open,
  onClose,
  onSubmit,
}: {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: { nome: string; telefone: string; data: string }) => void;
}) {
  const [nome, setNome] = useState("");
  const [telefone, setTelefone] = useState("");
  const [data, setData] = useState("");
  if (!open) return null;
  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(0,0,0,0.5)",
        zIndex: 9999,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <form
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit({ nome, telefone, data });
        }}
        style={{
          background: "#fff",
          borderRadius: 16,
          padding: 32,
          minWidth: 320,
          boxShadow: "0 8px 32px rgba(10,37,64,0.18)",
          display: "flex",
          flexDirection: "column",
          gap: 18,
        }}
      >
        <h2
          style={{
            margin: 0,
            color: "#1a6fa8",
            fontWeight: 700,
            fontSize: "1.3rem",
          }}
        >
          Solicitar Evento
        </h2>
        <label
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 4,
          }}
        >
          Nome
          <input
            type="text"
            value={nome}
            onChange={(e) => setNome(e.target.value)}
            required
            style={{
              padding: 8,
              borderRadius: 6,
              border: "1px solid #b3d6e8",
            }}
          />
        </label>
        <label
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 4,
          }}
        >
          Telefone
          <input
            type="tel"
            value={telefone}
            onChange={(e) => {
              // Permite apenas números, parênteses, espaço e traço
              const val = e.target.value.replace(/[^\d\-() ]/g, "");
              setTelefone(val);
            }}
            required
            placeholder="(99) 99999-9999"
            maxLength={15}
            style={{
              padding: 8,
              borderRadius: 6,
              border: "1px solid #b3d6e8",
            }}
          />
        </label>
        <label
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 4,
          }}
        >
          Data do evento
          <input
            type="date"
            value={data}
            onChange={(e) => setData(e.target.value)}
            required
            style={{
              padding: 8,
              borderRadius: 6,
              border: "1px solid #b3d6e8",
            }}
          />
        </label>
        <div
          style={{
            display: "flex",
            gap: 10,
            marginTop: 8,
          }}
        >
          <button
            type="button"
            onClick={onClose}
            style={{
              flex: 1,
              padding: 10,
              borderRadius: 8,
              border: "1px solid #b3d6e8",
              background: "#f7fbfd",
              color: "#1a6fa8",
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            Cancelar
          </button>
          <button
            type="submit"
            style={{
              flex: 1,
              padding: 10,
              borderRadius: 8,
              border: "none",
              background: "linear-gradient(90deg, #1a6fa8, #4db3d8)",
              color: "#fff",
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            Enviar
          </button>
        </div>
      </form>
    </div>
  );
}

function PopupConfirm({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  if (!open) return null;
  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(0,0,0,0.5)",
        zIndex: 9999,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          background: "#fff",
          borderRadius: 16,
          padding: 32,
          minWidth: 320,
          boxShadow: "0 8px 32px rgba(10,37,64,0.18)",
          display: "flex",
          flexDirection: "column",
          gap: 18,
          alignItems: "center",
        }}
      >
        <h2
          style={{
            color: "#1a6fa8",
            fontWeight: 700,
            fontSize: "1.2rem",
            margin: 0,
          }}
        >
          Solicitação enviada!
        </h2>
        <p
          style={{
            color: "#163d5c",
            fontSize: "1rem",
            textAlign: "center",
            margin: 0,
          }}
        >
          O Ocean Blue entrará em contato para confirmar os detalhes do seu
          evento.
        </p>
        <button
          onClick={onClose}
          style={{
            marginTop: 10,
            padding: "10px 28px",
            borderRadius: 8,
            border: "none",
            background: "linear-gradient(90deg, #1a6fa8, #4db3d8)",
            color: "#fff",
            fontWeight: 700,
            cursor: "pointer",
          }}
        >
          Fechar
        </button>
      </div>
    </div>
  );
}

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const navigate = useNavigate();
  const { notify } = useNotifications();
  const [eventoModalOpen, setEventoModalOpen] = useState(false);
  const [popupConfirmOpen, setPopupConfirmOpen] = useState(false);

  const handleGoToReserva = () => {
    notify({
      type: "info",
      title: "Iniciando reserva",
      message: "Você foi direcionado para escolher sua mesa.",
    });
    navigate("/reservas");
  };
  const handleGoToCardapio = () => {
    window.location.href = "/Cardápio.html";
  };
  return (
    <main className="home-page">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <header className="top-bar top-fixed">
        <div className="left-tools">
          <button
            className="icon-button"
            aria-label="Open navigation menu"
            onClick={() => setSidebarOpen(true)}
          >
            <span />
            <span />
            <span />
          </button>
          <a
            className="phone-link"
            href="tel:+552420260003"
            aria-label="Call restaurant"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M6.7 10.8a15.2 15.2 0 0 0 6.5 6.5l2.2-2.2a1 1 0 0 1 1-.24 11 11 0 0 0 3.45.55 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17.8 17.8 0 0 1 3 4a1 1 0 0 1 1-1h3.6a1 1 0 0 1 1 1c0 1.2.18 2.36.55 3.45a1 1 0 0 1-.25 1.02L6.7 10.8Z" />
            </svg>
            <span>+55 21 99999-9999</span>
          </a>
        </div>
        <div className="top-brand" aria-label="Ocean Blue logo">
          <img src="/logo.png" alt="Ocean Blue" />
        </div>
        <button
          className="reserve-button"
          type="button"
          onClick={handleGoToReserva}
        >
          RESERVAR
        </button>
      </header>

      <section
        className="hero"
        aria-label="Ocean Blue seafood restaurant cover"
      >
        <video className="hero-video" autoPlay muted loop playsInline>
          <source src="/Video%20Project%201.mp4" type="video/mp4" />
        </video>
        <div className="overlay" />
        <div
          className="brand-block"
          role="img"
          aria-label="Ocean Blue branding"
        >
          <p className="brand-title">OCEAN BLUE</p>
          <p className="brand-subtitle">Sabores do mar, tradição à mesa</p>
        </div>
      </section>

      <section className="about-section content-block">
        <div className="about-media" aria-hidden="true">
          <img
            src="https://images.unsplash.com/photo-1541544741938-0af808871cc0?auto=format&fit=crop&w=900&q=80"
            alt="Seafood platter"
          />
          <img
            src="https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=1200&q=80"
            alt="Restaurant interior by the sea"
          />
        </div>
        <div className="about-copy">
          <p className="eyebrow">Descubra o sabor</p>
          <h2>O MELHOR DO MAR EM CADA PRATO</h2>
          <p>
            Localizado na costa brasileira, o Ocean Blue e um restaurante de
            frutos do mar que celebra ingredientes frescos, receitas autorais e
            a atmosfera unica do litoral.
          </p>
          <p>
            Do almoço a luz do dia ao jantar especial, cada experiencia combina
            atendimento acolhedor, carta de vinhos selecionada e vistas
            inspiradoras para momentos inesqueciveis.
          </p>
          <button
            type="button"
            className="small-sand-button"
            onClick={handleGoToCardapio}
          >
            VER CARDAPIO
          </button>
        </div>
      </section>

      <section className="suites-section content-block">
        <p className="eyebrow">Sabores do mar</p>
        <h2>ESPECIALIDADES PREPARADAS COM FRESCOR E TECNICA</h2>
        <div className="suite-grid">
          {seafoodHighlights.map((item) => (
            <article className="suite-card" key={item.title}>
              <img src={item.image} alt={item.title} />
              <div className="suite-title">{item.title}</div>
            </article>
          ))}
        </div>
      </section>

      <section className="experience-section content-block">
        <div className="experience-copy">
          <p className="eyebrow">Experiencias</p>
          <h2>UMA JORNADA GASTRONOMICA COMPLETA</h2>
          <p>
            Do bar de ostras aos pratos quentes autorais, nosso menu foi pensado
            para surpreender o paladar com texturas, aromas e harmonizacoes que
            valorizam o melhor do oceano.
          </p>
          <button
            type="button"
            className="small-sand-button"
            onClick={handleGoToCardapio}
          >
            EXPLORAR MENU
          </button>
        </div>
        <div className="experience-media" aria-hidden="true">
          <img
            src="https://images.unsplash.com/photo-1600891964599-f61ba0e24092?auto=format&fit=crop&w=1100&q=80"
            alt="Seafood tasting"
          />
          <img
            src="https://images.unsplash.com/photo-1559339352-11d035aa65de?auto=format&fit=crop&w=1100&q=80"
            alt="Restaurant service"
          />
        </div>
      </section>

      <section className="events-wrap">
        <div className="events-hero" aria-hidden="true" />
        <div className="events-card content-block">
          <p className="eyebrow">Eventos</p>
          <h2>O CENARIO PERFEITO PARA CELEBRAR COM SABOR</h2>
          <p>
            Do aniversario intimista ao evento corporativo, montamos
            experiencias personalizadas com menu de frutos do mar, servico
            dedicado e ambientacao elegante a beira-mar.
          </p>
          <button
            type="button"
            className="outline-button"
            onClick={() => setEventoModalOpen(true)}
          >
            SOLICITAR EVENTO
          </button>
        </div>
      </section>
      <EventoModal
        open={eventoModalOpen}
        onClose={() => setEventoModalOpen(false)}
        onSubmit={() => {
          setEventoModalOpen(false);
          setPopupConfirmOpen(true);
        }}
      />
      <PopupConfirm
        open={popupConfirmOpen}
        onClose={() => setPopupConfirmOpen(false)}
      />
      <section className="quote-section content-block">
        <p>Saboreie a experiencia Ocean Blue</p>
      </section>

      <section
        className="chef-team-section content-block"
        aria-label="Equipe de mestres-cucas"
      >
        <div className="chef-team-media">
          <img src="/image.png" alt="Equipe de mestres-cucas do Ocean Blue" />
        </div>
        <div className="chef-team-copy">
          <p className="eyebrow">Nossa equipe</p>
          <h2>MESTRES-CUCAS QUE TRANSFORMAM O MAR EM ARTE</h2>
          <p>
            Nossa brigada e formada por chefs especializados em frutos do mar,
            com tecnica apurada e paixao por ingredientes frescos. Cada prato
            nasce de pesquisa, criatividade e respeito pelos sabores do oceano.
          </p>
          <p>
            Da cozinha quente ao bar de crus, nossos mestres-cucas trabalham em
            sintonia para oferecer uma experiencia autoral, elegante e memoravel
            em cada servico.
          </p>
        </div>
      </section>

      <footer className="footer">
        <div className="footer-content content-block">
          <div className="footer-mark" aria-label="Ocean Blue logo">
            <img src="/logo.png" alt="Ocean Blue" />
          </div>
          <nav className="footer-links" aria-label="Footer links">
            <a href="#" onClick={() => navigate("/")}>
              Ocean Blue
            </a>
            <a href="/Cardápio.html">Cardapio</a>
            <a href="#" onClick={() => navigate("/reservas")}>
              Reservas
            </a>
            <a href="#" onClick={() => navigate("/avaliacoes")}>
              Avaliações
            </a>
          </nav>
          <address className="footer-contact">
            <p>Rodovia BR 116 km 7, s/n</p>
            <p>Estrada do Mar - 25.365-123</p>
            <p>+55 21 99999-9999</p>
            <p>@oceanbluebrasil</p>
            <p className="mail">reservas@oceanblue.com.br</p>
          </address>
        </div>
        <p className="copyright">
          COPYRIGHT 2026 OCEAN BLUE RESTAURANTE - TODOS OS DIREITOS RESERVADOS.
        </p>
      </footer>
    </main>
  );
}

export default App;
