import { useState } from "react"

type Table = {
  id: number
  x: number
  y: number
  reserved?: boolean
}

const tables: Table[] = [
  { id: 1, x: 180, y: 150 },
  { id: 2, x: 330, y: 150 },
  { id: 3, x: 480, y: 150, reserved: true },

  { id: 4, x: 180, y: 310 },
  { id: 5, x: 340, y: 310 },
  { id: 6, x: 500, y: 310 },

  { id: 7, x: 760, y: 180 },
  { id: 8, x: 900, y: 180 },

  { id: 9, x: 760, y: 360 },
  { id: 10, x: 900, y: 360 }
]

export default function Reservas() {

  const [selectedTable, setSelectedTable] = useState<number | null>(null)

  function selectTable(table: Table) {
    if (table.reserved) return
    setSelectedTable(table.id)
  }

  function confirmReservation() {

    if (!selectedTable) {
      alert("Selecione uma mesa")
      return
    }

    localStorage.setItem(
      "reservation",
      JSON.stringify({
        table: selectedTable,
        createdAt: new Date()
      })
    )

    alert("Reserva confirmada!")
  }

  return (

    <div style={{ height: "100vh", minHeight: "100vh", background: "#1a6fa8", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "flex-start", fontFamily: "Manrope", color: "white", paddingTop: 60 }}>
      <h1 style={{ fontSize: 42, marginBottom: 10 }}>
        Escolha sua Mesa
      </h1>
      <p style={{ opacity: 0.7 }}>
        Planta do restaurante
      </p>
      <div
        style={{
          marginTop: 40,
          width: 1050,
          height: 520,
          position: "relative",
          background: "#15608c",
          border: "3px solid #aed6ec",
          borderRadius: 12,
            boxShadow: "0 20px 60px rgba(0,0,0,0.4)"
          }}
        >

          {/* PAREDE COZINHA */}

          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: 200,
              height: 100,
              background: "rgba(255,255,255,0.12)",
              borderRight: "3px solid rgba(255,255,255,0.3)",
              borderBottom: "3px solid rgba(255,255,255,0.3)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center"
            }}
          >
            Cozinha
          </div>

          {/* DIVISÃO INTERNA */}

          <div
            style={{
              position: "absolute",
              left: 650,
              top: 0,
              width: 2,
              height: "100%",
              background: "rgba(255,255,255,0.2)"
            }}
          />

          {/* LABELS */}

          <div style={{ position: "absolute", top: 10, left: 280, opacity: 0.6 }}>
            Salão Principal
          </div>

          <div style={{ position: "absolute", top: 10, right: 120, opacity: 0.6 }}>
            Área Externa
          </div>

          {/* PLANTAS DECORATIVAS */}



          {/* MESAS */}

          {tables.map((table) => {

            const selected = selectedTable === table.id

            let color = "#3498db"

            if (table.reserved) color = "#e74c3c"
            else if (selected) color = "#2ecc71"

            return (

              <div
                key={table.id}
                onClick={() => selectTable(table)}
                style={{
                  position: "absolute",
                  left: table.x,
                  top: table.y,
                  width: 70,
                  height: 70,
                  borderRadius: "50%",
                  background: color,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  cursor: table.reserved ? "not-allowed" : "pointer",
                  boxShadow: "0 10px 20px rgba(0,0,0,0.4)",
                  transition: "0.2s"
                }}
              >

                {/* CADEIRAS */}

                {table.id}
              </div>
            )
          })}
        </div>
        {/* BOTÃO */}
        <button
          onClick={confirmReservation}
          style={{
            marginTop: 40,
            padding: "16px 50px",
            fontSize: 16,
            borderRadius: 8,
            border: "none",
            background: "#27ae60",
            color: "white",
            cursor: "pointer",
            boxShadow: "0 8px 20px rgba(0,0,0,0.4)"
          }}
        >
          Confirmar Reserva
        </button>
      </div>
    )}