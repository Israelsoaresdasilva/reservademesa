# Mapa del proyecto

## Directorios relevantes
- public/
  - assets estáticos y archivos HTML públicos
  - incluye el cardápio original en HTML

- src/
  - App.tsx
  - App.css (sistema de diseño + componentes visuales)
  - main.tsx
  - assets/
  - features/
  - Pages/

## Páginas y flujos
### Home
- Hero con vídeo (ESTADO ORIGINAL: vídeo sin filtro, overlay transparente, marca centrada con animación fade-up)
- Presentación del restaurante (`.about-section`) con chips de atributos: pescado fresco, carta de vinos, vista al océano
- Especialidades (`.suites-section`, banda navy) con cards que se elevan al hover, zoom de imagen y chip de ranking Nº 01–03
- Experiencia gastronómica (`.experience-section`) con estadísticas (40+ platos, 18 vinos & espumantes, 4.9) y collage de imágenes con marco punteado
- Cardápio widget flotante estilo chat (fijo inferior derecho)
- Eventos (`.events-card`, card navy superpuesto sobre imagen) con chips: aniversarios, corporativos, a la orilla del mar
- Cita de marca (`.quote-section`, banda navy full-width con comilla decorativa)
- Testimonios (`.testimonials-section`, grid de 3 cards con estrellas, cita y autor)
- Equipo (`.chef-team-section`) con badge "20+ años de cocina" y firma
- Footer con logo, descripción, redes sociales, enlaces, contacto y horarios

### Cardápio
- Widget flotante estilo chat, fijo en la esquina inferior derecha
- Estado cerrado muestra el header compacto (avatar 🍽️, "Ocean Blue", "Cardápio Fechado")
- Estado abierto expande un panel con categorías, búsqueda e ítems con foto
- Sin overlay/blur: no bloquea la interacción con el resto de la página

### Reserva
- Flujo de selección de mesa y reserva
- Modal destacado y con foco en la acción principal

### Evaluaciones
- Visual de feedback del cliente
- Modal de destaque separado

## Arquivos sensibles
- App.tsx: punto central del comportamiento de la UI
- App.css: sistema de diseño (tokens en `:root`, componentes, media queries 1140/920/620)
- homepage.tsx: mayor volumen de contenido de la interfaz y control de la animación `.reveal`

## Recomendación para trabajo futuro
Aprovechar la estructura existente y el sistema de tokens de App.css para evolucionar el sitio sin perder la identidad visual del restaurante. El proyecto favorece la composición por bloques: nuevos componentes deben encajar en el mismo patrón (clases `.reveal`, tokens, elevación al hover, botones pill). No modificar el hero sin autorización explícita.