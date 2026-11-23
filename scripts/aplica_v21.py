# PROCESO 10: Aplicar las 5 decisiones del usuario (21-11-2026) → ficha v2.1 y datos de la tanda 1 recodificados.
# Insumo: ficha_v2.tsv, cambios_v2.tsv, v2_A/B/C.tsv, idb_fechas.txt (datos abiertos del BID).
# Resultado: ficha_v21.tsv, cambios_v21.tsv, v21_tanda1.tsv.

# pandas: edita la ficha y la tabla de datos.
import pandas as pd
# ast: lee las tuplas que trajo la consulta a los datos abiertos del BID.
import ast
# sys: rutas por línea de comandos.
import sys

S = sys.argv[1]
leer = lambda p: pd.read_csv(p, sep="\t", dtype=str, keep_default_na=False)
ficha = leer(f"{S}/ficha_v2.tsv"); cambios = leer(f"{S}/cambios_v2.tsv")
d = pd.concat([leer(f"{S}/{f}") for f in ["v2_A.tsv", "v2_B.tsv", "v2_C.tsv"]], ignore_index=True)
U = "Decisión del usuario (21-11-2026, segunda ronda)"

# ---------- Ficha v2.1 ----------
def regla(id_, texto, motivo):
    """cambia la regla de una variable y registra el cambio"""
    global cambios
    ficha.loc[ficha["id"] == id_, "regla de codificación"] = texto
    cambios = pd.concat([cambios, pd.DataFrame([[id_, "modificada", U, motivo]], columns=cambios.columns)], ignore_index=True)

regla("D02", "Entero = requisitos de las cláusulas tituladas «condiciones previas al (primer) desembolso», incluidas las que valen solo para un componente. Una lista de cargos cuenta como 1 requisito (número de cargos en la nota). Lo que frena desembolsos desde otras cláusulas va en D02c.",
      "Decisión 1: solo la cláusula oficial; lista de cargos = 1.")
regla("E03a", "sí / parcial / no / 0. «No se prevé» al firmar = «no», con la nota «el banco podría validarlo después». Condición literal en la nota.",
      "Decisión 2.")
regla("E12", "Lista y número SOLO de reglas de compra negociadas para este préstamo. Las cláusulas de plantilla (preferencia nacional, lista corta nacional, posesión legal del terreno) y las reglas país que se repiten en los contratos de una misma época (no exigir registro local, publicar en el OSCE, valor referencial) van en la nota. Si no hay negociadas: valor 0, estado 0.",
      "Decisión 3: solo lo negociado.")
regla("E13", "sí / no si el contrato lo dice. Si el contrato no lo menciona y remite a las políticas de adquisiciones del banco: valor «remite a la política del banco», estado «remite». Nunca 0 en ese caso.",
      "Decisión 4: la regla cambió de documento, no desapareció.")
regla("A06", "AAAA-MM-DD. Si el contrato reconoce gastos «desde la aprobación» a partir de una fecha, esa fecha es la de aprobación (estado «calculado», cláusula en la nota). Si no, valor = n.° de resolución con estado «remite» y la fecha de los datos abiertos del BID en la nota. Contrastar siempre con los datos abiertos del banco.",
      "Decisión 5: deducción aceptada y contrastada con los datos abiertos del BID (coincidió en los 7 casos comparables).")
i = ficha.index[ficha["id"] == "D02b"][0]
nueva = {"id": "D02c", "bloque": "D. Desembolso", "variable": "otras condiciones de desembolso (fuera de la cláusula)",
         "definición": "Requisitos que frenan desembolsos desde otras cláusulas (ejecución, condiciones contractuales especiales)",
         "regla de codificación": "Entero = número de requisitos; lista y cláusulas en la nota. Si no hay, 0.",
         "dónde buscar (BID)": "Cl. 3.03–3.05 «condiciones especiales de ejecución / contractuales»", "dónde buscar (BIRF)": "Schedule 2, Withdrawal Conditions por categoría",
         "pregunta que responde": "Desembolso"}
ficha = pd.concat([ficha.iloc[: i + 1], pd.DataFrame([nueva]), ficha.iloc[i + 1 :]], ignore_index=True)
cambios = pd.concat([cambios, pd.DataFrame([["D02c", "nueva", U, "Decisión 1: los candados fuera de la cláusula oficial van aparte."]], columns=cambios.columns)], ignore_index=True)

