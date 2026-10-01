export const TAMANOS = ["pequeno", "normal", "grande", "mayor"];
export const INDICE_NORMAL = 1;
export const CLAVE_TAMANO = "tamano_texto";

export function leerTamano() {
  try {
    const indice = TAMANOS.indexOf(window.localStorage.getItem(CLAVE_TAMANO));
    return indice >= 0 ? indice : INDICE_NORMAL;
  } catch {
    // Almacenamiento bloqueado (modo privado, politicas del navegador): tamano normal.
    return INDICE_NORMAL;
  }
}

export function guardarTamano(indice) {
  try {
    window.localStorage.setItem(CLAVE_TAMANO, TAMANOS[indice]);
  } catch {
    // Sin almacenamiento la preferencia solo dura la sesion; no es un error para quien consulta.
  }
}
