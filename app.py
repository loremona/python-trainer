import streamlit as st
import sys
import json
import os
import re
import random
import requests
import subprocess
import tempfile
from datetime import date, timedelta
from pathlib import Path

try:
    from streamlit_ace import st_ace
    HAS_ACE = True
except ImportError:
    HAS_ACE = False

st.set_page_config(page_title="🐍 Python Trainer", page_icon="🐍", layout="wide",
                   initial_sidebar_state="expanded")

SAVE_FILE = Path.home() / ".python_quest.json"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONSTANTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LEVELS = [
    (0,   "🐣 Uovo Python",    "#718096"),
    (60,  "🐍 Serpentino",     "#48bb78"),
    (180, "💻 Coder",          "#4299e1"),
    (360, "⚙️ Developer",      "#9f7aea"),
    (600, "☁️ Cloud Engineer", "#ed8936"),
    (900, "🧙 AWS Wizard",     "#f6e05e"),
]

XP_VALS = dict(esercizio=15, first_try=10, no_hint=5, modulo=25, streak=10)

BADGES = {
    "primo_passo":   ("🎯", "Primo Passo",        "Primo esercizio completato"),
    "fulmine":       ("⚡", "Fulmine",             "Esercizio al primo tentativo"),
    "senza_aiuto":   ("🧠", "Senza Aiuto",         "Modulo completato senza hint"),
    "fiamma":        ("🔥", "In Fiamme",           "Streak di 3 giorni"),
    "maestro":       ("🏆", "Maestro del Serpente","Tutti gli esercizi completati"),
    "cloud_warrior": ("☁️", "Cloud Warrior",       "Modulo boto3 completato"),
    "perfetto":      ("💯", "Perfezionista",        "5 esercizi al primo tentativo"),
    "notturno":      ("🌙", "Gufo Notturno",        "Studio dopo le 22:00"),
    "velocista":     ("🚀", "Velocista",            "3 esercizi nella stessa sessione"),
}

# Spaced repetition intervals (days)
SR_INTERVALS = [1, 3, 7, 14, 30]

# Python error → spiegazione in italiano
ERROR_EXPLANATIONS = {
    "NameError":        "Hai usato una variabile che non esiste ancora. Controlla il nome o definiscila prima di usarla.",
    "SyntaxError":      "Errore di sintassi: controlla parentesi, virgolette, e i `:` dopo `if`/`for`/`def`.",
    "IndentationError": "Indentazione sbagliata. In Python gli spazi contano: usa 4 spazi per ogni livello.",
    "TypeError":        "Tipo di dato sbagliato — es. stai sommando un numero a una stringa.",
    "IndexError":       "Stai cercando un elemento fuori dalla lista (indice troppo grande).",
    "KeyError":         "Stai cercando una chiave che non esiste nel dizionario.",
    "ZeroDivisionError":"Stai dividendo per zero!",
    "AttributeError":   "Stai chiamando un metodo che non esiste su questo tipo di dato.",
    "ValueError":       "Valore non valido passato a una funzione (es. `int('abc')`).",
    "RecursionError":   "Troppe chiamate ricorsive — probabilmente un loop infinito.",
    "TimeoutExpired":   "Il codice ha impiegato troppo tempo (>5s). Controlla se hai un loop infinito.",
}

