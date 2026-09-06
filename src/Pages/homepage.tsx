import { useEffect, useState } from "react";
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

const cardapio = [
  {
    title: "PRATOS",
    items: [
      {
        name: "Bolinho de Bacalhau",
        subtitle: "Clássico português",
        description:
          "Bolinhos crocantes de bacalhau desfiado, batata e temperos especiais. Servidos com molho tártaro.",
        image: "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=900&q=80",
      },
      {
        name: "Ceviche de Peixe Branco",
        subtitle: "Refrescante e cítrico",
        description:
          "Peixe branco marinado no limão, cebola roxa, coentro e pimenta dedo-de-moça. Acompanha chips de batata-doce.",
        image: "https://images.unsplash.com/photo-1559847844-5315695dadae?auto=format&fit=crop&w=900&q=80",
      },
      {
        name: "Camarão na Moranga",
        subtitle: "Camarões cremosos dentro de uma abóbora",
        description:
          "Tradicional prato brasileiro com camarões refogados em molho cremoso, servido dentro de uma moranga assada. Acompanha arroz branco.",
        image: "https://images.unsplash.com/photo-1559847844-5315695dadae?auto=format&fit=crop&w=900&q=80",
      },
      {
        name: "Moqueca Baiana",
        subtitle: "Peixe e camarão ao leite de coco",
        description:
          "Peixe e camarão cozidos com pimentões, tomate, cebola, leite de coco e azeite de dendê. Servido com arroz e farofa de dendê.",
        image: "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=900&q=80",
      },
      {
        name: "Risoto de Frutos do Mar",
        subtitle: "Arroz cremoso com frutos do mar",
        description:
          "Risoto preparado com arroz arbório, camarão, lula, polvo e mexilhões, finalizado com vinho branco e ervas frescas.",
        image: "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?auto=format&fit=crop&w=900&q=80",
      },
      {
        name: "Polvo Grelhado ao Azeite",
        subtitle: "Maciez e sabor do mar",
        description:
          "Tentáculos de polvo grelhados na brasa, regados com azeite de ervas, servidos com batatas rústicas e tomatinhos confitados.",
        image: "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?auto=format&fit=crop&w=900&q=80",
      },
      {
        name: "Bobó de Camarão",
        subtitle: "Cremosidade nordestina",
        description:
          "Camarões em creme de mandioca com leite de coco e dendê, finalizado com coentro fresco. Acompanha arroz branco.",
        image: "https://images.unsplash.com/photo-1626804475297-41608ea09aeb?auto=format&fit=crop&w=900&q=80",
      },
      {
        name: "Filé de Robalo ao Molho de Maracujá",
        subtitle: "Equilíbrio doce e cítrico",
        description:
          "Filé de robalo selado, coberto com molho agridoce de maracujá, sobre purê de banana-da-terra.",
        image: "https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&w=900&q=80",
      },
      {
        name: "Mousse de Maracujá",
        subtitle: "Leve e refrescante",
        description: "Mousse cremosa de maracujá com calda de frutas frescas.",
        image: "https://images.unsplash.com/photo-1551024601-bec78aea704b?auto=format&fit=crop&w=900&q=80",
      },
      {
        name: "Torta de Limão",
        subtitle: "Clássica e deliciosa",
        description: "Torta de limão com base crocante e cobertura de merengue.",
        image: "https://images.unsplash.com/photo-1551024506-0bccd828d307?auto=format&fit=crop&w=900&q=80",
      },
    ],
  },
  {
    title: "BEBIDAS",
    items: [
      {
        name: "Caipirinha",
        subtitle: "Clássico brasileiro",
        description: "Cachaça, limão, açúcar e gelo. Refrescante e perfeita para acompanhar frutos do mar.",
        image: "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?auto=format&fit=crop&w=900&q=80",
      },
      {
        name: "Mojito Tropical",
        subtitle: "Refrescância cubana",
        description: "Rum, hortelã fresca, limão, açúcar e água com gás. Refrescância cubana com toque brasileiro.",
        image: "https://images.unsplash.com/photo-1551538827-9c037cb4f32a?auto=format&fit=crop&w=900&q=80",
      },
      {
        name: "Vinho Branco da Casa",
        subtitle: "Sauvignon Blanc seco",
        description: "Vinho branco seco e leve, harmonização perfeita com peixes e frutos do mar.",
        image: "https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?auto=format&fit=crop&w=900&q=80",
      },
      {
        name: "Cerveja Artesanal IPA",
        subtitle: "Lúpulo cítrico",
        description: "Cerveja artesanal de lúpulo cítrico, corpo médio e final levemente amargo. Servida bem gelada.",
        image: "https://images.unsplash.com/photo-1608270586620-248524c67de9?auto=format&fit=crop&w=900&q=80",
      },
      {
        name: "Suco Natural",
        subtitle: "Diversos sabores",
        description: "Escolha entre laranja, abacaxi, maracujá ou limonada.",
        image: "https://images.unsplash.com/photo-1544145945-f90425340c7e?auto=format&fit=crop&w=900&q=80",
      },
      {
        name: "Água de Coco Gelada",
        subtitle: "Direto do coco verde",
        description: "Hidratante, levemente adocicada e servida bem gelada. Perfeita para um dia ensolarado.",
        image: "https://images.unsplash.com/photo-1536759808741-94b7d4af392c?auto=format&fit=crop&w=900&q=80",
      },
    ],
  },
];

