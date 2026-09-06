# Contexto para IA

## Identidad del proyecto
Proyecto de restaurante llamado Ocean Blue. El visual y el lenguaje deben mantener un tono elegante, naval, limpio y moderno, con referencia al mar, la luz del litoral y un menú premium de frutos del mar.

## Directrices de diseño
- Paleta oceánica profunda (tokens en `:root` de App.css): navy en 5 escalas (`--navy-950` a `--navy-700`), azules medios (`--blue-600/500`), azur (`--azure`, `--azure-light`) y cielo (`--sky`); dorado (`--gold`, #f5b968) como acento para estrellas, badges y detalles
- Fondos: bandas navy en degradado para secciones de impacto (especialidades, eventos, cita) y tonos claros crema/blanco para las secciones de lectura
- Botones tipo pill (border-radius 999px) con gradiente azur y hover que eleva el botón (translateY(-2px) + sombra)
- Sombras y radios tokenizados (`--shadow-sm/md/lg`, `--radius-sm/md/lg`); easing estándar `--ease`
- Alto contraste y acabado premium; evitar estilos pesados o caóticos

## Estructura de contenido
La interfaz principal está compuesta por:
1. Hero principal — ESTADO ORIGINAL (vídeo sin filtro, overlay transparente, títulos pastel, sin CTAs extra)
2. Presentación del restaurante (chips de atributos)
3. Especialidades / destacados de platos (banda navy, cards con ranking)
4. Experiencia gastronómica (estadísticas + collage)
5. Eventos (card navy sobre imagen, con chips)
6. Cita de marca
7. Testimonios (3 cards)
8. Equipo
9. Pie de página

## Flujos principales
- Clic en reservar → abre el modal de reserva
- Clic en cardápio → expande el widget flotante estilo chat (esquina inferior derecha)
- Cerrado, el widget muestra solo el header (avatar, "Ocean Blue", "Cardápio Fechado") y no bloquea el sitio
- Abierto, el widget expande un panel con categorías, búsqueda e ítems con foto
- Clic en evaluaciones → abre el modal de evaluaciones
- Sistema de notificaciones para confirmaciones y etapas del flujo

## Enseñanza de implementación
- Preferir evolucionar componentes existentes en lugar de crear estructuras totalmente nuevas
- Mantener consistencia de clases, tipos y nombres entre App.css y JSX
- El cardápio funciona como componente integrado (widget flotante), no como pantalla separada
- Los componentes expansibles deben mantener reutilización y evitar romper el layout general
- Nuevas secciones con animación de scroll: añadir la clase `.reveal` en el JSX (el `IntersectionObserver` de homepage.tsx agregará `.is-visible` al entrar en viewport)

## Limitaciones y cuidados
- No remover la lógica central de modales en App.tsx (reserva y evaluaciones) sin ajustar el flujo de navegación
- El widget flotante del cardápio es controlado en App.tsx junto a los modales, pero NO usa overlay ni blur
- No alterar las suposiciones de public/ para imágenes estáticas sin verificar la ruta de uso
- El cardápio puede tener versiones diferentes según el contexto, pero debe mantener legibilidad y coherencia visual
- Evitar duplicación excesiva de estilos; preferir extensiones por clases específicas y usar los tokens de `:root`
- HERO — NO MODIFICAR: conservar exactamente el estado original (App.css .hero/.hero-video/.overlay/.brand-block). No reintroducir `.hero-badge`, `.hero-actions`, `.hero-cta*`, `.hero-scroll-cue` ni `@keyframes heroCue`. El vídeo debe seguir en flujo con width 100%, aspect-ratio 1920/1080, max-height de una viewport (calc(100vh - 96px) y 104px en móvil), object-fit cover, object-position center, `filter: none`, y el overlay con `background: none`
- Animación de scroll: los elementos con `.reveal` comienzan en opacity 0; al agregar nuevos bloques recordar incluir la clase (y verificar el fallback de `prefers-reduced-motion`, que desactiva animaciones)

## Objetivo del agente de IA
El proyecto debe seguir funcionando como landing page, con modularización y buena experiencia visual. Cualquier cambio debe considerar:
- usabilidad
- visual premium
- compatibilidad con el resto de la interfaz
- facilidad de mantenimiento
- respeto del estado original del hero