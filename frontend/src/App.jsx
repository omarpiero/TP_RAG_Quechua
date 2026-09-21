import { useEffect, useState } from "react";

import { consultar, obtenerEstado } from "./api";
import CajaConsulta from "./componentes/CajaConsulta";
import Historial from "./componentes/Historial";
import Respuesta from "./componentes/Respuesta";
import "./App.css";

const TAMANOS = ["normal", "grande", "mayor"];

export default function App() {
  const [resultado, setResultado] = useState(null);
  const [historial, setHistorial] = useState([]);
  const [estado, setEstado] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);
  const [tamano, setTamano] = useState(0);

  useEffect(() => {
    obtenerEstado()
      .then(setEstado)
      .catch(() => setEstado(null));
  }, []);

  const lanzarConsulta = async (texto) => {
    setCargando(true);
    setError(null);
    try {
      const respuesta = await consultar(texto);
      setResultado(respuesta);
      setHistorial((previo) => [
        { consulta: texto, abstenida: respuesta.abstenida },
        ...previo,
      ]);
    } catch (e) {
      setError(e.message);
      setResultado(null);
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className={`aplicacion aplicacion--${TAMANOS[tamano]}`}>
      <header className="cabecera">
        <div>
          <h1 className="cabecera__titulo">Asistente de consulta del quechua wanka</h1>
          <p className="cabecera__subtitulo">
            Consulta sobre el corpus documental publicado de la variedad wanka de Junín
          </p>
        </div>
        <button
          className="cabecera__tipografia"
          onClick={() => setTamano((t) => (t + 1) % TAMANOS.length)}
          title="Cambiar el tamaño del texto"
        >
          A<span aria-hidden="true">+</span>
        </button>
      </header>

      <main className="contenido">
        <CajaConsulta onConsultar={lanzarConsulta} cargando={cargando} />

        {error && <p className="error">{error}</p>}
        {cargando && <p className="cargando">Buscando en el corpus…</p>}

        <Respuesta resultado={resultado} />
        <Historial entradas={historial} />
      </main>

      <footer className="pie">
        {estado ? (
          <span>
            {estado.fragmentos_indexados.toLocaleString("es-PE")} fragmentos indexados ·
            umbral de abstención {estado.umbral_abstencion} · modelo {estado.modelo} ·
            procesamiento local
          </span>
        ) : (
          <span>Sin conexión con el servicio local</span>
        )}
      </footer>
    </div>
  );
}
