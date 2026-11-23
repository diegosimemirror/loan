# PROCESO 6: Construir la ficha de codificación v2 a partir de la v1.
# Insumo: ficha_v1.tsv + decisiones del usuario (21-11-2026) + ajustes del piloto.
# Resultado: ficha_v2.tsv (variables) y cambios_v2.tsv (qué cambió, por qué y quién lo decidió).

# pandas: edita la tabla de variables y la guarda en TSV.
import pandas as pd
# sys: rutas por línea de comandos.
import sys

S = sys.argv[1]
f = pd.read_csv(f"{S}/ficha_v1.tsv", sep="\t", dtype=str, keep_default_na=False)
COLS = list(f.columns)
U, C = "Decisión del usuario (21-11-2026)", "Propuesta de Claude tras el piloto (por validar)"
cambios = []

def cambia(id_, origen, motivo, **campos):
    """id + nuevos textos de columnas → ficha modificada y registro del cambio"""
    i = f.index[f["id"] == id_][0]
    for k, v in campos.items():
        f.loc[i, k] = v
    cambios.append((id_, "modificada", origen, motivo))

def agrega(despues_de, fila, origen, motivo):
    """inserta una variable nueva después de otra → ficha ampliada y registro"""
    global f
    i = f.index[f["id"] == despues_de][0]
    nueva = pd.DataFrame([dict(zip(COLS, fila))])
    f = pd.concat([f.iloc[: i + 1], nueva, f.iloc[i + 1 :]], ignore_index=True)
    cambios.append((fila[0], "nueva", origen, motivo))

def quita(id_, origen, motivo):
    """elimina una variable reemplazada por otras"""
    global f
    f = f[f["id"] != id_].reset_index(drop=True)
    cambios.append((id_, "reemplazada", origen, motivo))

# --- Decisión 1: código del proyecto como metadato
cambia("A01", U, "El código no figura en el texto del contrato; se toma del nombre del archivo o de la tabla base.",
       **{"regla de codificación": "BID: PE-L####. BIRF: P######. Si no está en el texto, tomarlo del nombre del archivo o de la tabla base con estado «metadato»."})

# --- Decisión 4: margen → «lo fija el banco según su política» + cifra de fuente externa
cambia("C03", U, "El contrato no trae la cifra; se escribe de forma explícita quién la fija.",
       **{"regla de codificación": "Número (0.80) solo si el contrato lo trae. Si no, valor «lo fija el banco según su política» y estado «remite». Nunca 0."})
agrega("C03", ["C03b", "C. Interés y comisiones", "margen vigente al firmar (fuente externa)",
               "Margen que regía en la fecha de firma, según las tablas públicas del banco",
               "Número en % con estado «metadato». Fuente: BID, archivo de cargos actuales e históricos del capital ordinario; BIRF, tablas «IBRD Lending Rates and Spreads» de la fecha de firma. Anotar la fuente en la nota.",
               "Fuera del contrato", "Fuera del contrato", "Tasa"],
       U, "Para tener la cifra que el contrato no trae (pregunta del usuario: ¿dónde se consigue?).")

# --- Decisión 5: condiciones previas = requisitos + alcance
cambia("D02", U, "Se contaban cláusulas o requisitos según el lector.",
       **{"regla de codificación": "Entero = número de requisitos (no de cláusulas) dentro de la cláusula de condiciones previas o de retiro, incluidos los que valen solo para una parte del préstamo. Estado «calculado»."})
agrega("D02", ["D02b", "D. Desembolso", "alcance de las condiciones previas",
               "A qué parte del préstamo se aplica cada condición",
               "Lista: «todo el préstamo», «componente o parte N» o «cada retiro», una por requisito, en el mismo orden que D01",
               "Cl. 3.01", "Schedule 2, Sec. III.B / IV.C", "Desembolso"],
       U, "Complemento de D02: el Banco Mundial pone condiciones por categoría o para cada retiro.")

