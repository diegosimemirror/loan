# PROCESO 8: Comparar la primera lectura con la segunda (muestra) usando la ficha v2.
# Insumo: archivos de la primera lectura (v2_A/B/C.tsv), la muestra (v2_muestra2.tsv) y ficha_v2.tsv.
# Resultado: comparacion_v2.tsv y resumen de concordancia en pantalla.

# pandas: une ambas lecturas por contrato y variable.
import pandas as pd
# re: extrae números, fechas y sí/no.
import re
# sys: rutas y salida UTF-8.
import sys
# unicodedata: quita tildes al comparar textos.
import unicodedata

sys.stdout.reconfigure(encoding="utf-8")
S = sys.argv[1]
leer = lambda p: pd.read_csv(p, sep="\t", dtype=str, keep_default_na=False)
ficha = leer(f"{S}/ficha_v21.tsv")
p2 = leer(f"{S}/" + sys.argv[2])
p1 = pd.concat([leer(f"{S}/{f}") for f in sys.argv[3].split(",")])
p1 = p1[p1["contrato"].isin(p2["contrato"].unique())]

NUM = {"A08","B04","B06","C03","C05","C06","D02","D07","E06","E07","I01"}
FECHA = {"A06","A07","B02","B03"}
SINO = {"B08","D05","D06","E03a","E03b","E04","E08","E09","E11","E13","G01","G02","G03","I03"}

def plano(s):
    """texto → minúsculas sin tildes ni signos"""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9.% ]+", " ", s).strip()

def clave(id_, v):
    """valor → forma comparable según el tipo de variable"""
    v = v.strip()
    if id_ in NUM:
        m = re.search(r"\d+(?:[.,]\d+)?", v.replace(",", "."))
        return str(float(m.group())) if m else plano(v)
    if id_ in FECHA:
        m = re.search(r"\d{4}-\d{2}-\d{2}", v)
        return m.group() if m else plano(v)
    if id_ in SINO:
        pv = plano(v)
        for w in ("parcial", "si", "no"):
            if pv.startswith(w): return w
        return "0" if pv in ("", "0") else pv[:12]
    return plano(v)

def jaccard(a, b):
    A, B = set(a.split()), set(b.split())
    return len(A & B) / len(A | B) if A | B else 1.0

grupo = lambda e: "valor" if e in ("dato", "calculado") else e
m = p1.merge(p2, on=["contrato", "id"], suffixes=("_1", "_2"))
ver = []
for _, r in m.iterrows():
    e1, e2 = grupo(r.estado_1), grupo(r.estado_2)
    k1, k2 = clave(r.id, r.valor_1), clave(r.id, r.valor_2)
    if e1 != e2: ver.append("difiere (estado)")
    elif k1 == k2: ver.append("coincide")
    elif r.id not in NUM | FECHA | SINO and jaccard(k1, k2) >= 0.4: ver.append("parcial (texto)")
    else: ver.append("difiere (valor)")
m["veredicto"] = ver
m = m.merge(ficha[["id", "bloque", "variable"]], on="id")
m.to_csv(f"{S}/" + sys.argv[4], sep="\t", index=False)
print(m["veredicto"].value_counts().to_string())
print("\nCoinciden igual:", round((m.veredicto == "coincide").mean(), 3),
      "| igual + parcial:", round(m.veredicto.isin(["coincide", "parcial (texto)"]).mean(), 3))
for _, r in m[m.veredicto.str.startswith("difiere")].iterrows():
    print(f"{r.contrato[-6:]} {r.id:5} {r.veredicto[9:15]:6} | 1: [{r.estado_1}] {r.valor_1[:60]} | 2: [{r.estado_2}] {r.valor_2[:60]}")
