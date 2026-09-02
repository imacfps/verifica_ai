import { API_BASE_URL } from "../config.js";

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

/**
 * Envia uma imagem para análise. Usa AbortController para não deixar
 * a requisição pendurada indefinidamente caso a API não responda.
 */
export async function analyzeImage(file, { signal } = {}) {
  const form = new FormData();
  form.append("file", file);

  let res;
  try {
    res = await fetch(`${API_BASE_URL}/analyze`, {
      method: "POST",
      body: form,
      signal,
    });
  } catch {
    throw new ApiError("Não foi possível conectar à API. Verifique se ela está rodando.", 0);
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(body.detail || `Erro ${res.status} na API`, res.status);
  }

  return res.json();
}