MESSAGGI_OK = [
    "🔥 Boom! Hai capito tutto!", "⚡ Perfetto al primo colpo!",
    "🎯 Esatto! Sei un cannone!", "✨ Bravissimo, continua così!",
    "💥 Corretto! Python ti teme!", "🚀 Sei inarrestabile!",
    "🎉 Ottimo lavoro!", "🏆 Da manuale!",
]
MESSAGGI_RETRY = [
    "🤔 Quasi... riprova!", "💪 Non mollare, sei vicino!",
    "🧐 Controlla l'output e riprova", "😤 Ci manca poco!",
    "🐍 Python è capriccioso, ritenta!", "🔄 Ancora un tentativo!",
]
TIPS = [
    "💡 **Pro tip**: `enumerate()` ti dà indice e valore insieme nel for!",
    "💡 **Pro tip**: le f-string supportano espressioni: `f'{2+2}'` → `'4'`",
    "💡 **Pro tip**: `dict.get('key', default)` evita KeyError!",
    "💡 **Pro tip**: `*lista` la spacchetta: `print(*[1,2,3])` → `1 2 3`",
    "💡 **Pro tip**: `zip()` itera su due liste insieme!",
    "💡 **Pro tip**: in boto3 usa `try/except ClientError` per gli errori AWS!",
    "💡 **Pro tip**: `list comprehension` è più veloce di for + append!",
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONCETTI CHIAVE — contenuto didattico per ogni modulo
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from curriculum import _ol, CONCETTI, APPROCCIO, CURRICULUM

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# APPROCCIO ANALITICO — domande, pattern, checklist per modulo
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GLOSSARIO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GLOSSARIO = [
    ("Variabile",      "Un nome che fa riferimento a un valore in memoria. Come un'etichetta su una scatola."),
    ("Tipo (Type)",    "La categoria di un valore: `str` (testo), `int` (intero), `float` (decimale), `bool` (vero/falso)."),
    ("Stringa (str)",  "Testo racchiuso tra virgolette. Immutabile: non puoi cambiare un carattere, devi creare una nuova stringa."),
    ("Intero (int)",   "Numero senza decimali: `1`, `42`, `-7`. Operazioni: `+`, `-`, `*`, `//` (divisione intera), `%` (resto)."),
    ("Float",          "Numero decimale: `3.14`, `0.023`. Attenzione: `10 / 3` → `3.333...` non `3`."),
    ("Booleano (bool)","Solo due valori: `True` o `False`. Risultato di confronti (`==`, `>`, `in`, ...)."),
    ("Lista (list)",   "Sequenza ordinata di valori: `[1, 'a', True]`. Mutabile, indicizzata da 0."),
    ("Dizionario (dict)","Coppie chiave→valore: `{'nome': 'Lorenzo', 'età': 28}`. Accesso per chiave, non per posizione."),
    ("Funzione",       "Blocco di codice con un nome, che accetta parametri e (opzionalmente) ritorna un valore."),
    ("Parametro",      "Variabile dichiarata nella firma della funzione: `def f(parametro):`."),
    ("Argomento",      "Valore passato alla funzione quando la chiami: `f(42)` — `42` è l'argomento."),
    ("Return",         "Istruzione che fa uscire dalla funzione restituendo un valore. Senza `return` → `None`."),
    ("Iterazione",     "Un singolo 'giro' di un loop. Con 5 elementi, il for fa 5 iterazioni."),
    ("Indentazione",   "Gli spazi all'inizio di una riga. In Python definisce i blocchi di codice (if, for, def...)."),
    ("Eccezione",      "Un errore che si verifica durante l'esecuzione. Può essere gestita con `try/except`."),
    ("Traceback",      "Il messaggio di errore di Python: mostra cosa è andato storto e in quale riga."),
    ("Import",         "Istruzione per caricare un modulo esterno: `import os`, `import boto3`."),
    ("Modulo",         "Un file `.py` (o pacchetto) che contiene funzioni e variabili riutilizzabili."),
    ("API",            "Application Programming Interface: un modo standardizzato per comunicare con un servizio (es. AWS)."),
    ("JSON",           "Formato di dati testuale basato su dizionari e liste. Le risposte boto3 sono in formato JSON."),
    ("ARN",            "Amazon Resource Name: identificatore univoco di una risorsa AWS. Es: `arn:aws:s3:::mio-bucket`."),
    ("Client (boto3)", "Oggetto boto3 che rappresenta una connessione a un servizio AWS: `boto3.client('s3')`."),
    ("f-string",       "Stringa con variabili incorporate: `f'Ciao {nome}'`. Disponibile da Python 3.6+."),
    ("None",           "Valore speciale che significa 'nessun valore'. Ritornato da funzioni senza `return`."),
    ("List comprehension", "Modo compatto di creare liste: `[x*2 for x in lista if x > 0]`."),

    # ── Setup e Ambiente ──────────────────────────────────────────────────
    ("Virtual environment", "Ambiente Python isolato per progetto. Si crea con `python -m venv .venv`. Evita conflitti tra dipendenze di progetti diversi."),
    ("pip",                 "Package manager di Python. `pip install X` installa, `pip freeze > requirements.txt` congela le versioni."),
    ("requirements.txt",    "File che elenca le dipendenze con versioni esatte (`boto3==1.34.0`). Garantisce riproducibilità del progetto."),
    ("uv",                  "Alternativa moderna e molto più veloce a pip, scritta in Rust. `uv pip install boto3` — stessa interfaccia."),
    ("sys (modulo)",        "Modulo standard con informazioni sull'interprete Python: `sys.version`, `sys.executable`, `sys.argv`."),

    # ── Tipi, Casting e Operatori ─────────────────────────────────────────
    ("Casting",             "Conversione esplicita di tipo: `int('42')`, `float('3.14')`, `str(100)`, `bool(0)`."),
    ("Falsy",               "Valori che Python tratta come False in un contesto booleano: `0`, `''`, `[]`, `{}`, `None`, `False`."),
    ("Truthy",              "Qualsiasi valore non falsy. Attenzione: `'0'` e `[0]` sono truthy perché non sono vuoti."),
    ("Operatore ternario",  "Espressione condizionale in una riga: `x = a if condizione else b`. Alternativa compatta all'if/else di assegnazione."),
    ("Walrus operator `:=`","Assegna e valuta in un'unica espressione (Python 3.8+): `if n := len(lista) > 0: print(n)`. Riduce la ripetizione."),
    ("Divisione intera `//`","Divisione che tronca al numero intero: `10 // 3 → 3`. Utile per calcolare indici, pagine, step."),
    ("Modulo `%`",          "Resto della divisione intera: `10 % 3 → 1`. Usato per verificare parità (`n % 2 == 0`) e cicli circolari."),

    # ── Scope e Closures ──────────────────────────────────────────────────
    ("Scope",               "Regione del codice in cui un nome (variabile) è visibile e accessibile."),
    ("LEGB",                "Ordine di ricerca dei nomi in Python: Local → Enclosing → Global → Built-in."),
    ("global",              "Keyword che dichiara dentro una funzione che una variabile fa riferimento al livello di modulo: `global contatore`."),
    ("nonlocal",            "Keyword che dichiara che una variabile appartiene alla funzione esterna (Enclosing), non alla locale: `nonlocal x`."),
    ("Lambda",              "Funzione anonima in una riga: `lambda x: x * 2`. Usata come argomento per `sorted`, `map`, `filter`."),
    ("Closure",             "Funzione che ricorda le variabili dell'Enclosing scope anche dopo che la funzione esterna è terminata."),
    ("Funzione di prima classe", "In Python le funzioni sono oggetti: si passano come argomenti, si ritornano, si assegnano a variabili."),

    # ── Tuple e Mutabilità ────────────────────────────────────────────────
    ("Tupla (tuple)",       "Sequenza immutabile: `(1, 'a', True)`. Usata per dati fissi, chiavi di dizionario, ritorni multipli di funzioni."),
    ("Mutabile",            "Oggetto che può essere modificato dopo la creazione: liste, dizionari, set. `lista[0] = 99` funziona."),
    ("Immutabile",          "Oggetto che non può essere modificato: stringhe, tuple, int, float. Sicuro da condividere tra funzioni."),
    ("Unpacking",           "Assegnazione di più variabili da una sequenza in una riga: `a, b, c = (1, 2, 3)`. Funziona con liste e tuple."),
    ("copy.copy()",         "Copia superficiale: duplica il container ma condivide gli oggetti interni. `b = copy.copy(a)`."),
    ("copy.deepcopy()",     "Copia profonda: duplica tutto ricorsivamente. `b = copy.deepcopy(a)`. Sicuro per strutture annidate."),

    # ── Controllo Avanzato ────────────────────────────────────────────────
    ("break",               "Esce immediatamente dal loop corrente (for o while). Usato per uscire appena si trova quello che si cerca."),
    ("continue",            "Salta il resto del corpo del loop e passa all'iterazione successiva. Utile come filtro senza if annidati."),
    ("for/else",            "Il blocco `else` di un for esegue SOLO se il loop non ha fatto `break`. Utile per ricerche con 'non trovato'."),
    ("match/case",          "Pattern matching strutturato (Python 3.10+). Classifica valori o strutture dati con sintassi chiara. `case _:` è il default."),

    # ── Generatori e Iteratori ────────────────────────────────────────────
    ("Iteratore",           "Oggetto che produce valori uno alla volta con `next()`. Implementa `__iter__` e `__next__`."),
    ("Generatore",          "Funzione che usa `yield` invece di `return`. Produce valori lazy: uno alla volta, solo quando richiesto."),
    ("yield",               "Sospende la funzione, ritorna un valore, poi riprende da dove si era fermata alla prossima chiamata."),
    ("Generator expression","Comprehension con parentesi tonde: `(x**2 for x in range(n))`. Lazy: non crea la lista in memoria."),
    ("itertools",           "Modulo standard con strumenti per iteratori: `islice` (prendi N), `chain` (concatena), `groupby` (raggruppa)."),
    ("Lazy evaluation",     "Strategia che calcola i valori solo quando servono. I generatori sono lazy: risparmiano RAM su grandi dataset."),

    # ── OOP Base ──────────────────────────────────────────────────────────
    ("Classe",              "Template/progetto per creare oggetti. Definita con `class NomeClasse:`. Contiene attributi e metodi."),
    ("Istanza",             "Un oggetto creato da una classe: `obj = MiaClasse()`. Ogni istanza ha il suo stato indipendente."),
    ("self",                "Riferimento all'istanza corrente dentro i metodi della classe. Primo parametro obbligatorio di ogni metodo."),
    ("__init__",            "Metodo costruttore: eseguito automaticamente alla creazione di un'istanza. Inizializza gli attributi."),
    ("Attributo di istanza","Variabile legata a una specifica istanza: `self.nome = nome`. Ogni oggetto ha il suo valore."),
    ("Attributo di classe", "Variabile condivisa da tutte le istanze di una classe. Definita nel corpo della classe, fuori da `__init__`."),
    ("Ereditarietà",        "Una classe (figlia) estende un'altra (genitore): `class Figlio(Genitore):`. Eredita attributi e metodi."),
    ("super()",             "Chiama il metodo della classe genitore: `super().__init__(...)`. Essenziale nelle classi figlie."),
    ("Polimorfismo",        "Oggetti di classi diverse rispondono allo stesso metodo in modo specifico. `obj.costo()` funziona per EC2 e S3."),

    # ── OOP Avanzata ──────────────────────────────────────────────────────
    ("Metodi dunder",       "Metodi speciali con doppio underscore: `__str__`, `__repr__`, `__eq__`, `__len__`. Integrano l'oggetto con Python."),
    ("__str__",             "Ritorna una stringa leggibile per `print(obj)`. Pensato per l'utente finale."),
    ("__repr__",            "Ritorna una stringa tecnica per `repr(obj)` e il debugger. Deve idealmente ricreare l'oggetto."),
    ("@property",           "Decoratore che trasforma un metodo in attributo read-only: `obj.valore` invece di `obj.valore()`."),
    ("@classmethod",        "Metodo che riceve la classe (`cls`) invece dell'istanza. Usato per factory/costruttori alternativi."),
    ("@staticmethod",       "Metodo che non riceve né `self` né `cls`. Funzione pura che appartiene logicamente alla classe."),
    ("@dataclass",          "Decoratore (Python 3.7+) che genera automaticamente `__init__`, `__repr__`, `__eq__` da annotazioni di tipo."),
    ("field()",             "Funzione di dataclasses per specificare default factory per attributi mutabili: `field(default_factory=list)`."),

    # ── Decoratori ────────────────────────────────────────────────────────
    ("Decoratore",          "Funzione che avvolge un'altra funzione aggiungendo comportamento prima/dopo senza modificarla."),
    ("@functools.wraps",    "Decoratore da applicare al wrapper per preservare `__name__` e `__doc__` della funzione originale."),
    ("@lru_cache",          "Memoization automatica: salva i risultati di una funzione pura per evitare ricalcoli. `@lru_cache(maxsize=128)`."),
    ("functools.partial",   "Crea una nuova funzione con alcuni argomenti già fissati: `doppio = partial(moltiплica, y=2)`."),
    ("Memoization",         "Tecnica di ottimizzazione: salva il risultato di una chiamata funzione per riutilizzarlo se i parametri sono uguali."),

    # ── Moduli, Logging e Collections ─────────────────────────────────────
    ("__name__",            "Variabile speciale: vale `'__main__'` se lo script è eseguito direttamente, altrimenti il nome del modulo."),
    ("logging",             "Modulo standard per registrare messaggi con livelli (DEBUG, INFO, WARNING, ERROR, CRITICAL). Sostituisce print in produzione."),
    ("Logger",              "Oggetto `logging.getLogger(__name__)` che emette log. Ogni modulo dovrebbe avere il suo logger."),
    ("Counter",             "Da `collections`: dizionario specializzato per contare occorrenze. `Counter(['a','b','a'])` → `{'a':2,'b':1}`."),
    ("defaultdict",         "Da `collections`: dizionario che crea automaticamente un valore di default per chiavi mancanti. Evita KeyError."),
    ("Package",             "Directory Python con `__init__.py`. Raggruppa più moduli correlati: `from mio_package.utils import f`."),
    ("__init__.py",         "File che rende una directory un package Python. Può essere vuoto o contenere codice di inizializzazione."),

    # ── Eccezioni Avanzate ────────────────────────────────────────────────
    ("raise",               "Lancia esplicitamente un'eccezione: `raise ValueError('messaggio')`. Interrompe il flusso normale."),
    ("Eccezione personalizzata", "Classe che estende `Exception` per errori specifici del dominio: `class BudgetSuperatoError(Exception)`."),
    ("assert",              "Verifica un'invariante: `assert condizione, 'messaggio'`. Lancia `AssertionError` se falsa. Disabilitabile con `-O`."),
    ("Context manager",     "Oggetto che gestisce risorse con `with`: garantisce setup e cleanup automatico tramite `__enter__`/`__exit__`."),
    ("contextlib",          "Modulo standard per creare context manager con `@contextmanager` senza implementare `__enter__`/`__exit__`."),
    ("Exception chaining",  "`raise NuovoErrore() from e` — preserva l'eccezione originale nel traceback. Fondamentale per debug."),
    ("try/except/else",     "`else` in un try esegue solo se il try NON ha lanciato eccezioni. Separa il 'codice che può fallire' dal 'codice post-successo'."),
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PROGETTO FINALE — steps
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROGETTO_STEPS = [
    {
        "titolo": "Step 1 — Le risorse AWS",
        "descrizione": "Definisci le variabili di configurazione e la struttura dati delle risorse simulate.",
        "istruzioni": """
Crea:
- Una variabile `REGIONE = "eu-west-1"`
- Una variabile `SOGLIA_COSTO = 100` (EUR)
- Una lista `RISORSE` con almeno 4 risorse, ognuna un dizionario con chiavi:
  `tipo` ("EC2"/"S3"/"RDS"), `nome`, `costo_ora`, `ore_mese`
""",
        "placeholder": """REGIONE = "eu-west-1"
SOGLIA_COSTO = 100

RISORSE = [
    {"tipo": "EC2", "nome": "web-server-prod",  "costo_ora": 0.096, "ore_mese": 730},
    {"tipo": "EC2", "nome": "worker-staging",   "costo_ora": 0.023, "ore_mese": 200},
    {"tipo": "S3",  "nome": "backup-bucket",    "costo_ora": 0.002, "ore_mese": 730},
    {"tipo": "RDS", "nome": "db-prod",          "costo_ora": 0.145, "ore_mese": 730},
]

# Stampa quante risorse hai
print(f"Risorse caricate: {len(RISORSE)}")
print(f"Regione: {REGIONE}")""",
        "check": lambda out, err, vs: err is None and "Risorse caricate" in out and "eu-west-1" in out,
        "hint": 'print(f"Risorse caricate: {len(RISORSE)}")',
    },
    {
        "titolo": "Step 2 — Calcola i costi",
        "descrizione": "Scrivi una funzione che calcola il costo mensile di una risorsa.",
        "istruzioni": """
Scrivi la funzione `calcola_costo_mensile(risorsa)` che:
- Moltiplica `costo_ora * ore_mese`
- Arrotonda a 2 decimali con `round()`
- Ritorna il risultato

Poi itera su `RISORSE` e stampa: `EC2 | web-server-prod → $70.08`
""",
        "placeholder": """RISORSE = [
    {"tipo": "EC2", "nome": "web-server-prod",  "costo_ora": 0.096, "ore_mese": 730},
    {"tipo": "EC2", "nome": "worker-staging",   "costo_ora": 0.023, "ore_mese": 200},
    {"tipo": "S3",  "nome": "backup-bucket",    "costo_ora": 0.002, "ore_mese": 730},
    {"tipo": "RDS", "nome": "db-prod",          "costo_ora": 0.145, "ore_mese": 730},
]

def calcola_costo_mensile(risorsa):
    pass  # implementa qui

for r in RISORSE:
    costo = calcola_costo_mensile(r)
    print(f"{r['tipo']} | {r['nome']} → ${costo}")""",
        "check": lambda out, err, vs: err is None and "70.08" in out and "EC2" in out,
        "hint": "return round(risorsa['costo_ora'] * risorsa['ore_mese'], 2)",
    },
    {
        "titolo": "Step 3 — Analisi e alert",
        "descrizione": "Trova la risorsa più costosa e controlla se il totale supera la soglia.",
        "istruzioni": """
Aggiungi al codice precedente:
1. Una funzione `costo_totale(risorse)` che ritorna la somma di tutti i costi mensili
2. Stampa il totale: `Costo totale: $XXX.XX`
3. Se il totale supera `SOGLIA_COSTO = 100`, stampa `🚨 ALERT: budget superato!`
4. Trova e stampa la risorsa più costosa
""",
        "placeholder": """SOGLIA_COSTO = 100

RISORSE = [
    {"tipo": "EC2", "nome": "web-server-prod",  "costo_ora": 0.096, "ore_mese": 730},
    {"tipo": "EC2", "nome": "worker-staging",   "costo_ora": 0.023, "ore_mese": 200},
    {"tipo": "S3",  "nome": "backup-bucket",    "costo_ora": 0.002, "ore_mese": 730},
    {"tipo": "RDS", "nome": "db-prod",          "costo_ora": 0.145, "ore_mese": 730},
]

def calcola_costo_mensile(r):
    return round(r["costo_ora"] * r["ore_mese"], 2)

def costo_totale(risorse):
    pass  # somma tutti i costi

totale = costo_totale(RISORSE)
print(f"Costo totale: ${totale}")

# alert e risorsa più costosa
""",
        "check": lambda out, err, vs: err is None and "Costo totale" in out and "ALERT" in out,
        "hint": "sum(calcola_costo_mensile(r) for r in risorse)\nmax(RISORSE, key=lambda r: calcola_costo_mensile(r))",
    },
    {
        "titolo": "Step 4 — Salva il report",
        "descrizione": "Salva tutto in un file di testo formattato.",
        "istruzioni": """
Scrivi una funzione `salva_report(risorse, nome_file)` che:
1. Apre il file in scrittura
2. Scrive un'intestazione con la data di oggi
3. Scrive una riga per ogni risorsa con costo
4. Scrive il totale e l'eventuale alert

Poi chiamala: `salva_report(RISORSE, "aws_report.txt")`
Stampa: `Report salvato in aws_report.txt`
""",
        "placeholder": """from datetime import date

RISORSE = [
    {"tipo": "EC2", "nome": "web-server-prod",  "costo_ora": 0.096, "ore_mese": 730},
    {"tipo": "RDS", "nome": "db-prod",          "costo_ora": 0.145, "ore_mese": 730},
]
SOGLIA_COSTO = 100

def calcola_costo_mensile(r):
    return round(r["costo_ora"] * r["ore_mese"], 2)

def salva_report(risorse, nome_file):
    totale = sum(calcola_costo_mensile(r) for r in risorse)
    with open(nome_file, "w") as f:
        pass  # scrivi il report

salva_report(RISORSE, "aws_report.txt")
print("Report salvato in aws_report.txt")""",
        "check": lambda out, err, vs: err is None and "Report salvato" in out,
        "hint": 'f.write(f"=== Report AWS {date.today()} ===\\n")\nfor r in risorse:\n    f.write(f"{r[\'tipo\']} | {r[\'nome\']}: ${calcola_costo_mensile(r)}\\n")',
    },
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CSS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.markdown("""
<style>
.stApp { background: linear-gradient(160deg, #0d0d1a 0%, #0f1724 60%, #0d1a14 100%); }
section[data-testid="stSidebar"] { background: #0a0a14 !important; border-right: 1px solid #1a2040; }
section[data-testid="stSidebar"] * { color: #c8d6e8 !important; }
.stButton > button {
    background: linear-gradient(135deg, #1a1a3a, #1e2842);
    color: #e2e8f0 !important; border: 1px solid #2d3a5e;
    border-radius: 8px; transition: all 0.2s ease; font-weight: 500;
}
.stButton > button:hover {
    border-color: #4ade80; box-shadow: 0 0 14px rgba(74,222,128,0.25);
    transform: translateY(-1px);
}
button[kind="primary"] { background: linear-gradient(135deg,#065f46,#047857) !important; border-color: #4ade80 !important; }
.stTextArea textarea {
    font-family: 'Fira Code','Courier New',monospace !important; font-size: 0.88rem !important;
    background: #0d1117 !important; color: #e6edf3 !important;
    border: 1px solid #21262d !important; border-radius: 8px !important;
}
.stTextArea textarea:focus { border-color: #4ade80 !important; box-shadow: 0 0 10px rgba(74,222,128,0.15) !important; }
.stTabs [data-baseweb="tab-list"] { background: #0d0d1a; border-bottom: 1px solid #1a2040; gap: 4px; }
.stTabs [data-baseweb="tab"] { background: transparent; color: #94a3b8 !important; border-radius: 6px 6px 0 0; padding: 8px 20px; }
.stTabs [aria-selected="true"] { background: #1a1a3a !important; color: #4ade80 !important; border-bottom: 2px solid #4ade80 !important; }
.streamlit-expanderHeader { background: #12122a; border: 1px solid #1e2840; border-radius: 8px; color: #c8d6e8 !important; }
.streamlit-expanderContent { background: #0f0f22; border: 1px solid #1e2840; border-top: none; border-radius: 0 0 8px 8px; }
hr { border-color: #1a2040 !important; }
.stProgress > div > div { background: linear-gradient(90deg,#4ade80,#22d3ee) !important; border-radius: 4px; }
/* Ace editor container */
.ace-editor-wrapper { border: 1px solid #21262d; border-radius: 8px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PERSISTENCE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def default_save():
    return {
        "xp": 0,
        "completati": [],
        "badges": [],
        "streak": 0,
        "best_streak": 0,
        "last_study_date": None,
        "attempts": {},
        "hints_used": [],
        "modules_completed": [],
        "first_try_count": 0,
        "total_sessions": 0,
        # spaced repetition
        "completed_dates": {},   # eid → ISO date string
        "reviews": {},           # eid → [ISO date strings]
        # errori per modulo
        "errori_per_modulo": {}, # module_id → numero totale check falliti
    }

def _deep_merge(base: dict, data: dict) -> dict:
    """Merge ricorsivo: le chiavi di base mancanti in data vengono preservate."""
    result = base.copy()
    for key, val in data.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = val
    return result

def load_save():
    if SAVE_FILE.exists():
        try:
            data = json.loads(SAVE_FILE.read_text())
            return _deep_merge(default_save(), data)
        except Exception:
            pass
    return default_save()

def persist():
    """Salva i progressi in modo atomico: scrive su un file temporaneo nella
    stessa cartella, poi os.replace() (rename atomico). Un crash a metà
    scrittura lascia intatto il salvataggio precedente invece di corromperlo."""
    tmp = SAVE_FILE.with_suffix(SAVE_FILE.suffix + ".tmp")
    try:
        tmp.write_text(json.dumps(st.session_state.save, indent=2))
        os.replace(tmp, SAVE_FILE)
    except Exception as e:
        # Non propaghiamo (non vogliamo far cadere la UI), ma lo segnaliamo
        # invece di ingoiarlo in silenzio: prima un crash qui = progressi persi
        # senza che l'utente lo sapesse.
        print(f"persist: impossibile salvare i progressi ({e})", file=sys.stderr)
        try:
            tmp.unlink(missing_ok=True)
        except Exception:
            pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CODE RUNNER
# Esegue il codice utente in un sottoprocesso separato con timeout.
# NON è sandboxed: il codice gira con i permessi dell'utente corrente e
# ha accesso al filesystem, alla rete e alle variabili d'ambiente.
# L'unica protezione attiva è il timeout (default 5s) contro loop infiniti.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_code(code: str, timeout: int = 5):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                     delete=False, encoding="utf-8") as f:
        f.write(code)
        tmp = f.name
    try:
        result = subprocess.run(
            [sys.executable, tmp],
            capture_output=True, text=True, timeout=timeout,
        )
        stdout = result.stdout
        stderr = result.stderr.strip() if result.stderr.strip() else None
        return stdout, stderr, {}
    except subprocess.TimeoutExpired:
        return "", "TimeoutExpired: il codice ha impiegato troppo tempo (>5s)", {}
    except Exception as e:
        return "", str(e), {}
    finally:
        try:
            os.unlink(tmp)
        except Exception:
            pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ERROR EXPLAINER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def explain_error(stderr: str) -> str:
    if not stderr:
        return ""
    for key, msg in ERROR_EXPLANATIONS.items():
        if key in stderr:
            return f"**{key}** — {msg}"
    return ""


def explain_error_ai(code: str, stderr: str) -> str:
    """Manda codice + errore al backend AI; fallback su explain_error."""
    backend, param = detect_ai_backend()
    if not backend:
        return explain_error(stderr) or ""
    prompt = (
        f"Sei un insegnante di Python. Uno studente ha scritto questo codice:\n\n"
        f"```python\n{code}\n```\n\n"
        f"Ha ottenuto questo errore:\n```\n{stderr}\n```\n\n"
        "Spiega in italiano, in modo chiaro e conciso (max 120 parole):\n"
        "1. Cosa significa l'errore\n"
        "2. Quale riga del codice lo causa e perché\n"
        "3. Come correggerlo (con esempio minimo)\n"
        "Nessun testo introduttivo, vai diretto alla spiegazione."
    )
    try:
        if backend == "ollama":
            r = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": param, "prompt": prompt, "stream": False},
                timeout=20,
            )
            r.raise_for_status()
            return r.json()["response"].strip()
        else:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {param}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 300,
                },
                timeout=15,
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return explain_error(stderr) or ""


def _ai_explain_widget(key: str):
    """Bottone 'Spiegami l'errore' persistente. Chiama dopo ogni blocco run."""
    ctx = st.session_state.get(f"_ec_{key}")
    if not ctx:
        return
    code, err = ctx
    ai_text = st.session_state.get(f"_ea_{key}")
    if ai_text:
        st.markdown("**🤖 Spiegazione:**")
        st.info(ai_text)
    else:
        if st.button("🤖 Spiegami l'errore", key=f"_aibtn_{key}"):
            with st.spinner("Analisi in corso..."):
                result = explain_error_ai(code, err)
            st.session_state[f"_ea_{key}"] = result or "Nessuna spiegazione disponibile."
            st.rerun()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AI EXERCISE GENERATION (Ollama locale o Groq free tier)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _groq_key() -> str:
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        try:
            key = st.secrets.get("GROQ_API_KEY", "")
        except Exception:
            pass
    return key

def detect_ai_backend():
    """Returns ('ollama', model_name) or ('groq', api_key) or (None, None)."""
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=1)
        if r.status_code == 200:
            models = r.json().get("models", [])
            if models:
                return "ollama", models[0]["name"]
    except Exception:
        pass
    key = _groq_key()
    if key:
        return "groq", key
    return None, None

_AI_PROMPT_TEMPLATE = """Sei un insegnante di Python. Crea UN esercizio pratico sul tema "{title}".

Regole:
- Risolto con massimo 8 righe di codice Python
- Deve stampare qualcosa di preciso e verificabile
- Usa esempi con temi AWS/cloud quando possibile
- Adatto a principianti

Rispondi SOLO con questo JSON, nessun testo fuori:
{{
  "testo": "descrizione dell'esercizio in italiano (2-3 frasi)",
  "placeholder": "# codice starter con commenti guida",
  "expected": "stringa ESATTA (o parte di essa) che deve apparire nell'output",
  "hint": "suggerimento in una riga",
  "soluzione": "codice Python completo e funzionante"
}}"""

def generate_ai_exercise(module_title: str) -> dict | None:
    backend, param = detect_ai_backend()
    if not backend:
        return None
    prompt = _AI_PROMPT_TEMPLATE.format(title=module_title)
    try:
        if backend == "ollama":
            r = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": param, "prompt": prompt, "stream": False},
                timeout=30,
            )
            r.raise_for_status()
            raw = r.json()["response"]
        else:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {param}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.85,
                    "max_tokens": 600,
                },
                timeout=15,
            )
            r.raise_for_status()
            raw = r.json()["choices"][0]["message"]["content"]

        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if not match:
            return None
        data = json.loads(match.group())
        if not {"testo", "placeholder", "expected", "hint", "soluzione"}.issubset(data):
            return None
        return data
    except Exception:
        return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SPACED REPETITION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def days_until_review(eid: str) -> int | None:
    """Returns days until next review, 0 = due today, None = mastered/not done."""
    s = st.session_state.save
    if eid not in s["completati"]:
        return None
    reviews = s.get("reviews", {}).get(eid, [])
    n = len(reviews)
    if n >= len(SR_INTERVALS):
        return None  # mastered
    interval = SR_INTERVALS[n]
    if reviews:
        last_str = reviews[-1]
    else:
        last_str = s.get("completed_dates", {}).get(eid)
        if not last_str:
            return 0
    last = date.fromisoformat(last_str)
    due_in = (last + timedelta(days=interval) - date.today()).days
    return max(0, due_in)