# --- Decisión 2: compras con procedimientos del Perú → «parcial» con nota, y bloque E más detallado
quita("E03", U, "Se divide en E03a–E03c: el usuario indicó que la gestión de las adquisiciones es central para la ejecución.")
nuevas_E03 = [
 ["E03a", "E. Ejecución y adquisiciones", "uso del sistema o subsistema de país",
  "Si el contrato permite usar el sistema nacional de compras (o parte de él)",
  "sí = el contrato obliga a usarlo · parcial = lo permite con condiciones (validación previa del banco, umbrales o reglas adicionales; ver nota 1) · no = lo excluye · 0 = no lo menciona. Condición literal en la nota.",
  "Cl. 4.03(b) / 4.04(b) + NG art. 6.04(b)", "Schedule 2 / Procurement Regulations", "No objeción"],
 ["E03b", "E. Ejecución y adquisiciones", "licitación pública nacional (LPN)",
  "Si se permite la LPN y con qué límites",
  "sí / parcial / no / 0, como en E03a. En la nota: umbrales en US$ y condiciones (p. ej., «si el banco la considera compatible»)",
  "Cl. 4.03(d)–(e)", "Schedule 2, Sec. III (NCB)", "No objeción"],
 ["E03c", "E. Ejecución y adquisiciones", "umbral de licitación internacional",
  "Monto desde el que se exige licitación pública internacional",
  "Número en US$ si está en el contrato; si el contrato dice dónde se publica, valor = ese lugar con estado «remite»",
  "Cl. 4.03(c)", "Schedule 2 / Procurement Plan", "No objeción"],
]
prev = "E02"
for fila in nuevas_E03:
    agrega(prev, fila, U, "Detalle de compras pedido por el usuario."); prev = fila[0]

# --- Decisión 3: revisión previa = dato, también más detallada
quita("E05", U, "Se divide en E05a–E05d: la revisión previa (no objeción) define los tiempos de ejecución.")
nuevas_E05 = [
 ["E05a", "E. Ejecución y adquisiciones", "dónde se define la revisión previa (no objeción)",
  "Documento que fija qué compras revisa el banco antes de adjudicar",
  "Valor literal: «contrato», «Plan de Adquisiciones», «Procurement Regulations», etc. Es dato aunque ese documento no esté en el archivo (ver nota 3)",
  "Cl. 4.03–4.05 / NG", "Schedule 2, Sec. III.D", "No objeción"],
 ["E05b", "E. Ejecución y adquisiciones", "umbrales de revisión previa",
  "Montos desde los que una compra requiere no objeción previa",
  "Montos en US$ por tipo (obras, bienes, consultorías) si el contrato los trae; si están en otro documento, estado «remite»",
  "Cl. 4.03–4.05 (contratos antiguos: Cl. 5.02(d))", "Procurement Plan", "No objeción"],
 ["E05c", "E. Ejecución y adquisiciones", "actualización del plan de adquisiciones",
  "Cada cuánto se actualiza el plan y si el banco lo aprueba",
  "Frecuencia literal («al menos semestral») + «con aprobación del banco» si lo dice; si no lo dice, 0",
  "Cl. 4.05", "Schedule 2 / Procurement Regulations", "No objeción"],
 ["E05d", "E. Ejecución y adquisiciones", "sistema de seguimiento del plan",
  "Sistema informático en que se registra el plan",
  "Nombre (SEPA, STEP u otro) o «el que determine el banco»; si no lo dice, 0",
  "Cl. 4.05", "Procurement Regulations (STEP)", "No objeción"],
]
prev = "E04"
for fila in nuevas_E05:
    agrega(prev, fila, U, "Detalle de la no objeción pedido por el usuario."); prev = fila[0]
agrega("E11", ["E12", "E. Ejecución y adquisiciones", "condiciones especiales de adquisición",
               "Reglas de compra propias de este contrato, además de las políticas del banco",
               "Lista corta (p. ej., «no exigir registro local a extranjeros», «no usar dos sobres», «publicar en la web del OSCE», «posesión legal del terreno antes de adjudicar obras»); número en la nota",
               "Cl. 4.03 / 5.02 (incisos de «otras obligaciones»)", "Schedule 2, Sec. III.E (Special Provisions)", "No objeción"],
       C, "Los contratos de 2012 y 2013 traen reglas de compra propias que no cabían en otra variable.")
