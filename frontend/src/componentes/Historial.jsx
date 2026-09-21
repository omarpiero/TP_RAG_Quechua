export default function Historial({ entradas }) {
  if (entradas.length === 0) return null;

  return (
    <section className="historial">
      <h2 className="historial__titulo">Consultas de esta sesión</h2>
      <ul className="historial__lista">
        {entradas.map((entrada, indice) => (
          <li key={indice} className="historial__item">
            <span
              className={`historial__marca ${
                entrada.abstenida ? "historial__marca--abstenida" : ""
              }`}
              aria-hidden="true"
            />
            <span className="historial__consulta">{entrada.consulta}</span>
            <span className="historial__estado">
              {entrada.abstenida ? "sin respaldo" : "respondida"}
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}
