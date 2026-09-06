# Documentação do projeto

## Visão geral
Este projeto é um site de restaurante para reservas, visualização de cardápio e avaliações, construído em React + TypeScript + Vite.

Fue concebido como uma landing page moderna com navegación por seções, modales e componentes reutilizables para fluxo de reserva, apresentación do menu e feedback do cliente.

## Objetivo principal
- Mostrar o restaurante e seus diferenciais
- Permitir reservas de mesa
- Exibir cardápio digital
- Colectar e apresentar avaliações
- Ofrecer una experiencia visual moderna e responsiva

## Stack
- React 19
- TypeScript
- Vite
- CSS customizado (src/App.css actúa como sistema de diseño: tokens, componentes, animaciones)
- Three.js / React Three Fiber en partes del proyecto (presente en componentes de mapa/visualización)

## Estructura principal
- src/App.tsx: controle principal de los modales y composición general
- src/Pages/homepage.tsx: página inicial (hero, presentación, especialidades, experiencia, eventos, cita, testimonios, equipo y pie de página)
- src/Pages/reservas/: pantallas y lógica de reservas
- src/Pages/avaliacoes.tsx: página/visualización de evaluaciones
- src/features/notifications/: provider y centro de notificaciones
- src/App.css: estilos globales y sistema de diseño (tokens en `:root`)
- public/: assets estáticos, incluyendo el cardápio HTML

## Comandos útiles
- npm install
- npm run dev
- npm run build
- npm run preview
- npm run lint

## Reglas de mantenimiento
- Preferir componentes reutilizables y consistentes con el visual existente
- Mantener los modales (reserva y evaluaciones) y el widget flotante del cardápio separados por tipo de contenido
- No romper la navegación ni la presentación visual de la home
- Al modificar estilos, verificar el impacto en mobile y desktop
- Usar los tokens de `:root` de App.css (colores, sombras, radios, easing) en lugar de valores sueltos
- Mantener la animación de aparición al hacer scroll (clase `.reveal` + IntersectionObserver) y respetar `prefers-reduced-motion`

## Observaciones importantes para IA
- El proyecto usa una combinación de CSS customizado y componentes React
- El cardápio es un widget flotante estilo chat (sin overlay/blur), fijo a la derecha abajo; cerrado muestra el header y abierto expande el panel
- El app centraliza algunos flujos de modal en App.tsx
- El proyecto funciona como SPA con bloques de contenido y capas superpuestas
- La home fue rediseñada por completo; el hero se mantuvo EXACTAMENTE original (ver docs/ai-context.md)

## Puntos de atención
- El cardápio sigue siempre el patrón de widget flotante estilo chat (las versiones de página/modal fueron sustituidas por ese patrón)
- El sistema de notificaciones está centralizado y debe respetarse
- Los componentes visuales deben mantener la identidad del restaurante: navy profundo, azur, dorado como acento, ambiente costero
- Hero con vídeo — ESTADO ORIGINAL preservado: el vídeo (public/Video Project 1.mp4, 1920x1080 16:9) ocupa 100% de ancho y define la altura del hero vía aspect-ratio 1920/1080, limitado a una pantalla con max-height: calc(100vh - 96px) y object-fit: cover. NO reintroducir min-height fija, filtros sobre el vídeo, overlay oscuro, badges, CTAs extra ni indicador de scroll en el hero.