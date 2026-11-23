# Encargo: codificación de contratos de préstamo con la ficha v2

SCRATCHPAD = <carpeta de trabajo> (con las subcarpetas pag y los scripts)

## Insumos
- Ficha: `SCRATCHPAD\ficha_v21.tsv`. Tiene **67 variables**; léela completa antes de empezar. Cada variable trae su definición, su regla de codificación y dónde buscar.
- Contratos: archivos `SCRATCHPAD\pag\<archivo>.txt`. Son texto plano con marcadores `=== PÁG n ===`, donde n es el número de página del PDF.
- Cada contrato del BID tiene tres partes:
  - **Estipulaciones Especiales**, que es lo negociado (primeras 10 a 22 páginas);
  - **Normas Generales**, iguales para todos los préstamos de esa versión;
  - **Anexo Único**, que describe el programa.
- Lee completas las Estipulaciones Especiales y el Anexo. En las Normas Generales busca solo lo que la ficha pide (grep o lectura dirigida).
- En los contratos antiguos (2011-2015) la tasa, la comisión y las compras están en las Estipulaciones, con umbrales en US$. En los nuevos (2017 en adelante) remiten a las Normas Generales y al Plan de Adquisiciones.

## Estados permitidos (columna `estado`)
| Estado | Cuándo se usa |
|---|---|
| `dato` | Lo dice el contrato. |
| `calculado` | Sale de una cuenta con datos del contrato; la cuenta va en `nota`. Los conteos (cuotas, requisitos) son `calculado`, salvo que el número esté escrito en el texto. |
| `remite` | El contrato no da la cifra y dice quién o dónde se fija. Ejemplos: «lo fija el banco según su política»; «según el Plan de Adquisiciones» cuando la variable pide un número o umbral. |
| `metadato` | Viene del nombre del archivo o de la tabla base, no del texto (A01 casi siempre). |
| `0` | Se revisó y no está. En las variables sí/no, el valor es «no». |
| `NA` | Ilegible o imposible de saber. |
| `no aplica` | La pregunta no corresponde. Ejemplo: plazo de obras en un préstamo sin obras. |

## Reglas
1. Va una fila por contrato y por variable: **67 filas por contrato**. No se salta ninguna.
2. Toda fila con estado `dato` o `calculado` lleva:
   - `pagina`: el número del marcador `=== PÁG n ===` más cercano hacia arriba;
   - `cita`: copia literal del texto, de 300 caracteres como máximo.
   Si la cita salta entre trozos separados, únelos con « ... »; cada trozo debe ser literal.
3. Formatos:
   - fechas en AAAA-MM-DD;
   - montos como número sin separadores;
   - porcentajes como número (0.75 = 0,75 %);
   - sí/no escrito «sí» / «no».
4. Decisiones del usuario que hay que respetar:
   - **C03**: si no hay cifra, el valor es «lo fija el banco según su política» con estado `remite`. Nunca 0.
   - **C03b**: déjala con valor vacío, estado `NA` y nota «pendiente: tablas históricas del banco». La llenará otro proceso.
   - **E03a / E03b**: «parcial» = lo permite con condiciones (validación previa del banco, umbrales o reglas adicionales). La condición literal va en `nota`.
   - **E05a**: «según el Plan de Adquisiciones» es `dato`.
   - **D02**: cuenta requisitos, no cláusulas. **D02b** indica a qué parte se aplica cada uno.
   - **F05**: solo obligaciones que no estén ya en otra variable.
5. No infieras ni uses conocimiento externo. Si algo es ambiguo, codifica tu mejor lectura y explícala en `nota`.

## Salida
Archivo TSV en UTF-8, con este encabezado:
```
contrato	id	valor	estado	pagina	cita	nota
```
Reemplaza tabuladores y saltos de línea dentro de cada campo por un espacio. Python está en `/c/ProgramData/anaconda3/python`; córrelo con `-I`.

Antes de terminar, verifica las citas con:
```
/c/ProgramData/anaconda3/python -I SCRATCHPAD/verifica_citas_v2.py <tu_archivo.tsv> SCRATCHPAD/pag
```
Corrige toda cita que el verificador marque.

## Restricciones
- La laptop se recalienta. Solo lee textos y usa grep o Python liviano.
- Nada de OCR, procesos en paralelo ni Pool.
- No modifiques nada fuera de SCRATCHPAD. No toques G:\.
- No abras ni leas archivos de codificación de otros agentes (`v2_*.tsv` que no sean el tuyo, `pasada*.tsv`, `comparacion*.tsv`).
- No escribas la palabra en inglés para «entrenamiento» dentro de un comando de shell, porque un guardia la bloquea. Si la necesitas, ponla dentro de un archivo .py.

## Reglas de la ficha v2.1 (decisiones del usuario, ya incorporadas en la ficha)
- **D02**: cuenta solo los requisitos de las cláusulas tituladas «condiciones previas al (primer) desembolso». Una lista de cargos cuenta como 1 requisito. Lo que frena desembolsos desde otras cláusulas va en **D02c** (variable nueva).
- **E03a**: «no se prevé» al firmar = «no», con nota.
- **E12**: solo las reglas de compra **negociadas** para ese préstamo. Las cláusulas de plantilla y las reglas país que se repiten entre contratos van en la nota.
- **E13**: si el contrato no la menciona y remite a las políticas o guías del banco, valor «remite a la política del banco», estado `remite`.
- **A06**: si el contrato permite deducir la fecha de aprobación (por ejemplo, «X meses después de la aprobación del banco, que vencen el …»), es `calculado`. Si no, `NA` con nota.

## Contratos del Banco Mundial (BIRF): qué tener en cuenta
- Son *Loan Agreements* en inglés, con texto OCR que trae errores de tipeo. Las citas deben copiar esos errores tal cual.
- Estructura habitual:
  - Art. I: General Conditions.
  - Art. II: Loan (monto, Front-end Fee, Commitment Charge, tasa, Payment Dates).
  - Art. III: Project.
  - Art. IV: Effectiveness y condiciones adicionales.
  - Art. V: representante.
  - Schedule 1: descripción del proyecto.
  - Schedule 2: ejecución (arreglos institucionales, adquisiciones, retiros y Closing Date).
  - Schedule 3: cronograma de amortización.
  - Appendix: definiciones, incluida la versión de las General Conditions y de las guías o regulaciones de adquisiciones.
- **Las General Conditions no están en el archivo.** Todo lo que el contrato les deja a ellas lleva estado `remite`, con la sección en la nota.
- **Variables con regla propia en el BIRF:**

| Variable | Cómo codificar |
|---|---|
| C01 | «Reference Rate» (o LIBOR / SOFR si se nombra) |
| C02 | «Variable Spread» o «Fixed Spread» |
| D06 | Cuenta designada: `remite` a la Disbursement Letter |
| E06 / E07 | `no aplica` si el contrato no menciona contrapartida |
| E05a | «Procurement Plan» |
| E05d | «STEP» solo si se nombra |
| H01 | `remite` a las General Conditions |

- **Condiciones previas:** en el BIRF suelen estar en Art. IV (efectividad, va en D03) y en Schedule 2, Withdrawal Conditions (D01, D02, D02b). Las condiciones de retiro de una sola categoría cuentan en D02, con su alcance en D02b.
- **Enmiendas** (bloque I): cuando el contrato trae cartas de enmienda, léelas. Cuenta cuántas hay, resume qué cambian y anota si **amplían la Closing Date** (I03), de qué fecha a qué fecha. Algunos archivos de enmienda están casi vacíos por OCR: si no se pueden leer, usa `NA` con nota.