def exercises_due_today() -> list[str]:
    due = []
    for m in CURRICULUM:
        for j in range(len(m["esercizi"])):
            eid = f"{m['id']}_{j}"
            if days_until_review(eid) == 0:
                due.append(eid)
    return due

def mark_reviewed(eid: str):
    s = st.session_state.save
    s.setdefault("reviews", {}).setdefault(eid, []).append(str(date.today()))
    persist()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GAMIFICATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_level(xp):
    lvl = 0
    for i, (thr, *_) in enumerate(LEVELS):
        if xp >= thr:
            lvl = i
    return lvl

def get_level_info(xp):
    lvl = get_level(xp)
    _, title, color = LEVELS[lvl]
    cur_thr = LEVELS[lvl][0]
    if lvl + 1 < len(LEVELS):
        next_thr = LEVELS[lvl + 1][0]
        progress = (xp - cur_thr) / max(1, next_thr - cur_thr)
        xp_to_next = next_thr - xp
    else:
        progress = 1.0
        xp_to_next = 0
    return lvl, title, color, progress, xp_to_next

def award_xp(amount, reason=""):
    s = st.session_state.save
    old_lvl = get_level(s["xp"])
    s["xp"] += amount
    new_lvl = get_level(s["xp"])
    persist()
    st.session_state.xp_gained += amount
    if new_lvl > old_lvl:
        st.session_state.level_up = LEVELS[new_lvl][1]
    if reason:
        st.session_state.xp_log.append(f"+{amount} XP — {reason}")

