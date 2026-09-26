# Encargos en paralelo (septiembre 2026)

Tres sesiones independientes. Cada una en claude.ai/code → «New session» → repo
`Bu-chip/MEU` → pegar el prompt entero. No hace falta el Mac encendido.

Reglas comunes (van repetidas dentro de cada prompt):
- Nunca tocar `data/bandcamp_bilbaotags_clean.json` a mano.
- Nunca mergear PRs: los revisa Miguel.
- Cada sesión trabaja solo en sus ficheros; las otras dos están corriendo a la vez.

---

## Encargo 1 — Mapa de fusión de tags

```
Contexto: el MEU (este repo) es un catálogo de música underground de Euskal Herria
sacado de Bandcamp. Cada disco tiene una lista de tags de Bandcamp (unos 5.575 tags
distintos en total) y la web (app/src/pages/Explorar.jsx y Archivo.jsx) los usa para
navegar. Hay demasiados: variantes ortográficas (post-punk / postpunk / post punk),
idiomas (rock / rocka / rock vasco), tags de ubicación (bilbao, bilbo, euskal herria)
mezclados con tags de género, y microgéneros con 1-2 discos.

Objetivo: un MAPA DE FUSIÓN que reduzca los ~5.575 tags a unos 400-500 nodos
navegables, sin perder información: cada tag original apunta a un nodo canónico.

Punto de partida: la rama claude/meu-tags-diagnostic-lv6x9t tiene un diagnóstico
previo de los tags. Léelo primero (git log y ficheros de esa rama) y reaprovecha lo
que sirva; crea tu rama nueva a partir de main, no de esa.

Entregables:
1. scripts/tag_merge_map.py — construye el mapa a partir del catálogo. Reglas
   explícitas y documentadas: normalización (minúsculas, acentos, guiones, espacios),
   sinónimos entre idiomas (es/eu/en), separación de tags de LUGAR (van a un grupo
   aparte, no se fusionan con géneros), y umbral de frecuencia para microgéneros
   (un tag con < N discos se cuelga de su padre más cercano, con N documentado).
2. data/derived/tag_merge_map.json — { "tag_original": "nodo_canonico", ... } más
   una lista de nodos con recuento de discos. Determinista: correrlo dos veces da el
   mismo fichero.
3. data/derived/tag_merge_report.md — tabla resumen: nº tags antes/después, los 50
   nodos más grandes, y una sección "fusiones dudosas" para que Miguel las revise
   (casos donde la regla podría estar uniendo cosas distintas, p. ej. "hardcore" y
   "hardcore techno").
4. Tests en tests/ con unittest (el repo usa python3 -m unittest discover -s tests)
   para las funciones de normalización y para que el mapa sea determinista.
5. Una nota corta en docs/ explicando el método.

NO toques la web (app/) todavía: eso es una segunda fase cuando Miguel apruebe el
mapa. NO toques data/bandcamp_bilbaotags_clean.json. NO toques scripts/pipeline.py
ni .github/workflows (otras sesiones están trabajando ahí ahora mismo).

Al acabar: tests en verde, commit, push a tu rama y abre un PR contra main con el
resumen y las cifras. No lo mergees.

Miguel lee desde el móvil: respuestas cortas, en español.
```

---

## Encargo 2 — Auditoría de calidad del catálogo

