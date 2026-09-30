import { useEffect, useMemo, useState, type FormEvent } from "react";
import {
  excluirReserva,
  listarReservas,
  type Reserva,
} from "../../services/reservasService";

// Credenciais fixas (demonstração). Em produção, usar autenticação real no backend.
const ADMIN_USER = "oceanblueadm";
const ADMIN_PASS = "blue2026";
const AUTH_KEY = "oceanblue_admin";

function todayIsoDate(): string {
  const today = new Date();
  const y = today.getFullYear();
  const m = String(today.getMonth() + 1).padStart(2, "0");
  const d = String(today.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function formatDateBr(date: string): string {
  if (!date) return "-";
  return date.split("-").reverse().join("/");
}

function maskCpf(cpf: string): string {
  const digits = (cpf || "").replace(/\D/g, "");
  if (digits.length !== 11) return cpf;
  return `***.***.***-${digits.slice(-2)}`;
}

const NAVY = "#0a2540";
const AZURE = "#4db3d8";

export default function AdminReservas() {
  const [autenticado, setAutenticado] = useState(
    () => sessionStorage.getItem(AUTH_KEY) === "1",
  );
  const [usuario, setUsuario] = useState("");
  const [senha, setSenha] = useState("");
  const [loginError, setLoginError] = useState("");

  const [data, setData] = useState(todayIsoDate());
  const [reservas, setReservas] = useState<Reserva[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!autenticado) return;
    let active = true;
    listarReservas(data)
      .then((items) => {
        if (!active) return;
        setReservas(items);
        setError("");
      })
      .catch(() => {
        if (!active) return;
        setError("Não foi possível carregar as reservas. Verifique se o backend está no ar.");
        setReservas([]);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [data, autenticado]);

  const totalPessoas = useMemo(
    () => reservas.reduce((acc, r) => acc + r.numeroPessoas, 0),
    [reservas],
  );

  function handleLogin(event: FormEvent) {
    event.preventDefault();
    if (usuario.trim() === ADMIN_USER && senha === ADMIN_PASS) {
      sessionStorage.setItem(AUTH_KEY, "1");
      setAutenticado(true);
      setLoginError("");
      setLoading(true);
      setError("");
    } else {
      setLoginError("Usuário ou senha inválidos.");
    }
  }

  function handleLogout() {
    sessionStorage.removeItem(AUTH_KEY);
    setAutenticado(false);
    setUsuario("");
    setSenha("");
  }

  async function handleExcluir(id: string) {
    try {
      await excluirReserva(id);
      setReservas((prev) => prev.filter((r) => r.id !== id));
    } catch {
      setError("Não foi possível excluir a reserva.");
    }
  }

  if (!autenticado) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: `linear-gradient(135deg, ${NAVY} 0%, #163d5c 60%, #1a6fa8 100%)`,
          fontFamily: "Manrope, sans-serif",
          padding: 24,
        }}
      >
        <form
          onSubmit={handleLogin}
          style={{
            background: "rgba(8, 28, 48, 0.96)",
            border: "1px solid rgba(77, 179, 216, 0.25)",
            borderRadius: 20,
            padding: "36px 32px",
            width: 360,
            maxWidth: "92vw",
            display: "flex",
            flexDirection: "column",
            gap: 16,
            boxShadow: "0 24px 64px rgba(0,0,0,0.5)",
          }}
        >
          <h1
            style={{
              margin: 0,
              fontFamily: "Cormorant Garamond, serif",
              fontWeight: 700,
              fontSize: "1.7rem",
              color: "#e8f6ff",
              letterSpacing: "0.06em",
              textAlign: "center",
            }}
          >
            Painel Administrativo
          </h1>
          <p style={{ margin: 0, color: "#7fb8d4", fontSize: "0.85rem", textAlign: "center" }}>
            Ocean Blue — acesso restrito
          </p>

          <label style={{ display: "flex", flexDirection: "column", gap: 6, color: "#7fb8d4", fontSize: "0.75rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em" }}>
            Usuário
            <input
              type="text"
              value={usuario}
              onChange={(e) => setUsuario(e.target.value)}
              autoComplete="username"
              style={{
                padding: "12px 14px",
                borderRadius: 10,
                border: "1px solid rgba(77,179,216,0.3)",
                background: "rgba(77,179,216,0.08)",
                color: "#e8f6ff",
                fontSize: "1rem",
                outline: "none",
              }}
            />
          </label>

          <label style={{ display: "flex", flexDirection: "column", gap: 6, color: "#7fb8d4", fontSize: "0.75rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em" }}>
            Senha
            <input
              type="password"
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
              autoComplete="current-password"
              style={{
                padding: "12px 14px",
                borderRadius: 10,
                border: "1px solid rgba(77,179,216,0.3)",
                background: "rgba(77,179,216,0.08)",
                color: "#e8f6ff",
                fontSize: "1rem",
                outline: "none",
              }}
            />
          </label>

          {loginError && (
            <p style={{ margin: 0, color: "#e74c3c", fontSize: "0.82rem", fontWeight: 600 }}>
              {loginError}
            </p>
          )}

          <button
            type="submit"
            style={{
              padding: "13px 0",
              borderRadius: 12,
              border: "none",
              background: "linear-gradient(135deg, #1a6fa8 0%, #4db3d8 100%)",
              color: "#fff",
              fontWeight: 700,
              fontSize: "1rem",
              cursor: "pointer",
              letterSpacing: "0.06em",
            }}
          >
            Entrar
          </button>

          <p style={{ margin: 0, color: "#5a8faa", fontSize: "0.72rem", textAlign: "center" }}>
            Demonstração: usuário <strong>oceanblueadm</strong> · senha <strong>blue2026</strong>
          </p>
        </form>
      </div>
    );
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        background: `linear-gradient(135deg, ${NAVY} 0%, #163d5c 60%, #1a6fa8 100%)`,
        color: "#e8f6ff",
        fontFamily: "Manrope, sans-serif",
        padding: "32px 24px",
      }}
    >
      <div style={{ maxWidth: 960, margin: "0 auto" }}>
        <header style={{ marginBottom: 28, display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 16, flexWrap: "wrap" }}>
          <div>
            <h1
              style={{
                fontFamily: "Cormorant Garamond, serif",
                fontWeight: 700,
                fontSize: "2rem",
                letterSpacing: "0.06em",
                margin: 0,
              }}
            >
              Reservas do dia
            </h1>
            <p style={{ color: "#7fb8d4", margin: "6px 0 0", fontSize: "0.9rem" }}>
              Ocean Blue — painel administrativo
            </p>
          </div>
          <button
            onClick={handleLogout}
            style={{
              background: "rgba(231,76,60,0.12)",
              border: "1px solid rgba(231,76,60,0.35)",
              color: "#e74c3c",
              padding: "8px 16px",
              borderRadius: 8,
              cursor: "pointer",
              fontWeight: 700,
              fontSize: "0.8rem",
            }}
          >
            Sair
          </button>
        </header>

        <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginBottom: 24 }}>
          <label style={{ display: "flex", flexDirection: "column", gap: 6, fontSize: "0.78rem", color: "#7fb8d4", fontWeight: 600 }}>
            Selecione a data
            <input
              type="date"
              value={data}
              onChange={(e) => {
                setData(e.target.value);
                setLoading(true);
                setError("");
              }}
              style={{
                padding: "10px 14px",
                borderRadius: 10,
                border: `2px solid ${AZURE}`,
                background: "#e8f6ff",
                color: "#0b1e33",
                fontWeight: 700,
                fontSize: "1rem",
                colorScheme: "dark",
              }}
            />
          </label>
        </div>

        <div style={{ display: "flex", gap: 16, marginBottom: 24 }}>
          <div
            style={{
              flex: 1,
              background: "rgba(77, 179, 216, 0.08)",
              border: "1px solid rgba(77, 179, 216, 0.25)",
              borderRadius: 14,
              padding: "16px 20px",
            }}
          >
            <div style={{ color: "#7fb8d4", fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.08em" }}>
              Total de reservas
            </div>
            <div style={{ fontSize: "2rem", fontWeight: 700, marginTop: 4 }}>{reservas.length}</div>
          </div>
          <div
            style={{
              flex: 1,
              background: "rgba(77, 179, 216, 0.08)",
              border: "1px solid rgba(77, 179, 216, 0.25)",
              borderRadius: 14,
              padding: "16px 20px",
            }}
          >
            <div style={{ color: "#7fb8d4", fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.08em" }}>
              Total de pessoas
            </div>
            <div style={{ fontSize: "2rem", fontWeight: 700, marginTop: 4 }}>{totalPessoas}</div>
          </div>
        </div>

        {loading && (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              gap: 16,
              padding: "56px 24px",
              textAlign: "center",
            }}
          >
            <div
              style={{
                width: 44,
                height: 44,
                border: "4px solid rgba(174, 214, 236, 0.25)",
                borderTop: "4px solid #4db3d8",
                borderRadius: "50%",
                animation: "adminSpin 0.9s linear infinite",
              }}
            />
            <span style={{ color: "#aed6ec", fontSize: "0.95rem", fontWeight: 600 }}>
              Carregando reservas…
            </span>
          </div>
        )}

        {!loading && error && <p style={{ color: "#e74c3c", fontWeight: 600 }}>{error}</p>}

        {!loading && !error && reservas.length === 0 && (
          <div
            style={{
              border: "1px dashed rgba(77, 179, 216, 0.3)",
              borderRadius: 12,
              padding: "32px",
              textAlign: "center",
              color: "#7fb8d4",
            }}
          >
            Nenhuma reserva para {formatDateBr(data)}.
          </div>
        )}

        {!loading && !error && reservas.length > 0 && (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.9rem" }}>
              <thead>
                <tr style={{ textAlign: "left", color: "#7fb8d4", textTransform: "uppercase", fontSize: "0.72rem", letterSpacing: "0.08em" }}>
                  <th style={{ padding: "10px 12px", borderBottom: "1px solid rgba(77,179,216,0.3)" }}>Horário</th>
                  <th style={{ padding: "10px 12px", borderBottom: "1px solid rgba(77,179,216,0.3)" }}>Nome</th>
                  <th style={{ padding: "10px 12px", borderBottom: "1px solid rgba(77,179,216,0.3)" }}>Pessoas</th>
                  <th style={{ padding: "10px 12px", borderBottom: "1px solid rgba(77,179,216,0.3)" }}>Mesa</th>
                  <th style={{ padding: "10px 12px", borderBottom: "1px solid rgba(77,179,216,0.3)" }}>Telefone</th>
                  <th style={{ padding: "10px 12px", borderBottom: "1px solid rgba(77,179,216,0.3)" }}>CPF</th>
                  <th style={{ padding: "10px 12px", borderBottom: "1px solid rgba(77,179,216,0.3)" }}>Ações</th>
                </tr>
              </thead>
              <tbody>
                {reservas.map((r) => (
                  <tr key={r.id} style={{ borderBottom: "1px solid rgba(77,179,216,0.12)" }}>
                    <td style={{ padding: "12px", fontWeight: 700 }}>{r.horario}</td>
                    <td style={{ padding: "12px" }}>{r.nome}</td>
                    <td style={{ padding: "12px" }}>{r.numeroPessoas}</td>
                    <td style={{ padding: "12px" }}>{r.mesa}</td>
                    <td style={{ padding: "12px" }}>{r.telefone}</td>
                    <td style={{ padding: "12px", fontFamily: "monospace" }}>{maskCpf(r.cpf)}</td>
                    <td style={{ padding: "12px" }}>
                      <button
                        onClick={() => handleExcluir(r.id)}
                        style={{
                          background: "rgba(231,76,60,0.12)",
                          border: "1px solid rgba(231,76,60,0.35)",
                          color: "#e74c3c",
                          padding: "6px 12px",
                          borderRadius: 6,
                          cursor: "pointer",
                          fontWeight: 700,
                          fontSize: "0.78rem",
                        }}
                      >
                        Excluir
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      <style>{`
        @keyframes adminSpin { 100% { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
