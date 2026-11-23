# PROCESO 14: Unificar criterios en la tanda 3 (BIRF 2017-2026) y completar con fuentes oficiales.
# Insumo: v21_G/H/I/J.tsv, bm_fechas_t3.txt (API del Banco Mundial), bm_firmas_t3.txt (tabla base, Finances One).
# Resultado: v21_tanda3.tsv, bm_api_t3.tsv y base_codificada_v21.tsv actualizada (tandas 1, 2 y 3).

# pandas: edita y une las tablas.
import pandas as pd
# datetime: convierte fechas de la API y de Finances One.
from datetime import datetime
# sys: rutas por línea de comandos.
import sys

S = sys.argv[1]
leer = lambda p: pd.read_csv(p, sep="\t", dtype=str, keep_default_na=False)
d = pd.concat([leer(f"{S}/{f}") for f in ["v21_G.tsv", "v21_H.tsv", "v21_I.tsv", "v21_J.tsv"]], ignore_index=True)

def pon(c, id_, **kw):
    """contrato + variable → campos actualizados"""
    m = (d.contrato == c) & (d.id == id_); assert m.sum() == 1, (c, id_)
    for k, v in kw.items(): d.loc[m, k] = str(v)
def campo(c, id_, k): return d.loc[(d.contrato == c) & (d.id == id_), k].iloc[0]
def nota_mas(c, id_, txt):
    m = (d.contrato == c) & (d.id == id_); d.loc[m, "nota"] = (d.loc[m, "nota"] + " " + txt).str.strip()

# 1) D02c estricto: solo cláusulas que frenan retiros o desembolsos (criterio de las tandas 1 y 2)
for c in ["BIRF-9334", "BIRF-9616", "BIRF-9733", "BIRF-9874"]:
    previa = campo(c, "D02c", "nota")
    pon(c, "D02c", valor="0", estado="0", pagina="", cita="",
        nota="0 con el criterio unificado: lo que pide esta cláusula frena actividades o licitaciones, no retiros. Detalle: " + previa)

# 2) Compras sin sección propia: remite a las Procurement Regulations (criterio del piloto, BIRF 9274)
SIN_SECCION = ["BIRF-8975", "BIRF-9035", "BIRF-9039", "BIRF-9040", "BIRF-9616", "BIRF-9717", "BIRF-9733", "BIRF-9874"]
R = "remite a las Procurement Regulations (vía General Conditions)"
for c in SIN_SECCION:
    for v in ["E03a", "E03b", "E03c", "E04"]:
        if campo(c, v, "estado") != "remite":
            pon(c, v, valor=R, estado="remite", pagina="", cita="",
                nota="El contrato no tiene sección de compras: las deja a las Procurement Regulations, que no están en el archivo. Criterio unificado (antes: " + campo(c, v, "valor") + ").")
    if campo(c, "E05a", "estado") != "remite":
        pon(c, "E05a", valor="Procurement Regulations (vía General Conditions)", estado="remite", pagina="", cita="",
            nota="El contrato no nombra un Procurement Plan; la revisión previa la fijan las Procurement Regulations. Criterio unificado.")

# 3) Fechas oficiales: firma (Finances One) y aprobación y cierre (API del Banco Mundial)
firmas = {}
for l in open(f"{S}/bm_firmas_t3.txt", encoding="utf-8"):
    n, f = l.split("|")[0].split()
    firmas["BIRF-" + n] = datetime.strptime(f, "%d-%b-%Y").strftime("%Y-%m-%d")
P = {"P156250": "8682", "P151851": "8740", "P162833": "8975", "P162278": "9035", "P170658": "9039", "P170595": "9040",
     "P174812": "9288", "P178181": "9327", "P176297": "9334", "P179037": "9616", "P179923": "9717", "P178842": "9733", "P505093": "9874"}
api = {}
for l in open(f"{S}/bm_fechas_t3.txt", encoding="utf-8"):
    p = l.split(); ap = p[1]; cz = p[2]
    cierre = datetime.strptime(cz, "%m/%d/%Y").strftime("%Y-%m-%d") if cz != "NA" else ""
    api["BIRF-" + P[p[0]]] = ("" if ap == "NA" else ap, cierre)
for c in d.contrato.unique():
    est, val = campo(c, "A07", "estado"), campo(c, "A07", "valor")
    if est == "NA":
        pon(c, "A07", valor=firmas[c], estado="metadato", nota=(campo(c, "A07", "nota") + f" Fecha de firma de la tabla base (Finances One del Banco Mundial): {firmas[c]}.").strip())
    elif val != firmas[c]:
        pon(c, "A07", valor=firmas[c], estado="metadato", pagina="", cita="",
            nota=f"El OCR daba {val}; Finances One del Banco Mundial registra {firmas[c]}, que se toma como fecha de firma. Nota original: " + campo(c, "A07", "nota"))
    else:
        nota_mas(c, "A07", "Contraste con Finances One: coincide.")
    ap = api[c][0]
    if ap:
        v6 = campo(c, "A06", "valor")
        nota_mas(c, "A06", f"Contraste con la API del Banco Mundial: {'coincide' if v6 == ap else 'la API da ' + ap + ' (aprobación del proyecto)'}.")
    else:
        nota_mas(c, "A06", "La API del Banco Mundial no trae la fecha de aprobación de este proyecto.")

# Salida
ficha = leer(f"{S}/ficha_v21.tsv"); pos = {v: k for k, v in enumerate(ficha["id"])}
d["_o"] = d["id"].map(pos); d = d.sort_values(["contrato", "_o"]).drop(columns="_o")
d.to_csv(f"{S}/v21_tanda3.tsv", sep="\t", index=False)
pd.DataFrame([(c, a, cz) for c, (a, cz) in api.items()], columns=["contrato", "aprobacion_api", "cierre_final_api"]).to_csv(f"{S}/bm_api_t3.tsv", sep="\t", index=False)
base = pd.concat([leer(f"{S}/v21_tanda1.tsv"), leer(f"{S}/v21_tanda2.tsv"), d], ignore_index=True)
base.to_csv(f"{S}/base_codificada_v21.tsv", sep="\t", index=False)
print("tanda 3:", len(d), "filas | base:", len(base), "filas,", base.contrato.nunique(), "contratos")
for c in sorted(d.contrato.unique()):
    print(c, "A07", campo(c, "A07", "valor"), campo(c, "A07", "estado"), "| B01", campo(c, "B01", "valor")[:12], "| API cierre", api[c][1],
          "| B02", campo(c, "B02", "valor")[:10], "| B03", campo(c, "B03", "valor")[:10], "| B04", campo(c, "B04", "valor"), "| A08", campo(c, "A08", "valor"))
