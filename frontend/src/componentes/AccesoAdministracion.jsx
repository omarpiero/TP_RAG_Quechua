// S13 · ADR-035: en la nube, «Fuentes del corpus» e «Incorporar documentos» son de solo lectura
// para el publico. El token se guarda solo en memoria (api.js): ni localStorage, ni cookies, ni
// el bundle; se pierde al recargar. Se valida contra la API antes de desbloquear la gestion; aun
// asi, la autorizacion real la hace la API en cada escritura (401/403).
import { useState } from "react";

import { verificarTokenAdmin } from "../api";

export default function AccesoAdministracion({ onAcceso }) {
  const [valor, setValor] = useState("");
  const [error, setError] = useState(null);
  const [comprobando, setComprobando] = useState(false);

  const entrar = async (evento) => {
    evento.preventDefault();
    if (!valor.trim()) return;
    setComprobando(true);
    setError(null);
    try {
      await verificarTokenAdmin(valor);
      setValor("");
      onAcceso();
    } catch (e) {
      setError(
        e?.estado === 401 || e?.estado === 403
          ? "Token de administración no válido. La gestión sigue en solo lectura."
          : e.message,
      );
    } finally {
      setComprobando(false);
    }
  };

  return (
    <section className="solo-lectura" data-testid="solo-lectura">
      <h2>Modo solo lectura</h2>
      <p>
        En la versión pública la gestión del corpus está reservada al equipo: registrar, editar o
        eliminar fuentes e incorporar documentos requiere el token de administración. La consulta y
        la predicción siguen disponibles para todos.
      </p>
      <form onSubmit={entrar} className="solo-lectura__form">
        <label htmlFor="token-admin">Token de administración</label>
        <input
          id="token-admin"
          type="password"
          autoComplete="off"
          value={valor}
          onChange={(e) => setValor(e.target.value)}
        />
        <button type="submit" className="error__reintentar" disabled={comprobando}>
          {comprobando ? "Comprobando…" : "Acceder"}
        </button>
      </form>
      {error && (
        <p className="error__mensaje" role="alert" data-testid="token-invalido">
          {error}
        </p>
      )}
    </section>
  );
}
