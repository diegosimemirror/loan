# PROCESO W1: Preparar la carpeta data/ del sitio web «loan».
# Insumo: base codificada, ficha, cambios, comparaciones, fechas oficiales y tabla base (15_Loan).
# Resultado: archivos limpios en <repo>/data, sin rutas locales.

# pandas: lee y escribe las tablas.
import pandas as pd
# ast: lee las tuplas de fechas de los datos abiertos del BID.
import ast
# datetime: normaliza fechas de Finances One.
from datetime import datetime
# shutil y pathlib: copian archivos y arman rutas.
import shutil
from pathlib import Path
# sys: rutas por línea de comandos.
import sys

S, LOAN, REPO = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
D = REPO / "data"; D.mkdir(parents=True, exist_ok=True)
leer = lambda p: pd.read_csv(p, sep="\t", dtype=str, keep_default_na=False)

# 1) Base codificada, ficha y cambios (antes → después: mismos datos, nombres públicos)
base = leer(S / "base_codificada_v21.tsv")
base.to_csv(D / "base_codificada_v21.tsv", sep="\t", index=False)
leer(S / "ficha_v21.tsv").to_csv(D / "ficha_v21.tsv", sep="\t", index=False)
leer(S / "cambios_v21.tsv").to_csv(D / "cambios_ficha.tsv", sep="\t", index=False)

# 2) Concordancia de las dos muestras de doble lectura en una sola tabla
c1 = leer(S / "comparacion_v2.tsv"); c1.insert(0, "muestra", "tanda 1 (BID)")
c2 = leer(S / "comparacion_v21_t2.tsv"); c2.insert(0, "muestra", "tanda 2 (BIRF)")
c3 = leer(S / "comparacion_v21_t3.tsv"); c3.insert(0, "muestra", "tanda 3 (BIRF)")
cols = ["muestra", "contrato", "id", "variable", "veredicto", "valor_1", "estado_1", "valor_2", "estado_2"]
pd.concat([c1[cols], c2[cols], c3[cols]]).to_csv(D / "concordancia_muestras.tsv", sep="\t", index=False)

# 3) Fechas oficiales: datos abiertos del BID y API del Banco Mundial + Finances One
filas = []
for l in open(S / "idb_fechas.txt", encoding="utf-8"):
    cod, resto = l.strip().split(" ", 1); t = ast.literal_eval(resto)
    if t: filas.append(("BID-" + cod, t[0][0], t[0][1], "", "Datos abiertos del BID (data.iadb.org)"))
api = pd.concat([leer(S / "bm_api.tsv"), leer(S / "bm_api_t3.tsv")]).set_index("contrato")
lineas = open(S / "bm_firmas.txt", encoding="utf-8").read().splitlines() + [l.split("|")[0] for l in open(S / "bm_firmas_t3.txt", encoding="utf-8").read().splitlines()]
for l in lineas:
    n, f = l.split(); c = "BIRF-" + n
    firma = datetime.strptime(f, "%d-%b-%Y").strftime("%Y-%m-%d")
    filas.append((c, api.loc[c, "aprobacion_api"], firma, api.loc[c, "cierre_final_api"], "API del Banco Mundial (aprobación y cierre) y Finances One (firma)"))
pd.DataFrame(filas, columns=["contrato", "aprobacion", "firma", "cierre_final", "fuente"]).to_csv(D / "fechas_oficiales.tsv", sep="\t", index=False)

# 4) Enlaces oficiales de cada documento usado (archivo → URL de origen)
ver = pd.read_csv(LOAN / "VERIFICACION_PDF.tsv", sep="\t", dtype=str, keep_default_na=False)
ver["archivo_txt"] = ver["archivo"].str.split("/").str[-1].str.replace(r"\.(pdf|docx?)$", ".txt", regex=True)
mapa = leer(S / "archivos_v2.tsv")
fuentes = []
for r in mapa.itertuples(index=False):
    for a in r.archivos.split(";"):
        m = ver[ver["archivo_txt"] == a]
        fuentes.append((r.contrato, a.replace(".txt", ".pdf"), m["url_origen"].iloc[0] if len(m) else ""))
pd.DataFrame(fuentes, columns=["contrato", "documento", "url_oficial"]).to_csv(D / "fuentes_documentos.tsv", sep="\t", index=False)

# 5) Tabla base de 206 operaciones (fuentes oficiales; se conservan los enlaces a gob.pe)
shutil.copy(LOAN / "Prestamos_Peru_2011_2026.csv", D / "prestamos_peru_2011_2026.csv")

for p in sorted(D.iterdir()): print(p.name, p.stat().st_size)
print("contratos en la base:", base.contrato.nunique(), "| sin URL oficial:", sum(1 for f in fuentes if not f[2]))
