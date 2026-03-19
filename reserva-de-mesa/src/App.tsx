import { BrowserRouter, Routes, Route } from "react-router-dom"
import HomePage from "./Pages/homepage"
import Reservas from "./Pages/reservas/reservas"
import { NotificationCenter, NotificationProvider } from "./features/notifications"

function App() {
	return (
		<NotificationProvider>
			<BrowserRouter>
				<Routes>
					<Route path="/" element={<HomePage />} />
					<Route path="/reservas" element={<Reservas />} />
				</Routes>
				<NotificationCenter />
			</BrowserRouter>
		</NotificationProvider>
	)
}

export default App
