# Guia de desenvolvimento

## Ambiente
- Node.js + npm
- Vite
- TypeScript
- React 19

## Instalación
```bash
npm install
```

## Ejecución local
```bash
npm run dev
```

## Build
```bash
npm run build
```

## Lint
```bash
npm run lint
```

## Estructura crítica
- src/App.tsx: modal principal y composición de la interfaz
- src/Pages/homepage.tsx: landing page y bloques de contenido
- src/Pages/reservas/: flujo de reserva y mapa
- src/features/notifications/: notificaciones del app
- src/App.css: sistema de diseño global (tokens, componentes visuales, animaciones)
- public/: assets estáticos y cardápio HTML

## Convenciones
- Preferir componentes reutilizables
- Mantener el visual premium y consistente con la identidad del restaurante
- No romper el flujo de modales entre reserva y evaluaciones, ni el widget flotante del cardápio
- Validar siempre el build tras cambios visuales y de estructura
- Usar los tokens de `:root` de App.css (paleta `--navy-*`, `--azure*`, `--gold`; `--shadow-*`, `--radius-*`, `--ease`) en lugar de hex sueltos
- Los bloques que deben aparecer al hacer scroll usan la clase `.reveal` (opacity/transform iniciales); el componente `homepage.tsx` agrega `.is-visible` vía `IntersectionObserver`
- Respetar `prefers-reduced-motion` para animaciones y elementos decorativos

## Dicas para IA
- El proyecto es una SPA con varios bloques visuales y capas de superposición
- El cardápio es un widget flotante estilo chat (cerrado = header compacto; abierto = panel con categorías, búsqueda y fotos)
- El widget del cardápio no debe bloquear la interacción con el resto del sitio (sin overlay ni blur)
- Modales (reserva y evaluaciones) y notificaciones son parte central de la experiencia
- Priorizar mantenimiento, claridad y compatibilidad con el resto de la UI
- El hero está en ESTADO ORIGINAL: no agregar filtros al vídeo, overlays oscuros, badges, botones extra ni indicadores de scroll (ver docs/ai-context.md)
- Los media queries de App.css operan en 1140px / 920px / 620px; verificar el layout en cada breakpoint