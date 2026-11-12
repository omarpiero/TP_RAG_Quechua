// S13 · fase 2: modo nube (escritura_protegida) — solo lectura, token en memoria e historial por sesión.
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";

const ESTADO_NUBE = {
  fragmentos_indexados: 3607,
  umbral_abstencion: 0.48,
  generador_disponible: true,
  base_datos_disponible: true,
  modelo: "gemini-3.5-flash-lite",
  entorno: "staging",
  generador: "extractivo",
  escritura_protegida: true,
};
const json = (c, s = 200) => Promise.resolve({ ok: s < 400, status: s, json: () => Promise.resolve(c) });

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.resetModules();
});

describe("modo nube con escritura protegida", () => {
  it("las pestañas de administración piden el token y el historial no se pide al servidor", async () => {
    const falso = vi.fn((url) => {
      if (url.endsWith("/api/estado")) return json(ESTADO_NUBE);
      return json([]);
    });
    vi.stubGlobal("fetch", falso);
    render(<App />);
    await screen.findByText("Estado del sistema");
    expect(falso.mock.calls.some(([u]) => u.endsWith("/api/historial"))).toBe(false);
    expect(screen.getByText(/Solo ves las consultas de esta pestaña/)).toBeInTheDocument();

    const nav = within(document.querySelector("nav.pestanas"));
    fireEvent.click(nav.getByRole("button", { name: "Fuentes del corpus" }));
    expect(screen.getByTestId("solo-lectura")).toHaveTextContent("Modo solo lectura");
    expect(screen.queryByText("Registrar fuente")).not.toBeInTheDocument();
    fireEvent.click(nav.getByRole("button", { name: "Incorporar documentos" }));
    expect(screen.getByTestId("solo-lectura")).toBeInTheDocument();
  });

  it("con el token, la gestión se habilita y las peticiones llevan X-Admin-Token", async () => {
    const falso = vi.fn((url) => {
      if (url.endsWith("/api/estado")) return json(ESTADO_NUBE);
      return json([]);
    });
    vi.stubGlobal("fetch", falso);
    const localStorageSet = vi.spyOn(Storage.prototype, "setItem");
    render(<App />);
    await screen.findByText("Estado del sistema");
    const nav = within(document.querySelector("nav.pestanas"));
    fireEvent.click(nav.getByRole("button", { name: "Fuentes del corpus" }));
    fireEvent.change(screen.getByLabelText("Token de administración"), {
      target: { value: "token-de-prueba" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Acceder" }));
    expect(screen.queryByTestId("solo-lectura")).not.toBeInTheDocument();
    await screen.findByText("Registrar nueva fuente");
    const pedidaFuentes = falso.mock.calls.find(([u]) => u.endsWith("/api/fuentes"));
    expect(pedidaFuentes[1].headers["X-Admin-Token"]).toBe("token-de-prueba");
    expect(localStorageSet.mock.calls.some(([, v]) => String(v).includes("token-de-prueba"))).toBe(
      false,
    );
  });
});
