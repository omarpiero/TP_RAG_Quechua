// Capturas de evidencia de la S13 (FURPS+ y OWASP). Usa el Playwright de frontend/node_modules.
//
//   node capturar.mjs url  <salida.png> <url> [pestana] [esperarSelector]
//       Abre la URL, opcionalmente pulsa la pestana (texto del boton) y dibuja una barra con la
//       URL real y la hora UTC encima de la pagina, para que la captura muestre de donde sale.
//   node capturar.mjs texto <salida.png> <titulo> <archivo.txt>
//       Renderiza la salida de un comando (o un fragmento de codigo) como captura de terminal.
//
// No escribe nada en la API: solo navega (GET) y pulsa pestanas.
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const aqui = dirname(fileURLToPath(import.meta.url));
const require = createRequire(resolve(aqui, "../../../../frontend/package.json"));
const { chromium } = require("@playwright/test");

const [modo, salida, a, b, c] = process.argv.slice(2);
const escapar = (s) => s.replace(/[&<>]/g, (x) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" })[x]);

const navegador = await chromium.launch();
const page = await navegador.newPage({ viewport: { width: 1366, height: 900 }, locale: "es-PE" });

if (modo === "url") {
  await page.goto(a, { waitUntil: "networkidle", timeout: 180_000 });
  if (b) {
    await page.getByRole("button", { name: b }).click();
    await page.waitForLoadState("networkidle");
  }
  if (c) await page.locator(c).first().waitFor({ timeout: 120_000 });
  await page.waitForTimeout(1500);
  await page.evaluate((hora) => {
    const barra = document.createElement("div");
    barra.textContent = `URL: ${location.href}   ·   ${hora}`;
    barra.style.cssText =
      "position:relative;z-index:99999;background:#202124;color:#e8eaed;font:14px monospace;" +
      "padding:8px 12px;border-bottom:3px solid #8ab4f8";
    document.body.prepend(barra);
  }, new Date().toISOString().replace("T", " ").slice(0, 19) + " UTC");
} else if (modo === "texto") {
  const cuerpo = readFileSync(b, "utf8");
  await page.setContent(
    `<body style="margin:0;background:#1e1e1e"><div style="background:#323233;color:#ccc;` +
      `font:13px sans-serif;padding:6px 12px">${escapar(a)}</div><pre style="color:#d4d4d4;` +
      `font:13px Consolas,monospace;padding:12px;margin:0;white-space:pre-wrap">` +
      `${escapar(cuerpo)}</pre></body>`,
  );
} else {
  throw new Error("modo debe ser 'url' o 'texto'");
}
await page.screenshot({ path: salida, fullPage: true });
await navegador.close();
console.log("captura:", salida);
