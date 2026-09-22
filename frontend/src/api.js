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

export const listarDocumentos = () => pedir("/api/corpus/documentos");

export const reindexar = () =>
  pedir("/api/corpus/reindexar", { method: "POST" });

export async function ingestarDocumento(datos) {
  const cuerpo = new FormData();
  Object.entries(datos).forEach(([clave, valor]) => cuerpo.append(clave, valor));

  // Sin Content-Type explicito: el navegador anade el boundary de multipart.
  const respuesta = await fetch(`${BASE}/api/corpus/documentos`, {
    method: "POST",
    body: cuerpo,
  });
  if (!respuesta.ok) {
    const detalle = await respuesta.json().catch(() => ({}));
    throw new Error(detalle.detail ?? `Error ${respuesta.status}`);
  }
  return respuesta.json();
}
