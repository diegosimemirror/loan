# Préstamos multilaterales al Perú: contratos, plazos y simulador

Cómo funcionan en la práctica los préstamos del BID y del Banco Mundial al Perú, leídos contrato por contrato.

**Sitio:** https://diegosimemirror.github.io/loan/

## Qué hay
| Página | Qué muestra |
|---|---|
| `index.html` | Preguntas de partida y seis hallazgos con cifras, cada uno enlazado a su evidencia |
| `simulador.html` | Desembolso, gracia y pago de un préstamo en el tiempo, con 7 contratos reales o con supuestos propios |
| `datos.html` | Las 67 respuestas de cada uno de los 19 contratos, con cita literal y página |
| `pipeline.html` | El flujo de trabajo, al estilo n8n, con cada control y decisión |
| `metodo.html` | Método, calidad, límites y lecturas recomendadas |

## Datos (`data/`)
- `prestamos_peru_2011_2026.csv`: 206 operaciones de endeudamiento del Gobierno Nacional, tomadas de los decretos supremos del MEF y de las bases del BID y del Banco Mundial.
- `ficha_v21.tsv`: las 67 preguntas, con su definición, su regla para responder y dónde buscar.
- `base_codificada_v21.tsv`: 1 273 respuestas de 19 contratos (9 del BID y 10 del Banco Mundial), con estado, página, cita y nota.
- `concordancia_muestras.tsv`: las dos lecturas independientes de cada muestra, lado a lado.
- `fechas_oficiales.tsv`: aprobación, firma y cierre real, según los datos abiertos del BID y la API del Banco Mundial.
- `fuentes_documentos.tsv`: el enlace oficial de cada contrato y enmienda. Los PDF no se suben al repositorio.
- `cambios_ficha.tsv`: cada cambio de la ficha (v1 → v2 → v2.1) y quién lo decidió.

## Método
Se adapta el método de Gelpern, Horn, Morris, Parks y Trebesch (2023), «How China Lends» (*Economic Policy*): una misma ficha para todos los contratos, con doble lectura en una muestra.
- Las Normas Generales del BID y las General Conditions del Banco Mundial funcionan como plantilla.
- La lectura se concentra en lo negociado.
- Las citas se verifican palabra por palabra contra la página indicada (`scripts/verifica_citas_v2.py`).

Para reproducir:
1. `scripts/extrae_paginas.sh <salida> archivo.pdf …` convierte cada PDF a texto con marcadores `=== PÁG n ===`.
2. La lectura sigue `data/ficha_v21.tsv` y las instrucciones de `metodo/encargo_agentes_v21.md`.
3. `scripts/verifica_citas_v2.py <tabla.tsv> <carpeta_textos>` comprueba las citas. Necesita `archivos_v2.tsv`, que relaciona cada contrato con sus textos.
4. `scripts/compara_v21.py` mide el acuerdo entre dos lecturas.

## Límites
- Solo el BID y el Banco Mundial publican sus contratos; la CAF, el KfW y JICA no los publican.
- La verificación comprueba que las citas existan, no la interpretación jurídica.
- Faltan por codificar 13 préstamos de inversión del Banco Mundial de 2017 a 2026, 5 escaneados y 5 contratos del piloto.

## Licencia y autoría
- Código: licencia MIT (ver `LICENSE`).
- Datos y textos: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es). Las citas son fragmentos breves de documentos publicados por el BID, el Banco Mundial y el MEF; el crédito por esos documentos es de sus autores.

Diego Sime · con Claude Code · noviembre de 2026.