def update_streak():
    s = st.session_state.save
    today = str(date.today())
    if s["last_study_date"] == today:
        return
    if s["last_study_date"]:
        last = date.fromisoformat(s["last_study_date"])
        diff = (date.today() - last).days
        if diff == 1:
            s["streak"] += 1
            mult = min(s["streak"], 5)
            award_xp(XP_VALS["streak"] * mult, f"streak {s['streak']} giorni")
        elif diff > 1:
            s["streak"] = 1
    else:
        s["streak"] = 1
        award_xp(XP_VALS["streak"], "prima sessione!")
    s["best_streak"] = max(s["streak"], s.get("best_streak", 0))
    s["last_study_date"] = today
    s["total_sessions"] = s.get("total_sessions", 0) + 1
    persist()

def check_badges():
    s = st.session_state.save
    earned = set(s["badges"])
    new = []

    def unlock(key):
        if key not in earned:
            earned.add(key)
            new.append(key)

    if s["completati"]:                            unlock("primo_passo")
    if s.get("first_try_count", 0) >= 1:           unlock("fulmine")
    if s.get("first_try_count", 0) >= 5:           unlock("perfetto")
    if s["streak"] >= 3:                           unlock("fiamma")
    tot = sum(len(m["esercizi"]) for m in CURRICULUM)
    if len(s["completati"]) >= tot:                unlock("maestro")
    if "boto3_intro" in s.get("modules_completed", []):
        unlock("cloud_warrior")
    from datetime import datetime
    if datetime.now().hour >= 22 and s["completati"]:
        unlock("notturno")
    if len(st.session_state.session_completati) >= 3:
        unlock("velocista")
    for m in CURRICULUM:
        mid = m["id"]
        mod_keys = [f"{mid}_{j}" for j in range(len(m["esercizi"]))]
        if all(k in s["completati"] for k in mod_keys):
            if not any(k in s.get("hints_used", []) for k in mod_keys):
                unlock("senza_aiuto")
                break

    if new:
        s["badges"] = list(earned)
        st.session_state.new_badges.extend(new)
        persist()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━



# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CURRICULUM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━



# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SESSION INIT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def init_state():
    # These must be initialized BEFORE update_streak (which calls award_xp)
    if "xp_gained" not in st.session_state:
        st.session_state.xp_gained = 0
    if "xp_log" not in st.session_state:
        st.session_state.xp_log = []
    if "level_up" not in st.session_state:
        st.session_state.level_up = None
    if "session_completati" not in st.session_state:
        st.session_state.session_completati = []
    if "new_badges" not in st.session_state:
        st.session_state.new_badges = []
    if "save" not in st.session_state:
        st.session_state.save = load_save()
        update_streak()
    if "view" not in st.session_state:
        st.session_state.view = "map"
    if "modulo_idx" not in st.session_state:
        st.session_state.modulo_idx = 0
    if "codice" not in st.session_state:
        st.session_state.codice = {}


def is_unlocked(idx):
    if idx == 0:
        return True
    prev = CURRICULUM[idx - 1]
    keys = [f"{prev['id']}_{j}" for j in range(len(prev["esercizi"]))]
    return all(k in st.session_state.save["completati"] for k in keys)


