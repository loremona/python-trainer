#!/usr/bin/env python3
"""
Test di integrità del curriculum.

Verifica che ogni esercizio sia coerente, usando come "soluzione canonica"
i dati già presenti nell'esercizio stesso:

  • Esercizi normali / debug  → campo `hint` eseguito, poi la `check` deve passare.
  • Esercizi predict          → campo `codice` eseguito, l'output deve contenere `expected`.

Tre esiti per esercizio:
  PASS  — verificato: la soluzione canonica soddisfa la check.
  SKIP  — l'hint non è uno snippet eseguibile da solo (frammento/spiegazione):
          non auto-verificabile, NON è un errore.
  FAIL  — bug reale: la soluzione gira pulita ma la check/expected non combacia,
          oppure il codice di un predict va in errore.

Uso:
    python test_curriculum.py            # report completo
    python test_curriculum.py -q         # solo riepilogo + eventuali FAIL

Exit code 1 se c'è almeno un FAIL.
"""
import sys

# Importa il curriculum e il runner reali dall'app (la UI è dietro __main__,
# quindi l'import non avvia Streamlit; gli unici output sono warning innocui).
import os
import json

import app

CURRICULUM = app.CURRICULUM
run_code   = app.run_code

# Soluzioni canoniche complete (chiave "modulo#idx" → codice eseguibile).
# Coprono gli esercizi il cui `hint` è solo un frammento: con la soluzione
# completa l'harness può verificarli invece di limitarsi a SKIP.
_SOL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "soluzioni.json")
try:
    with open(_SOL_FILE, encoding="utf-8") as _f:
        SOLUZIONI = json.load(_f)
except Exception:
    SOLUZIONI = {}


def _norm(t: str) -> str:
    """Normalizzazione identica a quella usata in render_study per i predict."""
    return "\n".join(l.strip() for l in t.strip().splitlines())


def check_exercise(ex: dict, ref: str):
    """Ritorna (esito, dettaglio) con esito in {'PASS','SKIP','FAIL'}."""
    tipo = ex.get("tipo")

    # ── predict: il codice mostrato deve produrre l'output dichiarato ──────────
    if tipo == "predict" or ("codice" in ex and "expected" in ex):
        out, err, _ = run_code(ex["codice"])
        if err:
            return "FAIL", f"il codice del predict va in errore: {err.splitlines()[-1]}"
        expected = ex["expected"]
        if _norm(expected) == _norm(out) or expected.strip() in out:
            return "PASS", ""
        return "FAIL", f"output reale {out.strip()!r} non contiene expected {expected!r}"

    if "check" not in ex:
        return "SKIP", "nessuna check da verificare"

    # ── soluzione canonica: hint completo, oppure voce in soluzioni.json ───────
    soluzione = SOLUZIONI.get(ref)
    if soluzione is None and "hint" in ex:
        # Se l'hint gira da solo è già una soluzione completa; altrimenti è un
        # frammento e serve una voce in soluzioni.json.
        out, err, _ = run_code(ex["hint"])
        if err is None:
            soluzione = ex["hint"]

    if soluzione is None:
        return "SKIP", "hint frammentario e nessuna voce in soluzioni.json"

    out, err, vs = run_code(soluzione)
    if err:
        return "FAIL", f"la soluzione va in errore: {err.splitlines()[-1]}"
    try:
        ok = ex["check"](out, err, vs)
    except Exception as e:
        return "FAIL", f"la lambda check ha sollevato {type(e).__name__}: {e}"
    if ok:
        return "PASS", ""
    return "FAIL", f"soluzione gira pulita ma la check ritorna False (output: {out.strip()!r})"


def main():
    quiet = "-q" in sys.argv
    counts = {"PASS": 0, "SKIP": 0, "FAIL": 0}
    fails, skips = [], []

    for m in CURRICULUM:
        mid = m["id"]
        for j, ex in enumerate(m["esercizi"]):
            esito, dettaglio = check_exercise(ex, f"{mid}#{j}")
            counts[esito] += 1
            ref = f"{mid}#{j}"
            if esito == "FAIL":
                fails.append((ref, dettaglio, ex.get("testo", "")[:70]))
            elif esito == "SKIP":
                skips.append((ref, dettaglio))
            if not quiet:
                icona = {"PASS": "✅", "SKIP": "⏭️ ", "FAIL": "❌"}[esito]
                print(f"{icona} {ref:<22} {dettaglio}")

    print("\n" + "─" * 60)
    print(f"  PASS {counts['PASS']}   SKIP {counts['SKIP']}   FAIL {counts['FAIL']}"
          f"   (totale {sum(counts.values())})")

    if skips and quiet:
        print(f"\n  {len(skips)} esercizi non auto-verificabili (hint frammentari):")
        for ref, det in skips:
            print(f"    ⏭️  {ref}")

    if fails:
        print(f"\n  ❌ {len(fails)} ESERCIZI ROTTI:")
        for ref, det, testo in fails:
            print(f"    {ref}: {det}")
            print(f"        “{testo}…”")
        return 1

    print("  Nessun esercizio rotto. 🎉")
    return 0


if __name__ == "__main__":
    sys.exit(main())
