import { useState } from 'react'
import './App.css'

const seafoodHighlights = [
	{
		title: 'OSTRAS FRESCAS',
		image:
			'https://images.unsplash.com/photo-1559737558-2f5a35f4523b?auto=format&fit=crop&w=1200&q=80',
	},
	{
		title: 'RISOTO DE CAMARAO',
		image:
			'https://images.unsplash.com/photo-1476124369491-e7addf5db371?auto=format&fit=crop&w=1200&q=80',
	},
	{
		title: 'PAELLA DO CHEF',
		image:
			'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=1200&q=80',
	},
]

function ReservationBar() {
	return (
		<form className="reservation-floating" aria-label="Table reservation form">
			<label className="field">
				<span className="sr-only">Reservation date</span>
				<input type="text" placeholder="DATA" aria-label="Reservation date" />
				<svg viewBox="0 0 24 24" aria-hidden="true">
					<path d="M7 2h2v3h6V2h2v3h3a2 2 0 0 1 2 2v13a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h3V2Zm13 8H4v10h16V10Zm-2-3H6v1h12V7Z" />
				</svg>
			</label>
			<label className="field">
				<span className="sr-only">Reservation time</span>
				<input type="text" placeholder="HORARIO" aria-label="Reservation time" />
				<svg viewBox="0 0 24 24" aria-hidden="true">
					<path d="M7 2h2v3h6V2h2v3h3a2 2 0 0 1 2 2v13a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h3V2Zm13 8H4v10h16V10Zm-2-3H6v1h12V7Z" />
				</svg>
			</label>
			<button type="submit" className="submit-button">
				RESERVAR MESA
			</button>
		</form>
	)
}

function Sidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
	return (
		<>
			<div
				className={`sidebar-backdrop${open ? ' sidebar-backdrop--visible' : ''}`}
				onClick={onClose}
				aria-hidden="true"
			/>
			<nav
				className={`sidebar${open ? ' sidebar--open' : ''}`}
				aria-label="Menu principal"
				aria-hidden={!open}
			>
				<div className="sidebar-top">
					<button className="sidebar-close" onClick={onClose} aria-label="Fechar menu">
						<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/></svg>
					</button>
					<div className="sidebar-header-info">
						<div className="language-switch sidebar-lang" aria-label="Language selector">
							<span>PT</span>
							<span className="separator">|</span>
							<span className="inactive">EN</span>
						</div>
						<a className="phone-link" href="tel:+552420260003" aria-label="Ligar para o restaurante">
							<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.7 10.8a15.2 15.2 0 0 0 6.5 6.5l2.2-2.2a1 1 0 0 1 1-.24 11 11 0 0 0 3.45.55 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17.8 17.8 0 0 1 3 4a1 1 0 0 1 1-1h3.6a1 1 0 0 1 1 1c0 1.2.18 2.36.55 3.45a1 1 0 0 1-.25 1.02L6.7 10.8Z" /></svg>
							<span>+55 24 2026 0003</span>
						</a>
					</div>
				</div>

				<div className="sidebar-logo">
					<img src="/logo.png" alt="Ocean Blue" />
				</div>

				<ul className="sidebar-nav">
					{['Ocean Blue', 'Cardapio', 'Gastronomia', 'Experiencias', 'Eventos', 'Reservas'].map((item) => (
						<li key={item}>
							<a href="#" onClick={onClose}>{item.toUpperCase()}</a>
						</li>
					))}
				</ul>
			</nav>
		</>
	)
}

