# Ocean Blue - Sistema de Reservas e Cardápio

Este projeto é um sistema moderno para reservas de restaurante com visualização de mesas, cardápio digital e navegação SPA, desenvolvido em React + TypeScript.

## Desenvolvidos por

Keila da cunha rezende - 06015370
Israel Soares da Silva - 06010016
Matheus Prudente Silva - 06003440
Savio Emmanuel Silva da Conceição - 06009864
Patrick Quintino - 06016924

## Como rodar o projeto

1. Instale as dependências:
   ```bash
   npm install
   ```
2. Inicie o servidor de desenvolvimento:
   ```bash
   npm run dev
   ```
3. Acesse:
   - SPA: [http://localhost:5173/](http://localhost:5173/)
   - Cardápio: [http://localhost:5173/Cardápio.html](http://localhost:5173/Cardápio.html)

## Estrutura do Projeto

```
reservademesa/
  reserva-de-mesa/
    public/
      Cardápio.html         # Cardápio digital (HTML puro)
      Ocean Blue.png        # Imagens usadas no cardápio
      ...
    src/
      App.tsx              # Configuração de rotas SPA
      Pages/
        homepage.tsx       # Página inicial
        reservas/
          reservas.tsx     # Lógica de reservas
          MapFloor.tsx     # Mapa/calibração de mesas
        avaliacoes.tsx     # Tela de avaliações
      features/
        notifications/     # Sistema de notificações
      assets/              # Imagens e recursos
    package.json
    README.md
```

## Observações

- O cardápio é um arquivo HTML puro, mantido na pasta `public` para preservar o layout original.
- As imagens usadas no cardápio devem estar também na pasta `public`.
- As rotas SPA são gerenciadas pelo React Router.
- O projeto utiliza Vite
