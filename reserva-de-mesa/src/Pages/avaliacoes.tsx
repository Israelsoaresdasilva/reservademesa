import { useState, useEffect } from "react";
import "./avaliacoes.css";

interface Review {
  id: number;
  name: string;
  initials: string;
  rating: number;
  stars: number;
  date: string;
  title: string;
  text: string;
  cats: Record<string, number>;
  satisfied: boolean;
  featured: boolean;
  likes: number;
  _liked?: boolean;
}

const CAT_DEFS = [
  { key: "vaga", icon: "🪑", label: "Vaga" },
  { key: "ar", icon: "❄️", label: "Ar-cond." },
  { key: "comida", icon: "🍽️", label: "Comida" },
  { key: "musica", icon: "🎵", label: "Música" },
  { key: "bebida", icon: "🍹", label: "Bebidas" },
  { key: "atend", icon: "⏱️", label: "Atendimento" },
];

const avatarColors = [
  { bg: "rgba(24,95,165,0.3)", color: "#85B7EB" },
  { bg: "rgba(250,199,117,0.2)", color: "#FAC775" },
  { bg: "rgba(216,90,48,0.2)", color: "#F0997B" },
  { bg: "rgba(93,202,165,0.2)", color: "#5DCAA5" },
  { bg: "rgba(133,183,235,0.2)", color: "#B5D4F4" },
  { bg: "rgba(212,83,126,0.2)", color: "#ED93B1" },
];

const initialReviews: Review[] = [
  {
    id: 1,
    name: "Ana Beatriz M.",
    initials: "AB",
    rating: 5,
    stars: 5,
    date: "Maio 2025",
    title: "O melhor fruto do mar do Rio",
    text: "Uma experiência absolutamente extraordinária. O robalo ao molho de maracujá derreteu na boca e a vista para a Baía de Guanabara ao entardecer foi de tirar o fôlego.",
    cats: { vaga: 5, ar: 4, comida: 5, musica: 4, bebida: 5, atend: 5 },
    satisfied: true,
    featured: true,
    likes: 34,
  },
  {
    id: 2,
    name: "Carlos H. R.",
    initials: "CH",
    rating: 5,
    stars: 5,
    date: "Maio 2025",
    title: "Serviço impecável, voltarei sempre",
    text: "Trouxe minha esposa para comemorar nosso aniversário. A equipe nos surpreendeu com uma decoração especial na mesa. A lagosta grelhada estava perfeita.",
    cats: { vaga: 5, ar: 5, comida: 5, musica: 3, bebida: 4, atend: 5 },
    satisfied: true,
    featured: false,
    likes: 21,
  },
  {
    id: 3,
    name: "Fernanda S.",
    initials: "FS",
    rating: 4,
    stars: 4,
    date: "Abril 2025",
    title: "Ambiente sofisticado e aconchegante",
    text: "Fui em uma quinta-feira à noite e fiquei encantada com a decoração. A camarão na manteiga de ervas estava incrível. Só achei o ar-condicionado um pouco frio demais.",
    cats: { vaga: 4, ar: 2, comida: 5, musica: 4, bebida: 4, atend: 3 },
    satisfied: true,
    featured: false,
    likes: 15,
  },
  {
    id: 4,
    name: "Roberto A.",
    initials: "RA",
    rating: 5,
    stars: 5,
    date: "Abril 2025",
    title: "Vista para o mar é espetacular",
    text: "Mesa na varanda ao pôr do sol — não existe experiência mais bonita no Rio. O peixe do dia estava fresquíssimo e o atendimento foi muito atencioso do início ao fim.",
    cats: { vaga: 5, ar: 4, comida: 5, musica: 5, bebida: 5, atend: 5 },
    satisfied: true,
    featured: false,
    likes: 28,
  },
  {
    id: 5,
    name: "Juliana P.",
    initials: "JP",
    rating: 5,
    stars: 5,
    date: "Março 2025",
    title: "Gastronomia de nível internacional",
    text: "Morei em Lisboa por cinco anos e comi em restaurantes Michelin. O Ocean Blues está no mesmo patamar. O polvo grelhado com purê de batata-doce foi uma revelação.",
    cats: { vaga: 4, ar: 4, comida: 5, musica: 4, bebida: 5, atend: 4 },
    satisfied: true,
    featured: false,
    likes: 42,
  },
  {
    id: 6,
    name: "Marcelo T.",
    initials: "MT",
    rating: 4,
    stars: 4,
    date: "Março 2025",
    title: "Ótima opção para jantares especiais",
    text: "Reserva fácil pelo app, chegamos no horário marcado. A carta de vinhos é muito bem curada. A música estava um pouco alta para conversar.",
    cats: { vaga: 3, ar: 4, comida: 4, musica: 2, bebida: 5, atend: 4 },
    satisfied: true,
    featured: false,
    likes: 9,
  },
];

