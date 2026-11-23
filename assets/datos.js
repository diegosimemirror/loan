// ============================================================
// PROCESO D1: Explorador de la base codificada
// Insumo:    data/base_codificada_v21.tsv, data/ficha_v21.tsv, data/fuentes_documentos.tsv, data/fechas_oficiales.tsv
// Resultado: tabla por contrato o por pregunta, con filtros; la dirección (#contrato=… o #var=…) abre una vista directa
// ============================================================

// Nombres cortos de cada operación (el objeto completo está en la variable A05)
const NOMBRES = {
  "BID-PE-L1060": "Agua y saneamiento de Lima (SEDAPAL)",
  "BID-PE-L1132": "Sistema Nacional de Control (Contraloría)",
  "BID-PE-L1026": "Catastro y titulación rural (MINAGRI)",
  "BID-PE-L1122": "Información estadística agraria (MINAGRI)",
  "BID-PE-L1153": "Residuos sólidos (MINAM)",
  "BID-PE-L1222": "Servicios al ciudadano (PCM)",
  "BID-PE-L1227": "Educación superior (MINEDU)",
  "BID-PE-L1232": "Bosques y clima (MINAM)",
  "BID-PE-L1254": "Transporte eléctrico (COFIDE)",
  "BIRF-7961": "Nutrición en Juntos",
  "BIRF-8034": "Electrificación rural",
  "BIRF-8212": "Calidad de la educación superior",
  "BIRF-8222": "Inclusión social (asistencia técnica)",
  "BIRF-8246": "Desarrollo rural de la sierra",
  "BIRF-8331": "Innovación agraria",
  "BIRF-8468": "Agua de Lima (financiamiento adicional)",
  "BIRF-8517": "Línea 2 del Metro de Lima",
  "BIRF-8562": "Transporte subnacional",
  "BIRF-8680": "Calidad ambiental (OEFA)",
  "BIRF-8682": "Innovación (FONDECYT)",
  "BIRF-8740": "Gestión de recursos hídricos (ANA)",
  "BIRF-8975": "Servicios de justicia",
  "BIRF-9035": "Catastro urbano",
  "BIRF-9039": "Sistema de emergencias 911",
  "BIRF-9040": "Metropolitano: extensión norte",
  "BIRF-9288": "Electrificación (MINEM)",
  "BIRF-9327": "Vacunación COVID-19",
  "BIRF-9334": "Innovación II",
  "BIRF-9616": "Riego resiliente al clima",
  "BIRF-9717": "Focalización de programas sociales (SINAFO)",
  "BIRF-9733": "Gestión del tránsito de Lima",
  "BIRF-9874": "Aguas residuales y economía circular",
};

// Lector de TSV: respeta campos entre comillas (las comillas internas van dobladas)
function leerTSV(texto) {
  const filas = []; let campo = "", fila = [], q = false;
  for (let i = 0; i < texto.length; i++) {
    const c = texto[i];
    if (q) { if (c === '"') { if (texto[i + 1] === '"') { campo += '"'; i++; } else q = false; } else campo += c; }
    else if (c === '"' && campo === "") q = true;
    else if (c === "\t") { fila.push(campo); campo = ""; }
    else if (c === "\n" || c === "\r") { if (c === "\r" && texto[i + 1] === "\n") i++; fila.push(campo); filas.push(fila); fila = []; campo = ""; }
    else campo += c;
  }
  if (campo !== "" || fila.length) { fila.push(campo); filas.push(fila); }
  const [cab, ...resto] = filas.filter(f => f.length > 1 || f[0] !== "");
  return resto.map(f => Object.fromEntries(cab.map((h, j) => [h, f[j] ?? ""])));
}
const $ = id => document.getElementById(id);
const el = (tag, props = {}, ...hijos) => { const e = document.createElement(tag); Object.assign(e, props); hijos.forEach(h => e.append(h)); return e; };
const banco = c => c.startsWith("BID") ? "BID" : "BIRF";
const codigo = c => c.replace("BID-", "").replace("BIRF-", "BIRF ");
let BASE = [], FICHA = [], FUENTES = [], FECHAS = {}, POR = {};

