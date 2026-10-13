# 🐍 Python Trainer

Volevo imparare Python per l'automazione, ma i corsi online erano o troppo teorici o troppo
lenti. Così ho messo insieme un corso su misura in Streamlit: per ogni argomento c'è la
teoria, un esempio da eseguire e poi gli esercizi, dove il codice lo scrivo io e l'app
controlla se funziona.

In tutto sono **35 moduli e 154 esercizi**: si parte da variabili e cicli e si arriva a
testing, regex, SQLite, API HTTP e asyncio.

## Avvio

Serve Python 3.10 o più recente.

```bash
pip install -r requirements.txt
./run.sh        # apre l'app su http://localhost:8501
```

I progressi vengono salvati in `~/.python_quest.json`.

## Gli esercizi

Ci sono tre tipi di esercizio:

- **Scrivi il codice:** lo esegui dall'editor, l'app lo lancia in un processo separato (con
  un limite di 5 secondi) e controlla l'output. Gli esercizi più difficili sono segnati 🏆.
- **Trova il bug:** parti da un codice rotto e lo correggi.
- **Prevedi l'output:** leggi il codice e scrivi cosa stamperà, prima di vederlo.

Se mi blocco posso chiedere un indizio. La soluzione completa si sblocca solo dopo aver
risolto l'esercizio o chiesto l'indizio. Gli esercizi già fatti tornano dopo qualche giorno
per il ripasso. Per tenermi costante ci sono anche XP, livelli, badge e una sfida del giorno.

C'è anche un'opzione per generare esercizi extra con un modello AI, gratis con Groq o in
locale con Ollama. È facoltativa: il corso funziona benissimo anche senza.

## Cosa copre

| Base | Intermedio | Avanzato |
|------|------------|----------|
| Variabili e tipi | Scope, lambda e closures | Type hints |
| Stringhe | Tuple e mutabilità | Testing con pytest |
| Condizioni | Generatori e iteratori | Logging |
| Cicli | OOP base e avanzata | collections, itertools, functools |
| Funzioni | Decoratori | Espressioni regolari |
| Liste e dizionari | Moduli e collections | pathlib |
| File e automazione | Eccezioni avanzate | Context manager |
| Gestione errori | `*args` e `**kwargs` | SQLite |
| venv e pip | JSON e variabili d'ambiente | API HTTP con requests |
| Casting e operatori | Comprehensions | async / await |
| Controllo avanzato | Funzioni built-in | Packaging e design pattern |

## Com'è organizzato

```
app.py                 interfaccia Streamlit, esecuzione del codice, XP e badge
curriculum.py          i 35 moduli: teoria, esempi ed esercizi con la loro verifica
soluzioni.json         la soluzione di riferimento di ogni esercizio
criteri.json           cosa controlla la verifica, spiegato a parole
test_curriculum.py     controlla che il corso sia completo e coerente
test_gamification.py   controlla i calcoli di XP e badge
```

I test girano su GitHub Actions a ogni push. In locale:

```bash
python test_curriculum.py && python test_gamification.py
```

## Una nota

Il corso, cioè lezioni, esercizi e app, l'ho costruito con l'aiuto di Claude, perché mi
serviva uno strumento per studiare e non un progetto da sviluppare da zero. Il Python che
scrivo davvero da solo, una riga alla volta, sta in
[budget](https://github.com/loremona/budget).
