# 🐍 PYTHON TRAINER — Il corso Python a mondi

> Impara Python come un gioco di ruolo: 35 mondi, 154 esercizi verificati automaticamente,
> XP, badge, streak e boss challenge. Scrivi codice vero, l'app lo esegue e ti dice se hai vinto. ⚡

Corso **interattivo in Streamlit**, in italiano, con taglio pratico da automazione/SRE:
oltre alle basi copre testing, logging, regex, pathlib, SQLite, API HTTP, asyncio e design patterns.

---

## 🚀 Come si avvia

```bash
pip install -r requirements.txt
./run.sh          # = streamlit run app.py --server.port 8501
```

Poi apri `http://localhost:8501`. Serve **Python ≥ 3.10** (il curriculum usa `list[int]` e `int | None`).
I progressi (XP, esercizi completati, streak, badge) si salvano in `~/.python_quest.json`.

## 🎮 Come funziona

Ogni modulo è un "mondo" con 5 tab: **Teoria → Esempio eseguibile → Concetti → Approccio → Esercizi**.

Tre tipi di esercizio:
- **Normal / 🏆 Boss** — scrivi il codice nell'editor, premi *Esegui e verifica*: il codice gira
  in un subprocess (timeout 5s) e l'output passa dalla funzione `check` dell'esercizio.
- **🐛 Bug Hunt (debug)** — codice rotto da correggere, stessa verifica.
- **🔮 Predict** — leggi il codice e prevedi l'output riga per riga, poi lo riveli.

Gamification: XP per esercizio (+bonus first-try, senza hint, boss), livelli, streak giornaliero,
badge, sfida del giorno e **ripasso spaced** (gli esercizi tornano in scadenza dopo qualche giorno).
La **soluzione completa** di ogni esercizio si sblocca dopo averlo risolto o dopo aver chiesto l'hint.

### 🤖 Esercizi AI (opzionali)

In fondo a ogni modulo puoi generare esercizi extra con un LLM. Due backend gratuiti:
**Groq** (API key in `.streamlit/secrets.toml` → `GROQ_API_KEY = "gsk_..."`) oppure
**Ollama** in locale (`ollama pull llama3.2`). Senza backend il corso funziona comunque al 100%.

---

## 🗺️ I 35 mondi

| # | Mondo | Modulo | Esercizi |
|---|-------|--------|----------|
| 1 | 🌱 Foresta del Principiante | Variabili e Tipi | 4 |
| 2 | 🌿 Grotta del Testo | Stringhe | 3 |
| 3 | 🌳 Bivio delle Scelte | Condizioni | 4 |
| 4 | 🏔️ Montagna della Ripetizione | Cicli | 4 |
| 5 | 🏛️ Tempio della Riusabilità | Funzioni | 3 |
| 6 | 🗂️ Archivio dei Dati | Liste e Dizionari | 5 |
| 7 | 🏭 Fabbrica dell'Automazione | Automazione e File | 3 |
| 8 | ⚔️ Dungeon degli Errori | Gestione Errori | 4 |
| 9 | 🏗️ Cantiere di Setup | Setup e Ambiente (venv, pip) | 5 |
| 10 | ⚗️ Laboratorio dei Tipi | Tipi, Casting e Operatori | 5 |
| 11 | 🧅 Labirinto degli Scope | Scope, Lambda e Closures | 5 |
| 12 | 🏛️ Tempio dell'Immutabilità | Tuple e Mutabilità | 5 |
| 13 | 🌲 Foresta delle Decisioni | Controllo Avanzato | 5 |
| 14 | 🌊 Fiume dei Dati | Generatori e Iteratori | 5 |
| 15 | 🏛️ Accademia degli Oggetti | OOP Base | 5 |
| 16 | ⚗️ Laboratorio degli Oggetti | OOP Avanzata | 5 |
| 17 | 🎁 Magazzino degli Imballaggi | Decoratori | 5 |
| 18 | 📚 Biblioteca Standard | Moduli, Logging e Collections | 5 |
| 19 | 🔥 Sala di Crisi | Eccezioni Avanzate | 5 |
| 20 | 🔧 Officina dei Parametri | Unpacking e kwargs | 5 |
| 21 | 🌍 Portale della Configurazione | JSON e Variabili d'Ambiente | 5 |
| 22 | 🏎️ Circuito della Velocità | Comprehensions | 6 |
| 23 | 🧰 Cassetta degli Attrezzi | Strumenti Built-in | 5 |
| 24 | 🏢 Distretto del Codice Pulito | Type Hints & Annotazioni | 4 |
| 25 | 🧪 Laboratorio dei Test | Testing (assert & pytest) | 4 |
| 26 | 📜 Sala dei Registri | Logging | 4 |
| 27 | 🧰 Magazzino degli Strumenti | Standard Library (collections, itertools, functools) | 4 |
| 28 | 🔎 Sala dei Pattern | Espressioni Regolari (re) | 4 |
| 29 | 🗺️ Cartografia dei File | Pathlib | 4 |
| 30 | 🚪 Soglia delle Risorse | Context Manager (with) | 4 |
| 31 | 🗄️ Archivio SQL | Database con SQLite | 4 |
| 32 | 🌐 Porto delle API | API HTTP & JSON (requests) | 4 |
| 33 | ⚡ Dimensione Asincrona | Async / Await (asyncio) | 4 |
| 34 | 📦 Cantiere dei Pacchetti | Packaging & Versioning | 4 |
| 35 | 🧩 Tempio dei Pattern | Design Patterns | 4 |

**Totale: 154 esercizi**, tutti con verifica automatica, hint e soluzione di riferimento.

---

## 📐 Guida per chi sviluppa

### Struttura
```
├── app.py               # App Streamlit: UI, runner del codice, XP/badge, salvataggio
├── curriculum.py        # CURRICULUM: i 35 moduli (teoria, esempio, esercizi con check())
├── soluzioni.json       # Soluzione canonica per esercizio, chiave "modulo#idx"
├── criteri.json         # Descrizione leggibile del criterio di verifica, chiave "modulo#idx"
├── test_curriculum.py   # Test di integrità del curriculum
├── test_gamification.py # Test della logica XP/badge
└── run.sh               # Avvio rapido
```

### Schema di un esercizio (in `curriculum.py`)
```python
{ "testo": "Consegna in italiano, stile pratico",
  "placeholder": "codice di partenza nell'editor",
  "check": lambda out, err, vs: err is None and "atteso" in out,   # IL criterio di verifica
  "hint": "suggerimento (spesso un programma completo)",
  "tipo": "debug" | "predict",   # opzionale; default normal. 🏆 nei boss (xp_bonus)
  "expected": "...",             # solo per i predict
  "feedback": lambda out, err: "messaggio mirato se sbagli",  # opzionale
}
```

### Regole d'oro
1. **Ogni esercizio normal/debug deve avere la sua voce in `soluzioni.json` e `criteri.json`**
   (chiave `"modulo#idx"`). I `predict` no: la UI non mostra né soluzione né criterio per loro.
2. Una soluzione si committa solo **dopo averla eseguita e passata dalla `check()`**
   dell'esercizio (stesso meccanismo dell'app: subprocess + check sull'output).
3. Stile soluzioni: codice canonico pulito, senza commenti.
4. Prima di committare: `python test_curriculum.py && python test_gamification.py`
   (girano anche su GitHub Actions a ogni push).

## ✅ Stato

**Corso completo** (2026-07-02): 35/35 moduli, 154/154 esercizi verificabili,
128/128 soluzioni canoniche e 128/128 criteri per gli esercizi normal/debug.
