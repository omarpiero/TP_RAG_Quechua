export default function Respuesta({ resultado }) {
  if (!resultado) return null;

  const {
    abstenida,
    texto,
    respaldo,
    similitud_maxima,
    aviso,
    consulta_traducida,
    pasajes = [],
  } = resultado;

  const hayPasajes = pasajes.length > 0;

  return (
    <section
      className={`respuesta ${abstenida ? "respuesta--abstenida" : ""}`}
      aria-live="polite"
    >
      <h2 className="respuesta__titulo">
        {abstenida
          ? hayPasajes
            ? "Sin respuesta confirmada"
            : "Sin respaldo documental"
          : "Respuesta"}
      </h2>

      {consulta_traducida && (
        <p className="respuesta__traduccion">
          La consulta se tradujo al español para buscar en el corpus:{" "}
          <strong>{consulta_traducida}</strong>. El término en quechua se toma literal del
          fragmento, sin traducir.
        </p>
      )}

      <p className="respuesta__texto">{texto}</p>

      {respaldo.length > 0 && (
        <div className="respaldo">
          <h3 className="respaldo__titulo">Fuente consultada</h3>
          {respaldo.map((f) => (
            <article key={f.fragmento_id} className="respaldo__item">
              <blockquote className="respaldo__cita">{f.texto}</blockquote>
              <p className="respaldo__origen">
                {f.documento} — página {f.pagina}
              </p>
              <p className="respaldo__metricas">
                Similitud {f.puntuacion.toFixed(3)}
                {f.coincidencia_lema && " · entrada exacta del diccionario"}
              </p>
              {f.derivado_ocr && (
                <p className="respaldo__aviso-ocr">
                  Texto derivado por reconocimiento óptico: puede contener errores de
                  transcripción.
                </p>
              )}
            </article>
          ))}
        </div>
      )}

      {hayPasajes && (
        <div className="pasajes">
          <h3 className="pasajes__titulo">Pasajes que podrían tratarla</h3>
          <p className="pasajes__nota">
            El sistema no afirma que respondan a la consulta. La similitud léxica no
            distingue una pregunta de gramática que el corpus cubre de una que no, de modo
            que el material se entrega literal y citado para que lo juzgue quien consulta.
          </p>
          {pasajes.map((f) => (
            <article key={f.fragmento_id} className="pasajes__item">
              <blockquote className="pasajes__cita">{f.texto}</blockquote>
              <p className="pasajes__origen">
                {f.documento} — página {f.pagina}
              </p>
            </article>
          ))}
        </div>
      )}

      <footer className="respuesta__pie">
        <p className="respuesta__aviso">{aviso}</p>
        <p className="respuesta__similitud">
          Similitud máxima recuperada: {similitud_maxima.toFixed(3)}
        </p>
      </footer>
    </section>
  );
}
