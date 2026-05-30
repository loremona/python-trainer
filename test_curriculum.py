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
import app

CURRICULUM = app.CURRICULUM
run_code   = app.run_code


def _norm(t: str) -> str:
    """Normalizzazione identica a quella usata in render_study per i predict."""
    return "\n".join(l.strip() for l in t.strip().splitlines())


def check_exercise(ex: dict):
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

    # ── normali / debug: l'hint (soluzione) deve far passare la check ──────────
    if "check" in ex and "hint" in ex:
        out, err, vs = run_code(ex["hint"])
        if err:
            # L'hint non gira da solo: quasi sempre è un frammento o una
            # spiegazione, non la soluzione completa. Non auto-verificabile.
            return "SKIP", "hint non eseguibile da solo (frammento)"
        try:
            ok = ex["check"](out, err, vs)
        except Exception as e:
            return "FAIL", f"la lambda check ha sollevato {type(e).__name__}: {e}"
        if ok:
            return "PASS", ""
        return "FAIL", f"hint gira pulito ma la check ritorna False (output: {out.strip()!r})"

    # Nessun modo di verificarlo (es. esercizio AI runtime): salta.
    return "SKIP", "nessuna soluzione canonica da verificare"


def main():
    quiet = "-q" in sys.argv
    counts = {"PASS": 0, "SKIP": 0, "FAIL": 0}
    fails, skips = [], []

    for m in CURRICULUM:
        mid = m["id"]
        for j, ex in enumerate(m["esercizi"]):
            esito, dettaglio = check_exercise(ex)
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