function StarSVG({ filled, size = 14 }: { filled: boolean; size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill={filled ? "#FAC775" : "none"}
      stroke={filled ? "#FAC775" : "rgba(255,255,255,0.2)"}
      strokeWidth="1.5"
    >
      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01z" />
    </svg>
  );
}

function Avaliacoes() {
  const [reviews, setReviews] = useState<Review[]>(initialReviews);
  const [currentFilter, setCurrentFilter] = useState("all");
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedStars, setSelectedStars] = useState(0);
  const [satisfaction, setSatisfaction] = useState<boolean | null>(null);
  const [formData, setFormData] = useState({
    name: "",
    title: "",
    text: "",
    vaga: 3,
    ar: 3,
    comida: 3,
    musica: 3,
    bebida: 3,
    atend: 3,
  });

  const catAvg = (key: string) => {
    const vals = reviews
      .map((r) => r.cats?.[key] || 3)
      .filter((v) => v !== undefined);
    return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
  };

  const avgRating =
    reviews.length > 0
      ? reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length
      : 0;

  const recPct =
    reviews.length > 0
      ? Math.round(
          (reviews.filter((r) => r.satisfied).length / reviews.length) * 100
        )
      : 0;

  const filtered = reviews.filter((r) => {
    if (currentFilter === "all") return true;
    if (currentFilter === "5") return r.stars === 5;
    if (currentFilter === "4") return r.stars === 4;
    if (currentFilter === "3") return r.stars === 3;
    if (currentFilter === "sat") return r.satisfied;
    return true;
  });

  const handleSubmit = () => {
    if (
      !formData.name ||
      !formData.title ||
      !formData.text ||
      selectedStars === 0 ||
      satisfaction === null
    ) {
      alert("Preencha todos os campos, selecione a nota e indique se recomenda.");
      return;
    }

    const initials = formData.name
      .split(" ")
      .slice(0, 2)
      .map((w) => w[0].toUpperCase())
      .join("");

    const newReview: Review = {
      id: Date.now(),
      name: formData.name,
      initials,
      rating: selectedStars,
      stars: selectedStars,
      date: "Agora",
      title: formData.title,
      text: formData.text,
      cats: {
        vaga: formData.vaga,
        ar: formData.ar,
        comida: formData.comida,
        musica: formData.musica,
        bebida: formData.bebida,
        atend: formData.atend,
      },
      satisfied: satisfaction,
      featured: false,
      likes: 0,
    };

    setReviews([newReview, ...reviews]);
    setModalOpen(false);
    setSelectedStars(0);
    setSatisfaction(null);
    setFormData({
      name: "",
      title: "",
      text: "",
      vaga: 3,
      ar: 3,
      comida: 3,
      musica: 3,
      bebida: 3,
      atend: 3,
    });
  };

  const toggleLike = (id: number) => {
    setReviews(
      reviews.map((r) => {
        if (r.id === id) {
          return {
            ...r,
            _liked: !r._liked,
            likes: r._liked ? r.likes - 1 : r.likes + 1,
          };
        }
        return r;
      })
    );
  };

  const starCounts = [0, 0, 0, 0, 0];
  reviews.forEach((r) => starCounts[r.stars - 1]++);
  const maxCount = Math.max(...starCounts) || 1;

  return (
    <div className="avaliacoes-container">
      <div className="container">
        <header className="avaliacao-header">
          <div className="logo-wave">
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
          </div>
          <div className="project-tag">Reserva de Mesa</div>
          <h1>
            Ocean <em>Blues</em>
          </h1>
          <p className="tagline">
            Frutos do mar · Gastronomia de autor · Rio de Janeiro
          </p>

          <div className="rating-hero">
            <div className="big-score">
              <div className="number">{avgRating.toFixed(1)}</div>
              <div className="stars-row">
                {Array.from({ length: 5 }).map((_, i) => (
                  <span key={i} className="star">
                    <StarSVG filled={i < Math.round(avgRating)} size={22} />
                  </span>
                ))}
              </div>
              <div className="out-of">de 5.0 estrelas</div>
            </div>

            <div className="rating-bars">
              {[5, 4, 3, 2, 1].map((star) => {
                const count = starCounts[star - 1];
                const pct = ((count / maxCount) * 100).toFixed(0);
                return (
                  <div key={star} className="bar-row">
                    <span className="bar-label">{star} ★</span>
                    <div className="bar-track">
                      <div
                        className="bar-fill"
                        style={{
                          width: pct + "%",
                          animationDelay: (5 - star) * 0.1 + "s",
                        }}
                      ></div>
                    </div>
                    <span className="bar-count">{count}</span>
                  </div>
                );
              })}
            </div>

            <div className="stats-col">
              <div className="stat-item">
                <div className="stat-num">{reviews.length}</div>
                <div className="stat-label">Avaliações</div>
              </div>
              <div className="stat-item">
                <div className="stat-num">{recPct}%</div>
                <div className="stat-label">Recomendam</div>
              </div>
            </div>
          </div>

          <div className="cat-scores">
            {CAT_DEFS.map((c) => {
              const avg = catAvg(c.key);
              const color =
                avg >= 4.5 ? "#5DCAA5" : avg >= 3.5 ? "#FAC775" : "#F0997B";
              return (
                <div key={c.key} className="cat-score-card">
                  <div className="cat-icon">{c.icon}</div>
                  <div className="cat-name">{c.label}</div>
                  <div className="cat-val" style={{ color }}>
                    {avg.toFixed(1)}
                  </div>
                  <div className="cat-mini-stars">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <span key={i} className="star">
                        <StarSVG filled={i < Math.round(avg)} size={11} />
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </header>

        <div className="filters-bar">
          {["all", "5", "4", "3", "sat"].map((filter) => {
            const labels: Record<string, string> = {
              all: "Todas",
              "5": "★ 5 estrelas",
              "4": "★ 4 estrelas",
              "3": "★ 3 estrelas",
              sat: "Satisfeitos",
            };
            return (
              <button
                key={filter}
                className={`filter-btn ${currentFilter === filter ? "active" : ""}`}
                onClick={() => setCurrentFilter(filter)}
              >
                {labels[filter]}
              </button>
            );
          })}
          <button
            className="write-btn"
            onClick={() => setModalOpen(true)}
          >
            ✦ Escrever avaliação
          </button>
        </div>

        <div className="reviews-grid">
          {filtered.map((r, i) => {
            const color = avatarColors[i % avatarColors.length];
            return (
              <div
                key={r.id}
                className={`review-card ${r.featured ? "featured" : ""}`}
              >
                {r.featured && (
                  <span className="featured-badge">✦ Avaliação em destaque</span>
                )}
                <div className="card-header">
                  <div className="reviewer-info">
                    <div
                      className="avatar"
                      style={{
                        background: color.bg,
                        color: color.color,
                      }}
                    >
                      {r.initials}
                    </div>
                    <div>
                      <div className="reviewer-name">{r.name}</div>
                      <div className="reviewer-meta">{r.date}</div>
                    </div>
                  </div>
                  <div className="card-stars">
                    {Array.from({ length: 5 }).map((_, j) => (
                      <span key={j} className="star">
                        <StarSVG filled={j < r.rating} size={14} />
                      </span>
                    ))}
                  </div>
                </div>
                <div className="review-title">{r.title}</div>
                <p className="review-text">{r.text}</p>

                {r.satisfied !== undefined && (
                  <div className={`sat-badge ${r.satisfied ? "yes" : "no"}`}>
                    {r.satisfied
                      ? "✔ Recomenda"
                      : "✖ Não recomenda"}
                  </div>
                )}

                <div className="card-cats">
                  {CAT_DEFS.map((c) => (
                    <div key={c.key} className="card-cat-item">
                      <div className="card-cat-icon">{c.icon}</div>
                      <div className="card-cat-dots">
                        {Array.from({ length: 5 }).map((_, j) => {
                          const val = r.cats[c.key] || 0;
                          const on = j < val;
                          const hi = on && val >= 4;
                          return (
                            <div
                              key={j}
                              className={`dot${on ? " on" : ""}${hi ? " hi" : ""}`}
                            ></div>
                          );
                        })}
                      </div>
                      <div className="card-cat-label">{c.label}</div>
                    </div>
                  ))}
                </div>

                <div className="card-footer">
                  <div></div>
                  <button
                    className={`helpful-btn ${r._liked ? "liked" : ""}`}
                    onClick={() => toggleLike(r.id)}
                  >
                    <svg
                      width="12"
                      height="12"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                    >
                      <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3H14z" />
                      <path d="M7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3" />
                    </svg>
                    {r.likes}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <footer>
        <div className="footer-logo">Ocean Blues</div>
        <small>Reserva de Mesa © 2025 · Todos os direitos reservados</small>
      </footer>

      {modalOpen && (
        <div
          className="modal-overlay open"
          onClick={(e) => {
            if (e.target === e.currentTarget) setModalOpen(false);
          }}
        >
          <div className="modal-box">
            <h2>Sua avaliação</h2>
            <p className="sub">Conte-nos sobre sua experiência no Ocean Blues</p>

            <div className="form-group">
              <label>Nota geral</label>
              <div className="star-picker">
                {[1, 2, 3, 4, 5].map((val) => (
                  <svg
                    key={val}
                    className={`sp-star ${selectedStars >= val ? "on" : ""}`}
                    viewBox="0 0 24 24"
                    fill="currentColor"
                    onClick={() => setSelectedStars(val)}
                    onMouseEnter={() => setSelectedStars(val)}
                  >
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01z" />
                  </svg>
                ))}
              </div>
            </div>

            <div className="cats-section">
              <label>Avalie cada item (1 a 5)</label>
              <div className="cat-sliders-grid">
                {["vaga", "ar", "comida", "musica", "bebida", "atend"].map(
                  (key, idx) => {
                    const cat = CAT_DEFS[idx];
                    return (
                      <div key={key} className="cat-slider-row">
                        <div className="cat-slider-header">
                          <div className="cat-slider-name">
                            <span>{cat.icon}</span> {cat.label}
                          </div>
                          <div className="cat-slider-val">
                            {formData[key as keyof typeof formData]}
                          </div>
                        </div>
                        <input
                          type="range"
                          className="cat-range"
                          min="1"
                          max="5"
                          value={formData[key as keyof typeof formData]}
                          onChange={(e) =>
                            setFormData({
                              ...formData,
                              [key]: parseInt(e.target.value),
                            })
                          }
                        />
                      </div>
                    );
                  }
                )}
              </div>
            </div>

            <div className="form-group">
              <label>Ficou satisfeito com a experiência?</label>
              <div className="satisfaction-row">
                <button
                  className={`sat-btn yes ${satisfaction === true ? "active" : ""}`}
                  onClick={() => setSatisfaction(true)}
                >
                  ✔ Sim, recomendo
                </button>
                <button
                  className={`sat-btn no ${satisfaction === false ? "active" : ""}`}
                  onClick={() => setSatisfaction(false)}
                >
                  ✖ Não recomendo
                </button>
              </div>
            </div>

            <div className="form-group">
              <label>Seu nome</label>
              <input
                type="text"
                placeholder="Ex: Maria S."
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
              />
            </div>
            <div className="form-group">
              <label>Título da avaliação</label>
              <input
                type="text"
                placeholder="Ex: Uma experiência inesquecível"
                value={formData.title}
                onChange={(e) =>
                  setFormData({ ...formData, title: e.target.value })
                }
              />
            </div>
            <div className="form-group">
              <label>Sua experiência</label>
              <textarea
                placeholder="Conte o que você mais gostou..."
                value={formData.text}
                onChange={(e) =>
                  setFormData({ ...formData, text: e.target.value })
                }
              ></textarea>
            </div>

            <div className="modal-actions">
              <button
                className="btn-cancel"
                onClick={() => setModalOpen(false)}
              >
                Cancelar
              </button>
              <button className="btn-submit" onClick={handleSubmit}>
                Publicar avaliação
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Avaliacoes;