agrega("E12", ["E13", "E. Ejecución y adquisiciones", "elegibilidad por origen",
               "Si solo se pueden comprar bienes y servicios de países miembros del banco",
               "sí / no / 0; cita de la cláusula",
               "Cl. 3.01(b) (contratos antiguos) / NG", "General Conditions / Procurement Regulations", "Influencia"],
       C, "Mide si el préstamo abre o cierra mercado a proveedores de ciertos países.")

# --- Decisión 6: otras obligaciones sin repetir
cambia("F05", U, "Las listas de los dos lectores se superponían con otras variables.",
       **{"regla de codificación": "Lista corta solo con obligaciones que no estén ya codificadas en D, E, F01–F03 o G; número de obligaciones en la nota."})

# --- Ajustes propuestos por Claude tras el piloto (por validar)
cambia("A06", C, "La fecha de aprobación a veces solo se deduce (8226: límite de 18 meses).",
       **{"regla de codificación": "AAAA-MM-DD. Si solo hay número de resolución, valor = número y estado «remite». Si se deduce de otro plazo del contrato, estado «calculado» con la cuenta en la nota."})
cambia("A07", C, "Fechas ilegibles por OCR en los dos contratos del BIRF.",
       **{"regla de codificación": "AAAA-MM-DD. Si es ilegible, usar la fecha que citen las enmiendas (estado «dato», cita de la enmienda) o la tabla base (estado «metadato»)."})
cambia("B03", C, "Contratos antiguos dan fechas relativas («a más tardar a los 25 años»).",
       **{"regla de codificación": "AAAA-MM-DD. Si el contrato da plazos relativos, calcular desde la firma (estado «calculado»). Si hay VPP, comprobar que la fecha cuadre con ella y explicar en la nota."})
cambia("B04", C, "En PE-L1101 ambos lectores contaron 41 cuotas; la VPP del contrato implica 40.",
       **{"regla de codificación": "Entero. Contar en el cronograma (estado «calculado»). Si hay VPP, comprobar el conteo con ella."})
cambia("D07", C, "Componentes numerados frente a líneas del cuadro de costos.",
       **{"regla de codificación": "Entero = componentes numerados del Anexo o partes del Schedule 1. Las demás líneas de costo (administración, auditoría, imprevistos) van en la nota."})
quita("F02", C, "Se divide en frecuencia y auditor: el BIRF da la frecuencia pero no quién audita.")
agrega("F01", ["F02a", "F. Supervisión e influencia", "auditoría: frecuencia y plazo",
               "Cada cuánto se audita y en qué plazo se entrega",
               "Texto corto («anual, 120 días tras el cierre del ejercicio»); si lo regulan las condiciones generales, estado «remite»",
               "Cl. 5.02", "Schedule 2, Sec. II.B / General Conditions 5.09", "Influencia"],
       C, "División de F02.")
agrega("F02a", ["F02b", "F. Supervisión e influencia", "auditoría: quién audita",
                "Tipo de auditor exigido",
                "«firma independiente aceptable al banco», «Contraloría», etc.; si no lo dice, estado «remite»",
                "Cl. 5.02", "General Conditions 5.09", "Influencia"],
       C, "División de F02.")
cambia("G02", C, "No estaba claro si la asignación presupuestaria cuenta como traspaso.",
       **{"regla de codificación": "sí = los fondos pasan a otra entidad mediante un convenio (traspaso, adhesión, subpréstamo). La asignación por presupuesto no cuenta: va en la nota."})

f.to_csv(f"{S}/ficha_v2.tsv", sep="\t", index=False)
pd.DataFrame(cambios, columns=["id", "tipo de cambio", "origen", "motivo"]).to_csv(f"{S}/cambios_v2.tsv", sep="\t", index=False)
print(len(f), "variables en la v2;", len(cambios), "cambios registrados")
