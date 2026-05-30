#!/usr/bin/env python3
"""
Test della logica di gamification: livelli/XP, streak, badge, spaced repetition.

Queste funzioni decidono i progressi dell'utente: un bug qui falsa XP/streak/SR
in silenzio. Qui le isoliamo da Streamlit con un finto `session_state` e
neutralizziamo `persist()`, così i test NON toccano il file dei progressi reale
(~/.python_quest.json).

Uso:
    python test_gamification.py            # report completo
    python test_gamification.py -q         # solo riepilogo + fallimenti
Exit code 1 se almeno un test fallisce.
"""
import sys
import types
from datetime import date, timedelta

import app


# ── Finto session_state ───────────────────────────────────────────────────────
class FakeState:
    """Espone gli attributi che le funzioni di gamification leggono/scrivono."""
    def __init__(self, save):
        self.save                = save
        self.xp_gained           = 0
        self.level_up            = None
        self.xp_log              = []
        self.new_badges          = []
        self.session_completati  = []


def _install(save=None):
    """Installa un session_state fresco e neutralizza persist(). Ritorna lo stato."""
    state = FakeState(save if save is not None else app.default_save())
    app.st = types.SimpleNamespace(session_state=state)
    app.persist = lambda: None
    return state


def _iso(days_ago):
    return str(date.today() - timedelta(days=days_ago))


# ── Test: livelli e XP ────────────────────────────────────────────────────────
def test_get_level_soglie():
    # LEVELS soglie: 0, 60, 180, 360, 600, 900
    assert app.get_level(0)     == 0
    assert app.get_level(59)    == 0
    assert app.get_level(60)    == 1
    assert app.get_level(179)   == 1
    assert app.get_level(180)   == 2
    assert app.get_level(360)   == 3
    assert app.get_level(600)   == 4
    assert app.get_level(900)   == 5
    assert app.get_level(99999) == 5

def test_get_level_info():
    lvl, title, color, progress, xp_to_next = app.get_level_info(0)
    assert lvl == 0
    assert xp_to_next == 60
    assert 0.0 <= progress <= 1.0
    # livello massimo: progresso pieno, niente XP al prossimo
    lvl, _, _, progress, xp_to_next = app.get_level_info(5000)
    assert lvl == 5
    assert progress == 1.0
    assert xp_to_next == 0

def test_award_xp_levelup():
    s = _install()
    s.save["xp"] = 55
    app.award_xp(10, "test")
    assert s.save["xp"] == 65
    assert s.level_up == app.LEVELS[1][1]   # ha superato la soglia 60
    assert s.xp_gained == 10

def test_award_xp_no_levelup():
    s = _install()
    s.save["xp"] = 200
    app.award_xp(10)
    assert s.save["xp"] == 210
    assert s.level_up is None                # resta nello stesso livello


# ── Test: streak ──────────────────────────────────────────────────────────────
def test_streak_prima_sessione():
    s = _install()
    s.save["last_study_date"] = None
    app.update_streak()
    assert s.save["streak"] == 1
    assert s.save["total_sessions"] == 1
    assert s.save["last_study_date"] == str(date.today())

def test_streak_giorno_consecutivo():
    s = _install()
    s.save["last_study_date"] = _iso(1)      # ieri
    s.save["streak"] = 2
    app.update_streak()
    assert s.save["streak"] == 3             # +1

def test_streak_reset_dopo_buco():
    s = _install()
    s.save["last_study_date"] = _iso(3)      # 3 giorni fa
    s.save["streak"] = 5
    app.update_streak()
    assert s.save["streak"] == 1             # azzerato

def test_streak_stesso_giorno_noop():
    s = _install()
    s.save["last_study_date"] = str(date.today())
    s.save["streak"] = 4
    s.save["total_sessions"] = 9
    app.update_streak()
    assert s.save["streak"] == 4             # invariato
    assert s.save["total_sessions"] == 9     # nessuna nuova sessione


# ── Test: badge ───────────────────────────────────────────────────────────────
def test_badge_primo_passo():
    s = _install()
    s.save["completati"] = ["variabili_0"]
    app.check_badges()
    assert "primo_passo" in s.save["badges"]

def test_badge_fulmine_e_perfetto():
    s = _install()
    s.save["completati"] = ["variabili_0"]
    s.save["first_try_count"] = 5
    app.check_badges()
    assert "fulmine" in s.save["badges"]     # >= 1 al primo colpo
    assert "perfetto" in s.save["badges"]    # >= 5 al primo colpo

def test_badge_fiamma_streak():
    s = _install()
    s.save["completati"] = ["variabili_0"]
    s.save["streak"] = 3
    app.check_badges()
    assert "fiamma" in s.save["badges"]


# ── Test: spaced repetition ───────────────────────────────────────────────────
def test_sr_non_completato_none():
    s = _install()
    assert app.days_until_review("mai_visto_0") is None

def test_sr_primo_intervallo():
    s = _install()
    eid = "variabili_0"
    s.save["completati"] = [eid]
    s.save["completed_dates"] = {eid: str(date.today())}   # completato oggi
    # nessun review ancora: primo intervallo = SR_INTERVALS[0] = 1 giorno
    assert app.days_until_review(eid) == app.SR_INTERVALS[0]

def test_sr_scaduto_oggi():
    s = _install()
    eid = "variabili_0"
    s.save["completati"] = [eid]
    s.save["completed_dates"] = {eid: _iso(10)}            # completato 10 gg fa
    assert app.days_until_review(eid) == 0                 # scaduto, da ripassare

def test_sr_mastered():
    s = _install()
    eid = "variabili_0"
    s.save["completati"] = [eid]
    s.save["reviews"] = {eid: [_iso(40), _iso(30), _iso(20), _iso(10), _iso(1)]}
    # numero review >= len(SR_INTERVALS) → mastered
    assert app.days_until_review(eid) is None


# ── Runner ────────────────────────────────────────────────────────────────────
def main():
    quiet = "-q" in sys.argv
    tests = [(n, f) for n, f in sorted(globals().items())
             if n.startswith("test_") and callable(f)]
    passed, failed = 0, []
    for name, fn in tests:
        try:
            fn()
            passed += 1
            if not quiet:
                print(f"✅ {name}")
        except AssertionError as e:
            failed.append((name, f"assert fallito: {e}"))
        except Exception as e:
            failed.append((name, f"{type(e).__name__}: {e}"))

    print("\n" + "─" * 60)
    print(f"  PASS {passed}   FAIL {len(failed)}   (totale {len(tests)})")
    if failed:
        print("\n  ❌ TEST FALLITI:")
        for name, det in failed:
            print(f"    {name}: {det}")
        return 1
    print("  Gamification OK. 🎮")
    return 0


if __name__ == "__main__":
    sys.exit(main())
