import { useEffect, useState } from "react";

import { borrarHistorial, consultar, obtenerEstado, obtenerHistorial, URL_API } from "./api";
import ConfiguracionNube from "./componentes/ConfiguracionNube";
import CajaConsulta from "./componentes/CajaConsulta";
import EstadoInicial from "./componentes/EstadoInicial";
import GestionCorpus from "./componentes/GestionCorpus";
import GestionFuentes from "./componentes/GestionFuentes";
import Historial from "./componentes/Historial";
import PanelPrediccion from "./componentes/PanelPrediccion";
import Respuesta from "./componentes/Respuesta";
import TamanoTexto from "./componentes/TamanoTexto";
import { guardarTamano, leerTamano, TAMANOS } from "./tamanoTexto";
import "./App.css";

const PESTANAS = [
  { id: "consulta", texto: "Consultar" },
  { id: "fuentes", texto: "Fuentes del corpus" },
  { id: "corpus", texto: "Incorporar documentos" },
  { id: "prediccion", texto: "Predicción ML" },
];

function Pestanas({ vista, onCambiar }) {
  return (
    <nav className="pestanas">
      {PESTANAS.map(({ id, texto }) => (
        <button
          key={id}
          className={`pestana ${vista === id ? "pestana--activa" : ""}`}
          onClick={() => onCambiar(id)}
        >
          {texto}
        </button>
      ))}
    </nav>
  );
}

function PieEstado({ estado }) {
  if (!estado) {
    return <span>Sin conexión con el servicio local</span>;
  }
  if (estado.entorno && estado.entorno !== "local") {
    return (
      <span data-testid="pie-entorno">
        Entorno: {estado.entorno} · API: {URL_API} · base {estado.motor_base_datos} · corpus{" "}
        {estado.origen_corpus} ({estado.fragmentos_indexados.toLocaleString("es-PE")}{" "}
        fragmentos, {estado.documentos_corpus} documentos) · redacción {estado.generador}
        {estado.generador === "gemini" ? ` (${estado.modelo})` : ""} · modelos ML{" "}
        {estado.predictores_disponibles ? "cargados" : "no cargados"} · umbral{" "}
        {estado.umbral_abstencion}
      </span>
    );
  }
  return (
    <span>
      {estado.fragmentos_indexados.toLocaleString("es-PE")} fragmentos indexados ·
      umbral de abstención {estado.umbral_abstencion} · modelo {estado.modelo} ·
      {estado.predictores_disponibles ? " predictores ML activos ·" : ""}
      procesamiento local
    </span>
  );
}

export default function App() {
  const [vista, setVista] = useState("consulta");
  const [resultado, setResultado] = useState(null);
  const [historial, setHistorial] = useState({ entradas: [], disponible: true });
  const [estado, setEstado] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);
  const [ultimaConsulta, setUltimaConsulta] = useState(null);
  const [tamano, setTamano] = useState(leerTamano);

  const cambiarTamano = (indice) => {
    const acotado = Math.min(TAMANOS.length - 1, Math.max(0, indice));
    setTamano(acotado);
    guardarTamano(acotado);
  };

  const cargarHistorial = () =>
    obtenerHistorial()
      .then((entradas) => setHistorial({ entradas, disponible: true }))
      .catch(() => setHistorial({ entradas: [], disponible: false }));

  useEffect(() => {
    obtenerEstado()
      .then(setEstado)
      .catch(() => setEstado(null));
    cargarHistorial();
  }, []);

  const lanzarConsulta = async (texto) => {
    setCargando(true);
    setError(null);
    setUltimaConsulta(texto);
    try {
      const respuesta = await consultar(texto);
      setResultado(respuesta);
      await cargarHistorial();
    } catch (e) {
      setError(e.message);
      setResultado(null);
    } finally {
      setCargando(false);
    }
  };

  const borrar = async () => {
    try {
      await borrarHistorial();
    } finally {
      await cargarHistorial();
    }
  };

  const otrasVistas = {
    prediccion: <PanelPrediccion />,
    fuentes: <GestionFuentes />,
    corpus: <GestionCorpus />,
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
        <TamanoTexto indice={tamano} onCambiar={cambiarTamano} />
      </header>

      {estado?.generador === "gemini" && (
        <output className="aviso-privacidad" data-testid="aviso-privacidad">
          En la versión en la nube, el texto de la consulta y los fragmentos se envían a la API de
          Google para redactar; no se envían datos personales.
        </output>
      )}

      {estado?.base_demostracion && (
        <output className="aviso-demostracion" data-testid="base-demostracion">
          Base de demostración: la mayoría de las consultas guardadas son generadas por pruebas, no
          demanda real.
        </output>
      )}

      <Pestanas vista={vista} onCambiar={setVista} />

      <main className="contenido">
        {vista === "consulta" ? (
          <>
            <EstadoInicial estado={estado} />
            {estado?.generador === "gemini" && <ConfiguracionNube />}
            <CajaConsulta onConsultar={lanzarConsulta} cargando={cargando} />

            {error && (
              <div className="error" role="alert">
                <p className="error__mensaje">{error}</p>
                <button
                  type="button"
                  className="error__reintentar"
                  onClick={() => lanzarConsulta(ultimaConsulta)}
                  disabled={cargando || !ultimaConsulta}
                >
                  Reintentar
                </button>
              </div>
            )}
            {cargando && (
              <output className="cargando">
                <span className="giro" aria-hidden="true" /> Buscando en el corpus…
              </output>
            )}

            <Respuesta resultado={resultado} />
            <Historial
              enLaNube={Boolean(estado?.entorno && estado.entorno !== "local")}
              entradas={historial.entradas}
              disponible={historial.disponible}
              onBorrar={borrar}
            />
          </>
        ) : (
          otrasVistas[vista]
        )}
      </main>

      <footer className="pie">
        <PieEstado estado={estado} />
      </footer>
    </div>
  );
}
