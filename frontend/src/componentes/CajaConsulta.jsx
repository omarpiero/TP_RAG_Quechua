import { useState } from "react";

const EJEMPLOS = ["perro", "agua", "zorro", "casa"];

export default function CajaConsulta({ onConsultar, cargando }) {
  const [texto, setTexto] = useState("");

  const enviar = (evento) => {
    evento.preventDefault();
    const limpio = texto.trim();
    if (limpio && !cargando) onConsultar(limpio);
  };

  const usarEjemplo = (palabra) => {
    const consulta = `¿cómo se dice ${palabra} en quechua wanka?`;
    setTexto(consulta);
    onConsultar(consulta);
  };

  return (
    <form className="caja" onSubmit={enviar}>
      <label className="caja__etiqueta" htmlFor="consulta">
        Escriba su consulta en español o inglés
      </label>
      <div className="caja__fila">
        <input
          id="consulta"
          className="caja__entrada"
          type="text"
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          placeholder="¿cómo se dice zorro en quechua wanka?"
          autoComplete="off"
          disabled={cargando}
        />
        <button className="caja__boton" type="submit" disabled={cargando || !texto.trim()}>
          {cargando ? "Consultando…" : "Consultar"}
        </button>
      </div>

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
