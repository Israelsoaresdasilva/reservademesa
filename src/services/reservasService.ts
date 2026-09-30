// Serviço de reservas — consome os endpoints públicos /api/reservas do backend.
import { request } from "./api";

export interface Reserva {
  id: string;
  nome: string;
  cpf: string;
  telefone: string;
  numeroPessoas: number;
  data: string; // YYYY-MM-DD
  horario: string; // HH:MM
  mesa: string;
  createdAt: string;
  updatedAt: string;
}

export interface CriarReservaInput {
  nome: string;
  cpf: string;
  telefone: string;
  numeroPessoas: number;
  data: string;
  horario: string;
  mesa: string;
}

interface CriarReservaResponse {
  success: boolean;
  message: string;
  reserva: Reserva;
}

interface ListarReservasResponse {
  success: boolean;
  items: Reserva[];
  total: number;
}

export async function criarReserva(input: CriarReservaInput): Promise<Reserva> {
  const body = await request<CriarReservaResponse>("/api/reservas", {
    method: "POST",
    body: JSON.stringify(input),
  });
  return body.reserva;
}

export async function listarReservas(data?: string): Promise<Reserva[]> {
  const query = data ? `?data=${encodeURIComponent(data)}` : "";
  const body = await request<ListarReservasResponse>(`/api/reservas${query}`);
  return body.items;
}

export async function excluirReserva(id: string): Promise<void> {
  await request<{ success: boolean }>(`/api/reservas/${id}`, { method: "DELETE" });
}
