# Propuestas del público («proponer un disco»)

Cualquiera puede sugerir un disco, un grupo o un sello desde la web
(`#/proponer`). Sigue el patrón de los robots de descubrimiento
(`docs/scraping-method.md`): formulario → PR de candidatos → Miguel
aprueba. Sin backend, sin cuentas, sin nada que mantener.

## Piezas

| Pieza | Dónde | Qué hace |
|---|---|---|
| Página PROPONER | `app/src/pages/Proponer.jsx` | Formulario con la estética del MEU. Valida que el enlace sea de `bandcamp.com`, lleva un campo trampa contra bots y envía por `POST` (modo `no-cors`) a un Google Form. |
| Buzón | Google Form privado de Miguel → Sheet de respuestas | Nadie lo ve. Solo importa que existan sus cinco campos (`entry.*` en `Proponer.jsx`). El Sheet está **publicado en la web como CSV** de solo lectura (la hoja en sí sigue siendo privada). |
| Robot | `scripts/proposals.py` | Lee el CSV, saca las URL de `*.bandcamp.com`, pide las fichas (o la discografía entera si es una cuenta) con los parsers de `discover_accounts.py`, dedupe contra todo, y escribe `data/candidates_propuestas-YYYY-MM.json`. |
| Workflow | `.github/workflows/proposals.yml` | Cron el día 5 de cada mes + manual. Estado en la rama `discovery-state-propuestas`; PR desde `candidates/propuestas-YYYY-MM`. |

## Campos del formulario

Solo el enlace es obligatorio. El resto (lugar, sello, grupos
relacionados, comentario) viaja en el candidato bajo `proposal`, **sin
verificar**, y se muestra en la tabla del PR para ayudar a decidir. Al
hacer el merge se descarta como el resto de campos de procedencia. Del
campo «relacionados» se sacan también las URL de Bandcamp que contenga.

## Qué hace con cada enlace

| Enlace | Resultado |
|---|---|
| `cuenta.bandcamp.com/album/…` | Ficha del disco → candidato. |
| `cuenta.bandcamp.com` o `/music` | Recorre la discografía como `discover_accounts.py`; cada disco que falte → candidato. Si `discover_accounts` ya recorrió esa cuenta, no se vuelve a pedir. |
| `cuenta.bandcamp.com/track/…` | No se propone (el canónico no tiene temas sueltos); queda anotado. |
| Dominio propio u otra web | `revisar_a_mano` en la tabla del PR. |

## Spam

El formulario es público y el robot lo trata como tal: tope de 10
enlaces por propuesta, solo `*.bandcamp.com`, y **nada entra sin el
PR**. El campo trampa de la web frena a los bots tontos; los listos
producen candidatos que Miguel tira en la revisión, como cualquier otro.

## Operar

```
# Cambiar el Sheet sin tocar código:
PROPOSALS_CSV="https://…/pub?output=csv" python3 scripts/proposals.py

# Tabla de un fichero de candidatos:
python3 scripts/proposals.py --table data/candidates_propuestas-2026-09.json

# Al aprobar el PR:
python3 scripts/merge_candidates.py propuestas-2026-09 --pr <nº>
```

Si se cambia el Form de Google (preguntas nuevas, otro Form), hay que
actualizar los `entry.*` de `Proponer.jsx` (menú ⋮ → «Rellenar
previamente el formulario» → «Obtener enlace»: los códigos van en la
URL) y, si cambia el Sheet, la variable `PROPOSALS_CSV` o `CSV_URL` en
`scripts/proposals.py`.
