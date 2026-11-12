// S13 · ADR-035: en la nube, «Fuentes del corpus» e «Incorporar documentos» son de solo lectura
// para el publico. El token se guarda solo en memoria (api.js): ni localStorage, ni cookies, ni
// el bundle; se pierde al recargar. La autorizacion real la hace la API (401/403).
import { useState } from "react";

import { fijarTokenAdmin } from "../api";

export default function AccesoAdministracion({ onAcceso }) {
  const [valor, setValor] = useState("");

  const entrar = (evento) => {
    evento.preventDefault();
    if (!valor.trim()) return;
    fijarTokenAdmin(valor);
    setValor("");
    onAcceso();
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
        <button type="submit" className="error__reintentar">
          Acceder
        </button>
      </form>
    </section>
  );
}