// ============================================================
// PROCESO D2: Cargar los datos y preparar los selectores
// ============================================================
Promise.all(["base_codificada_v21.tsv", "ficha_v21.tsv", "fuentes_documentos.tsv", "fechas_oficiales.tsv"]
  .map(f => fetch("data/" + f).then(r => { if (!r.ok) throw new Error(f); return r.text(); })))
  .then(([b, f, fu, fe]) => {
    BASE = leerTSV(b); FICHA = leerTSV(f); FUENTES = leerTSV(fu);
    leerTSV(fe).forEach(r => FECHAS[r.contrato] = r);
    BASE.forEach(r => (POR[r.contrato] ||= {})[r.id] = r);
    const contratos = Object.keys(POR).sort((a, b) => (POR[a].A07?.valor || "").localeCompare(POR[b].A07?.valor || ""));
    contratos.forEach(c => $("selContrato").append(el("option", { value: c, textContent: `${banco(c) === "BID" ? "BID" : "Banco Mundial"} ${codigo(c)} · ${NOMBRES[c] || ""} · ${(POR[c].A07?.valor || "").slice(0, 4)}` })));
    let grupo = null;
    FICHA.forEach(v => {
      if (!grupo || grupo.label !== v.bloque) { grupo = el("optgroup", { label: v.bloque }); $("selVariable").append(grupo); }
      grupo.append(el("option", { value: v.id, textContent: `${v.id} · ${v.variable}` }));
    });
    leerHash(); pintar();
  })
  .catch(e => { $("cuenta").textContent = "No se pudieron cargar los datos (" + e.message + "). Si abriste el archivo directamente, usa la versión publicada del sitio."; });

// ============================================================
// PROCESO D3: Vistas y filtros
// ============================================================
let modo = "contrato";
function leerHash() {
  const h = new URLSearchParams(location.hash.slice(1));
  if (h.get("var") && FICHA.some(v => v.id === h.get("var"))) { modo = "variable"; $("selVariable").value = h.get("var"); }
  else if (h.get("contrato") && POR[h.get("contrato")]) { modo = "contrato"; $("selContrato").value = h.get("contrato"); }
}
function fijarHash() { history.replaceState(null, "", modo === "variable" ? "#var=" + $("selVariable").value : "#contrato=" + $("selContrato").value); }
function chip(estado) { return el("span", { className: "estado " + estado.replace(" ", "-"), textContent: estado }); }
function celdaCita(r) {
  const td = el("td", { className: "cita" });
  if (r.cita) td.append(el("q", { textContent: r.cita }));
  return td;
}
function coincide(r, txt) { if (!txt) return true; const t = txt.toLowerCase(); return [r.valor, r.cita, r.nota].some(x => (x || "").toLowerCase().includes(t)); }