```
Contexto: el MEU (este repo) es un catálogo de música underground de Euskal Herria
sacado de Bandcamp. El fichero canónico es data/bandcamp_bilbaotags_clean.json.
Desde julio han entrado tres oleadas de candidatos (data/candidates_2026-07/08/09.json,
mergeadas con scripts/merge_candidates.py) y la normalización vive en
scripts/pipeline.py. Sospechamos que se han colado problemas de calidad.

Fase 1 — SOLO LECTURA. Escribe scripts/quality_audit.py que recorra el canónico y
saque un informe docs/quality-audit-2026-09.md con, como mínimo:
- Duplicados: mismo album_id, o misma URL normalizada (sin query, sin barra final,
  http/https, mayúsculas), o mismo artista+título normalizados con distinta URL.
- Artistas con capitalización rara (TODO EN MAYÚSCULAS, todo en minúsculas cuando el
  resto del catálogo lo tiene con mayúscula inicial), o con el mismo nombre escrito
  de varias formas (compara normalizando).
- genres / tags null o vacíos.
- URLs "sucias" (parámetros ?from=, fragmentos #, espacios, dominio que no es
  bandcamp.com).
- Fechas imposibles o vacías, portadas vacías, campos fuera del esquema.
Para cada categoría: recuento, y una tabla con ejemplos (máx. 30 por categoría)
con album_id y URL para que Miguel pueda mirarlos.

Lee antes docs/mapa-data-audit.md y docs/mapa-audit.md: ya hay una auditoría
anterior y no queremos repetir lo que ya está resuelto.

Fase 2 — solo cuando la fase 1 esté hecha y commiteada: si hay casos CLAROS y
mecánicos (p. ej. duplicado exacto por album_id, URL con ?from= que basta con
recortar), propón el arreglo como una regla en scripts/pipeline.py con su test, en
un PR pequeño y separado por tipo de problema. Nada de arreglos "a ojo" sobre
artistas: eso lo decide Miguel a partir del informe.

NO edites data/bandcamp_bilbaotags_clean.json a mano en ningún caso. NO toques
.github/workflows ni los scripts de descubrimiento (discover_*.py): otras sesiones
están ahí ahora mismo. Los tests se corren con python3 -m unittest discover -s tests.

Al acabar cada fase: commit, push a tu rama, PR contra main. No mergees nada.

Miguel lee desde el móvil: respuestas cortas, en español.
```

---

## Encargo 3 — CI en los PR del robot y actualización de actions

```
Contexto: el MEU (este repo) tiene dos robots de descubrimiento en GitHub Actions:
.github/workflows/discover-tags.yml y discover-accounts.yml. Cada uno abre o
actualiza un PR de candidatos (ramas candidates/...) usando el GITHUB_TOKEN. Por
diseño de GitHub, los push hechos con GITHUB_TOKEN no disparan otros workflows, así
que el workflow Tests (.github/workflows/tests.yml) NUNCA corre sobre esos PR y
Miguel no ve checks en ellos.

Objetivo 1: que los PR de los robots tengan el workflow Tests en verde (o rojo)
como cualquier otro PR. Opciones a evaluar, en este orden de preferencia:
  a) Al final de discover-tags.yml y discover-accounts.yml, lanzar Tests
     explícitamente sobre la rama del PR (gh workflow run tests.yml --ref <rama>),
     añadiendo workflow_dispatch a tests.yml si no lo tiene.
  b) Un workflow_run que se dispare cuando acaban los de descubrimiento.
  c) Un PAT o GitHub App: SOLO como recomendación documentada, no lo implementes
     (requiere secretos que solo Miguel puede crear).
Elige a) salvo que encuentres un motivo fuerte; explica el motivo en el PR.
Ten en cuenta que los workflows de descubrimiento comparten un grupo de concurrencia
y que a veces hay varios runs seguidos sobre el mismo PR: el último run es el que
debe dejar los checks.

Objetivo 2: en TODOS los workflows de .github/workflows/, actualizar las actions a
versiones que no dependan de Node 20 (GitHub lo está deprecando): actions/checkout,
actions/setup-python, actions/setup-node, actions/upload-artifact,
actions/download-artifact, actions/cache y cualquier otra. Comprueba en la
documentación de cada action cuál es la versión mayor vigente y usa esa. Si tests.yml
fija node-version: 20 para el build de la app (app/ es Vite + React), eso es otra
cosa: súbelo a la LTS actual solo si el build sigue pasando en local (cd app && npm
ci && npm run build).

Verificación antes de hacer push: los YAML deben ser válidos (python3 -c "import
yaml, sys; [yaml.safe_load(open(f)) for f in sys.argv[1:]]" .github/workflows/*.yml),
los tests de Python en verde (python3 -m unittest discover -s tests) y el build de
la app en verde.

Ojo: ahora mismo hay un run de discover-accounts en marcha sobre main y otras
sesiones editando scripts/ y data/. Tú SOLO tocas .github/workflows/*.yml y, si hace
falta, docs/. No toques scripts/, data/ ni app/ (salvo el build de comprobación, sin
commitear nada de app/). No relances ni canceles runs en Actions.

Al acabar: commit, push a tu rama, PR contra main con un resumen de qué cambia y
por qué. No lo mergees. Si algo no se puede verificar sin mergear (p. ej. el
dispatch desde el robot), dilo claramente en el PR.

Miguel lee desde el móvil: respuestas cortas, en español.
```
