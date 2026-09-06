import React, { useEffect, useState } from 'react'

export type CalibratedPoint = {
  id: string
  number: number
  capacity: number
  position: [number, number, number]
  rotation?: [number, number, number]
  status?: 'available' | 'locked' | 'reserved'
}

type Props = {
  active: boolean
  lastClickedPos?: { x: number; y: number; z: number } | null
  onAddPoint?: (p: CalibratedPoint) => void
  onSaveAll?: (points: CalibratedPoint[]) => void
  onClose?: () => void
  initialNextNumber?: number
}

/**
 * CalibrateMode - UI simples para aceitar o clique atual como ponto de mesa,
 * coletar número/capacidade, manter lista local e exportar JSON.
 *
 * Integração: ReservasPage passa `lastClickedPos` quando o usuário clicar no MapFloor.
 */
const CalibrateMode: React.FC<Props> = ({ active, lastClickedPos = null, onAddPoint, onSaveAll, onClose, initialNextNumber = 1 }) => {
  const [tempPos, setTempPos] = useState<{ x: number; y: number; z: number } | null>(null)
  const [nextNumber, setNextNumber] = useState<number>(initialNextNumber)
  const [capacity, setCapacity] = useState<number>(4)
  const [points, setPoints] = useState<CalibratedPoint[]>([])
  const [message, setMessage] = useState<string | null>(null)

  // quando receber nova posição clicada do pai, mostra como tempPos
  useEffect(() => {
    if (
      lastClickedPos &&
      (tempPos?.x !== lastClickedPos.x ||
        tempPos?.y !== lastClickedPos.y ||
        tempPos?.z !== lastClickedPos.z)
    ) {
      setTempPos(lastClickedPos)
      setMessage('Posição capturada — ajuste e clique em "Salvar como mesa"')
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lastClickedPos])

  function saveTempAsPoint() {
    if (!tempPos) {
      setMessage('Nenhuma posição capturada. Clique no mapa primeiro.')
      return
    }
    const newPoint: CalibratedPoint = {
      id: `p_${Date.now()}`,
      number: nextNumber,
      capacity,
      position: [Number(tempPos.x.toFixed(3)), Number(tempPos.y.toFixed(3)), Number(tempPos.z.toFixed(3))],
      rotation: [0, 0, 0],
      status: 'available',
    }
    setPoints((s) => [...s, newPoint])
    if (onAddPoint) onAddPoint(newPoint)
    setNextNumber((n) => n + 1)
    setTempPos(null)
    setMessage('Mesa salva.')
  }

  function removePoint(id: string) {
    setPoints((s) => s.filter((p) => p.id !== id))
  }

  function exportJSON() {
    const out = points.map((p) => ({
      id: p.id,
      number: p.number,
      capacity: p.capacity,
      position: p.position,
      rotation: p.rotation,
      status: p.status ?? 'available',
    }))
    const content = JSON.stringify(out, null, 2)
    const blob = new Blob([content], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'table-map-calibrated.json'
    a.click()
    URL.revokeObjectURL(url)
    setMessage('JSON exportado.')
  }

  if (!active) return null

  return (
    <div style={{
      position: 'fixed',
      right: 16,
      top: 80,
      width: 360,
      maxHeight: '70vh',
      overflow: 'auto',
      background: 'rgba(255,255,255,0.96)',
      padding: 12,
      borderRadius: 8,
      zIndex: 9999,
      boxShadow: '0 6px 20px rgba(0,0,0,0.2)',
      fontFamily: 'Inter, Roboto, Arial, sans-serif'
    }}>
      <h3 style={{ marginTop: 0 }}>Modo Calibração</h3>
      <p style={{ marginTop: 0 }}>Clique em "Aguardar clique" e, em seguida, clique sobre o mapa para capturar a posição.</p>

      <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
        <button type="button" onClick={() => { setTempPos(null); setMessage('Pronto para capturar clique no mapa.') }}>Aguardar clique</button>
        <button type="button" onClick={() => { setTempPos(null); setMessage(null) }}>Limpar</button>
        <button type="button" onClick={exportJSON} style={{ marginLeft: 'auto' }}>Exportar JSON</button>
      </div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          Nº:
          <input type="number" value={nextNumber} onChange={(e) => setNextNumber(Number(e.target.value))} style={{ width: 72 }} />
        </label>
        <label style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          Capacidade:
          <input type="number" value={capacity} min={1} onChange={(e) => setCapacity(Number(e.target.value))} style={{ width: 72 }} />
        </label>
      </div>

      {tempPos ? (
        <div style={{ padding: 8, background: '#eef', borderRadius: 6, marginBottom: 8 }}>
          <div style={{ fontSize: 13 }}>Coordenadas capturadas:</div>
          <div style={{ fontFamily: 'monospace', fontSize: 13 }}>{`x: ${tempPos.x.toFixed(3)}, y: ${tempPos.y.toFixed(3)}, z: ${tempPos.z.toFixed(3)}`}</div>
          <div style={{ marginTop: 8, display: 'flex', gap: 8 }}>
            <button onClick={saveTempAsPoint}>Salvar como mesa {nextNumber}</button>
            <button onClick={() => { setTempPos(null); setMessage('Captura cancelada.') }}>Cancelar</button>
          </div>
        </div>
      ) : (
        <div style={{ marginBottom: 8, color: '#666' }}>{message ?? 'Nenhuma captura ativa'}</div>
      )}

      <h4 style={{ margin: '8px 0' }}>Mesas calibradas ({points.length})</h4>
      <ul style={{ paddingLeft: 16, marginTop: 0 }}>
        {points.map((p) => (
          <li key={p.id} style={{ marginBottom: 6, fontSize: 13 }}>
            #{p.number} cap:{p.capacity} — [{p.position.map((v) => v.toFixed(2)).join(', ')}]
            <button onClick={() => removePoint(p.id)} style={{ marginLeft: 8 }}>remover</button>
          </li>
        ))}
      </ul>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 12 }}>
        <button onClick={() => { if (onClose) onClose() }}>Fechar</button>
        <button
          onClick={() => { if (onSaveAll && points.length > 0) onSaveAll(points) }}
          disabled={points.length === 0}
          style={{
            background: points.length > 0 ? '#27ae60' : '#ccc',
            color: '#fff',
            border: 'none',
            padding: '6px 16px',
            borderRadius: 6,
            fontWeight: 700,
            cursor: points.length > 0 ? 'pointer' : 'not-allowed',
          }}
        >
          Salvar Todas ({points.length})
        </button>
        <button onClick={exportJSON}>Exportar JSON</button>
      </div>
    </div>
  )
}

export default CalibrateMode