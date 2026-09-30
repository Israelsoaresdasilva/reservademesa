// Camada HTTP mínima para o backend FastAPI.
// A URL base vem de `VITE_API_URL` (ex.: http://localhost:8000); sem ela, usa o default.

const BASE_URL = (import.meta.env.VITE_API_URL ?? "http://localhost:8000").replace(/\/+$/, "");

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers ?? {}),
      },
    });
  } catch {
    throw new ApiError("Não foi possível conectar ao servidor.", 0);
  }

  const data = (await response.json().catch(() => null)) as Record<string, unknown> | null;

  if (!response.ok) {
    const message =
      typeof data?.message === "string" ? data.message : `Erro ${response.status}`;
    throw new ApiError(message, response.status);
  }

  return data as T;
}