function pintar() {
  $("vContrato").setAttribute("aria-pressed", modo === "contrato"); $("vVariable").setAttribute("aria-pressed", modo === "variable");
  $("lContrato").hidden = modo !== "contrato"; $("lVariable").hidden = modo !== "variable";
  const tabla = $("tabla"); tabla.replaceChildren(); $("cabecera").replaceChildren();
  const txt = $("buscar").value.trim(), bco = $("selBanco").value;
  let n = 0;
  if (modo === "contrato") {
    // Si el filtro de banco excluye el contrato elegido, pasa al primero que cumple
    if (bco && banco($("selContrato").value) !== bco) { const o = [...$("selContrato").options].find(o => banco(o.value) === bco); if (o) $("selContrato").value = o.value; }
    [...$("selContrato").options].forEach(o => o.hidden = !!bco && banco(o.value) !== bco);
    const c = $("selContrato").value, d = POR[c] || {};
    const f = FECHAS[c] || {};
    const fila = (k, v) => el("div", {}, el("b", { textContent: k }), el("span", { textContent: v || "—" }));
    const monto = d.A08 ? "US$ " + (Number(d.A08.valor) / 1e6).toLocaleString("es-PE", { maximumFractionDigits: 1 }) + " M" : "—";
    $("cabecera").append(el("div", { className: "ficha-contrato" },
      fila("Banco", banco(c) === "BID" ? "BID" : "Banco Mundial (BIRF)"), fila("Préstamo", d.A02?.valor), fila("Monto", monto),
      fila("Firma", d.A07?.valor), fila("Aprobación (fuente oficial)", f.aprobacion), fila("Cierre real (Banco Mundial)", f.cierre_final)));
    const docs = FUENTES.filter(r => r.contrato === c);
    if (docs.length) { const p = el("p", { className: "docs" }, "Documentos oficiales: "); docs.forEach((r, i) => { if (i) p.append(" · "); p.append(el("a", { href: r.url_oficial, textContent: r.documento.replace(/^\d{4}_/, "").replace(/_/g, " ").replace(".pdf", ""), target: "_blank", rel: "noopener" })); }); $("cabecera").append(p); }
    tabla.append(el("thead", {}, el("tr", {}, ...["Pregunta", "Respuesta", "Estado", "Pág.", "Cita literal", "Nota"].map((t, i) => el("th", { textContent: t, className: i === 3 ? "num" : i === 5 ? "nt" : "" })))));
    const tb = el("tbody"); let bloque = null;
    FICHA.forEach(v => {
      const r = d[v.id]; if (!r || !coincide(r, txt)) return;
      if (v.bloque !== bloque) { bloque = v.bloque; tb.append(el("tr", { className: "bloque" }, el("td", { colSpan: 6, textContent: bloque }))); }
      tb.append(el("tr", {}, el("td", { textContent: `${v.id} · ${v.variable}` }), el("td", { className: "valor", textContent: r.valor }),
        el("td", {}, chip(r.estado)), el("td", { className: "num", textContent: r.pagina }), celdaCita(r), el("td", { className: "nt", textContent: r.nota })));
      n++;
    });
    tabla.append(tb);
    $("cuenta").textContent = `${n} de ${FICHA.length} respuestas` + (txt ? ` que contienen «${txt}»` : "");
  } else {
    const id = $("selVariable").value, v = FICHA.find(x => x.id === id) || {};
    $("cabecera").append(el("p", { className: "sub" }, el("b", { textContent: `${v.id} · ${v.variable}. ` }), v["definición"] || "", " ", el("span", { className: "small", textContent: "Regla: " + (v["regla de codificación"] || "") })));
    tabla.append(el("thead", {}, el("tr", {}, ...["Contrato", "Firma", "Respuesta", "Estado", "Pág.", "Cita literal", "Nota"].map((t, i) => el("th", { textContent: t, className: i === 4 ? "num" : i === 6 ? "nt" : "" })))));
    const tb = el("tbody");
    [...$("selContrato").options].map(o => o.value).forEach(c => {
      if (bco && banco(c) !== bco) return;
      const r = (POR[c] || {})[id]; if (!r || !coincide(r, txt)) return;
      const nombre = el("td", {}, el("span", { className: "banco " + banco(c).toLowerCase() }, el("i"), codigo(c)), el("br"), el("span", { className: "small", textContent: NOMBRES[c] || "" }));
      tb.append(el("tr", {}, nombre, el("td", { className: "fecha", textContent: (POR[c].A07?.valor || "") }), el("td", { className: "valor", textContent: r.valor }),
        el("td", {}, chip(r.estado)), el("td", { className: "num", textContent: r.pagina }), celdaCita(r), el("td", { className: "nt", textContent: r.nota })));
      n++;
    });
    tabla.append(tb);
    $("cuenta").textContent = `${n} contratos` + (txt ? ` cuya respuesta, cita o nota contiene «${txt}»` : "");
  }
  fijarHash();
}
$("vContrato").addEventListener("click", () => { modo = "contrato"; pintar(); });
$("vVariable").addEventListener("click", () => { modo = "variable"; pintar(); });
["selContrato", "selVariable", "selBanco"].forEach(id => $(id).addEventListener("change", pintar));
$("buscar").addEventListener("input", pintar);
window.addEventListener("hashchange", () => { leerHash(); pintar(); });
