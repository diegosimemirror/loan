# PROCESO 3: Verificar que cada cita sea literal y esté en la página indicada.
# Insumo: un TSV de codificación y la carpeta pag/ con los textos por página.
# Resultado: lista de citas no encontradas (en la página o en todo el archivo).

# csv: lee el TSV respetando comillas.
import csv
# re: normaliza espacios y separa las páginas por sus marcadores.
import re
# sys: recibe rutas por línea de comandos.
import sys
# pathlib: arma las rutas de los textos.
from pathlib import Path

tsv, carpeta = sys.argv[1], Path(sys.argv[2])
sys.stdout.reconfigure(encoding="utf-8")

# archivos_v2.tsv: contrato → archivos de texto (separados por ;)
ARCH = {}
for linea in (carpeta.parent / "archivos_v2.tsv").read_text(encoding="utf-8").splitlines()[1:]:
    k, v = linea.split("	"); ARCH[k] = v.split(";")


def norm(s):
    """texto con comillas y espacios variados → texto en minúsculas con un solo espacio"""
    s = s.replace("“", '"').replace("”", '"').replace("’", "'")
    return re.sub(r"\s+", " ", s).strip().lower()

def paginas(nombre):
    """archivo con marcadores '=== PÁG n ===' → dict {n: texto normalizado}"""
    t = (carpeta / nombre).read_text(encoding="utf-8")
    partes = re.split(r"=== PÁG (\d+) ===", t)
    return {int(partes[i]): norm(partes[i + 1]) for i in range(1, len(partes), 2)}

cache = {}
def docs_de(k):
    if k not in cache: cache[k] = [paginas(a) for a in ARCH[k]]
    return cache[k]
malas, total = 0, 0
with open(tsv, encoding="utf-8") as fh:
    for r in csv.DictReader(fh, delimiter="\t"):
        cita = r["cita"].strip()
        if not cita:
            continue
        total += 1
        trozos = [norm(x) for x in cita.split("...") if norm(x)]
        docs = docs_de(r["contrato"])
        en_pag = False
        if r["pagina"].strip().isdigit():
            p = int(r["pagina"])
            # la cita puede cruzar a la página siguiente
            texto = " ".join(d.get(p, "") + " " + d.get(p + 1, "") for d in docs)
            en_pag = all(t in texto for t in trozos)
        en_doc = all(any(t in " ".join(d.values()) for d in docs) for t in trozos)
        if not en_pag:
            malas += 1
            estado = "en otra página" if en_doc else "NO ENCONTRADA"
            print(f'{r["contrato"]}\t{r["id"]}\tpág {r["pagina"] or "—"}\t{estado}\t{cita[:90]}')
print(f"\n{total} citas revisadas; {malas} sin coincidencia exacta en la página indicada")
