import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./Pages/homepage";
import Reservas from "./Pages/reservas/reservas";
import {
  NotificationCenter,
  NotificationProvider,
} from "./features/notifications";
import Avaliacoes from "./Pages/avaliacoes";

function App() {
  return (
    <NotificationProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/reservas" element={<Reservas />} />
          <Route path="/avaliacoes" element={<Avaliacoes />} />
        </Routes>
        <NotificationCenter />
      </BrowserRouter>
    </NotificationProvider>
  );
}

export default App;
