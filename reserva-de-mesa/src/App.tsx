import { BrowserRouter, Routes, Route } from "react-router-dom"
import HomePage from "./Pages/homepage"
import Reservas from "./Pages/reservas"

function App() {
	return (
		<BrowserRouter>
			<Routes>
				<Route path="/" element={<HomePage />} />
				<Route path="/reservas" element={<Reservas />} />
			</Routes>
		</BrowserRouter>
	)
}

export default App