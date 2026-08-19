import type { DocumentItem, PublicConfig, QueryResponse } from "./types";

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

async function parseResponse<T>(response: Response): Promise<T> {
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message ?? data.detail ?? "La solicitud no pudo completarse.");
  }
  return data as T;
}

export async function getConfig(): Promise<PublicConfig> {
  return parseResponse(await fetch(`${API_URL}/config`, { cache: "no-store" }));
}

export async function getDocuments(): Promise<DocumentItem[]> {
  return parseResponse(await fetch(`${API_URL}/documents`, { cache: "no-store" }));
}

export async function uploadDocument(file: File): Promise<DocumentItem> {
  const form = new FormData();
  form.append("file", file);
  return parseResponse(await fetch(`${API_URL}/documents`, { method: "POST", body: form }));
}

export async function askQuestion(
  question: string,
  topK: number,
  sessionId?: string,
): Promise<QueryResponse> {
  return parseResponse(
    await fetch(`${API_URL}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, top_k: topK, session_id: sessionId }),
    }),
  );
}