# ---------- Datos de la tanda 1 ----------
def pon(c, id_, **kw):
    """contrato + variable + nuevos campos → fila actualizada"""
    m = (d["contrato"] == c) & (d["id"] == id_)
    assert m.sum() == 1, (c, id_)
    for k, v in kw.items(): d.loc[m, k] = str(v)

# Decisión 1: D02 solo cláusula oficial; D02c para lo de otras cláusulas
pon("BID-PE-L1060", "D02", valor="2", nota="Cl. 3.02 (a)-(b). Las 3 condiciones de la Cl. 3.03 (CIRA, permisos legales, MGSA, previas al desembolso de cada obra) van en D02c.")
pon("BID-PE-L1060", "D02b", valor="todo el préstamo; todo el préstamo")
pon("BID-PE-L1026", "D02", valor="6", nota="Cl. 3.02: (a) UCP, coordinadores y especialistas = 3; (b) Comité de Gestión e instancia de participación = 2; (c) MOP = 1. Las Cl. 3.05(c)-(d) van en D02c.")
pon("BID-PE-L1026", "D02b", valor="todo el préstamo; todo el préstamo; todo el préstamo; todo el préstamo; todo el préstamo; todo el préstamo", nota="Las seis son de la Cl. 3.02 (primer desembolso).")
pon("BID-PE-L1153", "D02", valor="2", nota="(1) MOP aprobado; (2) personal clave seleccionado, incluido el responsable ambiental de la frase «Adicionalmente» (lista de cargos = 1 requisito).")
pon("BID-PE-L1153", "D02b", valor="todo el préstamo; todo el préstamo")
pon("BID-PE-L1122", "D02", nota="Cl. 3.02 (4 requisitos) + Cl. 3.03, que también es cláusula de condición previa al primer desembolso, solo para el Componente I. El inciso 3.02(c) cuenta como dos: conformar la UCP y contratar su personal.")
D02C = {
 "BID-PE-L1060": ("3", "calculado", "5", "Condiciones especiales de ejecución de las obras. Previa al desembolso", "Cl. 3.03 (a)-(c): CIRA, permisos legales y MGSA, para cada obra."),
 "BID-PE-L1026": ("2", "calculado", "6", "previo al desembolso para la ejecución de la actividades contempladas en el ... previo al desembolso para la ejecución de las actividades contempladas en el", "Cl. 3.05(c): traspaso legal del catastro rural, para el Componente 2; Cl. 3.05(d): propuesta de cambio normativo, para el Componente 1 en Selva y Ceja de Selva."),
}
filas_c = []
for c in d["contrato"].unique():
    v, e, p, ci, n = D02C.get(c, ("0", "0", "", "", "No hay candados de desembolso fuera de la cláusula de condiciones previas (según la lectura de las Estipulaciones)."))
    if c == "BID-PE-L1153":
        n = "0. La Cl. 3.04 pone requisitos antes de licitar o adjudicar obras; se registran en E12 para no contarlos dos veces."
    filas_c.append({"contrato": c, "id": "D02c", "valor": v, "estado": e, "pagina": p, "cita": ci, "nota": n})
d = pd.concat([d, pd.DataFrame(filas_c)], ignore_index=True)

# Decisión 2: «no se prevé» = «no» con nota
for c in ["BID-PE-L1132", "BID-PE-L1122"]:
    m = (d.contrato == c) & (d.id == "E03a"); d.loc[m, "nota"] = d.loc[m, "nota"] + " El contrato dice que no se prevé al firmar; el banco podría validarlo después."