export function MenuChat({
  onClose,
  onOpenReserva,
}: {
  onClose: () => void;
  onOpenReserva: () => void;
}) {
  const [category, setCategory] = useState("Todos");
  const [query, setQuery] = useState("");

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const categories = ["Todos", ...cardapio.map((group) => group.title)];
  const normalized = query.trim().toLocaleLowerCase();

  const groups = cardapio
    .map((group) => ({
      ...group,
      items: group.items.filter(
        (item) =>
          (category === "Todos" || group.title === category) &&
          (normalized === "" ||
            `${item.name} ${item.subtitle} ${item.description}`
              .toLocaleLowerCase()
              .includes(normalized)),
      ),
    }))
    .filter((group) => group.items.length > 0);

  return (
    <section
      id="cardapio"
      className="menu-chat"
      role="dialog"
      aria-modal="false"
      aria-label="Cardápio Ocean Blue"
    >
      <header className="menu-chat-header">
        <div className="menu-chat-avatar" aria-hidden="true">
          🍽️
        </div>
        <div className="menu-chat-identity">
          <strong>Ocean Blue</strong>
          <span className="menu-chat-status">
            <i aria-hidden="true" />
            Cardápio aberto
          </span>
        </div>
        <button
          type="button"
          className="menu-chat-close"
          onClick={onClose}
          aria-label="Fechar cardápio"
        >
          ✕
        </button>
      </header>

      <div className="menu-chat-categories" aria-label="Categorias do cardápio">
        {categories.map((name) => (
          <button
            key={name}
            type="button"
            aria-pressed={category === name}
            className={`menu-chat-cat${category === name ? " menu-chat-cat--active" : ""}`}
            onClick={() => setCategory(name)}
          >
            {name}
          </button>
        ))}
      </div>

      <div className="menu-chat-body">
        {groups.map((group) => (
          <div key={group.title} className="menu-chat-group">
            <h3>{group.title}</h3>
            <ul className="menu-chat-list">
              {group.items.map((item) => (
                <li key={item.name} className="menu-chat-item">
                  <img
                    className="menu-chat-item-img"
                    src={item.image}
                    alt={item.name}
                    loading="lazy"
                  />
                  <div className="menu-chat-item-copy">
                    <strong>{item.name}</strong>
                    <span className="menu-chat-item-sub">{item.subtitle}</span>
                    <p>{item.description}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        ))}
        {groups.length === 0 && (
          <p className="menu-chat-empty">Sem resultados para a sua busca.</p>
        )}
      </div>

      <footer className="menu-chat-footer">
        <label className="menu-chat-search">
          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <circle cx="10.5" cy="10" r="7" />
            <path d="M10.5 15.5 l0 3.5" />
          </svg>
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Buscar no cardápio..."
            aria-label="Buscar no cardápio"
          />
        </label>
        <button
          type="button"
          className="menu-chat-reserve"
          onClick={onOpenReserva}
          aria-label="Reservar mesa"
        >
          Reservar
        </button>
      </footer>
    </section>
  );
}

function Sidebar({
  open,
  onClose,
  onOpenModal,
}: {
  open: boolean;
  onClose: () => void;
  onOpenModal: (modal: "cardapio" | "reserva" | "avaliacoes") => void;
}) {
  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

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
              href="#top"
              onClick={(event) => {
                event.preventDefault();
                onClose();
                scrollToSection("top");
              }}
            >
              OCEAN BLUE
            </a>
          </li>
          <li>
            <a
              href="#cardapio"
              onClick={(event) => {
                event.preventDefault();
                onClose();
                onOpenModal("cardapio");
              }}
            >
              CARDAPIO
            </a>
          </li>
          <li>
            <a
              href="#reserva"
              onClick={(event) => {
                event.preventDefault();
                onClose();
                onOpenModal("reserva");
              }}
            >
              RESERVA
            </a>
          </li>
          <li>
            <a
              href="#avaliacoes"
              onClick={(event) => {
                event.preventDefault();
                onClose();
                onOpenModal("avaliacoes");
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

function App({ onOpenModal }: { onOpenModal: (modal: "cardapio" | "reserva" | "avaliacoes") => void }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { notify } = useNotifications();
  const [eventoModalOpen, setEventoModalOpen] = useState(false);
  const [popupConfirmOpen, setPopupConfirmOpen] = useState(false);

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  const handleGoToReserva = () => {
    notify({
      type: "info",
      title: "Iniciando reserva",
      message: "Você foi direcionado para escolher sua mesa.",
    });
    onOpenModal("reserva");
  };
  const handleGoToCardapio = () => {
    onOpenModal("cardapio");
  };

  /* Animación de aparición al hacer scroll (UX) */
  useEffect(() => {
    const elements = document.querySelectorAll<HTMLElement>(".reveal");
    try {
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          });
        },
        { threshold: 0.14, rootMargin: "0px 0px -60px 0px" },
      );
      elements.forEach((element) => observer.observe(element));
      return () => observer.disconnect();
    } catch {
      elements.forEach((element) => element.classList.add("is-visible"));
      return;
    }
  }, []);

  return (
    <main className="home-page">
      <Sidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onOpenModal={onOpenModal}
      />
      <header className="top-bar top-fixed" id="top">
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

      <section className="about-section content-block reveal">
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
            Localizado na costa brasileira, o Ocean Blue é um restaurante de
            frutos do mar que celebra ingredientes frescos, receitas autorais e
            a atmosfera única do litoral.
          </p>
          <p>
            Do almoço à luz do dia ao jantar especial, cada experiência combina
            atendimento acolhedor, carta de vinhos selecionada e vistas
            inspiradoras para momentos inesquecíveis.
          </p>
          <div className="about-chips" aria-hidden="true">
            <span className="about-chip">Pescado fresco diário</span>
            <span className="about-chip">Carta de vinhos</span>
            <span className="about-chip">Vista ao oceano</span>
          </div>
          <button
            type="button"
            className="small-sand-button"
            onClick={handleGoToCardapio}
          >
            VER CARDÁPIO
          </button>
        </div>
      </section>

      <section className="suites-section content-block reveal">
        <p className="eyebrow">Sabores do mar</p>
        <h2>ESPECIALIDADES PREPARADAS COM FRESCOR E TECNICA</h2>
        <div className="suite-grid">
          {seafoodHighlights.map((item, index) => (
            <article className="suite-card" key={item.title}>
              <img src={item.image} alt={item.title} />
              <span className="suite-rank">Nº 0{index + 1}</span>
              <div className="suite-title">{item.title}</div>
            </article>
          ))}
        </div>
      </section>

      <section className="experience-section content-block reveal">
        <div className="experience-copy">
          <p className="eyebrow">Experiencias</p>
          <h2>UMA JORNADA GASTRONÓMICA COMPLETA</h2>
          <p>
            Do bar de ostras aos pratos quentes autorais, nosso menu foi pensado
            para surpreender o paladar com texturas, aromas e harmonizacoes que
            valorizam o melhor do oceano.
          </p>
          <div className="experience-stats" aria-label="Ocean Blue em números">
            <p className="exp-stat">
              <b>40+</b>
              <span>Pratos do mar</span>
            </p>
            <p className="exp-stat">
              <b>18</b>
              <span>Vinhos &amp; espumantes</span>
            </p>
            <p className="exp-stat">
              <b>4.9</b>
              <span>Opinião dos clientes</span>
            </p>
          </div>
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
        <div className="events-card content-block reveal">
          <p className="eyebrow">Eventos</p>
          <h2>O CENÁRIO PERFEITO PARA CELEBRAR COM SABOR</h2>
          <p>
            Do aniversario íntimo ao evento corporativo, montamos
            experiencias personalizadas com menu de frutos do mar, serviço
            dedicado e ambientación elegante à beira-mar.
          </p>
          <div className="events-features" aria-hidden="true">
            <span className="event-feature">Aniversarios</span>
            <span className="event-feature">Eventos corporativos</span>
            <span className="event-feature">À beira-mar</span>
          </div>
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
      <section className="quote-section">
        <p>Saboreie a experiência Ocean Blue</p>
        <p className="quote-sign">Ocean Blue · Restaurante de frutos do mar</p>
      </section>

      <section className="testimonials-section content-block reveal">
        <p className="eyebrow">Testimonios</p>
        <h2>O QUE DICEN NUESTROS COMENSALES</h2>
        <div className="testimonial-grid">
          <article className="testimonial-card">
            <span className="testimonial-stars" aria-label="5 de 5 estrellas">
              ★★★★★
            </span>
            <p className="testimonial-quote">
              “A moqueca baiana foi inesquecível. O serviço impecável e a
              vista ao mar fizeram o resto. Vamos voltar.”
            </p>
            <p className="testimonial-author">
              <span className="testimonial-avatar" aria-hidden="true">M</span>
              <span className="testimonial-meta">
                <strong>María G.</strong>
                <span>Comensal frecuente</span>
              </span>
            </p>
          </article>
          <article className="testimonial-card">
            <span className="testimonial-stars" aria-label="5 de 5 estrellas">
              ★★★★★
            </span>
            <p className="testimonial-quote">
              “Celebramos o nosso aniversário em Ocean Blue e tudo foi
              perfeito: a mesa à beira-mar, o risotto e a atenção de toda a
              brigada.”
            </p>
            <p className="testimonial-author">
              <span className="testimonial-avatar" aria-hidden="true">C</span>
              <span className="testimonial-meta">
                <strong>Carlos M.</strong>
                <span>Reserva de aniversario</span>
              </span>
            </p>
          </article>
          <article className="testimonial-card">
            <span className="testimonial-stars" aria-label="5 de 5 estrellas">
              ★★★★★
            </span>
            <p className="testimonial-quote">
              “As ostras frescas e o ceviche estão fora de série. Para nós é o
              melhor restaurante de frutos do mar do litoral.”
            </p>
            <p className="testimonial-author">
              <span className="testimonial-avatar" aria-hidden="true">L</span>
              <span className="testimonial-meta">
                <strong>Lucía R.</strong>
                <span>Experiencia de fin de semana</span>
              </span>
            </p>
          </article>
        </div>
      </section>

      <section
        className="chef-team-section content-block reveal"
        aria-label="Equipe de mestres-cucas"
      >
        <div className="chef-team-media">
          <span className="chef-badge">20+ años de cocina</span>
          <img src="/image.png" alt="Equipe de mestres-cucas do Ocean Blue" />
        </div>
        <div className="chef-team-copy">
          <p className="eyebrow">Nossa equipe</p>
          <h2>MESTRES-CUCAS QUE TRANSFORMAM O MAR EM ARTE</h2>
          <p>
            Nossa brigada é formada por chefs especializados em frutos do mar,
            com técnica apurada e paixão por ingredientes frescos. Cada prato
            nasce de pesquisa, criatividade e respeito pelos sabores do oceano.
          </p>
          <p>
            Da cozinha quente ao bar de crus, nossos mestres-cucas trabalham em
            sintonia para oferecer uma experiência autoral, elegante e
            memorável em cada serviço.
          </p>
          <p className="chef-signature">— A brigada Ocean Blue</p>
        </div>
      </section>

      <footer className="footer">
        <div className="footer-content content-block">
          <div className="footer-mark" aria-label="Ocean Blue logo">
            <img src="/logo.png" alt="Ocean Blue" />
            <p>Frutos do mar, arte e hospitalidade na costa brasileira.</p>
            <div className="footer-social">
              <a
                href="#"
                aria-label="Instagram"
                onClick={(event) => event.preventDefault()}
              >
                <span aria-hidden="true">IG</span>
              </a>
              <a
                href="#"
                aria-label="Facebook"
                onClick={(event) => event.preventDefault()}
              >
                <span aria-hidden="true">f</span>
              </a>
              <a
                href="#"
                aria-label="WhatsApp"
                onClick={(event) => event.preventDefault()}
              >
                <span aria-hidden="true">✆</span>
              </a>
            </div>
          </div>
          <nav className="footer-links" aria-label="Footer links">
            <a href="#top" onClick={(event) => { event.preventDefault(); scrollToSection("top"); }}>
              Ocean Blue
            </a>
            <a href="#cardapio" onClick={(event) => { event.preventDefault(); onOpenModal("cardapio"); }}>
              Cardápio
            </a>
            <a href="#reserva" onClick={(event) => { event.preventDefault(); onOpenModal("reserva"); }}>
              Reservas
            </a>
            <a href="#avaliacoes" onClick={(event) => { event.preventDefault(); onOpenModal("avaliacoes"); }}>
              Avaliações
            </a>
          </nav>
          <address className="footer-contact">
            <p>Rodovia BR 116 km 7, s/n</p>
            <p>Estrada do Mar - 25.365-123</p>
            <p>+55 21 99999-9999</p>
            <p>@oceanbluebrasil</p>
            <p className="footer-hours">
              <span>Ma–Do · 12:00–23:00</span>
              <span>Barra de ostras · 17:00–00:00</span>
            </p>
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
