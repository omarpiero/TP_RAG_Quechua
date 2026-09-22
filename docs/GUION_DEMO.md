# Guion de la demostración del PMV

Orden sugerido para la grabación y para la sesión 3 de monitoreo. Duración estimada: entre
6 y 8 minutos. Cada bloque indica qué mostrar y qué conviene decir mientras se muestra.

## Antes de empezar

Arrancar el back-end **al menos dos minutos antes** de grabar. El modelo tarda cerca de un
minuto en cargarse en memoria de video, y hasta que termina la primera consulta sería
lenta. Comprobar en `http://127.0.0.1:8000/api/estado` que `generador_disponible` y
`base_datos_disponible` están ambos en `true`.

Dejar abiertas cuatro pestañas: la aplicación (`localhost:5173`), la documentación de la
API (`localhost:8000/docs`), el editor con la estructura de carpetas y una terminal.

## 1. El problema (40 s)

Mostrar uno de los PDF del corpus, por ejemplo el diccionario. Señalar que son cientos de
páginas sin ninguna forma de consulta semántica, y que el quechua wanka está clasificado
como lengua severamente amenazada.

> «El material existe y es público, pero no se puede consultar. Ese es el problema que
> resuelve el sistema.»

## 2. Consulta con respaldo documental (60 s)

En la pestaña **Consultar**, escribir `¿cómo se dice zorro en quechua wanka?`.

Señalar tres cosas en la respuesta: la forma quechua, el fragmento original y el documento
con su número de página.

> «La respuesta no sale del modelo: sale del fragmento recuperado, y el sistema muestra de
> dónde lo sacó para que cualquiera pueda verificarlo en la fuente.»

## 3. La salvaguarda antialucinación (60 s)

Escribir `¿cómo se dice criptomoneda en quechua wanka?`.

Mostrar que el sistema declara la ausencia de información y que la similitud recuperada
(0.050) queda muy por debajo del umbral de 0.48.

> «Aquí está la decisión central del proyecto. El sistema podría inventar una palabra y
> sonaría convincente. Sobre una lengua en peligro, una forma inventada entra en
> circulación y ya no se retira, así que preferimos no responder. Y el modelo de lenguaje
> ni siquiera llega a ejecutarse: la decisión se toma antes.»

Conviene mencionar el dato medido: sobre 28 consultas construidas deliberadamente fuera de
la cobertura del corpus, el sistema se abstuvo en las 28.

## 4. Consulta en inglés (50 s)

Escribir `how do you say dog in Wanka Quechua?`.

Señalar el recuadro que indica con qué término se buscó realmente.

> «La consulta se traduce al español antes de buscar, porque el corpus está en español y
> quechua. Lo que nunca se traduce es la forma quechua: esa sale literal del documento.»

## 5. Arquitectura hexagonal (90 s)

Mostrar en el editor la estructura `domain / application / infrastructure`, abrir un puerto
—por ejemplo `GeneradorTextoPort`— y después su adaptador `OllamaGenerador`.

> «El núcleo no sabe que existe Ollama, ni PostgreSQL, ni React. Solo conoce interfaces. Por
> eso, cuando el proyecto pase a la aplicación móvil, se sustituye el adaptador y el núcleo
> no cambia.»

Mostrar `infrastructure/contenedor.py` como el único punto donde se decide qué tecnología
concreta se usa.

## 6. Base de datos y trazabilidad persistida (50 s)

Ir a `localhost:8000/docs` y ejecutar `GET /api/historial`.

> «Cada consulta queda registrada con su respuesta, su similitud y los fragmentos que la
> respaldan. Las consultas en las que el sistema se abstiene son, además, el dato con el que
> el siguiente incremento entrenará los modelos de predicción de cobertura.»

## 7. Gestión de fuentes e ingesta documental (70 s)

En la pestaña **Fuentes del corpus**, mostrar el registro de una fuente e intentar guardar
una sin licenciamiento: el sistema la rechaza.

> «No es una validación del formulario: es una regla del dominio. Una fuente sin
> licenciamiento declarado no puede entrar al corpus, y eso responde al compromiso de
> gobernanza de datos indígenas que asumimos.»

En la pestaña **Incorporar documentos**, subir un PDF y mostrar el resultado: páginas con
capa de texto, fragmentos generados y el índice reconstruido sin reiniciar el servicio.

## 8. Verificación automatizada (40 s)

En la terminal, ejecutar `pytest tests/ -v`.

> «Las pruebas no comprueban solo que el código funciona: comprueban que el sistema no
> responde a ninguna de las consultas que quedan fuera de la cobertura del corpus. Si
> alguien rompe la salvaguarda, la batería falla.»

## 9. Cierre (30 s)

> «Todo se ejecuta en local: ninguna consulta ni ningún fragmento del corpus sale del
> equipo. Y el sistema no pretende ser una autoridad lingüística: es una herramienta de
> consulta sobre fuentes ya publicadas, que siempre dice de dónde viene lo que responde.»

## Datos que conviene tener a mano

| Dato | Valor |
|---|---|
| Fragmentos indexados | 3 605 |
| Documentos del corpus | 8 |
| recall@5 en español | 1.000 |
| recall@5 en inglés con traducción previa | 0.950 |
| Umbral de abstención | 0.48 |
| Falsos positivos | 0 de 28 |
| Latencia de respuesta | 3,3 s en español · 5,8 s en inglés |
| Pruebas automatizadas | 27 |
