# PROCESO 12: Unificar criterios en la tanda 2 (BIRF) y completar con fuentes oficiales.
# Insumo: v21_D/E/F.tsv, bm_fechas.txt (API del Banco Mundial), bm_firmas.txt (tabla base, Finances One).
# Resultado: v21_tanda2.tsv y base_codificada_v21.tsv (tandas 1 y 2 juntas).

# pandas: edita y une las tablas.
import pandas as pd
# datetime: convierte fechas de la API y de Finances One.
from datetime import datetime
# sys: rutas por línea de comandos.
import sys

S = sys.argv[1]
leer = lambda p: pd.read_csv(p, sep="\t", dtype=str, keep_default_na=False)
d = pd.concat([leer(f"{S}/{f}") for f in ["v21_D.tsv", "v21_E.tsv", "v21_F.tsv"]], ignore_index=True)

def pon(c, id_, **kw):
    """contrato + variable → campos actualizados"""
    m = (d.contrato == c) & (d.id == id_); assert m.sum() == 1, (c, id_)
    for k, v in kw.items(): d.loc[m, k] = str(v)
def nota_mas(c, id_, txt):
    m = (d.contrato == c) & (d.id == id_); d.loc[m, "nota"] = (d.loc[m, "nota"] + " " + txt).str.strip()

# 1) D02: la exclusión de pagos anteriores a la firma no es un requisito (va en D05), como en los lotes D y E
for c in ["BIRF-8517", "BIRF-8562", "BIRF-8680"]:
    m = (d.contrato == c) & (d.id == "D02")
    if d.loc[m, "valor"].iloc[0] == "2":
        pon(c, "D02", valor="1", nota="Solo el pago de la Front-end Fee. La prohibición de pagar gastos anteriores a la firma (salvo financiamiento retroactivo) es un límite, no un requisito: va en D05. Criterio unificado con los demás contratos BIRF.")
        pon(c, "D02b", valor="todo el préstamo")

# 2) Fechas oficiales: firma (Finances One, en la tabla base) y aprobación y cierre (API del Banco Mundial)
firmas = {}
for l in open(f"{S}/bm_firmas.txt", encoding="utf-8"):
    n, f = l.split(); firmas["BIRF-" + n] = datetime.strptime(f, "%d-%b-%Y").strftime("%Y-%m-%d")
P = {"P117310": "7961", "P117864": "8034", "P122194": "8212", "P131029": "8222", "P079165": "8246", "P131013": "8331",
     "P117293": "8468", "P145610": "8517", "P132515": "8562", "P147342": "8680", "P174177": "9274", "P123151": "8226"}
api = {}
for l in open(f"{S}/bm_fechas.txt", encoding="utf-8"):
    p = l.split(); ap = p[1]; cierre = datetime.strptime(p[2], "%m/%d/%Y").strftime("%Y-%m-%d")
    api["BIRF-" + P[p[0]]] = (ap, cierre)
for c in d.contrato.unique():
    m = (d.contrato == c) & (d.id == "A07")
    if d.loc[m, "estado"].iloc[0] == "NA":
        pon(c, "A07", valor=firmas[c], estado="metadato", nota=(d.loc[m, "nota"].iloc[0] + f" Fecha de firma de la tabla base (Finances One del Banco Mundial): {firmas[c]}.").strip())
    else:
        ok = "coincide" if d.loc[m, "valor"].iloc[0] == firmas[c] else f"NO coincide ({firmas[c]})"
        nota_mas(c, "A07", f"Contraste con Finances One: {ok}.")
    ap = api[c][0]; v = d.loc[(d.contrato == c) & (d.id == "A06"), "valor"].iloc[0]
    if v == ap: nota_mas(c, "A06", f"Contraste con la API del Banco Mundial: coincide ({ap}).")
    else: nota_mas(c, "A06", f"La API del Banco Mundial da {ap} para el proyecto (P-number). Si es un financiamiento adicional, esa fecha es la del proyecto original.")

# Salida tanda 2 y base consolidada
ficha = leer(f"{S}/ficha_v21.tsv"); pos = {v: k for k, v in enumerate(ficha["id"])}
d["_o"] = d["id"].map(pos); d = d.sort_values(["contrato", "_o"]).drop(columns="_o")
d.to_csv(f"{S}/v21_tanda2.tsv", sep="\t", index=False)
base = pd.concat([leer(f"{S}/v21_tanda1.tsv"), d], ignore_index=True)
base.to_csv(f"{S}/base_codificada_v21.tsv", sep="\t", index=False)
pd.DataFrame([(c, a, cz) for c, (a, cz) in api.items()], columns=["contrato", "aprobacion_api", "cierre_final_api"]).to_csv(f"{S}/bm_api.tsv", sep="\t", index=False)
print("tanda 2:", len(d), "filas;", "base:", len(base), "filas,", base.contrato.nunique(), "contratos")
for c in sorted(d.contrato.unique()):
    g = d[d.contrato == c].set_index("id")
    print(c, "A06", g.loc["A06", "valor"], "| A07", g.loc["A07", "valor"], g.loc["A07", "estado"], "| B01", g.loc["B01", "valor"][:30], "| API cierre", api[c][1], "| D02", g.loc["D02", "valor"], "| I01", g.loc["I01", "valor"])
