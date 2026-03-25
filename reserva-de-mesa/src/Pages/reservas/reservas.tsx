import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useNotifications } from "../../features/notifications";

interface Mesa {
  id: number;
  label: string;
  x: number;
  y: number;
  lugares: number;
}

const DEFAULT_MESAS: Mesa[] = [
  { id: 1, label: "1", x: 15.41, y: 20.3, lugares: 8 },
  { id: 2, label: "2", x: 23.327, y: 19.909, lugares: 8 },
  { id: 3, label: "3", x: 31.021, y: 19.714, lugares: 4 },
  { id: 4, label: "4", x: 31.244, y: 42.936, lugares: 4 },
  { id: 5, label: "5", x: 65.254, y: 42.741, lugares: 4 },
  { id: 6, label: "6", x: 65.254, y: 65.963, lugares: 4 },
  { id: 7, label: "7", x: 64.92, y: 77.866, lugares: 4 },
  { id: 8, label: "8", x: 55.665, y: 78.256, lugares: 4 },
  { id: 9, label: "9", x: 49.42, y: 75.524, lugares: 4 },
  { id: 10, label: "10", x: 41.726, y: 78.061, lugares: 4 },
  { id: 11, label: "11", x: 30.352, y: 74.939, lugares: 4 },
  { id: 12, label: "12", x: 23.327, y: 74.549, lugares: 4 },
  { id: 13, label: "13", x: 80.308, y: 16.982, lugares: 4 },
  { id: 14, label: "14", x: 89.897, y: 17.568, lugares: 4 },
  { id: 15, label: "15", x: 75.513, y: 27.325, lugares: 4 },
  { id: 16, label: "16", x: 89.786, y: 34.155, lugares: 4 },
  { id: 17, label: "17", x: 86.218, y: 47.034, lugares: 4 },
  { id: 18, label: "18", x: 75.178, y: 47.229, lugares: 4 },
  { id: 19, label: "19", x: 75.736, y: 58.937, lugares: 4 },
  { id: 20, label: "20", x: 84.88, y: 58.742, lugares: 4 },
  { id: 21, label: "21", x: 86.441, y: 70.06, lugares: 4 },
  { id: 22, label: "22", x: 90.232, y: 84.111, lugares: 4 },
  { id: 23, label: "23", x: 80.085, y: 84.891, lugares: 4 },
];

function loadCalibratedMesas(): Mesa[] {
  try {
    const saved = localStorage.getItem("mesas_calibradas");
    return saved ? JSON.parse(saved) : DEFAULT_MESAS;
  } catch {
    return DEFAULT_MESAS;
  }
}

type MesaStatus = "livre" | "selecionada" | "reservada";

const STATUS_COLORS: Record<MesaStatus, { bg: string; border: string; text: string }> = {
  livre: { bg: "rgba(46, 204, 113, 0.75)", border: "#27ae60", text: "#fff" },
  selecionada: { bg: "rgba(241, 196, 15, 0.85)", border: "#f39c12", text: "#333" },
  reservada: { bg: "rgba(231, 76, 60, 0.8)", border: "#c0392b", text: "#fff" },
};

interface Reserva {
  nome?: string;
  cpf: string;
  mesas: number[];
  data: string; // YYYY-MM-DD
}

// Mesas bloqueadas (reservadas por outras pessoas — apenas visuais no mapa)
const MESAS_BLOQUEADAS: number[] = [3, 5, 7, 14, 17, 21];

function loadReservas(): Reserva[] {
  try {
    const saved = localStorage.getItem("mesas_reservadas_v2");
    return saved ? JSON.parse(saved) : [];
  } catch {
    return [];
  }
}

function saveReservas(reservas: Reserva[]) {
  localStorage.setItem("mesas_reservadas_v2", JSON.stringify(reservas));
}

function getMesasReservadas(reservas: Reserva[]): number[] {
  return reservas.flatMap((r) => r.mesas);
}

function formatCpf(value: string): string {
  const digits = value.replace(/\D/g, "").slice(0, 11);
  if (digits.length <= 3) return digits;
  if (digits.length <= 6) return `${digits.slice(0, 3)}.${digits.slice(3)}`;
  if (digits.length <= 9) return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6)}`;
  return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6, 9)}-${digits.slice(9)}`;
}

function formatDateBr(date: string): string {
  if (!date) return "-";
  return date.split("-").reverse().join("/");
}

