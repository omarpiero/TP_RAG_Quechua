import { useState } from "react";

import { MAXIMO_CARACTERES, validarConsulta } from "../validacion";

const EJEMPLOS = ["perro", "agua", "zorro", "casa"];
export default function CajaConsulta({ onConsultar, cargando }) {
  const [texto, setTexto] = useState("");
  const [avisoValidacion, setAvisoValidacion] = useState(null);

  const enviar = (evento) => {
    evento.preventDefault();
    if (cargando) return;
    const problema = validarConsulta(texto);
    setAvisoValidacion(problema);
    // Una consulta no valida nunca llega a la API.
    if (!problema) onConsultar(texto.trim());
  };

  const usarEjemplo = (palabra) => {
    const consulta = `¿cómo se dice ${palabra} en quechua wanka?`;
    setTexto(consulta);
    setAvisoValidacion(null);
    onConsultar(consulta);
  };

  const largo = texto.trim().length;
  const excedido = largo > MAXIMO_CARACTERES;

  return (
    <form className="caja" onSubmit={enviar} noValidate>
      <label className="caja__etiqueta" htmlFor="consulta">
        Escriba su consulta en español o inglés
      </label>
      <div className="caja__fila">
        <input
          id="consulta"
          className="caja__entrada"
          type="text"
          value={texto}
          onChange={(e) => {
            setTexto(e.target.value);
            setAvisoValidacion(null);
          }}
          placeholder="¿cómo se dice zorro en quechua wanka?"
          autoComplete="off"
          disabled={cargando}
          aria-invalid={Boolean(avisoValidacion) || excedido}
          aria-describedby="consulta-contador consulta-aviso"
        />
        <button className="caja__boton" type="submit" disabled={cargando}>
          {cargando ? (
            <>
              <span className="giro" aria-hidden="true" /> Consultando…
            </>
          ) : (
            "Consultar"
          )}
        </button>
      </div>

      <p
        id="consulta-contador"
        className={`caja__contador ${excedido ? "caja__contador--excedido" : ""}`}
      >
        {largo} / {MAXIMO_CARACTERES} caracteres
      </p>
      <p id="consulta-aviso" className="caja__aviso" role="alert">
        {avisoValidacion}
      </p>

      <div className="caja__ejemplos">
        <span className="caja__ejemplos-titulo">Ejemplos:</span>
        {EJEMPLOS.map((palabra) => (
          <button
            key={palabra}
            type="button"
            className="caja__ejemplo"
            onClick={() => usarEjemplo(palabra)}
            disabled={cargando}
          >
            {palabra}
          </button>
        ))}
      </div>
    </form>
  );
}
