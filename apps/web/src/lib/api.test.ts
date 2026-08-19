import { afterEach, describe, expect, it, vi } from "vitest";

import { askQuestion } from "./api";

afterEach(() => vi.restoreAllMocks());

describe("API client", () => {
  it("surfaces the backend message on an error", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ message: "Documento inválido" }), {
          status: 400,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    await expect(askQuestion("pregunta válida", 5)).rejects.toThrow("Documento inválido");
  });
});
