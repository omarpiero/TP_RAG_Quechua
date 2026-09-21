const BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

async function pedir(ruta, opciones = {}) {
  const respuesta = await fetch(`${BASE}${ruta}`, {
    headers: { "Content-Type": "application/json" },
    ...opciones,
  });
  if (!respuesta.ok) {
    const detalle = await respuesta.json().catch(() => ({}));
    throw new Error(detalle.detail ?? `Error ${respuesta.status}`);
  }
  return respuesta.status === 204 ? null : respuesta.json();
}

export const consultar = (texto) =>
  pedir("/api/consultas", { method: "POST", body: JSON.stringify({ texto }) });

export const obtenerEstado = () => pedir("/api/estado");

export const obtenerHistorial = () => pedir("/api/historial");

export const listarFuentes = () => pedir("/api/fuentes");

export const crearFuente = (fuente) =>
  pedir("/api/fuentes", { method: "POST", body: JSON.stringify(fuente) });

export const actualizarFuente = (id, fuente) =>
  pedir(`/api/fuentes/${id}`, { method: "PUT", body: JSON.stringify(fuente) });

export const eliminarFuente = (id) =>
  pedir(`/api/fuentes/${id}`, { method: "DELETE" });