function todayIsoDate(): string {
  const today = new Date();
  const y = today.getFullYear();
  const m = String(today.getMonth() + 1).padStart(2, "0");
  const d = String(today.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function diffDays(fromDate: string, toDate: string): number {
  const from = new Date(`${fromDate}T12:00:00`);
  const to = new Date(`${toDate}T12:00:00`);
  const ms = from.getTime() - to.getTime();
  return Math.round(ms / (1000 * 60 * 60 * 24));
}

export default function Reservas() {
  const navigate = useNavigate();
  const { notify } = useNotifications();
  const [loading, setLoading] = useState(true);
  const mesas = loadCalibratedMesas();
  const [reservas, setReservas] = useState<Reserva[]>(loadReservas);
  const [selecionadas, setSelecionadas] = useState<number[]>([]);
  const [confirmMsg, setConfirmMsg] = useState("");
  const [showCpfModal, setShowCpfModal] = useState(false);
  const [cpfInput, setCpfInput] = useState("");
  const [nomeInput, setNomeInput] = useState("");
  const [cpfError, setCpfError] = useState("");
  const [dataReserva, setDataReserva] = useState("");
  const [showReceipt, setShowReceipt] = useState<Reserva | null>(null);
  const [lastReserva, setLastReserva] = useState<Reserva | null>(() => {
    const saved = localStorage.getItem("ultima_reserva_confirmada_v2");
    return saved ? JSON.parse(saved) : null;
  });

  // Permite nova reserva se o dia for diferente
  const reservaBloqueada = reservas.some(r => r.cpf === cpfInput.replace(/\D/g, "") && r.data === dataReserva);
  const receiptRef = useRef<HTMLDivElement>(null);
  const demoTimersRef = useRef<number[]>([]);
  const avisoInicialRef = useRef(false);
  const feedbackNotificadoRef = useRef<string>("");

  // Impede novas reservas após confirmação
  const reservaConfirmada = !!lastReserva;

  const reservadasUsuario = getMesasReservadas(reservas);
  const reservadas = [...new Set([...MESAS_BLOQUEADAS, ...reservadasUsuario])];

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 1200);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (avisoInicialRef.current) return;
    avisoInicialRef.current = true;
    notify({
      type: "info",
      title: "Aviso do restaurante",
      message: "Chegue com 10 minutos de antecedencia para agilizar seu atendimento.",
    });
  }, [notify]);

  useEffect(() => {
    if (!lastReserva?.data) return;
    const hoje = todayIsoDate();
    if (lastReserva.data >= hoje) return;

    const feedbackKey = `${lastReserva.cpf}-${lastReserva.data}`;
    if (feedbackNotificadoRef.current === feedbackKey) return;
    feedbackNotificadoRef.current = feedbackKey;

    notify({
      type: "info",
      title: "Feedback pos-reserva",
      message: `Como foi sua experiencia do dia ${formatDateBr(lastReserva.data)}? Sua opiniao ajuda muito.`,
    });
  }, [lastReserva, notify]);

  useEffect(() => {
    return () => {
      demoTimersRef.current.forEach((id) => window.clearTimeout(id));
      demoTimersRef.current = [];
    };
  }, []);

  function dispararNotificacoesDemo() {
    demoTimersRef.current.forEach((id) => window.clearTimeout(id));
    demoTimersRef.current = [];

    const baseDate = dataReserva || todayIsoDate();
    const lista = [
      { type: "success" as const, title: "Reserva confirmada", message: `Mesa 3 reservada para ${formatDateBr(baseDate)}.` },
      { type: "info" as const, title: "Lembrete da reserva", message: "Faltam 24h para sua reserva. Nos vemos em breve." },
      { type: "info" as const, title: "Prazo de chegada", message: "Sua mesa fica reservada por ate 15 minutos apos o horario." },
      { type: "info" as const, title: "Reserva alterada", message: "Sua reserva foi alterada para outra data com sucesso." },
      { type: "error" as const, title: "Reserva cancelada", message: "Sua reserva foi cancelada. Toque em Reservar novamente." },
      { type: "error" as const, title: "Mesa indisponivel", message: "Esta mesa acabou de ser reservada. Escolha outra opcao no mapa." },
      { type: "info" as const, title: "Pagamento e consumo", message: "Para grupos grandes pode haver consumo minimo. Consulte a equipe." },
      { type: "error" as const, title: "Confirmacao pendente", message: "Revise nome, CPF e data antes de concluir a reserva." },
      { type: "success" as const, title: "Check-in liberado", message: "Sua reserva e hoje. Check-in disponivel na recepcao." },
      { type: "success" as const, title: "Beneficio liberado", message: "Cliente fidelidade: voce ganhou uma cortesia especial." },
      { type: "info" as const, title: "Aviso do restaurante", message: "Hoje teremos menu especial de frutos do mar a noite." },
      { type: "info" as const, title: "Feedback pos-reserva", message: "Como foi sua experiencia? Avalie sua visita em 1 minuto." },
    ];

    lista.forEach((item, index) => {
      const timerId = window.setTimeout(() => {
        notify(item);
      }, index * 160);
      demoTimersRef.current.push(timerId);
    });
  }

  function getStatus(id: number): MesaStatus {
    if (reservadas.includes(id)) return "reservada";
    if (selecionadas.includes(id)) return "selecionada";
    return "livre";
  }

  function handleClickMesa(id: number) {
    // Bloqueia apenas se já existe reserva para o mesmo CPF e data
    if (reservaBloqueada) {
      setConfirmMsg("Você já possui uma reserva para este dia.");
      setTimeout(() => setConfirmMsg("") , 4000);
      notify({
        type: "error",
        title: "Reserva já existente",
        message: "Você já possui uma reserva para a data selecionada.",
      });
      return;
    }
    if (reservadas.includes(id)) {
      notify({
        type: "error",
        title: "Mesa indisponivel",
        message: `A mesa ${id} ja esta reservada. Escolha outra mesa no mapa.`,
      });
      return;
    }
    // Only allow one selection at a time
    if (selecionadas.length === 0) {
      setSelecionadas([id]);
      setConfirmMsg("");
    } else if (selecionadas.includes(id)) {
      setSelecionadas([]);
      setConfirmMsg("");
    } else {
      setConfirmMsg("Não é possível reservar duas mesas no mesmo dia.");
      setTimeout(() => setConfirmMsg(""), 4000);
      notify({
        type: "error",
        title: "Limite de reserva",
        message: "Não é possível reservar duas mesas no mesmo dia. Finalize a reserva atual primeiro.",
      });
    }
  }

  function handleAbrirModal() {
    if (reservaBloqueada) {
      setConfirmMsg("Você já possui uma reserva para este dia.");
      setTimeout(() => setConfirmMsg(""), 4000);
      notify({
        type: "error",
        title: "Reserva bloqueada",
        message: "Você já possui uma reserva para este dia.",
      });
      return;
    }
    if (selecionadas.length === 0) return;
    if (!dataReserva) {
      setConfirmMsg("Selecione a data da reserva antes de confirmar.");
      setTimeout(() => setConfirmMsg(""), 3000);
      notify({
        type: "info",
        title: "Data obrigatória",
        message: "Selecione uma data antes de confirmar sua reserva.",
      });
      return;
    }
    setCpfInput("");
    setNomeInput("");
    setCpfError("");
    notify({
      type: "info",
      title: "Prazo de chegada",
      message: "A mesa fica reservada por ate 15 minutos apos o horario combinado.",
    });
    notify({
      type: "info",
      title: "Pagamento e consumo",
      message: "Para grupos maiores, pode haver consumo minimo no periodo noturno.",
    });
    setShowCpfModal(true);
  }

  function handleConfirmarComCpf() {
    if (!nomeInput.trim()) {
      setCpfError("Por favor, informe seu nome.");
      notify({
        type: "error",
        title: "Confirmacao pendente",
        message: "Informe seu nome para concluir a reserva.",
      });
      return;
    }
    const cpfDigits = cpfInput.replace(/\D/g, "");
    if (cpfDigits.length !== 11) {
      setCpfError("CPF inválido. Deve conter 11 números.");
      notify({
        type: "error",
        title: "Confirmacao pendente",
        message: "CPF invalido. Digite os 11 numeros para continuar.",
      });
      return;
    }
    if (reservas.some((r) => r.cpf === cpfDigits && r.data === dataReserva)) {
      setCpfError("Este CPF já possui uma reserva para este dia.");
      notify({
        type: "error",
        title: "Reserva duplicada",
        message: "Este CPF ja possui reserva para a mesma data.",
      });
      return;
    }
    const novaReserva: Reserva = { cpf: cpfDigits, mesas: [...selecionadas], data: dataReserva, nome: nomeInput.trim() };
    const novasReservas = [...reservas, novaReserva];
    setReservas(novasReservas);
    saveReservas(novasReservas);
    setSelecionadas([]);
    setShowCpfModal(false);
    setCpfInput("");
    setNomeInput("");
    setDataReserva("");
    setShowReceipt(novaReserva);
    setLastReserva(novaReserva);
    localStorage.setItem("ultima_reserva_confirmada_v2", JSON.stringify(novaReserva));

    const hoje = todayIsoDate();
    const diasParaReserva = diffDays(novaReserva.data, hoje);
    const totalReservasCliente = novasReservas.filter((r) => r.cpf === cpfDigits).length;

    if (lastReserva && lastReserva.cpf === cpfDigits && lastReserva.data !== novaReserva.data) {
      notify({
        type: "info",
        title: "Reserva alterada",
        message: `Sua reserva foi atualizada para ${formatDateBr(novaReserva.data)}.`,
      });
    }

    notify({
      type: "success",
      title: "Reserva confirmada",
      message: `Mesa ${novaReserva.mesas.join(", ")} reservada para ${formatDateBr(novaReserva.data)}.`,
    });

    if (diasParaReserva === 1) {
      notify({
        type: "info",
        title: "Lembrete da reserva",
        message: "Faltam 24h para sua reserva. Te esperamos.",
      });
    } else if (diasParaReserva === 0) {
      notify({
        type: "info",
        title: "Lembrete da reserva",
        message: "Sua reserva e hoje. Faltam poucas horas para seu horario.",
      });
      notify({
        type: "success",
        title: "Check-in liberado",
        message: "Pode fazer seu check-in na entrada ao chegar no restaurante.",
      });
    } else if (diasParaReserva > 1) {
      notify({
        type: "info",
        title: "Lembrete programado",
        message: "Vamos te lembrar novamente perto da data da reserva.",
      });
    }

    if (totalReservasCliente >= 2) {
      notify({
        type: "success",
        title: "Beneficio fidelidade",
        message: "Voce recebeu um beneficio especial por reservar novamente.",
      });
    }
  }

  const handleBaixarReserva = useCallback(() => {
    const el = receiptRef.current;
    if (!el) return;
    const canvas = document.createElement("canvas");
    const scale = 2;
    canvas.width = el.offsetWidth * scale;
    canvas.height = el.offsetHeight * scale;
    const ctx = canvas.getContext("2d")!;
    ctx.scale(scale, scale);

    // Render via foreignObject in SVG
    const data = new XMLSerializer().serializeToString(el);
    const svgStr = `<svg xmlns="http://www.w3.org/2000/svg" width="${el.offsetWidth}" height="${el.offsetHeight}"><foreignObject width="100%" height="100%"><div xmlns="http://www.w3.org/1999/xhtml">${data}</div></foreignObject></svg>`;
    const img = new Image();
    const blob = new Blob([svgStr], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    img.onload = () => {
      ctx.drawImage(img, 0, 0);
      URL.revokeObjectURL(url);
      const link = document.createElement("a");
      link.download = "minha-reserva.png";
      link.href = canvas.toDataURL("image/png");
      link.click();
    };
    img.src = url;
  }, []);

  // Remove reserva específica por CPF e data
  function handleCancelarReservaPorCpfData(cpf: string, data: string) {
    const novas = reservas.filter(r => !(r.cpf === cpf && r.data === data));
    setReservas(novas);
    saveReservas(novas);
    if (lastReserva && lastReserva.cpf === cpf && lastReserva.data === data) {
      setLastReserva(null);
      localStorage.removeItem("ultima_reserva_confirmada_v2");
    }
    setConfirmMsg("Reserva cancelada.");
    setTimeout(() => setConfirmMsg("") , 4000);
    notify({
      type: "error",
      title: "Reserva cancelada",
      message: `A reserva do dia ${formatDateBr(data)} foi cancelada.`,
    });
  }

  

  const totalLugaresSelecionados = selecionadas.reduce(
    (acc, id) => acc + (mesas.find((m) => m.id === id)?.lugares ?? 0),
    0
  );

  return (
    <div
      style={{
        height: "100vh",
        width: "100vw",
        display: "flex",
        background: "linear-gradient(135deg, #0a2540 0%, #163d5c 50%, #1a6fa8 100%)",
        fontFamily: "Manrope, sans-serif",
        padding: 0,
        margin: 0,
        overflow: "hidden",
        position: "relative",
      }}
    >
      {/* Loading */}
      {loading && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            background: "linear-gradient(135deg, #0a2540 0%, #163d5c 50%, #1a6fa8 100%)",
            zIndex: 100,
            animation: "fadeIn 0.5s",
          }}
        >
          <div
            style={{
              width: 56,
              height: 56,
              border: "5px solid rgba(174, 214, 236, 0.3)",
              borderTop: "5px solid #4db3d8",
              borderRadius: "50%",
              animation: "spin 0.9s linear infinite",
              marginBottom: 24,
            }}
          />
          <span style={{ color: "#aed6ec", fontSize: "1.1rem", opacity: 0.9 }}>
            Carregando planta...
          </span>
        </div>
      )}

      {/* ===== SIDEBAR ESQUERDA ===== */}
      <aside
        style={{
          width: 340,
          minWidth: 340,
          height: "100vh",
          background: "#0c2e50",
          borderRight: "1px solid rgba(77, 179, 216, 0.18)",
          display: "flex",
          flexDirection: "column",
          padding: 0,
          zIndex: 2,
          animation: "slideRight 0.8s ease",
        }}
      >
        {/* Top bar — logo + back */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "1rem 1.4rem",
            borderBottom: "1px solid rgba(77, 179, 216, 0.18)",
          }}
        >
          <button
            onClick={() => navigate("/")}
            style={{
              background: "none",
              border: "none",
              color: "#4db3d8",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: 6,
              fontFamily: "Manrope, sans-serif",
              fontSize: "0.78rem",
              fontWeight: 600,
              letterSpacing: "0.12em",
              textTransform: "uppercase" as const,
              padding: 0,
            }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
            VOLTAR
          </button>
          <a
            href="tel:+552420260003"
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 5,
              color: "#c8e8f8",
              textDecoration: "none",
              fontSize: "0.82rem",
            }}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="#4db3d8"><path d="M6.7 10.8a15.2 15.2 0 0 0 6.5 6.5l2.2-2.2a1 1 0 0 1 1-.24 11 11 0 0 0 3.45.55 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17.8 17.8 0 0 1 3 4a1 1 0 0 1 1-1h3.6a1 1 0 0 1 1 1c0 1.2.18 2.36.55 3.45a1 1 0 0 1-.25 1.02L6.7 10.8Z"/></svg>
            <span style={{ fontSize: "0.78rem", letterSpacing: "0.01em" }}>+55 24 2026 0003</span>
          </a>
        </div>

        {/* Logo */}
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            padding: "1.6rem 2rem 0.8rem",
          }}
        >
          <img
            src="/logo.png"
            alt="Ocean Blue"
            style={{
              height: 80,
              width: "auto",
              objectFit: "contain",
              filter: "drop-shadow(0 6px 18px rgba(0,0,0,0.45))",
            }}
          />
        </div>

        {/* Title */}
        <div style={{ textAlign: "center", padding: "0 1.4rem 1.2rem" }}>
          <h1
            style={{
              fontSize: "1.7rem",
              fontFamily: "Cormorant Garamond, serif",
              color: "#e8f6ff",
              fontWeight: 700,
              margin: 0,
              letterSpacing: "0.1em",
            }}
          >
            Reserva de Mesa
          </h1>
          <div
            style={{
              width: 50,
              height: 2,
              background: "linear-gradient(90deg, #1a6fa8, #4db3d8)",
              borderRadius: 2,
              margin: "8px auto 0",
            }}
          />
          <p style={{ color: "#7fb8d4", fontSize: "0.8rem", margin: "8px 0 0", letterSpacing: "0.04em" }}>
            Selecione as mesas no mapa
          </p>
        </div>

        {/* Legenda */}
        <div style={{ padding: "14px 24px 12px", borderTop: "1px solid rgba(77,179,216,0.14)" }}>
          <span
            style={{
              fontSize: "0.7rem",
              fontWeight: 600,
              color: "#7fb8d4",
              textTransform: "uppercase",
              letterSpacing: "0.12em",
            }}
          >
            Legenda
          </span>
          <div style={{ display: "flex", gap: "14px", marginTop: 10 }}>
            {([
              { status: "livre" as MesaStatus, label: "Livre" },
              { status: "selecionada" as MesaStatus, label: "Selecionada" },
              { status: "reservada" as MesaStatus, label: "Reservada" },
            ]).map((item) => (
              <div
                key={item.status}
                style={{ display: "flex", alignItems: "center", gap: 6 }}
              >
                <div
                  style={{
                    width: 12,
                    height: 12,
                    borderRadius: "50%",
                    background: STATUS_COLORS[item.status].bg,
                    border: `2px solid ${STATUS_COLORS[item.status].border}`,
                  }}
                />
                <span style={{ color: "#c0dcea", fontSize: "0.78rem" }}>{item.label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Mesas selecionadas */}
        <div
          style={{
            padding: "14px 24px",
            borderTop: "1px solid rgba(77, 179, 216, 0.14)",
            flex: 1,
            overflowY: "auto",
          }}
        >
          <span
            style={{
              fontSize: "0.7rem",
              fontWeight: 600,
              color: "#7fb8d4",
              textTransform: "uppercase",
              letterSpacing: "0.12em",
            }}
          >
            Mesas selecionadas
          </span>

          {selecionadas.length === 0 && reservadas.length === 0 ? (
            <div
              style={{
                marginTop: 16,
                color: "#5a8faa",
                fontSize: "0.88rem",
                textAlign: "center",
                padding: "24px 8px",
                border: "1px dashed rgba(77, 179, 216, 0.2)",
                borderRadius: 12,
              }}
            >
              Nenhuma mesa selecionada.
              <br />
              <span style={{ fontSize: "0.78rem", opacity: 0.7 }}>
                Clique no mapa para selecionar
              </span>
            </div>
          ) : (
            <div style={{ marginTop: 12, display: "flex", flexDirection: "column", gap: 8 }}>
              {/* Mesas selecionadas (amarelas) */}
              {selecionadas
                .sort((a, b) => a - b)
                .map((id) => {
                  const mesa = mesas.find((m) => m.id === id)!;
                  return (
                    <div
                      key={id}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        background: "rgba(241, 196, 15, 0.1)",
                        border: "1px solid rgba(241, 196, 15, 0.25)",
                        borderRadius: 10,
                        padding: "10px 14px",
                        animation: "fadeIn 0.3s",
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                        <div
                          style={{
                            width: 32,
                            height: 32,
                            borderRadius: "50%",
                            background: STATUS_COLORS.selecionada.bg,
                            border: `2px solid ${STATUS_COLORS.selecionada.border}`,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            color: "#333",
                            fontWeight: 700,
                            fontSize: "0.85rem",
                          }}
                        >
                          {mesa.label}
                        </div>
                        <div>
                          <div style={{ color: "#e8f6ff", fontSize: "0.88rem", fontWeight: 600 }}>
                            Mesa {mesa.label}
                          </div>
                          <div style={{ color: "#7fb8d4", fontSize: "0.72rem" }}>
                            {mesa.lugares} lugares
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => handleClickMesa(id)}
                        style={{
                          background: "none",
                          border: "none",
                          color: "#e74c3c",
                          cursor: "pointer",
                          fontSize: "1.1rem",
                          padding: "4px 8px",
                          borderRadius: 6,
                          lineHeight: 1,
                        }}
                        title="Remover seleção"
                      >
                        ✕
                      </button>
                    </div>
                  );
                })}

              {/* Reservas já feitas (vermelhas) */}
              {reservas.map((reserva, idx) => (
                <div
                  key={`reserva-${idx}`}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    background: "rgba(231, 76, 60, 0.08)",
                    border: "1px solid rgba(231, 76, 60, 0.2)",
                    borderRadius: 10,
                    padding: "10px 14px",
                    marginBottom: 6,
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <div
                      style={{
                        width: 32,
                        height: 32,
                        borderRadius: "50%",
                        background: STATUS_COLORS.reservada.bg,
                        border: `2px solid ${STATUS_COLORS.reservada.border}`,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        color: "#fff",
                        fontWeight: 700,
                        fontSize: "0.85rem",
                      }}
                    >
                      {reserva.mesas.join(",")}
                    </div>
                    <div>
                      <div style={{ color: "#e8f6ff", fontSize: "0.88rem", fontWeight: 600 }}>
                        Mesa(s): {reserva.mesas.join(",")}
                      </div>
                      <div style={{ color: "#e74c3c", fontSize: "0.72rem", fontWeight: 500 }}>
                        Reservada
                      </div>
                      <div style={{ color: "#5a8faa", fontSize: "0.65rem", marginTop: 1 }}>
                        CPF: {reserva.cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4")}
                      </div>
                      <div style={{ color: "#5a8faa", fontSize: "0.65rem" }}>
                        Data: {reserva.data.split("-").reverse().join("/")}
                      </div>
                    </div>
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                    <button
                      onClick={() => setShowReceipt(reserva)}
                      style={{
                        background: "rgba(77,179,216,0.12)",
                        border: "1px solid rgba(77,179,216,0.3)",
                        color: "#4db3d8",
                        cursor: "pointer",
                        fontSize: "0.7rem",
                        padding: "4px 10px",
                        borderRadius: 6,
                        fontWeight: 600,
                      }}
                      title="Ver reserva"
                    >
                      Ver Reserva
                    </button>
                    <button
                      onClick={() => handleCancelarReservaPorCpfData(reserva.cpf, reserva.data)}
                      style={{
                        background: "rgba(231,76,60,0.12)",
                        border: "1px solid rgba(231,76,60,0.3)",
                        color: "#e74c3c",
                        cursor: "pointer",
                        fontSize: "0.7rem",
                        padding: "4px 10px",
                        borderRadius: 6,
                        fontWeight: 600,
                      }}
                      title="Cancelar esta reserva"
                    >
                      Cancelar
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Resumo + Ações */}
        <div
          style={{
            padding: "16px 24px 24px",
            borderTop: "1px solid rgba(77,179,216,0.14)",
            display: "flex",
            flexDirection: "column",
            gap: 10,
          }}
        >
          {/* Data da reserva */}
          {selecionadas.length > 0 && (
            <div>
              <label
                style={{
                  display: "block",
                  fontSize: "0.7rem",
                  fontWeight: 600,
                  color: "#7fb8d4",
                  textTransform: "uppercase",
                  letterSpacing: "0.1em",
                  marginBottom: 6,
                }}
              >
                Data da reserva
              </label>
              <input
                type="date"
                value={dataReserva}
                min={new Date().toISOString().split("T")[0]}
                onChange={(e) => setDataReserva(e.target.value)}
                style={{
                  width: "100%",
                  padding: "10px 12px",
                  fontSize: "0.88rem",
                  fontFamily: "Manrope, sans-serif",
                  background: "rgba(77, 179, 216, 0.08)",
                  border: "1px solid rgba(77, 179, 216, 0.2)",
                  borderRadius: 10,
                  color: "#e8f6ff",
                  outline: "none",
                  boxSizing: "border-box",
                  colorScheme: "dark",
                }}
              />
            </div>
          )}

          {/* Resumo */}
          {selecionadas.length > 0 && (
            <div
              style={{
                background: "rgba(77, 179, 216, 0.08)",
                borderRadius: 10,
                padding: "10px 14px",
                display: "flex",
                justifyContent: "space-between",
                fontSize: "0.82rem",
              }}
            >
              <span style={{ color: "#7fb8d4" }}>
                {selecionadas.length} mesa{selecionadas.length > 1 ? "s" : ""} &middot;{" "}
                {totalLugaresSelecionados} lugar{totalLugaresSelecionados > 1 ? "es" : ""}
              </span>
            </div>
          )}

          {/* Mensagem */}
          {confirmMsg && (
            <div
              style={{
                padding: "10px 14px",
                background: confirmMsg.includes("cancelada")
                  ? "rgba(231,76,60,0.1)"
                  : "rgba(46,204,113,0.1)",
                border: confirmMsg.includes("cancelada")
                  ? "1px solid rgba(231,76,60,0.3)"
                  : "1px solid rgba(46,204,113,0.3)",
                borderRadius: 10,
                color: confirmMsg.includes("cancelada") ? "#e74c3c" : "#2ecc71",
                fontSize: "0.82rem",
                fontWeight: 600,
                textAlign: "center",
                animation: "fadeIn 0.4s",
              }}
            >
              {confirmMsg}
            </div>
          )}

          {/* Botão confirmar */}
          <button
            onClick={handleAbrirModal}
            disabled={reservaConfirmada || selecionadas.length === 0}
            style={{
              width: "100%",
              padding: "13px 0",
              fontSize: "0.82rem",
              fontWeight: 700,
              borderRadius: 6,
              border: "none",
              background:
                selecionadas.length === 0
                  ? "rgba(77, 179, 216, 0.15)"
                  : "#4db3d8",
              color: selecionadas.length === 0 ? "#5a8faa" : "#e8f6ff",
              cursor: selecionadas.length === 0 ? "not-allowed" : "pointer",
              letterSpacing: "0.16em",
              textTransform: "uppercase" as const,
              fontFamily: "Manrope, sans-serif",
              transition: "filter 0.25s ease",
            }}
          >
            Confirmar Reserva
          </button>

          <button
            onClick={dispararNotificacoesDemo}
            type="button"
            style={{
              width: "100%",
              padding: "11px 0",
              fontSize: "0.75rem",
              fontWeight: 700,
              borderRadius: 6,
              border: "1px solid rgba(77, 179, 216, 0.35)",
              background: "rgba(13, 49, 79, 0.45)",
              color: "#9ed0e6",
              cursor: "pointer",
              letterSpacing: "0.14em",
              textTransform: "uppercase" as const,
              fontFamily: "Manrope, sans-serif",
            }}
          >
            Ver Todas Notificacoes
          </button>

        </div>
      </aside>

      {/* ===== AREA DO MAPA ===== */}
      <main
        style={{
          flex: 1,
          height: "100vh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          position: "relative",
          padding: 24,
          overflow: "hidden",
        }}
      >
        {/* Título no topo do mapa */}
        <div style={{ textAlign: "center", marginBottom: 16, animation: "fadeIn 1s" }}>
          <h2
            style={{
              fontSize: "1.8rem",
              fontFamily: "Cormorant Garamond, serif",
              color: "#e8f6ff",
              fontWeight: 700,
              margin: 0,
              letterSpacing: "0.1em",
              textShadow: "0 4px 16px rgba(10,37,64,0.3)",
            }}
          >
            Planta do Restaurante
          </h2>
          <p style={{ color: "#7fb8d4", fontSize: "0.85rem", margin: "4px 0 0", opacity: 0.8 }}>
            Clique nas mesas para selecionar
          </p>
        </div>

        {/* Container do mapa */}
        <div
          style={{
            position: "relative",
            flex: 1,
            width: "100%",
            maxWidth: 900,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <div
            style={{
              position: "relative",
              width: "100%",
              borderRadius: 20,
              overflow: "hidden",
              boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
              border: "2px solid rgba(77,179,216,0.2)",
              background: "rgba(237,247,251,0.98)",
              animation: "fadeIn 0.8s",
            }}
          >
            <img
              src="/map.jpg"
              alt="Planta do restaurante"
              style={{
                width: "100%",
                height: "auto",
                display: "block",
                userSelect: "none",
                pointerEvents: "none",
              }}
            />

            {/* Mesas clicáveis (dinâmicas — calibradas) */}
            {mesas.length === 0 && (
              <div
                style={{
                  position: "absolute",
                  inset: 0,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "#5a8faa",
                  fontSize: "1rem",
                  fontWeight: 600,
                  textAlign: "center",
                  pointerEvents: "none",
                }}
              >
                Nenhuma mesa calibrada.<br />Clique em "Calibrar" para posicionar as mesas.
              </div>
            )}
            {mesas.map((mesa) => {
              const status = getStatus(mesa.id);
              const colors = STATUS_COLORS[status];
              const isReservada = status === "reservada";
              const modalAberta = !!showCpfModal || !!showReceipt;
              return (
                <button
                  key={mesa.id}
                  onClick={() => handleClickMesa(mesa.id)}
                  title={
                    isReservada
                      ? `Mesa ${mesa.label} — Reservada`
                      : status === "selecionada"
                      ? `Mesa ${mesa.label} — Clique para desselecionar`
                      : `Mesa ${mesa.label} — ${mesa.lugares} lugares`
                  }
                  disabled={modalAberta || isReservada}
                  style={{
                    position: "absolute",
                    left: `${mesa.x}%`,
                    top: `${mesa.y}%`,
                    transform: "translate(-50%, -50%)",
                    width: 28,
                    height: 28,
                    borderRadius: "50%",
                    background: colors.bg,
                    border: `2px solid ${colors.border}`,
                    color: colors.text,
                    fontWeight: 700,
                    fontSize: "0.65rem",
                    fontFamily: "Manrope, sans-serif",
                    cursor: modalAberta ? "not-allowed" : isReservada ? "not-allowed" : "pointer",
                    display: modalAberta ? "none" : "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    boxShadow:
                      status === "selecionada"
                        ? "0 0 18px rgba(241,196,15,0.5), 0 0 6px rgba(241,196,15,0.3)"
                        : status === "reservada"
                        ? "0 0 12px rgba(231,76,60,0.35)"
                        : "0 4px 12px rgba(46,204,113,0.25)",
                    transition: "all 0.25s ease",
                    zIndex: 2,
                    opacity: isReservada ? 0.8 : 1,
                    padding: 0,
                    outline: "none",
                  }}
                >
                  {mesa.label}
                </button>
              );
            })}
          </div>
        </div>
      </main>

      {/* ===== MODAL CPF ===== */}
      {showCpfModal && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.6)",
            backdropFilter: "blur(6px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 9999,
            animation: "fadeIn 0.25s",
          }}
          onClick={() => setShowCpfModal(false)}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              background: "rgba(8, 28, 48, 0.97)",
              border: "1px solid rgba(77, 179, 216, 0.25)",
              borderRadius: 20,
              padding: "36px 32px 28px",
              width: 380,
              maxWidth: "90vw",
              display: "flex",
              flexDirection: "column",
              gap: 16,
              boxShadow: "0 24px 64px rgba(0,0,0,0.5)",
              animation: "fadeIn 0.3s",
            }}
          >
            <h3
              style={{
                margin: 0,
                fontFamily: "Cormorant Garamond, serif",
                fontSize: "1.5rem",
                color: "#e8f6ff",
                fontWeight: 700,
                letterSpacing: "0.06em",
              }}
            >
              Confirmar Reserva
            </h3>
            <p style={{ margin: 0, color: "#7fb8d4", fontSize: "0.85rem" }}>
              Mesa{selecionadas.length > 1 ? "s" : ""}{" "}
              <strong style={{ color: "#e8f6ff" }}>
                {selecionadas.sort((a, b) => a - b).join(", ")}
              </strong>
            </p>

            <div>
              <label
                style={{
                  display: "block",
                  fontSize: "0.72rem",
                  fontWeight: 600,
                  color: "#7fb8d4",
                  textTransform: "uppercase",
                  letterSpacing: "0.1em",
                  marginBottom: 8,
                }}
              >
                Informe seu nome
              </label>
              <input
                type="text"
                value={nomeInput}
                onChange={(e) => {
                  setNomeInput(e.target.value);
                  setCpfError("");
                }}
                placeholder="Seu nome completo"
                style={{
                  width: "100%",
                  padding: "12px 16px",
                  fontSize: "1.1rem",
                  fontFamily: "Manrope, sans-serif",
                  fontWeight: 600,
                  letterSpacing: "0.12em",
                  background: "rgba(77, 179, 216, 0.08)",
                  border: cpfError
                    ? "2px solid #e74c3c"
                    : "2px solid rgba(77, 179, 216, 0.2)",
                  borderRadius: 12,
                  color: "#e8f6ff",
                  outline: "none",
                  boxSizing: "border-box",
                  transition: "border-color 0.3s",
                  marginBottom: 12,
                }}
              />
              <label
                style={{
                  display: "block",
                  fontSize: "0.72rem",
                  fontWeight: 600,
                  color: "#7fb8d4",
                  textTransform: "uppercase",
                  letterSpacing: "0.1em",
                  marginBottom: 8,
                }}
              >
                Informe seu CPF
              </label>
              <input
                type="text"
                inputMode="numeric"
                value={cpfInput}
                onChange={(e) => {
                  setCpfInput(formatCpf(e.target.value));
                  setCpfError("");
                }}
                onKeyDown={(e) => e.key === "Enter" && handleConfirmarComCpf()}
                placeholder="000.000.000-00"
                style={{
                  width: "100%",
                  padding: "12px 16px",
                  fontSize: "1.1rem",
                  fontFamily: "Manrope, sans-serif",
                  fontWeight: 600,
                  letterSpacing: "0.12em",
                  background: "rgba(77, 179, 216, 0.08)",
                  border: cpfError
                    ? "2px solid #e74c3c"
                    : "2px solid rgba(77, 179, 216, 0.2)",
                  borderRadius: 12,
                  color: "#e8f6ff",
                  outline: "none",
                  boxSizing: "border-box",
                  transition: "border-color 0.3s",
                }}
              />
              {cpfError && (
                <p
                  style={{
                    margin: "8px 0 0",
                    color: "#e74c3c",
                    fontSize: "0.8rem",
                    fontWeight: 600,
                    animation: "fadeIn 0.3s",
                  }}
                >
                  {cpfError}
                </p>
              )}
            </div>

            <div style={{ display: "flex", gap: 10, marginTop: 4 }}>
              <button
                onClick={() => setShowCpfModal(false)}
                style={{
                  flex: 1,
                  padding: "12px 0",
                  fontSize: "0.88rem",
                  fontWeight: 600,
                  borderRadius: 12,
                  border: "1px solid rgba(77,179,216,0.2)",
                  background: "transparent",
                  color: "#7fb8d4",
                  cursor: "pointer",
                  transition: "all 0.3s",
                }}
              >
                Cancelar
              </button>
              <button
                onClick={handleConfirmarComCpf}
                style={{
                  flex: 1,
                  padding: "12px 0",
                  fontSize: "0.88rem",
                  fontWeight: 700,
                  borderRadius: 12,
                  border: "none",
                  background: "linear-gradient(135deg, #1a6fa8 0%, #4db3d8 100%)",
                  color: "#fff",
                  cursor: "pointer",
                  letterSpacing: "0.08em",
                  transition: "all 0.3s",
                }}
              >
                Confirmar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ===== POPUP MINHA RESERVA ===== */}
      {showReceipt && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.65)",
            backdropFilter: "blur(8px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 9999,
            animation: "fadeIn 0.3s",
          }}
          onClick={() => setShowReceipt(null)}
        >
          <div onClick={(e) => e.stopPropagation()} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 16 }}>
            {/* Cartão da reserva (capturável) */}
            <div
              ref={receiptRef}
              style={{
                background: "#0b1e33",
                borderRadius: 24,
                padding: "36px 40px 32px",
                width: 400,
                maxWidth: "92vw",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: 18,
                boxShadow: "0 32px 80px rgba(0,0,0,0.5)",
                border: "1px solid rgba(77,179,216,0.2)",
                fontFamily: "Manrope, sans-serif",
                color: "#e8f6ff",
              }}
            >
              {/* Título */}
              <div style={{ textAlign: "center" }}>
                <h2
                  style={{
                    margin: 0,
                    fontFamily: "Cormorant Garamond, serif",
                    fontSize: "1.8rem",
                    fontWeight: 700,
                    letterSpacing: "0.1em",
                    color: "#e8f6ff",
                  }}
                >
                  Minha Reserva
                </h2>
                <div
                  style={{
                    width: 60,
                    height: 3,
                    background: "linear-gradient(90deg, #1a6fa8, #4db3d8)",
                    borderRadius: 2,
                    margin: "10px auto 0",
                  }}
                />
              </div>

              {/* Info */}
              <div style={{ width: "100%", display: "flex", flexDirection: "column", gap: 12 }}>
                                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                                  <span style={{ fontSize: "0.75rem", color: "#7fb8d4", textTransform: "uppercase", letterSpacing: "0.1em", fontWeight: 600 }}>Nome</span>
                                  <span style={{ fontSize: "1.05rem", fontWeight: 600 }}>
                                    {showReceipt.nome || "-"}
                                  </span>
                                </div>
                                <div style={{ height: 1, background: "rgba(77,179,216,0.15)" }} />
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: "0.75rem", color: "#7fb8d4", textTransform: "uppercase", letterSpacing: "0.1em", fontWeight: 600 }}>Mesa{showReceipt.mesas.length > 1 ? "s" : ""}</span>
                  <span style={{ fontSize: "1.15rem", fontWeight: 700 }}>
                    {showReceipt.mesas.sort((a, b) => a - b).join(", ")}
                  </span>
                </div>
                <div style={{ height: 1, background: "rgba(77,179,216,0.15)" }} />
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: "0.75rem", color: "#7fb8d4", textTransform: "uppercase", letterSpacing: "0.1em", fontWeight: 600 }}>Data</span>
                  <span style={{ fontSize: "1.05rem", fontWeight: 600 }}>
                    {showReceipt.data.split("-").reverse().join("/")}
                  </span>
                </div>
                <div style={{ height: 1, background: "rgba(77,179,216,0.15)" }} />
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: "0.75rem", color: "#7fb8d4", textTransform: "uppercase", letterSpacing: "0.1em", fontWeight: 600 }}>CPF</span>
                  <span style={{ fontSize: "0.95rem", fontWeight: 600, letterSpacing: "0.05em" }}>
                    {showReceipt.cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4")}
                  </span>
                </div>
                <div style={{ height: 1, background: "rgba(77,179,216,0.15)" }} />
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: "0.75rem", color: "#7fb8d4", textTransform: "uppercase", letterSpacing: "0.1em", fontWeight: 600 }}>Lugares</span>
                  <span style={{ fontSize: "1.05rem", fontWeight: 600 }}>
                    {showReceipt.mesas.reduce((acc, id) => acc + (mesas.find((m) => m.id === id)?.lugares ?? 0), 0)}
                  </span>
                </div>
              </div>

              {/* QR Code genérico (SVG inline) */}
              <div style={{ marginTop: 4, display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
                <svg width="120" height="120" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
                  <rect width="120" height="120" fill="#fff" rx="8" />
                  {/* Top-left position pattern */}
                  <rect x="8" y="8" width="28" height="28" fill="#0b1e33" rx="3" />
                  <rect x="12" y="12" width="20" height="20" fill="#fff" rx="2" />
                  <rect x="16" y="16" width="12" height="12" fill="#0b1e33" rx="1" />
                  {/* Top-right position pattern */}
                  <rect x="84" y="8" width="28" height="28" fill="#0b1e33" rx="3" />
                  <rect x="88" y="12" width="20" height="20" fill="#fff" rx="2" />
                  <rect x="92" y="16" width="12" height="12" fill="#0b1e33" rx="1" />
                  {/* Bottom-left position pattern */}
                  <rect x="8" y="84" width="28" height="28" fill="#0b1e33" rx="3" />
                  <rect x="12" y="88" width="20" height="20" fill="#fff" rx="2" />
                  <rect x="16" y="92" width="12" height="12" fill="#0b1e33" rx="1" />
                  {/* Data modules */}
                  <rect x="44" y="8" width="6" height="6" fill="#0b1e33" />
                  <rect x="56" y="8" width="6" height="6" fill="#0b1e33" />
                  <rect x="44" y="20" width="6" height="6" fill="#0b1e33" />
                  <rect x="68" y="20" width="6" height="6" fill="#0b1e33" />
                  <rect x="44" y="32" width="6" height="6" fill="#0b1e33" />
                  <rect x="56" y="32" width="6" height="6" fill="#0b1e33" />
                  <rect x="8" y="44" width="6" height="6" fill="#0b1e33" />
                  <rect x="20" y="44" width="6" height="6" fill="#0b1e33" />
                  <rect x="32" y="44" width="6" height="6" fill="#0b1e33" />
                  <rect x="44" y="44" width="6" height="6" fill="#0b1e33" />
                  <rect x="56" y="44" width="6" height="6" fill="#0b1e33" />
                  <rect x="68" y="44" width="6" height="6" fill="#0b1e33" />
                  <rect x="80" y="44" width="6" height="6" fill="#0b1e33" />
                  <rect x="92" y="44" width="6" height="6" fill="#0b1e33" />
                  <rect x="104" y="44" width="6" height="6" fill="#0b1e33" />
                  <rect x="8" y="56" width="6" height="6" fill="#0b1e33" />
                  <rect x="32" y="56" width="6" height="6" fill="#0b1e33" />
                  <rect x="56" y="56" width="6" height="6" fill="#0b1e33" />
                  <rect x="80" y="56" width="6" height="6" fill="#0b1e33" />
                  <rect x="104" y="56" width="6" height="6" fill="#0b1e33" />
                  <rect x="8" y="68" width="6" height="6" fill="#0b1e33" />
                  <rect x="20" y="68" width="6" height="6" fill="#0b1e33" />
                  <rect x="44" y="68" width="6" height="6" fill="#0b1e33" />
                  <rect x="68" y="68" width="6" height="6" fill="#0b1e33" />
                  <rect x="92" y="68" width="6" height="6" fill="#0b1e33" />
                  <rect x="44" y="80" width="6" height="6" fill="#0b1e33" />
                  <rect x="56" y="80" width="6" height="6" fill="#0b1e33" />
                  <rect x="68" y="80" width="6" height="6" fill="#0b1e33" />
                  <rect x="44" y="92" width="6" height="6" fill="#0b1e33" />
                  <rect x="68" y="92" width="6" height="6" fill="#0b1e33" />
                  <rect x="80" y="92" width="6" height="6" fill="#0b1e33" />
                  <rect x="92" y="92" width="6" height="6" fill="#0b1e33" />
                  <rect x="56" y="104" width="6" height="6" fill="#0b1e33" />
                  <rect x="80" y="104" width="6" height="6" fill="#0b1e33" />
                  <rect x="104" y="104" width="6" height="6" fill="#0b1e33" />
                </svg>
                <span style={{ fontSize: "0.65rem", color: "#5a8faa", letterSpacing: "0.08em" }}>Apresente na entrada</span>
              </div>
            </div>

            {/* Botões fora do cartão (não capturados no PNG) */}
            <div style={{ display: "flex", gap: 12, width: 400, maxWidth: "92vw" }}>
              <button
                onClick={() => setShowReceipt(null)}
                style={{
                  flex: 1,
                  padding: "13px 0",
                  fontSize: "0.88rem",
                  fontWeight: 600,
                  borderRadius: 12,
                  border: "1px solid rgba(77,179,216,0.25)",
                  background: "rgba(8,28,48,0.8)",
                  color: "#7fb8d4",
                  cursor: "pointer",
                  fontFamily: "Manrope, sans-serif",
                }}
              >
                Fechar
              </button>
              <button
                onClick={handleBaixarReserva}
                style={{
                  flex: 1,
                  padding: "13px 0",
                  fontSize: "0.88rem",
                  fontWeight: 700,
                  borderRadius: 12,
                  border: "none",
                  background: "linear-gradient(135deg, #1a6fa8 0%, #4db3d8 100%)",
                  color: "#fff",
                  cursor: "pointer",
                  letterSpacing: "0.08em",
                  fontFamily: "Manrope, sans-serif",
                }}
              >
                Adicionar a Wallet
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes spin { 100% { transform: rotate(360deg); } }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slideRight { from { opacity: 0; transform: translateX(-30px); } to { opacity: 1; transform: translateX(0); } }
      `}</style>
    </div>
  );
}