function App() {
	const [sidebarOpen, setSidebarOpen] = useState(false)
	return (
		<main className="home-page">
			<Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
			<header className="top-bar top-fixed">
				<div className="left-tools">
					<button className="icon-button" aria-label="Open navigation menu" onClick={() => setSidebarOpen(true)}>
						<span />
						<span />
						<span />
					</button>
					<div className="language-switch" aria-label="Language selector">
						<span>PT</span>
						<span className="separator">|</span>
						<span className="inactive">EN</span>
					</div>
					<a className="phone-link" href="tel:+552420260003" aria-label="Call restaurant">
						<svg viewBox="0 0 24 24" aria-hidden="true">
							<path d="M6.7 10.8a15.2 15.2 0 0 0 6.5 6.5l2.2-2.2a1 1 0 0 1 1-.24 11 11 0 0 0 3.45.55 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17.8 17.8 0 0 1 3 4a1 1 0 0 1 1-1h3.6a1 1 0 0 1 1 1c0 1.2.18 2.36.55 3.45a1 1 0 0 1-.25 1.02L6.7 10.8Z" />
						</svg>
						<span>+55 24 2026 0003</span>
					</a>
				</div>
				<div className="top-brand" aria-label="Ocean Blue logo">
					<img src="/logo.png" alt="Ocean Blue" />
				</div>
				<button className="reserve-button" type="button">
					RESERVAR
				</button>
			</header>

			<section className="hero" aria-label="Ocean Blue seafood restaurant cover">
				<video className="hero-video" autoPlay muted loop playsInline>
					<source src="/Video%20Project%201.mp4" type="video/mp4" />
				</video>
				<div className="overlay" />
				<div className="brand-block" role="img" aria-label="Ocean Blue branding">
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
						Localizado na costa brasileira, o Ocean Blue e um restaurante de frutos do mar
						que celebra ingredientes frescos, receitas autorais e a atmosfera unica do litoral.
					</p>
					<p>
						Do almoço a luz do dia ao jantar especial, cada experiencia combina atendimento
						acolhedor, carta de vinhos selecionada e vistas inspiradoras para momentos inesqueciveis.
					</p>
					<button type="button" className="small-sand-button">
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
						Do bar de ostras aos pratos quentes autorais, nosso menu foi pensado para surpreender
						o paladar com texturas, aromas e harmonizacoes que valorizam o melhor do oceano.
					</p>
					<button type="button" className="small-sand-button">
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
						Do aniversario intimista ao evento corporativo, montamos experiencias personalizadas
						com menu de frutos do mar, servico dedicado e ambientacao elegante a beira-mar.
					</p>
					<button type="button" className="outline-button">
						SOLICITAR EVENTO
					</button>
				</div>
			</section>

			<section className="quote-section content-block">
				<p>Saboreie a experiencia Ocean Blue</p>
			</section>

			<section className="chef-team-section content-block" aria-label="Equipe de mestres-cucas">
				<div className="chef-team-media">
					<img
						src="/image.png"
						alt="Equipe de mestres-cucas do Ocean Blue"
					/>
				</div>
				<div className="chef-team-copy">
					<p className="eyebrow">Nossa equipe</p>
					<h2>MESTRES-CUCAS QUE TRANSFORMAM O MAR EM ARTE</h2>
					<p>
						Nossa brigada e formada por chefs especializados em frutos do mar, com tecnica apurada
						e paixao por ingredientes frescos. Cada prato nasce de pesquisa, criatividade e respeito
						pelos sabores do oceano.
					</p>
					<p>
						Da cozinha quente ao bar de crus, nossos mestres-cucas trabalham em sintonia para
						oferecer uma experiencia autoral, elegante e memoravel em cada servico.
					</p>
				</div>
			</section>

			<footer className="footer">
				<div className="footer-content content-block">
					<div className="footer-mark" aria-label="Ocean Blue logo">
						<img src="/logo.png" alt="Ocean Blue" />
					</div>
					<nav className="footer-links" aria-label="Footer links">
						<a href="#">Ocean Blue</a>
						<a href="#">Cardapio</a>
						<a href="#">Gastronomia</a>
						<a href="#">Experiencias</a>
						<a href="#">Eventos</a>
						<a href="#">Reservas</a>
					</nav>
					<address className="footer-contact">
						<p>Rodovia BR 040 km 38, s/n</p>
						<p>Estrada Julioca - 25.845-000</p>
						<p>+55 24 2026-0003</p>
						<p>@oceanbluebrasil</p>
						<p className="mail">reservas@oceanblue.com.br</p>
					</address>
				</div>
				<p className="copyright">COPYRIGHT 2026 OCEAN BLUE RESTAURANTE - TODOS OS DIREITOS RESERVADOS.</p>
			</footer>

			<ReservationBar />
		</main>
	)
}

export default App
