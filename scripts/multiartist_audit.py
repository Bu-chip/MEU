#!/usr/bin/env python3
"""Mini-auditoría: peso de las ubicaciones que vienen de cuentas multiartista.

SOLO LECTURA. Lee data/locations/resolutions.json, data/locations/places.json,
data/derived/labels.json y el canónico; escribe
data/locations/reports/multiartist-audit.md. No cambia datos ni semántica.

«Cuenta multiartista» = cuenta presente en data/derived/labels.json (índice
de sellos heurístico: ≥2 artistas distintos o léxico de sello), que es lo que
la resolución marca como account_kind = "label".

La fuente de la ubicación de cada tipo:
  direct          → la propia release (su cuenta)
  same_account    → otra release de la MISMA cuenta
  artist_inferred → releases del mismo artista en sus cuentas propias
                    (nunca cuentas multiartista, por construcción)
Así, una ubicación «procede de una cuenta multiartista» si es direct o
same_account y la cuenta de la release es multiartista.

Uso: python3 scripts/multiartist_audit.py
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOC = ROOT / "data" / "locations"
OUT = LOC / "reports" / "multiartist-audit.md"

PLACED = ("direct", "same_account", "artist_inferred", "manual")


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def pct(n, d):
    return f"{100 * n / d:.1f} %" if d else "—"


def main():
    res = {int(k): v for k, v in load(LOC / "resolutions.json").items()}
    places = {p["id"]: p for p in load(LOC / "places.json")["places"]}
    labels = {r["account_id"]: r for r in load(ROOT / "data/derived/labels.json")}
    albums = {a["id"]: a for a in load(ROOT / "data/bandcamp_bilbaotags_clean.json")["albums"]}
    name = lambda pid: places[pid]["name"]  # noqa: E731

    located = {i: r for i, r in res.items() if r["type"] in PLACED and r.get("place")}
    direct = {i: r for i, r in located.items() if r["type"] in ("direct", "manual")}
    inferred = {i: r for i, r in located.items() if r["type"] in ("same_account", "artist_inferred")}
    same_acc = {i: r for i, r in inferred.items() if r["type"] == "same_account"}
    art_inf = {i: r for i, r in inferred.items() if r["type"] == "artist_inferred"}
    multi = lambda r: r.get("account_kind") == "label"  # noqa: E731
    inf_multi = {i: r for i, r in same_acc.items() if multi(r)}
    dir_multi = {i: r for i, r in direct.items() if multi(r)}
    any_multi = {**inf_multi, **dir_multi}

    # Cuentas multiartista implicadas y ranking por releases situadas.
    by_acc = defaultdict(lambda: {"total": 0, "same_account": 0, "direct": 0, "places": Counter(), "artists": set()})
    for i, r in any_multi.items():
        b = by_acc[r["account"]]
        b["total"] += 1
        b["same_account" if r["type"] == "same_account" else "direct"] += 1
        b["places"][r["place"]] += 1
        b["artists"].add(albums[i]["artist"])
    ranking = sorted(by_acc.items(), key=lambda x: (-x[1]["total"], x[0]))

    places_inf_multi = Counter(r["place"] for r in inf_multi.values())
    places_any_multi = Counter(r["place"] for r in any_multi.values())

    # Escenarios.
    A = Counter(r["place"] for r in located.values())
    B = Counter(r["place"] for r in direct.values())
    C = Counter(r["place"] for i, r in direct.items() if not multi(r))  # extra: B sin cuentas multiartista
    # D: A sin las inferencias desde cuentas multiartista (conserva same_account
    # de cuentas de un solo artista, que en Bandcamp es el mismo dato que direct).
    D = Counter(r["place"] for i, r in located.items() if i not in inf_multi)
    sa_single = Counter(r["place"] for r in same_acc.values() if not multi(r))
    sa_multi = Counter(r["place"] for r in same_acc.values() if multi(r))
    lost = len(located) - len(direct)

    # Concentración por cuenta dentro de cada municipio (escenario A).
    acc_in_place = defaultdict(Counter)
    for r in located.values():
        acc_in_place[r["place"]][r["account"]] += 1

    L = [
        "# Auditoría: ubicaciones procedentes de cuentas multiartista",
        "",
        "*Generado por `python3 scripts/multiartist_audit.py` (solo lectura). No cambia datos ni semántica.*",
        "",
        "«Cuenta multiartista» = cuenta en `data/derived/labels.json` (índice heurístico de sellos: "
        "≥2 artistas distintos o léxico de sello). Su ubicación en Bandcamp es la de la cuenta, "
        "no necesariamente la del grupo.",
        "",
        "## Cifras",
        "",
        "| # | Métrica | Releases | % de localizadas |",
        "|---|---|---:|---:|",
        f"| 1 | Releases con ubicación resuelta (mapa por defecto) | {len(located)} | 100 % |",
        f"| 2 | Ubicación directa (Bandcamp en esta release; incluye manual: {sum(1 for r in direct.values() if r['type']=='manual')}) | {len(direct)} | {pct(len(direct), len(located))} |",
        f"| 3 | Inferidas por otra release/cuenta o por artista | {len(inferred)} | {pct(len(inferred), len(located))} |",
        f"| 3a | · misma cuenta (same_account) | {len(same_acc)} | {pct(len(same_acc), len(located))} |",
        f"| 3b | · mismo artista (artist_inferred; nunca desde cuentas multiartista) | {len(art_inf)} | {pct(len(art_inf), len(located))} |",
        f"| 4 | Inferidas que proceden de cuentas multiartista | {len(inf_multi)} | {pct(len(inf_multi), len(located))} |",
        f"| 4b | *Aparte:* directas cuya cuenta es multiartista (también ciudad de la cuenta) | {len(dir_multi)} | {pct(len(dir_multi), len(located))} |",
        f"| 5 | Cuentas multiartista implicadas (inferidas) | {len({r['account'] for r in inf_multi.values()})} | |",
        f"| 5b | Cuentas multiartista implicadas (inferidas + directas) | {len(by_acc)} | |",
        f"| 8 | Mapa que desaparecería sin inferencias (escenario B) | {lost} | {pct(lost, len(located))} |",
        f"| 8b | Mapa que desaparecería sin nada que venga de cuentas multiartista (4 + 4b) | {len(any_multi)} | {pct(len(any_multi), len(located))} |",
        "",
        "## 6. Las 20 cuentas multiartista que más releases sitúan",
        "",
        "| Cuenta | Releases situadas | vía misma cuenta | directas | Artistas distintos | Municipio(s) |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for acc, b in ranking[:20]:
        pl = ", ".join(f"{name(p)} ({n})" for p, n in b["places"].most_common(3))
        L.append(f"| `{acc}` | {b['total']} | {b['same_account']} | {b['direct']} | {len(b['artists'])} | {pl} |")
    L += ["", "## 7. Municipios que más releases reciben por esta vía", "",
          "| Municipio | Inferidas desde cuenta multiartista | Todo lo que viene de cuentas multiartista | Total en el mapa | % del municipio desde cuentas multiartista |",
          "|---|---:|---:|---:|---:|"]
    for p, n in places_any_multi.most_common(15):
        L.append(f"| {name(p)} | {places_inf_multi.get(p, 0)} | {n} | {A[p]} | {pct(n, A[p])} |")

    def top(counter, k=15):
        return counter.most_common(k)

    L += ["", "## Escenarios", "",
          "| | A — actual (directas + inferidas) | B — conservador (solo directas/manual) | C — extra: B sin cuentas multiartista | D — extra: A sin inferencias desde cuentas multiartista |",
          "|---|---:|---:|---:|---:|",
          f"| Releases localizadas | {len(located)} | {len(direct)} | {sum(C.values())} | {sum(D.values())} |",
          f"| % del catálogo ({len(res)}) | {pct(len(located), len(res))} | {pct(len(direct), len(res))} | {pct(sum(C.values()), len(res))} | {pct(sum(D.values()), len(res))} |",
          f"| Municipios visibles | {len(A)} | {len(B)} | {len(C)} | {len(D)} |",
          "",
          "**Ojo al leer B.** `same_account` no es una inferencia débil: Bandcamp localiza la *cuenta*, "
          "así que en una cuenta de un solo artista es el mismo dato que `direct`. En el catálogo "
          "original de Bilbao se visitó **una ficha por cuenta** (fase 3), así que el resto de "
          "releases de cada cuenta quedaron como `same_account`: B castiga sobre todo ese artefacto "
          "de método, no evidencia peor. D quita solo lo realmente dudoso.",
          "",
          "| Municipio | same_account (cuenta de un artista) | same_account (cuenta multiartista) |",
          "|---|---:|---:|",
          *[f"| {name(p)} | {n} | {sa_multi.get(p, 0)} |" for p, n in sa_single.most_common(6)],
          "", "### Top 15 municipios", "",
          "| # | A | B | C | D |", "|---:|---|---|---|---|"]
    ta, tb, tc, td = top(A), top(B), top(C), top(D)
    for k in range(15):
        f = lambda t: f"{name(t[k][0])} {t[k][1]}" if k < len(t) else ""  # noqa: E731
        L.append(f"| {k + 1} | {f(ta)} | {f(tb)} | {f(tc)} | {f(td)} |")

    diffs = sorted(((p, A[p], B.get(p, 0)) for p in A), key=lambda x: -(x[1] - x[2]))
    L += ["", "### Mayores diferencias A → B (releases que se pierden)", "",
          "| Municipio | A | B | Pierde | % que conserva | Cuota del mapa A → B |", "|---|---:|---:|---:|---:|---|"]
    TA, TB = len(located), len(direct)
    for p, a, b in diffs[:15]:
        L.append(f"| {name(p)} | {a} | {b} | {a - b} | {pct(b, a)} | {pct(a, TA)} → {pct(b, TB)} |")
    radical = [(p, a, B.get(p, 0)) for p in A for a in [A[p]] if a >= 10 and B.get(p, 0) / a < 0.5]
    gone = [p for p in A if p not in B]
    L += ["", "### Cambios radicales de peso", "",
          "Municipios con ≥10 releases en A que conservan menos de la mitad en B:", ""]
    L += [f"- **{name(p)}**: {a} → {b} ({pct(b, a)})" for p, a, b in sorted(radical, key=lambda x: x[2] / x[1])] or ["- Ninguno."]
    L += ["", f"Municipios que desaparecen del todo en B: {len(gone)}"
          + (" — " + ", ".join(f"{name(p)} ({A[p]})" for p in sorted(gone, key=lambda p: -A[p])) if gone else "")]

    L += ["", "### ¿Concentraciones que vienen sobre todo de una cuenta multiartista?", "",
          "Municipios (≥20 releases en A) donde una sola cuenta multiartista aporta ≥25 % de sus releases:", "",
          "| Municipio | Releases A | Cuenta | Releases de esa cuenta | % | Artistas distintos en la cuenta |",
          "|---|---:|---|---:|---:|---:|"]
    rows = []
    for p, accs in acc_in_place.items():
        if A[p] < 20:
            continue
        for acc, n in accs.most_common(3):
            if acc in labels and n / A[p] >= 0.25:
                rows.append((p, acc, n))
    for p, acc, n in sorted(rows, key=lambda x: -x[2] / A[x[0]]):
        L.append(f"| {name(p)} | {A[p]} | `{acc}` | {n} | {pct(n, A[p])} | {labels[acc].get('n_artistas', '?')} |")
    if not rows:
        L.append("| — | | | | | |")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