def module_progress(idx):
    m = CURRICULUM[idx]
    keys = [f"{m['id']}_{j}" for j in range(len(m["esercizi"]))]
    done = sum(1 for k in keys if k in st.session_state.save["completati"])
    return done, len(keys)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CODE EDITOR COMPONENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def code_editor(default: str, key: str, height: int = 200) -> str:
    if HAS_ACE:
        return st_ace(
            value=default,
            language="python",
            theme="monokai",
            font_size=14,
            tab_size=4,
            show_gutter=True,
            show_print_margin=False,
            wrap=False,
            auto_update=False,
            height=height,
            key=key,
        )
    return st.text_area("Codice:", value=default, height=height, key=key)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# XP BAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def render_xp_bar():
    s = st.session_state.save
    lvl, title, color, progress, xp_to_next = get_level_info(s["xp"])
    pct = int(progress * 100)
    xp_label = f"{xp_to_next} XP al prossimo" if xp_to_next else "LIVELLO MASSIMO"
    st.markdown(f"""
<div style="background:#0d0d1a;border:1px solid #1a2040;border-radius:12px;
            padding:14px 18px;margin-bottom:8px;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
    <span style="font-size:1.05rem;font-weight:700;color:{color};">{title}</span>
    <span style="font-size:0.85rem;color:#94a3b8;">⭐ {s['xp']} XP</span>
  </div>
  <div style="background:#1a1a3a;border-radius:6px;height:12px;overflow:hidden;">
    <div style="width:{pct}%;background:linear-gradient(90deg,#4ade80,#22d3ee);
                height:100%;border-radius:6px;"></div>
  </div>
  <div style="display:flex;justify-content:space-between;margin-top:5px;">
    <span style="font-size:0.7rem;color:#4b5563;">Lv {lvl}</span>
    <span style="font-size:0.7rem;color:#4b5563;">{xp_label}</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SIDEBAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def render_sidebar():
    s = st.session_state.save
    due_today = exercises_due_today()

    with st.sidebar:
        st.markdown("## 🐍 Python Quest")
        render_xp_bar()

        streak_color = "#f97316" if s["streak"] >= 3 else "#94a3b8"
        tot_done = len(s["completati"])
        tot_all  = sum(len(m["esercizi"]) for m in CURRICULUM)

        st.markdown(f"""
<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:10px 0;">
  <div style="background:#0f0f22;border:1px solid #1e2840;border-radius:8px;padding:10px;text-align:center;">
    <div style="font-size:1.4rem;color:{streak_color};">🔥 {s['streak']}</div>
    <div style="font-size:0.7rem;color:#64748b;">streak</div>
  </div>
  <div style="background:#0f0f22;border:1px solid #1e2840;border-radius:8px;padding:10px;text-align:center;">
    <div style="font-size:1.4rem;color:#4ade80;">✅ {tot_done}/{tot_all}</div>
    <div style="font-size:0.7rem;color:#64748b;">esercizi</div>
  </div>
  <div style="background:#0f0f22;border:1px solid #1e2840;border-radius:8px;padding:10px;text-align:center;">
    <div style="font-size:1.4rem;color:#f59e0b;">🏅 {len(s['badges'])}</div>
    <div style="font-size:0.7rem;color:#64748b;">badge</div>
  </div>
  <div style="background:#0f0f22;border:1px solid {'#f97316' if due_today else '#1e2840'};
              border-radius:8px;padding:10px;text-align:center;">
    <div style="font-size:1.4rem;color:{'#f97316' if due_today else '#94a3b8'};">
      📅 {len(due_today)}
    </div>
    <div style="font-size:0.7rem;color:#64748b;">da ripassare</div>
  </div>
</div>
""", unsafe_allow_html=True)

        if due_today:
            st.warning(f"📅 {len(due_today)} esercizi da ripassare oggi!")

        st.divider()
        st.markdown("**Navigazione**")
        views = [("🗺️ Mappa Mondo", "map"), ("📅 Ripasso", "review"),
                 ("📖 Guida", "guida"), ("🎓 Progetto Finale", "progetto"),
                 ("📊 Statistiche", "stats"), ("🏅 Badge", "badges"),
                 ("🧪 Playground", "playground")]
        for label, v in views:
            active = st.session_state.view == v
            badge = f" ({len(due_today)})" if v == "review" and due_today else ""
            if st.button(label + badge, key=f"nav_{v}", use_container_width=True,
                         type="primary" if active else "secondary"):
                st.session_state.view = v
                st.rerun()

        st.divider()
        st.markdown("**Moduli**")
        for i, m in enumerate(CURRICULUM):
            done, tot = module_progress(i)
            unlocked = is_unlocked(i)
            active = (st.session_state.view == "study" and st.session_state.modulo_idx == i)
            icon = m["icon"] if unlocked else "🔒"
            label = f"{icon} {m['title']} {done}/{tot}"
            if st.button(label, key=f"mod_{i}", use_container_width=True,
                         type="primary" if active else "secondary",
                         disabled=not unlocked):
                st.session_state.modulo_idx = i
                st.session_state.view = "study"
                st.rerun()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAP VIEW
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def render_map():
    st.markdown("# 🗺️ Mappa del Mondo")
    st.markdown("Completa ogni modulo per sbloccare il successivo.")
    due_eids = set(exercises_due_today())

    cols = st.columns(4)
    for i, m in enumerate(CURRICULUM):
        done, tot = module_progress(i)
        unlocked = is_unlocked(i)
        complete = done == tot
        mod_eids = {f"{m['id']}_{j}" for j in range(tot)}
        has_review = bool(mod_eids & due_eids)

        if complete:
            border, bg = "#4ade80", "rgba(74,222,128,0.08)"
            status, sc = "✅ Completato", "#4ade80"
        elif unlocked:
            border, bg = "#4299e1", "rgba(66,153,225,0.06)"
            status, sc = f"📝 {done}/{tot} esercizi", "#4299e1"
        else:
            border, bg = "#2d3748", "rgba(0,0,0,0.3)"
            status, sc = "🔒 Bloccato", "#4a5568"

        if has_review:
            border = "#f97316"

        pct = int((done / tot) * 100) if tot else 0
        col = cols[i % 4]
        with col:
            review_badge = '<div style="font-size:0.7rem;color:#f97316;margin-bottom:4px;">📅 ripasso disponibile</div>' if has_review else ""
            st.markdown(f"""
<div style="background:{bg};border:1px solid {border};border-radius:12px;
            padding:16px;margin-bottom:16px;opacity:{'1' if unlocked else '0.55'};">
  {review_badge}
  <div style="font-size:2rem;text-align:center;margin-bottom:6px;">
    {m['icon'] if unlocked else '🔒'}
  </div>
  <div style="font-weight:700;color:#e2e8f0;text-align:center;margin-bottom:4px;font-size:0.85rem;">
    {m['title']}
  </div>
  <div style="font-size:0.72rem;color:#64748b;text-align:center;margin-bottom:10px;">{m['world']}</div>
  <div style="background:#1a1a3a;border-radius:4px;height:6px;margin-bottom:8px;">
    <div style="width:{pct}%;background:{border};height:100%;border-radius:4px;"></div>
  </div>
  <div style="font-size:0.75rem;color:{sc};text-align:center;">{status}</div>
</div>
""", unsafe_allow_html=True)
            if unlocked and st.button(
                "▶ Studia" if not complete else "🔄 Ripassa",
                key=f"map_go_{i}", use_container_width=True
            ):
                st.session_state.modulo_idx = i
                st.session_state.view = "study"
                st.rerun()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# REVIEW VIEW (spaced repetition)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def render_review():
    st.markdown("# 📅 Sessione di Ripasso")
    due = exercises_due_today()
    s = st.session_state.save

    if not due:
        st.success("🎉 Nessun esercizio da ripassare oggi! Torna domani.")
        return

    st.info(f"**{len(due)} esercizi** da ripassare per consolidare la memoria a lungo termine.")

    # Build lookup
    ex_lookup = {}
    for m in CURRICULUM:
        for j, ex in enumerate(m["esercizi"]):
            eid = f"{m['id']}_{j}"
            ex_lookup[eid] = (m, j, ex)

    for eid in due:
        if eid not in ex_lookup:
            continue
        m, j, ex = ex_lookup[eid]
        reviews_done = len(s.get("reviews", {}).get(eid, []))
        next_interval = SR_INTERVALS[reviews_done] if reviews_done < len(SR_INTERVALS) else "∞"

        with st.expander(f"📅 {m['icon']} {m['title']} — Esercizio {j+1}", expanded=True):
            st.info(ex["testo"])
            rk = f"rev_{eid}"
            default = st.session_state.codice.get(rk, ex["placeholder"])
            code = code_editor(default, key=rk, height=150)
            st.session_state.codice[rk] = code

            c1, c2 = st.columns(2)
            with c1:
                if st.button("▶️ Verifica ripasso", key=f"revrun_{eid}"):
                    out, err, lv = run_code(code)
                    if err:
                        explanation = explain_error(err)
                        st.error("**Errore nel codice**")
                        if explanation:
                            st.warning(explanation)
                        st.code(err, language="")
                        st.session_state[f"_ec_rev_{eid}"] = (code, err)
                        st.session_state.pop(f"_ea_rev_{eid}", None)
                    else:
                        st.session_state.pop(f"_ec_rev_{eid}", None)
                        st.session_state.pop(f"_ea_rev_{eid}", None)
                        if out:
                            st.code(out, language="")
                        try:
                            ok = ex["check"](out, err, lv)
                        except Exception:
                            ok = False
                        if ok:
                            mark_reviewed(eid)
                            st.success(f"✅ Ottimo! Prossimo ripasso tra **{next_interval} giorni**.")
                            st.rerun()
                        else:
                            fb = ex.get("feedback")
                            msg = fb(out, err) if fb else random.choice(MESSAGGI_RETRY)
                            st.warning(msg)
                            epm = s.setdefault("errori_per_modulo", {})
                            epm[m["id"]] = epm.get(m["id"], 0) + 1
                            persist()
            with c2:
                if st.button("💡 Hint", key=f"revhint_{eid}"):
                    st.info(f"💡 {ex['hint']}")
            _ai_explain_widget(f"rev_{eid}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DIFF HELPER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _render_diff(left_label: str, left: str, right_label: str, right: str):
    """Mostra due testi affiancati con righe diverse evidenziate in rosso."""
    def norm_lines(text: str) -> list[str]:
        return [l.strip() for l in text.strip().splitlines()] if text.strip() else []

    ll = norm_lines(left)
    rl = norm_lines(right)
    n  = max(len(ll), len(rl), 1)

    rows = []
    for i in range(n):
        lv = ll[i] if i < len(ll) else ""
        rv = rl[i] if i < len(rl) else ""
        same = (lv == rv)
        bg   = "rgba(74,222,128,0.07)"  if same else "rgba(248,113,113,0.13)"
        bdr  = "#4ade80"                if same else "#f87171"
        mark = "✓"                      if same else "✗"
        mc   = "#4ade80"                if same else "#f87171"
        esc  = lambda t: t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        dash = "<em style='color:#4b5563'>—</em>"
        rows.append(f"""<tr style="border-bottom:1px solid #1e2840;">
  <td style="padding:4px 10px;font-family:monospace;font-size:0.85rem;color:#e2e8f0;
             background:{bg};border-left:3px solid {bdr};width:46%;">{esc(lv) if lv else dash}</td>
  <td style="padding:4px 6px;text-align:center;color:{mc};font-weight:bold;font-size:0.8rem;">{mark}</td>
  <td style="padding:4px 10px;font-family:monospace;font-size:0.85rem;color:#e2e8f0;
             background:{bg};border-left:3px solid {bdr};width:46%;">{esc(rv) if rv else dash}</td>
</tr>""")

    st.markdown(f"""
<table style="width:100%;border-collapse:collapse;background:#0d0d1a;
              border:1px solid #1e2840;border-radius:8px;overflow:hidden;margin-top:8px;">
  <thead><tr style="background:#12122a;">
    <th style="padding:8px 10px;color:#94a3b8;text-align:left;font-size:0.78rem;font-weight:600;">{left_label}</th>
    <th style="width:28px;"></th>
    <th style="padding:8px 10px;color:#94a3b8;text-align:left;font-size:0.78rem;font-weight:600;">{right_label}</th>
  </tr></thead>
  <tbody>{"".join(rows)}</tbody>
</table>""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STUDY VIEW
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@st.cache_data
def _load_soluzioni():
    """Soluzioni canoniche complete (chiave 'modulo#idx'). Vuoto se assente."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "soluzioni.json")
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def soluzione_completa(m, j, ex):
    """Soluzione di riferimento per un esercizio: voce in soluzioni.json,
    oppure l'hint se è già un programma completo. None se non disponibile."""
    return _load_soluzioni().get(f"{m['id']}#{j}") or ex.get("hint")

@st.cache_data
def _load_criteri():
    """Descrizioni in italiano del criterio di successo (chiave 'modulo#idx')."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "criteri.json")
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def render_study(idx):
    m = CURRICULUM[idx]
    done_n, tot = module_progress(idx)
    s = st.session_state.save

    st.markdown(f"# {m['icon']} {m['title']}")
    st.caption(f"{m['world']} · {done_n}/{tot} esercizi completati")

    tab_t, tab_e, tab_c, tab_a, tab_ex = st.tabs(["📖 Teoria", "▶️ Esempio", "🧠 Concetti", "🎯 Approccio", "✏️ Esercizi"])

    with tab_t:
        st.markdown(m["teoria"])

    with tab_e:
        if HAS_ACE:
            st.caption("Editor con syntax highlighting. Premi **Esegui** quando sei pronto.")
        else:
            st.caption("Modifica il codice e premi Esegui.")
        ek = f"es_{m['id']}"
        code = code_editor(
            st.session_state.codice.get(ek, m["esempio"]),
            key=f"ace_es_{m['id']}", height=220
        )
        st.session_state.codice[ek] = code
        _ek = f"es_{m['id']}"
        if st.button("▶️ Esegui", key=f"run_es_{m['id']}"):
            out, err, _ = run_code(code)
            if err:
                explanation = explain_error(err)
                st.error("**Errore:**")
                if explanation:
                    st.warning(explanation)
                st.code(err, language="")
                st.session_state[f"_ec_{_ek}"] = (code, err)
                st.session_state.pop(f"_ea_{_ek}", None)
            else:
                st.success("Output:")
                st.code(out or "(nessun output)", language="")
                st.session_state.pop(f"_ec_{_ek}", None)
                st.session_state.pop(f"_ea_{_ek}", None)
        _ai_explain_widget(_ek)

    with tab_c:
        c = CONCETTI.get(m["id"])
        if not c:
            st.info("Concetti in arrivo per questo modulo.")
        else:
            st.markdown("### 🎭 L'Analogia")
            st.info(c["analogia"])

            st.markdown("### 🤔 Il Perché")
            st.markdown(c["perche"])

            st.markdown("### ⚠️ Errori Comuni")
            for err_item in c["errori_comuni"]:
                with st.expander(err_item["titolo"]):
                    st.markdown(err_item["testo"])
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**❌ Sbagliato**")
                        st.code(err_item["codice_sbagliato"], language="python")
                    with col2:
                        st.markdown("**✅ Giusto**")
                        st.code(err_item["codice_giusto"], language="python")

            st.markdown("### ✅ Quando Usarlo")
            st.success(c["quando_usarlo"])

    with tab_a:
        ap = APPROCCIO.get(m["id"])
        if not ap:
            st.info("Contenuto in arrivo per questo modulo.")
        else:
            st.markdown(f"""
<div style="background:rgba(74,222,128,0.07);border:1px solid #4ade80;border-radius:12px;
            padding:16px 20px;margin-bottom:20px;">
  <div style="font-size:0.8rem;color:#4ade80;font-weight:600;margin-bottom:6px;">DOMANDA CHIAVE</div>
  <div style="font-size:1.05rem;color:#e2e8f0;font-style:italic;">"{ap['domanda_chiave']}"</div>
</div>
""", unsafe_allow_html=True)

            st.markdown("### ❓ Prima di scrivere codice, chiediti:")
            for q in ap["prima_di_codificare"]:
                st.markdown(f"- {q}")

            st.markdown("### 🔄 Pattern da riconoscere")
            for p in ap["pattern"]:
                st.markdown(f"- {p}")

            st.markdown("### ✅ Checklist — verifica la tua soluzione")
            for item in ap["checklist"]:
                st.markdown(f"- [ ] {item}")

            st.markdown("---")
            st.caption("Torna qui ogni volta che ti blocchi: spesso la risposta è in una di queste domande.")

    with tab_ex:
        for j, ex in enumerate(m["esercizi"]):
            eid = f"{m['id']}_{j}"
            done_ex = eid in s["completati"]
            tipo = ex.get("tipo", "normale")
            is_boss = "🏆" in ex.get("testo", "")
            due = days_until_review(eid)

            if tipo == "predict":
                label_prefix = "✅ " if done_ex else "🔍 "
                label = label_prefix + f"Esercizio {j+1} — PREVEDI"
            elif tipo == "debug":
                label_prefix = "✅ " if done_ex else "🐛 "
                label = label_prefix + f"Esercizio {j+1} — DEBUG"
            else:
                label = ("✅ " if done_ex else "🏆 " if is_boss else "📝 ")
                label += f"Esercizio {j+1}"
                if is_boss:
                    label += " — BOSS"
            if done_ex and due == 0:
                label += " 📅"

            with st.expander(label, expanded=not done_ex):
                # ── Predict exercise ──────────────────────────────────
                if tipo == "predict":
                    st.markdown("""
<div style="background:rgba(56,189,248,0.07);border:1px solid #38bdf8;
            border-radius:8px;padding:10px 14px;margin-bottom:10px;">
  🔍 <b>Leggi il codice</b> — scrivi la tua previsione, poi rivela l'output
</div>
""", unsafe_allow_html=True)
                    st.info(ex["testo"])
                    st.code(ex["codice"], language="python")
                    pred_key = f"pred_{eid}"
                    if pred_key not in st.session_state:
                        st.session_state[pred_key] = ""
                    pred = st.text_area(
                        "✏️ Cosa stamperà? (scrivi riga per riga)",
                        value=st.session_state[pred_key],
                        height=100, key=f"ta_pred_{eid}",
                        placeholder="es:\n10\n99",
                    )
                    st.session_state[pred_key] = pred
                    cp1, cp2 = st.columns(2)
                    with cp1:
                        if st.button("🔍 Rivela output", key=f"run_{eid}"):
                            actual, aerr, _ = run_code(ex["codice"])
                            if aerr:
                                st.error(aerr)
                            else:
                                def _norm(t: str) -> str:
                                    return "\n".join(l.strip() for l in t.strip().splitlines())
                                correct = (_norm(pred) == _norm(actual)) or (ex["expected"].strip() in actual)
                                _render_diff("Output reale", actual, "La tua previsione", pred)
                                if eid not in s["completati"]:
                                    xp = XP_VALS["esercizio"] + ex.get("xp_bonus", 0) if correct else 5
                                    award_xp(xp, f"predict {m['title']}")
                                    s["completati"].append(eid)
                                    s.setdefault("completed_dates", {})[eid] = str(date.today())
                                    st.session_state.session_completati.append(eid)
                                    check_badges()
                                    persist()
                                if correct:
                                    st.success("🎯 Previsione corretta! Sai leggere il codice.")
                                    if eid in s["completati"]:
                                        st.rerun()
                                else:
                                    st.warning("Non esatto — le righe rosse mostrano dove differisce.")
                    with cp2:
                        if st.button("💡 Hint", key=f"hint_{eid}"):
                            st.info(f"💡 {ex['hint']}")
                    continue

                # ── Debug / Normal exercise ───────────────────────────
                if tipo == "debug":
                    st.markdown("""
<div style="background:rgba(248,113,113,0.07);border:1px solid #f87171;
            border-radius:8px;padding:10px 14px;margin-bottom:10px;">
  🐛 <b>Bug Hunt</b> — trova e correggi il bug nel codice
</div>
""", unsafe_allow_html=True)
                elif is_boss:
                    st.markdown(f"""
<div style="background:rgba(245,158,11,0.08);border:1px solid #d97706;
            border-radius:8px;padding:10px 14px;margin-bottom:10px;">
  🏆 <b>Boss Challenge</b> — XP extra per completamento
</div>
""", unsafe_allow_html=True)
                if done_ex and due == 0:
                    st.info("📅 Questo esercizio è in scadenza per ripasso oggi!")

                st.info(ex["testo"])

                # Criterio di verifica (come un mini-test): cosa deve fare l'output.
                criterio = _load_criteri().get(f"{m['id']}#{j}")
                with st.expander("🧪 Come viene valutato"):
                    if criterio:
                        st.caption(f"✓ {criterio}")
                    else:
                        st.caption("✓ Il tuo codice viene eseguito e l'output confrontato "
                                   "con la condizione di successo dell'esercizio. Premi "
                                   "Esegui per verificare.")

                attempts = s["attempts"].get(eid, 0)
                if attempts > 0:
                    st.caption(f"Tentativi: {attempts}")

                ck = f"ace_{eid}"
                code_ex = code_editor(
                    st.session_state.codice.get(ck, ex["placeholder"]),
                    key=ck, height=160
                )
                st.session_state.codice[ck] = code_ex

                c1, c2 = st.columns(2)
                with c1:
                    if st.button("▶️ Esegui e verifica", key=f"run_{eid}"):
                        out, err, lv = run_code(code_ex)
                        s["attempts"][eid] = s["attempts"].get(eid, 0) + 1
                        persist()

                        if err:
                            explanation = explain_error(err)
                            st.error("**Errore nel codice**")
                            if explanation:
                                st.warning(explanation)
                            st.code(err, language="")
                            st.session_state[f"_ec_{eid}"] = (code_ex, err)
                            st.session_state.pop(f"_ea_{eid}", None)
                        else:
                            st.session_state.pop(f"_ec_{eid}", None)
                            st.session_state.pop(f"_ea_{eid}", None)
                            if out:
                                st.code(out, language="")
                            try:
                                ok = ex["check"](out, err, lv)
                            except Exception:
                                ok = False

                            if ok and eid not in s["completati"]:
                                xp_total = XP_VALS["esercizio"] + ex.get("xp_bonus", 0)
                                is_first = s["attempts"][eid] == 1
                                used_hint = eid in s.get("hints_used", [])

                                award_xp(xp_total, f"{m['title']} #{j+1}")
                                if is_first:
                                    award_xp(XP_VALS["first_try"], "primo tentativo!")
                                    s["first_try_count"] = s.get("first_try_count", 0) + 1
                                if not used_hint:
                                    award_xp(XP_VALS["no_hint"], "senza hint")

                                s["completati"].append(eid)
                                s.setdefault("completed_dates", {})[eid] = str(date.today())
                                st.session_state.session_completati.append(eid)

                                mod_keys = [f"{m['id']}_{jj}" for jj in range(len(m["esercizi"]))]
                                if all(k in s["completati"] for k in mod_keys):
                                    if m["id"] not in s.get("modules_completed", []):
                                        s.setdefault("modules_completed", []).append(m["id"])
                                        award_xp(XP_VALS["modulo"], f"modulo '{m['title']}' completato!")

                                check_badges()
                                persist()

                                st.success(random.choice(MESSAGGI_OK))
                                if is_first:
                                    st.toast("⚡ First Try! +10 XP bonus", icon="⚡")
                                for bid in st.session_state.new_badges:
                                    icon, name, _ = BADGES[bid]
                                    st.toast(f"{icon} Badge: **{name}**!", icon=icon)
                                st.session_state.new_badges = []
                                if st.session_state.level_up:
                                    st.balloons()
                                    st.toast(f"🎉 LEVEL UP! {st.session_state.level_up}", icon="🎉")
                                    st.session_state.level_up = None
                                if random.random() < 0.35:
                                    st.info(random.choice(TIPS))
                                st.rerun()

                            elif ok and eid in s["completati"]:
                                st.success("✅ Già completato! Ottimo ripasso.")
                                if due == 0:
                                    mark_reviewed(eid)
                                    st.toast("📅 Ripasso registrato!", icon="📅")
                            else:
                                fb = ex.get("feedback")
                                msg = fb(out, err) if fb else random.choice(MESSAGGI_RETRY)
                                st.warning(msg)
                                epm = s.setdefault("errori_per_modulo", {})
                                epm[m["id"]] = epm.get(m["id"], 0) + 1
                                persist()

                with c2:
                    if st.button("💡 Hint", key=f"hint_{eid}"):
                        if eid not in s.get("hints_used", []):
                            s.setdefault("hints_used", []).append(eid)
                            persist()
                        st.info(f"💡 {ex['hint']}")
                _ai_explain_widget(eid)

                # Soluzione di riferimento: disponibile dopo aver risolto
                # o dopo aver chiesto un hint (per non spoilerare subito).
                sol = soluzione_completa(m, j, ex)
                if sol and (done_ex or eid in s.get("hints_used", [])):
                    with st.expander("✅ Soluzione completa"):
                        st.code(sol, language="python")

        # ── AI Exercises ──────────────────────────────────────────────
        st.divider()
        st.markdown("### 🤖 Esercizi generati dall'AI")

        backend, _ = detect_ai_backend()
        if not backend:
            st.info(
                "Per abilitare gli esercizi AI (gratis):\n\n"
                "**Opzione 1 — Groq** (account free, 6000 chiamate/giorno):\n"
                "1. Registrati su [console.groq.com](https://console.groq.com)\n"
                "2. Crea una API key gratuita\n"
                "3. Aggiungila in `.streamlit/secrets.toml`:\n"
                "```toml\nGROQ_API_KEY = \"gsk_...\"\n```\n\n"
                "**Opzione 2 — Ollama** (100% locale, nessun account):\n"
                "```bash\ncurl -fsSL https://ollama.com/install.sh | sh\n"
                "ollama pull llama3.2\n```"
            )
        else:
            ai_key = f"ai_ex_{m['id']}"
            if ai_key not in st.session_state:
                st.session_state[ai_key] = []

            if st.button("✨ Genera esercizio", key=f"gen_{m['id']}", type="primary"):
                with st.spinner("Sto generando un esercizio..."):
                    ex_ai = generate_ai_exercise(m["title"])
                if ex_ai:
                    st.session_state[ai_key].append(ex_ai)
                    st.rerun()
                else:
                    st.error("Generazione fallita — controlla la connessione o la chiave API.")

            for ai_idx, ai_ex in enumerate(reversed(st.session_state[ai_key])):
                real_idx = len(st.session_state[ai_key]) - 1 - ai_idx
                eid_ai = f"ai_{m['id']}_{real_idx}"
                with st.expander(f"🤖 Esercizio AI #{real_idx + 1}", expanded=(ai_idx == 0)):
                    st.info(ai_ex["testo"])
                    code_ai = code_editor(
                        st.session_state.codice.get(eid_ai, ai_ex["placeholder"]),
                        key=f"ace_{eid_ai}", height=160,
                    )
                    st.session_state.codice[eid_ai] = code_ai

                    ca1, ca2, ca3 = st.columns(3)
                    with ca1:
                        if st.button("▶️ Verifica", key=f"run_{eid_ai}"):
                            out, err, _ = run_code(code_ai)
                            if err:
                                exp = explain_error(err)
                                st.error("**Errore:**")
                                if exp:
                                    st.warning(exp)
                                st.code(err, language="")
                                st.session_state[f"_ec_{eid_ai}"] = (code_ai, err)
                                st.session_state.pop(f"_ea_{eid_ai}", None)
                            else:
                                st.session_state.pop(f"_ec_{eid_ai}", None)
                                st.session_state.pop(f"_ea_{eid_ai}", None)
                                if out:
                                    st.code(out, language="")
                                if ai_ex["expected"].strip() in out:
                                    st.success("✅ Corretto! +10 XP")
                                    award_xp(10, f"AI esercizio {m['title']}")
                                    persist()
                                else:
                                    st.warning(f"⚠️ L'output deve contenere: `{ai_ex['expected']}`")
                    with ca2:
                        if st.button("💡 Hint", key=f"hint_{eid_ai}"):
                            st.info(f"💡 {ai_ex['hint']}")
                    with ca3:
                        if st.button("👁️ Soluzione", key=f"sol_{eid_ai}"):
                            st.code(ai_ex["soluzione"], language="python")
                    _ai_explain_widget(eid_ai)

    st.divider()
    p, _, n = st.columns([1, 3, 1])
    with p:
        if idx > 0 and st.button("← Precedente", use_container_width=True):
            st.session_state.modulo_idx = idx - 1
            st.rerun()
    with n:
        if idx < len(CURRICULUM) - 1:
            next_ok = is_unlocked(idx + 1)
            if st.button("Prossimo →", use_container_width=True,
                         type="primary", disabled=not next_ok):
                st.session_state.modulo_idx = idx + 1
                st.rerun()
            if not next_ok:
                st.caption("Completa tutti gli esercizi per sbloccare")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BADGES VIEW
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def render_badges():
    s = st.session_state.save
    earned = set(s["badges"])
    st.markdown("# 🏅 Badge")
    st.caption(f"Sbloccati: {len(earned)} / {len(BADGES)}")

    cols = st.columns(3)
    for i, (bid, (icon, name, desc)) in enumerate(BADGES.items()):
        got = bid in earned
        border = "#f59e0b" if got else "#2d3748"
        bg     = "rgba(245,158,11,0.1)" if got else "rgba(0,0,0,0.2)"
        opacity = "1" if got else "0.4"
        check  = "✅ Sbloccato" if got else "🔒 Non ancora"
        cols[i % 3].markdown(f"""
<div style="background:{bg};border:1px solid {border};border-radius:12px;
            padding:20px;text-align:center;margin-bottom:12px;opacity:{opacity};">
  <div style="font-size:2.5rem;">{icon}</div>
  <div style="font-weight:700;color:#e2e8f0;margin:6px 0 4px;">{name}</div>
  <div style="font-size:0.78rem;color:#94a3b8;">{desc}</div>
  <div style="margin-top:8px;font-size:0.78rem;color:{'#f59e0b' if got else '#4a5568'};">{check}</div>
</div>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STATS VIEW
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def render_stats():
    s = st.session_state.save
    lvl, title, color, progress, xp_to_next = get_level_info(s["xp"])
    tot_all  = sum(len(m["esercizi"]) for m in CURRICULUM)
    done_all = len(s["completati"])

    st.markdown("# 📊 Statistiche")

    c1, c2, c3, c4 = st.columns(4)
    def stat_card(col, emoji, val, label, color="#4ade80"):
        col.markdown(f"""
<div style="background:#0f0f22;border:1px solid #1e2840;border-radius:10px;
            padding:18px;text-align:center;">
  <div style="font-size:2rem;">{emoji}</div>
  <div style="font-size:1.6rem;font-weight:800;color:{color};">{val}</div>
  <div style="font-size:0.78rem;color:#64748b;">{label}</div>
</div>""", unsafe_allow_html=True)

    stat_card(c1, "⭐", s["xp"],              "XP totali",         "#f59e0b")
    stat_card(c2, "🔥", s["streak"],           "streak giorni",     "#f97316")
    stat_card(c3, "✅", f"{done_all}/{tot_all}","esercizi",         "#4ade80")
    stat_card(c4, "🏅", len(s["badges"]),      f"badge/{len(BADGES)}", "#a78bfa")

    st.markdown("")
    st.markdown("### Livello")
    st.markdown(f"**{title}** — {s['xp']} XP")
    st.progress(progress)
    if xp_to_next:
        st.caption(f"{xp_to_next} XP al prossimo livello")
    else:
        st.caption("Livello massimo! 🧙")

    st.markdown("### Progresso per modulo")
    for i, m in enumerate(CURRICULUM):
        done, tot = module_progress(i)
        unlocked = is_unlocked(i)
        icon = m["icon"] if unlocked else "🔒"
        st.markdown(f"**{icon} {m['title']}** — {done}/{tot}")
        st.progress(done / tot if tot else 0)

    st.markdown("### Ripasso (Spaced Repetition)")
    mastered, pending, not_started = 0, 0, 0
    for m in CURRICULUM:
        for j in range(len(m["esercizi"])):
            eid = f"{m['id']}_{j}"
            d = days_until_review(eid)
            if d is None and eid in s["completati"]:
                mastered += 1
            elif d is not None:
                pending += 1
            elif eid not in s["completati"]:
                not_started += 1

    col1, col2, col3 = st.columns(3)
    stat_card(col1, "🧠", mastered,    "padroneggiati",   "#4ade80")
    stat_card(col2, "📅", pending,     "in ripasso",      "#4299e1")
    stat_card(col3, "🔒", not_started, "non ancora fatti","#64748b")

    if s.get("first_try_count", 0):
        st.markdown(f"**⚡ First-try perfetti:** {s['first_try_count']}")
    if s.get("best_streak", 0):
        st.markdown(f"**🔥 Streak record:** {s['best_streak']} giorni")
    if HAS_ACE:
        st.markdown("**🎨 Editor:** Ace (syntax highlighting attivo)")

    st.markdown("### 🎯 I tuoi punti deboli")
    errori = s.get("errori_per_modulo", {})
    if not errori:
        st.caption("Nessun errore registrato — continua ad esercitarti!")
    else:
        titoli = {m["id"]: f"{m['icon']} {m['title']}" for m in CURRICULUM}
        ordinati = sorted(errori.items(), key=lambda x: x[1], reverse=True)
        max_err = ordinati[0][1]
        for mid, count in ordinati:
            nome = titoli.get(mid, mid)
            pct = int((count / max_err) * 100)
            st.markdown(f"""
<div style="margin-bottom:10px;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
    <span style="color:#e2e8f0;font-size:0.88rem;">{nome}</span>
    <span style="color:#f87171;font-size:0.85rem;font-weight:600;">{count} ✗</span>
  </div>
  <div style="background:#1a1a3a;border-radius:4px;height:6px;">
    <div style="width:{pct}%;background:#f87171;height:100%;border-radius:4px;"></div>
  </div>
</div>""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GUIDA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def render_guida():
    st.markdown("# 📖 Guida del Corso")

    tab_traceback, tab_pensiero, tab_percorso, tab_glossario = st.tabs([
        "🔍 Leggere gli Errori",
        "🧠 Pensare da Programmatore",
        "🗺️ Il Percorso",
        "📚 Glossario",
    ])

    with tab_traceback:
        st.markdown("## Come leggere un errore Python")
        st.markdown("""
Quando il codice va storto, Python ti dà un **traceback**. La maggior parte dei principianti lo legge dall'alto — sbagliato. **Leggi sempre dall'ultima riga in su.**

```
Traceback (most recent call last):
  File "script.py", line 12, in <module>   ←  dove è successo
    print(nome_bucket)                      ←  la riga esatta
NameError: name 'nome_bucket' is not defined  ←  LEGGI QUESTA PRIMA
```

**Anatomia dell'errore:**
| Parte | Significato |
|-------|-------------|
| `Traceback (most recent call last)` | Sta per arrivare l'errore |
| `File "...", line N` | Dove nel codice è successo |
| La riga di codice | Esattamente cosa stava eseguendo |
| `TipoErrore: messaggio` | **Cosa è andato storto** — leggi qui per primo |

---

### Gli errori più comuni e cosa significano
""")
        for tipo, spieg in ERROR_EXPLANATIONS.items():
            if tipo == "TimeoutExpired":
                continue
            with st.expander(f"`{tipo}`"):
                st.markdown(spieg)
                if tipo == "NameError":
                    st.code("# Causa più comune:\nprint(x)  # x non è ancora definita\n\n# Fix:\nx = 42\nprint(x)", language="python")
                elif tipo == "IndentationError":
                    st.code("# Sbagliato:\nif True:\nprint('ciao')  # IndentationError\n\n# Giusto:\nif True:\n    print('ciao')", language="python")
                elif tipo == "KeyError":
                    st.code("# Sbagliato:\nd = {'nome': 'Lorenzo'}\nprint(d['eta'])  # KeyError\n\n# Giusto:\nprint(d.get('eta', 'N/A'))", language="python")

    with tab_pensiero:
        st.markdown("## Come pensare da programmatore")
        st.markdown("""
La programmazione non è memorizzare sintassi — è **scomporre problemi**.

---

### Il metodo in 5 passi

**1. Capisci l'input e l'output**
Prima di scrivere una riga, chiediti: *cosa ho? cosa voglio ottenere?*
```
Ho: una lista di istanze EC2 con stato e costo orario
Voglio: un report con il costo totale delle istanze running
```

**2. Scomponi in passi piccoli**
```
Passo 1: filtra solo le istanze "running"
Passo 2: per ognuna calcola il costo mensile
Passo 3: somma tutto
Passo 4: stampa il report
```

**3. Scrivi il codice per un passo alla volta**
Non cercare di scrivere tutto in una volta. Scrivi il passo 1, testalo, poi vai al passo 2.

**4. Testa con dati semplici prima**
```python
# Prima testa con 2 istanze fake, non 500 reali
istanze_test = [
    {"id": "i-001", "stato": "running", "costo_ora": 0.10},
    {"id": "i-002", "stato": "stopped", "costo_ora": 0.05},
]
```

**5. Gestisci i casi d'errore**
Cosa succede se la lista è vuota? Se la chiave non esiste? Se la rete cade?

---

### Regole d'oro
- **DRY** — Don't Repeat Yourself. Se copi-incolli, fai una funzione.
- **KISS** — Keep It Simple. La soluzione più semplice che funziona è la migliore.
- **Nomi che parlano** — `lista` è un cattivo nome. `istanze_running_eu` è un buon nome.
- **Testa spesso** — un passo alla volta, non tutto alla fine.
- **Gli errori sono normali** — ogni programmatore, anche senior, ha errori. La differenza è quanto velocemente li risolve.
""")

    with tab_percorso:
        st.markdown("## Come si connettono i moduli")
        st.markdown("""
Questo corso non è una lista di argomenti casuali — è una **progressione**.
Ogni modulo ti dà uno strumento che userai nei successivi.
""")
        percorso = [
            ("📦", "Variabili",        "Salvi Access Key, nomi bucket, regioni"),
            ("✏️", "Stringhe",         "Manipoli ARN, tag, log, nomi risorse"),
            ("🔀", "Condizioni",        "Decidi: il bucket esiste? L'istanza è running?"),
            ("🔁", "Cicli",            "Iteri su 100 istanze come su 1"),
            ("⚙️", "Funzioni",         "Organizzi il codice in blocchi riutilizzabili"),
            ("📋", "Liste e Dict",      "Navighi le risposte JSON di boto3"),
            ("🤖", "Automazione",       "Leggi config, salvi report, gestisci file"),
            ("☁️", "boto3",            "Metti tutto insieme: automazione AWS reale"),
        ]
        for i, (icon, titolo, uso_boto3) in enumerate(percorso):
            connettore = "↓" if i < len(percorso) - 1 else "🎯"
            st.markdown(f"""
<div style="background:#0f0f22;border:1px solid #1e2840;border-radius:10px;
            padding:14px 18px;margin-bottom:4px;display:flex;align-items:center;gap:16px;">
  <span style="font-size:1.8rem;">{icon}</span>
  <div>
    <div style="font-weight:700;color:#e2e8f0;">{titolo}</div>
    <div style="font-size:0.82rem;color:#64748b;">In boto3: {uso_boto3}</div>
  </div>
</div>
<div style="text-align:center;color:#4ade80;font-size:1.2rem;margin:2px 0;">{connettore}</div>
""", unsafe_allow_html=True)

        st.markdown("""
---
### Cosa sai fare alla fine del corso

- Leggere e scrivere Python da zero
- Navigare risposte JSON complesse (come quelle di boto3)
- Scrivere funzioni riutilizzabili per operazioni AWS
- Iterare su liste di risorse cloud
- Salvare report e leggere configurazioni da file
- Filtrare, calcolare, automatizzare con Python
- Scrivere i tuoi primi script boto3 reali
""")

    with tab_glossario:
        st.markdown("## Glossario Python & AWS")
        st.markdown("Tutti i termini tecnici spiegati in italiano semplice.")
        st.markdown("")

        cerca = st.text_input("🔍 Cerca un termine...", placeholder="es. dizionario, ARN, return...")
        termini_filtrati = [
            (t, d) for t, d in GLOSSARIO
            if not cerca or cerca.lower() in t.lower() or cerca.lower() in d.lower()
        ]

        if not termini_filtrati:
            st.warning("Nessun termine trovato.")
        else:
            for i in range(0, len(termini_filtrati), 2):
                c1, c2 = st.columns(2)
                for col, idx in [(c1, i), (c2, i+1)]:
                    if idx < len(termini_filtrati):
                        termine, desc = termini_filtrati[idx]
                        col.markdown(f"""
<div style="background:#0f0f22;border:1px solid #1e2840;border-radius:8px;
            padding:12px 16px;margin-bottom:8px;">
  <div style="font-weight:700;color:#4ade80;font-family:monospace;">{termine}</div>
  <div style="font-size:0.82rem;color:#94a3b8;margin-top:4px;">{desc}</div>
</div>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PROGETTO FINALE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def render_progetto_finale():
    s = st.session_state.save
    tot_all  = sum(len(m["esercizi"]) for m in CURRICULUM)
    done_all = len(s["completati"])
    sbloccato = done_all >= tot_all // 2  # sbloccato dopo metà corso

    st.markdown("# 🎓 Progetto Finale — AWS Cost Monitor")

    if not sbloccato:
        st.warning(f"Completa almeno metà degli esercizi ({tot_all // 2}/{tot_all}) per sbloccare il progetto finale.")
        st.progress(done_all / tot_all)
        return

    st.markdown("""
Costruisci un **AWS Cost Monitor** — uno script completo che usa tutto quello che hai imparato.

> Variabili · Stringhe · Condizioni · Cicli · Funzioni · Liste/Dict · File · boto3 (simulato)

Il progetto è diviso in **4 step progressivi**. Ogni step si appoggia al precedente.
""")

    prog_key = "progetto_steps_done"
    steps_done = s.get(prog_key, [])

    for i, step in enumerate(PROGETTO_STEPS):
        done = i in steps_done
        prev_done = i == 0 or (i - 1) in steps_done

        label = ("✅ " if done else "🔒 " if not prev_done else "🔨 ") + step["titolo"]
        with st.expander(label, expanded=(not done and prev_done)):
            if not prev_done:
                st.info("Completa lo step precedente per sbloccare questo.")
                continue

            st.markdown(f"**Obiettivo:** {step['descrizione']}")
            st.markdown("**Istruzioni:**")
            st.markdown(step["istruzioni"])

            pk = f"progetto_{i}"
            code = code_editor(
                st.session_state.codice.get(pk, step["placeholder"]),
                key=pk, height=220
            )
            st.session_state.codice[pk] = code

            c1, c2 = st.columns(2)
            with c1:
                if st.button("▶️ Esegui e verifica", key=f"prog_run_{i}"):
                    out, err, lv = run_code(code)
                    if err:
                        explanation = explain_error(err)
                        st.error("**Errore:**")
                        if explanation:
                            st.warning(explanation)
                        st.code(err, language="")
                        st.session_state[f"_ec_prog_{i}"] = (code, err)
                        st.session_state.pop(f"_ea_prog_{i}", None)
                    else:
                        st.session_state.pop(f"_ec_prog_{i}", None)
                        st.session_state.pop(f"_ea_prog_{i}", None)
                        if out:
                            st.code(out, language="")
                        try:
                            ok = step["check"](out, err, lv)
                        except Exception:
                            ok = False
                        if ok:
                            if i not in steps_done:
                                steps_done.append(i)
                                s[prog_key] = steps_done
                                award_xp(30, f"Progetto Step {i+1}")
                                persist()
                                if len(steps_done) == len(PROGETTO_STEPS):
                                    st.balloons()
                                    st.toast("🎓 Progetto completato! Sei un Cloud Developer!", icon="🎓")
                            st.success("✅ Step completato!")
                            st.rerun()
                        else:
                            st.warning("Non ancora corretto — ricontrolla le istruzioni.")
            with c2:
                if st.button("💡 Hint", key=f"prog_hint_{i}"):
                    st.info(f"💡 {step['hint']}")
            _ai_explain_widget(f"prog_{i}")

    done_count = len(steps_done)
    if done_count > 0:
        st.divider()
        st.markdown(f"**Progresso progetto: {done_count}/{len(PROGETTO_STEPS)} step completati**")
        st.progress(done_count / len(PROGETTO_STEPS))
        if done_count == len(PROGETTO_STEPS):
            st.success("🎓 **Progetto completato!** Hai costruito un AWS Cost Monitor funzionante da zero.")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PLAYGROUND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def render_playground():
    st.markdown("# 🧪 Playground")
    st.caption("Scrivi Python liberamente — nessun check, nessun XP, solo esecuzione.")

    default = st.session_state.get("playground_code", "# Scrivi qui il tuo codice\nprint('Ciao, Python!')")
    code = code_editor(default, key="playground_editor", height=320)
    st.session_state["playground_code"] = code

    if st.button("▶️ Esegui", type="primary", key="playground_run"):
        out, err, _ = run_code(code)
        if err:
            explanation = explain_error(err)
            st.error("**Errore:**")
            if explanation:
                st.warning(explanation)
            st.code(err, language="")
            st.session_state["_ec_playground"] = (code, err)
            st.session_state.pop("_ea_playground", None)
        else:
            st.success("Output:")
            st.code(out or "(nessun output)", language="")
            st.session_state.pop("_ec_playground", None)
            st.session_state.pop("_ea_playground", None)
    _ai_explain_widget("playground")


def main():
    init_state()
    render_sidebar()
    v = st.session_state.view
    if v == "map":
        render_map()
    elif v == "study":
        render_study(st.session_state.modulo_idx)
    elif v == "review":
        render_review()
    elif v == "badges":
        render_badges()
    elif v == "stats":
        render_stats()
    elif v == "guida":
        render_guida()
    elif v == "progetto":
        render_progetto_finale()
    elif v == "playground":
        render_playground()


if __name__ == "__main__":
    main()
