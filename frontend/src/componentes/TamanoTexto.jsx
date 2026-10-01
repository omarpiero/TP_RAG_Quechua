import { INDICE_NORMAL, TAMANOS } from "../tamanoTexto";

export default function TamanoTexto({ indice, onCambiar }) {
  return (
    <div className="tamano" role="group" aria-label="Tamaño del texto">
      <button
        type="button"
        className="tamano__boton"
        aria-label="Reducir tamaño del texto"
        onClick={() => onCambiar(indice - 1)}
        disabled={indice <= 0}
      >
        A<span aria-hidden="true">−</span>
      </button>
      <button
        type="button"
        className="tamano__boton"
        aria-label="Restablecer tamaño del texto"
        onClick={() => onCambiar(INDICE_NORMAL)}
        disabled={indice === INDICE_NORMAL}
      >
        <span aria-hidden="true">A</span>
      </button>
      <button
        type="button"
        className="tamano__boton"
        aria-label="Aumentar tamaño del texto"
        onClick={() => onCambiar(indice + 1)}
        disabled={indice >= TAMANOS.length - 1}
      >
        A<span aria-hidden="true">+</span>
      </button>
    </div>
  );
}