# Decisión 3: E12 solo negociadas
E12 = {
 "BID-PE-L1060": ("0", "Plantilla o reglas país (no se cuentan): posesión legal de inmuebles; confidencialidad de la evaluación; no exigir registro local; publicar en el OSCE; párrafos de LPN de las Políticas; valor referencial no anula la licitación; lista corta nacional."),
 "BID-PE-L1132": ("0", "Reglas país 2012-2015 (no se cuentan): no exigir registro local; publicar en el OSCE; valor referencial no anula la licitación."),
 "BID-PE-L1122": ("0", "Reglas país 2012-2015 (no se cuentan): no exigir registro local; publicar en el OSCE; valor referencial no anula la licitación."),
 "BID-PE-L1222": ("0", "Plantilla (no se cuenta): margen de preferencia doméstica en LPI."),
 "BID-PE-L1227": ("0", "Plantilla (no se cuentan): margen de preferencia doméstica; lista corta nacional bajo el umbral."),
 "BID-PE-L1232": ("0", "Plantilla (no se cuentan): lista corta nacional; obligaciones ambientales y sociales en contratos con terceros."),
}
for c, (v, n) in E12.items():
    pon(c, "E12", valor=v, estado="0", pagina="", cita="", nota=n)
pon("BID-PE-L1153", "E12", valor="3: antes de licitar obras, terrenos con derechos de uso y posesión legal a cargo de las municipalidades; antes de adjudicar obras, plan de inclusión de recicladores en ejecución; antes de adjudicar obras, relleno sanitario en marcha con su EIA",
    pagina="5", cita="CLÁUSULA 3.04. Otros requisitos para la utilización de los recursos del Préstamo.",
    nota="Cl. 3.04(a), (c)(a) y (c)(b). Plantilla (no se cuenta): margen de preferencia doméstica en LPI.")
pon("BID-PE-L1026", "E12", nota="2 negociadas: Cl. 3.05(b) y Anexo 4.05.")

# Decisión 4: E13 remite en contratos que no lo mencionan
for c in ["BID-PE-L1153", "BID-PE-L1222", "BID-PE-L1227", "BID-PE-L1232", "BID-PE-L1254"]:
    pon(c, "E13", valor="remite a la política del banco", estado="remite", pagina="", cita="",
        nota="El contrato no lo menciona; la regla de origen estaría en las políticas de adquisiciones del BID (por confirmar al descargarlas)." + (" Ojo: este préstamo viene de un fondo de clima (ventanilla SX), que puede tener otra regla." if c == "BID-PE-L1232" else ""))

# Decisión 5: A06 deducida y contrastada con los datos abiertos del BID
abiertos = {}
for linea in open(f"{S}/idb_fechas.txt", encoding="utf-8"):
    cod, resto = linea.strip().split(" ", 1); t = ast.literal_eval(resto)
    if t: abiertos["BID-" + cod] = t[0][0]
pon("BID-PE-L1153", "A06", valor="2017-09-14", estado="calculado", pagina="5", cita="con posterioridad al 14 de septiembre de 2017",
    nota="Fecha desde la que se reconocen gastos elegibles (Cl. 3.02); resolución DE-43/17.")
pon("BID-PE-L1222", "A06", valor="2017-11-22", estado="calculado", pagina="5", cita="con posterioridad al 22 de noviembre de 2017",
    nota="Fecha desde la que se reconocen gastos elegibles (Cl. 3.02); resolución DE-88/17.")
for c in ["BID-PE-L1227", "BID-PE-L1232", "BID-PE-L1254"]:
    m = (d.contrato == c) & (d.id == "A06")
    d.loc[m, "nota"] = d.loc[m, "nota"] + f" Datos abiertos del BID: aprobado el {abiertos[c]}."
for c in d["contrato"].unique():
    m = (d.contrato == c) & (d.id == "A06")
    if d.loc[m, "estado"].iloc[0] == "calculado":
        ok = "coincide" if d.loc[m, "valor"].iloc[0] == abiertos[c] else f"NO coincide ({abiertos[c]})"
        d.loc[m, "nota"] = d.loc[m, "nota"] + f" Contraste con datos abiertos del BID: {ok}."

# Orden y salida
pos = {v: k for k, v in enumerate(ficha["id"])}
d["_o"] = d["id"].map(pos); d = d.sort_values(["contrato", "_o"]).drop(columns="_o")
ficha.to_csv(f"{S}/ficha_v21.tsv", sep="\t", index=False)
cambios.to_csv(f"{S}/cambios_v21.tsv", sep="\t", index=False)
d.to_csv(f"{S}/v21_tanda1.tsv", sep="\t", index=False)
print(len(ficha), "variables;", len(d), "filas;", d.groupby("contrato").size().unique())
print(d[d.id == "A06"][["contrato", "valor", "estado", "nota"]].to_string())
