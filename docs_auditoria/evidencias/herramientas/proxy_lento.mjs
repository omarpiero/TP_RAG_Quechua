// Simula el arranque en frio de Render para las capturas de REF-02 (ADR-033): reenvia todo a la
// API local y retrasa las peticiones a /api/estado y /api/consultas los milisegundos indicados.
//   node proxy_lento.mjs <puerto> <api_destino> <retraso_ms>
import http from "node:http";

const [puerto, destino, retraso] = [Number(process.argv[2]), new URL(process.argv[3]), Number(process.argv[4])];

http
  .createServer((pet, res) => {
    const lento = /^\/api\/(estado|consultas)/.test(pet.url) && pet.method !== "OPTIONS";
    setTimeout(
      () => {
        const sal = http.request(
          { host: destino.hostname, port: destino.port, path: pet.url, method: pet.method, headers: pet.headers },
          (r) => {
            res.writeHead(r.statusCode, r.headers);
            r.pipe(res);
          },
        );
        sal.on("error", () => res.writeHead(502).end());
        pet.pipe(sal);
      },
      lento ? retraso : 0,
    );
  })
  .listen(puerto, "127.0.0.1", () => console.log(`proxy lento en ${puerto} -> ${destino} (+${retraso} ms)`));
