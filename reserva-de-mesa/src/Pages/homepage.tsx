import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import "../App.css"

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
]

function ReservationBar() {
	const navigate = useNavigate();
	function handleSubmit(e: React.FormEvent) {
		e.preventDefault();
		navigate("/reservas");
	}
	return (
		<form className="reservation-floating" aria-label="Table reservation form" onSubmit={handleSubmit}>
			<label className="field">
				<span className="sr-only">Reservation date</span>
				<input type="text" placeholder="DATA" aria-label="Reservation date" />
				<svg viewBox="0 0 24 24">
					<path d="M7 2h2v3h6V2h2v3h3a2 2 0 0 1 2 2v13a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h3V2Zm13 8H4v10h16V10Zm-2-3H6v1h12V7Z" />
				</svg>
			</label>
			<label className="field">
				<span className="sr-only">Reservation time</span>
				<input type="text" placeholder="HORARIO" aria-label="Reservation time" />
				<svg viewBox="0 0 24 24">
					<path d="M7 2h2v3h6V2h2v3h3a2 2 0 0 1 2 2v13a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h3V2Zm13 8H4v10h16V10Zm-2-3H6v1h12V7Z" />
				</svg>
			</label>
			<button type="submit" className="submit-button">
				RESERVAR MESA
			</button>
		</form>
	);
}


function Sidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
	return (
		<>
			<div
				className={`sidebar-backdrop${open ? " sidebar-backdrop--visible" : ""}`}
				onClick={onClose}
			/>

			<nav className={`sidebar${open ? " sidebar--open" : ""}`}>
				<div className="sidebar-top">
					<button className="sidebar-close" onClick={onClose}>
						X
					</button>
				</div>

				<div className="sidebar-logo">
					<img src="/logo.png" alt="Ocean Blue" />
				</div>

				<ul className="sidebar-nav">
					{[
						"Ocean Blue",
						"Cardapio",
						"Gastronomia",
						"Experiencias",
						"Eventos",
						"Reservas",
					].map((item) => (
						<li key={item}>
							<a href="#">{item.toUpperCase()}</a>
						</li>
					))}
				</ul>
			</nav>
		</>
	)
}

export default function HomePage() {
	const [sidebarOpen, setSidebarOpen] = useState(false)

	return (
		<main className="home-page">
			<Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

			<header className="top-bar top-fixed">
				<div className="left-tools">
					<button
						className="icon-button"
						onClick={() => setSidebarOpen(true)}
					>
						<span />
						<span />
						<span />
					</button>
				</div>

				<div className="top-brand">
					<img src="/logo.png" alt="Ocean Blue" />
				</div>

				 <Link to="/reservas" className="reserve-button">RESERVAR</Link>
			</header>

			<section className="hero">
				<video className="hero-video" autoPlay muted loop playsInline>
					<source src="/Video%20Project%201.mp4" type="video/mp4" />
				</video>

				<div className="overlay" />

				<div className="brand-block">
					<p className="brand-title">OCEAN BLUE</p>
					<p className="brand-subtitle">Sabores do mar, tradição à mesa</p>
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

			<footer className="footer">
				<div className="footer-content content-block">
					<div className="footer-mark">
						<img src="/logo.png" alt="Ocean Blue" />
					</div>
				</div>

				<p className="copyright">
					COPYRIGHT 2026 OCEAN BLUE RESTAURANTE - TODOS OS DIREITOS RESERVADOS.
				</p>
			</footer>

			<ReservationBar />
		</main>
	)
}