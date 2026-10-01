export const MAXIMO_CARACTERES = 300;

export function validarConsulta(texto) {
  const limpio = texto.trim();
  if (limpio.length === 0) return "Escribe una consulta (entre 1 y 300 caracteres).";
  if (limpio.length > MAXIMO_CARACTERES) {
    return `La consulta supera los ${MAXIMO_CARACTERES} caracteres (${limpio.length}). Acórtala.`;
  }
  return null;
}
