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

CONCETTI = {
    "variabili": {
        "analogia": """
**La variabile è un post-it appiccicato su un valore.**

Immagina di aprire AWS per la prima volta. Hai il tuo Access Key, il nome della regione, il nome del bucket.
Potresti riscriverli ogni volta — oppure metterli su un post-it e usare il post-it.

```python
regione   = "eu-west-1"        # post-it "regione"
bucket    = "mio-bucket-logs"  # post-it "bucket"
max_size  = 500                # post-it "max_size"
```

Python tiene traccia del post-it. Se il valore cambia, aggiorni solo il post-it — il resto del codice non sa nulla di diverso.
""",
        "perche": """
**Perché esistono le variabili?**

1. **Evitare la ripetizione** — se il nome del bucket cambia, lo cambi in un posto solo.
2. **Dare un nome alle cose** — `credito_aws = 150` è più leggibile di `150` sparso nel codice.
3. **Conservare risultati intermedi** — `totale = prezzo * quantita` salva il risultato per usarlo dopo.
4. **Comunicare l'intenzione** — il nome della variabile spiega cosa contiene.

In boto3 userai variabili continuamente:
```python
client    = boto3.client("s3")
risposta  = client.list_buckets()
bucket_id = risposta["Buckets"][0]["Name"]
```
Ogni riga salva qualcosa che serve alla riga successiva.
""",
        "errori_comuni": [
            {
                "titolo": "❌ Confondere = con ==",
                "testo": "`=` **assegna** un valore. `==` **confronta** due valori. Errore classico dentro un `if`.",
                "codice_sbagliato": "if ruolo = 'admin':  # SyntaxError!",
                "codice_giusto":    "if ruolo == 'admin':  # confronto corretto",
            },
            {
                "titolo": "❌ Usare una variabile prima di crearla",
                "testo": "Python legge il codice dall'alto in basso. Se usi `nome` prima di definirlo → `NameError`.",
                "codice_sbagliato": "print(nome)       # NameError\nnome = 'Lorenzo'",
                "codice_giusto":    "nome = 'Lorenzo'  # prima definisci\nprint(nome)       # poi usi",
            },
            {
                "titolo": "❌ Sovrascrivere funzioni built-in",
                "testo": "Evita nomi come `list`, `type`, `input`, `id` — sono funzioni di Python e le sovrascriveresti.",
                "codice_sbagliato": "type = 't3.micro'  # hai distrutto la funzione type()",
                "codice_giusto":    "tipo_istanza = 't3.micro'  # nome descrittivo e sicuro",
            },
        ],
        "quando_usarlo": "Sempre — le variabili sono il mattone base. Ogni valore che usi più di una volta merita una variabile.",
    },

    "stringhe": {
        "analogia": """
**La stringa è un collier di perle — ogni perla è un carattere.**

Puoi contare le perle (`len`), prenderne una (`s[0]`), tagliare il collier (`s[2:5]`),
trasformarlo tutto in oro (`upper()`) o argento (`lower()`).

```python
arn = "arn:aws:s3:::mio-bucket"
#      0123456789...
print(arn[0:3])    # "arn"   → prime 3 perle
print(arn[-6:])    # "bucket" → ultime 6 perle
print(len(arn))    # 24      → quante perle
```

La cosa importante: **le stringhe sono immutabili**. Non puoi cambiare una perla — devi creare un nuovo collier.
""",
        "perche": """
**Perché le stringhe sono così importanti per AWS?**

In AWS quasi tutto è testo: nomi di bucket, ARN, ID di istanze, regioni, tag, messaggi di log.
Sapere manipolare le stringhe significa saper lavorare con le risorse AWS.

Esempi reali:
```python
# Estrarre la regione da un ARN
arn = "arn:aws:ec2:eu-west-1:123456:instance/i-001"
parti   = arn.split(":")
regione = parti[3]   # "eu-west-1"

# Costruire nomi di bucket dinamici
ambiente = "prod"
nome_bucket = f"mio-progetto-{ambiente}-logs"  # "mio-progetto-prod-logs"

# Filtrare log per parola chiave
linea = "2024-01-15 ERROR: connection timeout"
if "ERROR" in linea:
    print(f"Problema trovato: {linea}")
```
""",
        "errori_comuni": [
            {
                "titolo": "❌ Modificare una stringa in-place",
                "testo": "Le stringhe sono immutabili. Per 'modificarle' crei sempre una nuova stringa.",
                "codice_sbagliato": 's = "hello"\ns[0] = "H"  # TypeError!',
                "codice_giusto":    's = "hello"\ns = "H" + s[1:]  # "Hello"',
            },
            {
                "titolo": "❌ Dimenticare le virgolette",
                "testo": "Senza virgolette, Python pensa che sia un nome di variabile, non testo.",
                "codice_sbagliato": "regione = eu-west-1   # NameError (o errore matematica)",
                "codice_giusto":    'regione = "eu-west-1"  # stringa corretta',
            },
            {
                "titolo": "❌ Concatenare stringa e numero",
                "testo": "Non puoi unire direttamente testo e numero con `+`. Usa f-string.",
                "codice_sbagliato": 'print("Costo: " + 42)      # TypeError',
                "codice_giusto":    'print(f"Costo: {42}")       # oppure str(42)',
            },
        ],
        "quando_usarlo": "Ogni volta che lavori con testo: nomi di risorse, log, messaggi, ARN, tag AWS, output da formattare.",
    },

    "condizioni": {
        "analogia": """
**Il codice è come un semaforo: prende decisioni.**

Senza condizioni, il codice fa sempre la stessa cosa — come un robot che non guarda dove va.
Con le condizioni, il codice *reagisce* alla realtà.

```python
credito_aws = 12  # EUR rimasti

if credito_aws < 10:
    print("🚨 Ricarica subito!")
elif credito_aws < 50:
    print("⚠️  Credito in esaurimento")
else:
    print("✅ Tutto ok")
```

Python legge la condizione, decide quale ramo prendere, esegue solo quello.
Gli altri rami non vengono eseguiti.
""",
        "perche": """
**Perché le condizioni sono essenziali nell'automazione AWS?**

Un script boto3 deve *decidere*:
- Il bucket esiste già? → salta la creazione
- L'istanza è stopped? → avviala, altrimenti lasciala stare
- Il costo supera la soglia? → manda un alert

```python
stato = istanza["State"]["Name"]

if stato == "stopped":
    ec2.start_instances(InstanceIds=[istanza["InstanceId"]])
    print(f"Avviata {istanza['InstanceId']}")
elif stato == "running":
    print("Già in esecuzione, skip")
else:
    print(f"Stato inaspettato: {stato}")
```

Senza `if`, lo script farebbe sempre la stessa cosa — inutile per l'automazione reale.
""",
        "errori_comuni": [
            {
                "titolo": "❌ Dimenticare i due punti",
                "testo": "Ogni `if`, `elif`, `else` deve finire con `:`. È la sintassi di Python.",
                "codice_sbagliato": "if x > 0\n    print(x)  # SyntaxError",
                "codice_giusto":    "if x > 0:\n    print(x)",
            },
            {
                "titolo": "❌ Indentazione sbagliata",
                "testo": "Il blocco dentro l'if deve essere indentato di 4 spazi. Python usa gli spazi per capire i confini.",
                "codice_sbagliato": "if x > 0:\nprint(x)    # IndentationError",
                "codice_giusto":    "if x > 0:\n    print(x)  # 4 spazi",
            },
            {
                "titolo": "❌ Usare = invece di ==",
                "testo": "`=` assegna, `==` confronta. Dentro un `if` vuoi confrontare.",
                "codice_sbagliato": 'if stato = "running":  # SyntaxError',
                "codice_giusto":    'if stato == "running":',
            },
        ],
        "quando_usarlo": "Ogni volta che il comportamento del codice deve cambiare in base a una condizione. In boto3: controllo stati, soglie, esistenza di risorse.",
    },

    "cicli": {
        "analogia": """
**Il for loop è un operaio su un nastro trasportatore.**

Ogni oggetto sul nastro (la lista) viene preso, lavorato, rimesso giù — uno alla volta, senza che tu debba dire "adesso il secondo, adesso il terzo".

```python
bucket_list = ["logs", "backup", "data", "archive"]

for bucket in bucket_list:          # prende uno alla volta
    print(f"Controllo: {bucket}")   # lo lavora
                                    # poi passa al prossimo
```

Con 4 bucket o 400, il codice è identico. **Questa è la potenza dei cicli.**
""",
        "perche": """
**Perché i cicli sono il cuore dell'automazione AWS?**

boto3 ti restituisce sempre liste:
- Lista di bucket S3
- Lista di istanze EC2
- Lista di log CloudWatch
- Lista di snapshot EBS

Senza for loop, dovresti scrivere 100 righe per 100 istanze. Con il for, scrivi 3 righe per qualsiasi numero.

```python
# Ferma TUTTE le istanze running in una regione
for res in ec2.describe_instances()["Reservations"]:
    for ist in res["Instances"]:
        if ist["State"]["Name"] == "running":
            ec2.stop_instances(InstanceIds=[ist["InstanceId"]])
            print(f"Fermata: {ist['InstanceId']}")
```

Questo script funziona con 1 istanza o con 1000. Non cambia nulla.
""",
        "errori_comuni": [
            {
                "titolo": "❌ range(10) non va da 1 a 10",
                "testo": "`range(10)` genera 0,1,2,...,9. Per 1-10 usa `range(1, 11)`.",
                "codice_sbagliato": "for i in range(10):\n    print(i)  # stampa 0..9, non 1..10",
                "codice_giusto":    "for i in range(1, 11):\n    print(i)  # 1..10",
            },
            {
                "titolo": "❌ Loop infinito con while",
                "testo": "Se dimentichi di aggiornare la variabile del while, il loop non si ferma mai.",
                "codice_sbagliato": "n = 0\nwhile n < 5:\n    print(n)  # loop infinito! n non cambia mai",
                "codice_giusto":    "n = 0\nwhile n < 5:\n    print(n)\n    n += 1  # fondamentale",
            },
            {
                "titolo": "❌ Modificare la lista mentre ci iteri sopra",
                "testo": "Rimuovere elementi da una lista durante il for causa comportamenti imprevedibili.",
                "codice_sbagliato": "for x in lista:\n    lista.remove(x)  # salta elementi!",
                "codice_giusto":    "lista = [x for x in lista if condizione]  # list comprehension",
            },
        ],
        "quando_usarlo": "Ogni volta che hai una collezione di cose da processare. In boto3: quasi sempre — tutte le risposte AWS sono liste.",
    },

    "funzioni": {
        "analogia": """
**Una funzione è una ricetta.**

La scrivi una volta, la segui ogni volta che vuoi quel piatto, con ingredienti diversi.

```python
def calcola_costo(ore, prezzo_orario):   # la ricetta
    return ore * prezzo_orario

costo_dev  = calcola_costo(730, 0.023)   # ingredienti: istanza dev
costo_prod = calcola_costo(730, 0.096)   # ingredienti: istanza prod
```

La ricetta non cambia. Cambiano solo gli ingredienti (parametri).

**DRY: Don't Repeat Yourself** — se scrivi lo stesso codice due volte, fanne una funzione.
""",
        "perche": """
**Perché le funzioni sono essenziali per script AWS professionali?**

Senza funzioni, ogni script boto3 diventa un muro di codice illeggibile.
Con le funzioni, ogni operazione ha un nome e uno scopo.

```python
def ottieni_istanze_running(ec2_client, regione):
    risposta = ec2_client.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    )
    istanze = []
    for res in risposta["Reservations"]:
        istanze.extend(res["Instances"])
    return istanze

def ferma_istanza(ec2_client, instance_id):
    ec2_client.stop_instances(InstanceIds=[instance_id])
    print(f"✅ Fermata: {instance_id}")

# Main script — leggibile come una lista di passi
ec2      = boto3.client("ec2", region_name="eu-west-1")
running  = ottieni_istanze_running(ec2, "eu-west-1")
for ist in running:
    ferma_istanza(ec2, ist["InstanceId"])
```

Ogni funzione fa **una cosa sola** e ha un **nome che spiega cosa fa**.
Se trovi un bug, lo correggi in un posto — si aggiusta ovunque.
""",
        "errori_comuni": [
            {
                "titolo": "❌ Dimenticare return",
                "testo": "Senza `return`, la funzione ritorna `None` silenziosamente. Nessun errore — solo risultati strani.",
                "codice_sbagliato": "def doppio(n):\n    n * 2  # calcola ma non ritorna nulla\n\nprint(doppio(5))  # stampa None",
                "codice_giusto":    "def doppio(n):\n    return n * 2\n\nprint(doppio(5))  # stampa 10",
            },
            {
                "titolo": "❌ Chiamare la funzione senza parentesi",
                "testo": "Senza `()` non chiami la funzione — ottieni solo un riferimento ad essa.",
                "codice_sbagliato": "print(doppio)   # <function doppio at 0x...>",
                "codice_giusto":    "print(doppio(5))  # 10",
            },
            {
                "titolo": "❌ Variabili locali vs globali",
                "testo": "Le variabili create dentro una funzione esistono solo dentro di essa.",
                "codice_sbagliato": "def crea():\n    x = 10\n\ncrea()\nprint(x)  # NameError! x non esiste fuori",
                "codice_giusto":    "def crea():\n    return 10\n\nx = crea()\nprint(x)  # 10",
            },
        ],
        "quando_usarlo": "Ogni volta che scrivi lo stesso codice più di una volta, o quando vuoi dare un nome chiaro a un'operazione. Regola: una funzione = una responsabilità.",
    },

    "liste_dizionari": {
        "analogia": """
**Lista = scaffale numerato. Dizionario = rubrica telefonica.**

Lo scaffale (lista) è ordinato: primo piano, secondo piano, terzo piano.
La rubrica (dizionario) ha etichette: cerchi "Lorenzo" e trovi il numero — non importa in che posizione è.

```python
# Scaffale numerato (lista)
regioni = ["eu-west-1", "us-east-1", "ap-southeast-1"]
print(regioni[0])   # "eu-west-1" — primo scaffale

# Rubrica (dizionario)
istanza = {"id": "i-001", "tipo": "t3.micro", "stato": "running"}
print(istanza["tipo"])   # "t3.micro" — cerchi per nome, non per posizione
```

**La differenza chiave:** nella lista sai dove stai. Nel dizionario sai come si chiama.
""",
        "perche": """
**Perché liste e dizionari sono fondamentali per boto3?**

Ogni risposta di boto3 è un dizionario che contiene liste che contengono dizionari.

```python
risposta = ec2.describe_instances()
# {
#   "Reservations": [           ← lista
#     {                         ← dizionario
#       "Instances": [          ← lista
#         {                     ← dizionario
#           "InstanceId": "i-001",
#           "State": {"Name": "running"},
#           "Tags": [{"Key": "Name", "Value": "WebServer"}]
#         }
#       ]
#     }
#   ]
# }
```

Sapere navigare dizionari annidati **è il 70% del lavoro con boto3**.
Ogni servizio AWS ha la sua struttura, ma il pattern è sempre lo stesso: dict dentro list dentro dict.
""",
        "errori_comuni": [
            {
                "titolo": "❌ KeyError — chiave che non esiste",
                "testo": "Accedere a una chiave inesistente in un dizionario causa KeyError. Usa `.get()` per sicurezza.",
                "codice_sbagliato": 'ist["PublicIp"]  # KeyError se l\'istanza non ha IP pubblico',
                "codice_giusto":    'ist.get("PublicIp", "N/A")  # ritorna "N/A" se non esiste',
            },
            {
                "titolo": "❌ IndexError — indice fuori range",
                "testo": "Lista con 3 elementi: indici validi sono 0, 1, 2. L'indice 3 causa IndexError.",
                "codice_sbagliato": "lista = [1, 2, 3]\nprint(lista[3])  # IndexError",
                "codice_giusto":    "if lista:\n    print(lista[0])  # controlla prima che non sia vuota",
            },
            {
                "titolo": "❌ Confondere lista di dict con dict",
                "testo": "boto3 spesso ritorna una lista di dizionari, non un dizionario singolo.",
                "codice_sbagliato": 'risposta["Buckets"]["Name"]  # TypeError — Buckets è una lista',
                "codice_giusto":    'risposta["Buckets"][0]["Name"]  # prima elemento, poi chiave',
            },
        ],
        "quando_usarlo": "Liste per sequenze ordinate di cose simili. Dizionari per dati con campi nominati (come JSON, come le risposte boto3).",
    },

    "automazione": {
        "analogia": """
**Il tuo script è un robot in fabbrica.**

`os` è il braccio che si muove tra i cassetti del filesystem.
`open()` è la mano che apre e chiude scatole (file).
Il for loop è il nastro trasportatore che porta ogni file al robot.

```python
import os

for nome_file in os.listdir("/var/log/aws"):     # nastro
    if nome_file.endswith(".log"):                # filtro
        with open(nome_file, "r") as f:           # apri scatola
            contenuto = f.read()                  # leggi
            if "ERROR" in contenuto:
                print(f"Problema in: {nome_file}")
```

Il robot non si stanca. Processa 1 file o 10.000 con lo stesso sforzo.
""",
        "perche": """
**Perché automazione e file sono cruciali nel lavoro Cloud?**

Scenari reali in cui userai questi strumenti:

1. **Report di costo** — scarichi i dati di billing AWS (CSV) e li elabori con Python
2. **Analisi log** — leggi file di log da S3, cerchi pattern di errore
3. **Backup automatici** — crei cartelle con timestamp, sposti file
4. **Config management** — leggi file YAML/JSON con configurazioni di deploy

```python
import os
from datetime import date

# Crea cartella backup con data odierna
oggi = str(date.today())
cartella = f"backup_{oggi}"
os.makedirs(cartella, exist_ok=True)

# Salva report
with open(f"{cartella}/report.txt", "w") as f:
    f.write(f"Report del {oggi}\\n")
    f.write("Istanze attive: 12\\n")
    f.write("Costo stimato: $142.50\\n")
```
""",
        "errori_comuni": [
            {
                "titolo": "❌ Non usare 'with' per aprire file",
                "testo": "Senza `with`, se il codice crasha il file rimane aperto e bloccato.",
                "codice_sbagliato": "f = open('file.txt')\ncontenuto = f.read()\n# se qui crasha, f rimane aperto",
                "codice_giusto":    "with open('file.txt') as f:\n    contenuto = f.read()\n# chiuso automaticamente",
            },
            {
                "titolo": "❌ Modalità sbagliata",
                "testo": "`'r'` legge, `'w'` scrive (sovrascrive), `'a'` aggiunge alla fine. `'w'` cancella il contenuto esistente!",
                "codice_sbagliato": "with open('log.txt', 'w') as f:\n    f.write('nuova riga')  # cancella tutto il log!",
                "codice_giusto":    "with open('log.txt', 'a') as f:\n    f.write('nuova riga\\n')  # aggiunge in fondo",
            },
            {
                "titolo": "❌ Path relativo vs assoluto",
                "testo": "Un path relativo dipende da dove esegui lo script. Usa `os.path.join()` per costruire path portabili.",
                "codice_sbagliato": "open('data/file.txt')  # funziona solo se esegui dalla cartella giusta",
                "codice_giusto":    "base = os.path.dirname(__file__)\npath = os.path.join(base, 'data', 'file.txt')",
            },
        ],
        "quando_usarlo": "Ogni volta che devi leggere/scrivere file, navigare cartelle, salvare report, leggere configurazioni. Fondamentale per qualsiasi script di automazione reale.",
    },

    "boto3_intro": {
        "analogia": """
**boto3 è il telecomando per AWS.**

Ogni metodo è un tasto. `list_buckets()` è il tasto "mostra cosa c'è su S3".
`start_instances()` è il tasto "accendi quella macchina".

La differenza con la console AWS: il telecomando boto3 puoi **programmarlo**.
Puoi dirgli "ogni lunedì alle 8 accendi queste 3 istanze e alle 18 spegnile" — e lo fa da solo.

```python
import boto3

ec2 = boto3.client("ec2", region_name="eu-west-1")  # "sintonizza" sulla regione

# Tasto: mostrami le istanze
risposta = ec2.describe_instances()

# Naviga la risposta (sempre un dizionario)
for res in risposta["Reservations"]:
    for ist in res["Instances"]:
        print(ist["InstanceId"], "→", ist["State"]["Name"])
```
""",
        "perche": """
**Perché boto3 è il punto di arrivo di questo corso?**

Tutto quello che hai imparato porta qui:

| Modulo | Come lo usi con boto3 |
|--------|----------------------|
| Variabili | Salvi client, risposte, ID di risorse |
| Stringhe | Manipoli ARN, nomi, tag, log |
| Condizioni | Decidi cosa fare in base allo stato delle risorse |
| Cicli | Iteri su liste di istanze, bucket, snapshot |
| Funzioni | Organizzi le operazioni in blocchi riutilizzabili |
| Liste/Dict | Navighi le risposte JSON di boto3 |
| File | Salvi report, leggi configurazioni |

**boto3 è Python applicato all'infrastruttura cloud.**
Con questo puoi scrivere il tuo primo script di automazione reale.

**Setup locale:**
```bash
pip install boto3
aws configure  # inserisci: Access Key ID, Secret Key, regione
```
""",
        "errori_comuni": [
            {
                "titolo": "❌ NoCredentialsError",
                "testo": "boto3 non trova le credenziali AWS. Devi configurarle con `aws configure` o settare le variabili d'ambiente.",
                "codice_sbagliato": "# boto3.client('s3') senza credenziali → NoCredentialsError",
                "codice_giusto":    "# Nel terminale:\n# aws configure\n# AWS Access Key ID: AKIA...\n# AWS Secret Access Key: ...\n# Default region name: eu-west-1",
            },
            {
                "titolo": "❌ Regione sbagliata",
                "testo": "Le risorse sono regionali. Un bucket creato in eu-west-1 non si vede se cerchi in us-east-1.",
                "codice_sbagliato": "ec2 = boto3.client('ec2')  # usa la regione di default, potrebbe essere sbagliata",
                "codice_giusto":    'ec2 = boto3.client("ec2", region_name="eu-west-1")  # esplicito è meglio',
            },
            {
                "titolo": "❌ Non gestire ClientError",
                "testo": "Se la risorsa non esiste o non hai i permessi, boto3 lancia `ClientError`. Gestiscila sempre.",
                "codice_sbagliato": "s3.get_object(Bucket='mio-bucket', Key='file.txt')  # crasha se non esiste",
                "codice_giusto":    "from botocore.exceptions import ClientError\ntry:\n    s3.get_object(Bucket='mio-bucket', Key='file.txt')\nexcept ClientError as e:\n    print(f\"Errore: {e.response['Error']['Message']}\")",
            },
        ],
        "quando_usarlo": "Ogni volta che vuoi interagire con AWS programmaticamente: creare risorse, leggerle, modificarle, cancellarle, automatizzare operazioni ripetitive.",
    },

    "errori": {
        "analogia": """
**Il try/except è un parafulmine.**

Metti il codice *rischioso* dentro `try`. Se arriva il fulmine (eccezione), `except` lo assorbe — il resto del programma rimane in piedi.

```python
try:
    dati = leggi_da_aws()       # potrebbe fallire
except ConnectionError:
    print("Rete non disponibile, riprova")
# il programma continua da qui
```

Senza parafulmine, un singolo errore imprevisto abbatte tutto lo script.
""",
        "perche": """
**Perché try/except è obbligatorio con boto3?**

Il cloud non è affidabile per definizione. Ogni chiamata API può fallire:
- Rete non disponibile
- Credenziali scadute o insufficienti
- Risorsa non trovata
- Rate limiting

```python
from botocore.exceptions import ClientError

def ottieni_file(bucket, chiave):
    try:
        r = s3.get_object(Bucket=bucket, Key=chiave)
        return r["Body"].read()
    except ClientError as e:
        codice = e.response["Error"]["Code"]
        if codice == "NoSuchKey":
            return None      # gestito: file non esiste
        raise               # altri errori: rilancia
```

Uno script senza try/except crasha al primo problema reale.
""",
        "errori_comuni": [
            {
                "titolo": "❌ except: generico — nasconde tutto",
                "testo": "`except Exception:` cattura qualsiasi errore, anche quelli che non ti aspetti. Rende i bug impossibili da trovare.",
                "codice_sbagliato": "try:\n    fai()\nexcept Exception:\n    pass  # inghiotte tutto silenziosamente",
                "codice_giusto":    "try:\n    fai()\nexcept ValueError as e:\n    print(f'Valore errato: {e}')\nexcept KeyError as e:\n    print(f'Chiave mancante: {e}')",
            },
            {
                "titolo": "❌ Try troppo grande",
                "testo": "Proteggere 50 righe con un unico try rende impossibile capire quale riga ha fallito.",
                "codice_sbagliato": "try:\n    # 50 righe...\nexcept Exception:\n    print('Qualcosa è andato storto')",
                "codice_giusto":    "config = leggi_config()   # sicuro, fuori dal try\ntry:\n    r = s3.get_object(**config)  # solo questa può fallire\nexcept ClientError as e:\n    gestisci(e)",
            },
            {
                "titolo": "❌ Eccezione sbagliata",
                "testo": "Ogni operazione lancia tipi di eccezione specifici. Catturare il tipo sbagliato = non catturare nulla.",
                "codice_sbagliato": "try:\n    x = 10 / 0\nexcept ValueError:   # ZeroDivisionError non è ValueError!",
                "codice_giusto":    "try:\n    x = 10 / 0\nexcept ZeroDivisionError:\n    print('Divisione per zero')",
            },
        ],
        "quando_usarlo": "Ogni volta che interagisci col mondo esterno: rete, file, API, database. NON per logica di business — quella si gestisce con if/else.",
    },

    "kwargs_unpacking": {
        "analogia": """
**`**kwargs` è come un modulo di configurazione a firma variabile.**

Chiami un servizio AWS: a volte passi solo `Bucket`, a volte aggiungi `Key`, `MaxKeys`, `Delimiter`.
La firma non cambia — il servizio accetta tutto quello che gli mandi come dizionario.

```python
def configura(**opzioni):
    for k, v in opzioni.items():
        print(f"{k}: {v}")

configura(regione="eu-west-1", servizio="s3", timeout=30)
```

`**kwargs` cattura tutto come dizionario. `*args` cattura tutto come tupla.
""",
        "perche": """
**Perché kwargs è fondamentale con boto3?**

Ogni metodo boto3 accetta decine di parametri opzionali. Il pattern professionale:

```python
params = {"Bucket": bucket_name, "Key": file_path}
if version_id:
    params["VersionId"] = version_id   # aggiunto solo se serve

risposta = s3.get_object(**params)     # ** spacchetta il dict
```

Costruisci la chiamata dinamicamente invece di annidare if/else nella signature.
""",
        "errori_comuni": [
            {
                "titolo": "❌ Dict senza ** a boto3",
                "testo": "Senza `**`, passi il dizionario come argomento posizionale — TypeError immediato.",
                "codice_sbagliato": "params = {'Bucket': 'test'}\ns3.get_object(params)    # TypeError",
                "codice_giusto":    "params = {'Bucket': 'test'}\ns3.get_object(**params)  # corretto",
            },
            {
                "titolo": "❌ Confondere *args e **kwargs",
                "testo": "`*args` → tupla di positional. `**kwargs` → dict di keyword. Non intercambiabili.",
                "codice_sbagliato": "def f(*kwargs):\n    print(kwargs['nome'])  # TypeError: tuple non ha chiavi",
                "codice_giusto":    "def f(**kwargs):\n    print(kwargs.get('nome', 'N/A'))",
            },
            {
                "titolo": "❌ Ordine sbagliato nella firma",
                "testo": "L'ordine obbligatorio è: posizionali, *args, keyword-only, **kwargs.",
                "codice_sbagliato": "def f(**kwargs, nome):  # SyntaxError",
                "codice_giusto":    "def f(nome, **kwargs):  # posizionale prima",
            },
        ],
        "quando_usarlo": "Quando una funzione deve accettare parametri variabili, o quando costruisci chiamate boto3 dinamicamente.",
    },

    "json_env": {
        "analogia": """
**`json` è il traduttore tra Python e il mondo esterno. `os.environ` è la cassaforte delle credenziali.**

boto3 ti risponde sempre con un dizionario Python, ma sotto c'è JSON.
Capire `json.loads` / `json.dumps` significa capire come i dati entrano ed escono dal cloud.

```python
# Risposta API → dict Python
dati = json.loads('{"stato": "running", "costo": 0.096}')
print(dati["stato"])   # running

# Config Python → file/log
print(json.dumps(dati, indent=2))
```

`os.environ` è dove vivono le credenziali — mai nel codice sorgente.
""",
        "perche": """
**Perché JSON e env var sono il pane quotidiano del Cloud Engineer?**

- Le risposte boto3 hanno struttura JSON — devi saper navigarle
- I file di configurazione sono quasi sempre JSON o YAML
- Le credenziali AWS vanno in variabili d'ambiente, non nel codice

```python
import os, json

# Credenziali da env (boto3 le legge automaticamente)
# export AWS_ACCESS_KEY_ID="AKIA..."
# export AWS_DEFAULT_REGION="eu-west-1"

# Config da file JSON
with open("config.json") as f:
    cfg = json.load(f)

regione = os.environ.get("AWS_REGION", cfg["regione_default"])
```
""",
        "errori_comuni": [
            {
                "titolo": "❌ json.loads vs json.load",
                "testo": "`json.loads` → da stringa. `json.load` → da file. Confonderli causa TypeError.",
                "codice_sbagliato": 'with open("cfg.json") as f:\n    dati = json.loads(f)  # TypeError: expects str',
                "codice_giusto":    'with open("cfg.json") as f:\n    dati = json.load(f)   # corretto per file',
            },
            {
                "titolo": "❌ os.environ['KEY'] su variabile mancante",
                "testo": "`os.environ['KEY']` lancia `KeyError` se la variabile non esiste. Usa `.get()` con default.",
                "codice_sbagliato": "regione = os.environ['AWS_REGION']  # KeyError se non impostata",
                "codice_giusto":    "regione = os.environ.get('AWS_REGION', 'eu-west-1')  # default sicuro",
            },
            {
                "titolo": "❌ Credenziali nel codice sorgente",
                "testo": "Hardcodare access key nel codice è un rischio di sicurezza grave — basta un commit pubblico.",
                "codice_sbagliato": 'client = boto3.client("s3", aws_access_key_id="AKIA123...")  # MAI',
                "codice_giusto":    '# export AWS_ACCESS_KEY_ID="AKIA123..."\nclient = boto3.client("s3")  # legge da env auto',
            },
        ],
        "quando_usarlo": "Ogni volta che leggi/scrivi configurazioni, parsi risposte API, o gestisci credenziali e segreti.",
    },

    "comprehensions": {
        "analogia": """
**La comprehension è una fabbrica in una riga.**

Invece di costruire una lista passo dopo passo con un loop, la descrivi in una frase:
*"dammi tutti gli X che soddisfano Y, trasformati in Z".*

```python
# Loop classico
running = []
for ist in istanze:
    if ist["stato"] == "running":
        running.append(ist["id"])

# Comprehension — stessa cosa, una riga
running = [ist["id"] for ist in istanze if ist["stato"] == "running"]
```

Più leggibile, più veloce, più Pythonic.
""",
        "perche": """
**Perché le comprehension dominano il codice boto3 professionale?**

Le risposte boto3 sono liste di dizionari. Le comprehension permettono di
filtrare, estrarre e trasformare in modo conciso:

```python
# Estrai tutti gli ID delle istanze running
ids = [i["InstanceId"] for i in istanze if i["State"]["Name"] == "running"]

# Mappa nome → stato (dict comprehension)
stati = {i["InstanceId"]: i["State"]["Name"] for i in istanze}

# Costo totale con generator expression
totale = sum(b["size_gb"] * 0.023 for b in buckets)
```

| Tipo | Sintassi | Output |
|------|----------|--------|
| List | `[expr for x in it if cond]` | lista |
| Dict | `{k: v for x in it}` | dizionario |
| Set  | `{expr for x in it}` | insieme |
| Gen  | `(expr for x in it)` | iteratore lazy |
""",
        "errori_comuni": [
            {
                "titolo": "❌ Condizione dopo l'espressione, non prima",
                "testo": "Il `if` di filtro va DOPO il `for`, non prima dell'espressione.",
                "codice_sbagliato": "[if x > 0: x for x in lista]  # SyntaxError",
                "codice_giusto":    "[x for x in lista if x > 0]   # if DOPO il for",
            },
            {
                "titolo": "❌ Comprehension per effetti collaterali",
                "testo": "Le comprehension servono per creare collezioni, non per eseguire azioni. Usa un for loop se non ti serve il risultato.",
                "codice_sbagliato": "[print(x) for x in lista]  # crea una lista di None inutile",
                "codice_giusto":    "for x in lista:\n    print(x)  # loop esplicito per effetti collaterali",
            },
            {
                "titolo": "❌ Comprensioni annidate illeggibili",
                "testo": "Più di un livello di nesting in una comprehension diventa illeggibile. Spezzala in più righe o usa loop.",
                "codice_sbagliato": "[y for x in matrix for y in x if y > 0 if y < 10]  # illeggibile",
                "codice_giusto":    "# Spezza o usa loop espliciti quando è più chiaro",
            },
        ],
        "quando_usarlo": "Per creare liste/dict/set filtrando o trasformando sequenze. Evitale se la logica è complessa — un loop esplicito è più chiaro.",
    },

    "builtins": {
        "analogia": """
**enumerate, zip, sorted sono gli attrezzi che i falegnami esperti usano senza pensarci.**

I principianti scrivono loop con indici manuali. I professionisti usano questi built-in
perché esprimono l'*intenzione* del codice, non i meccanismi.

```python
# Principiante
for i in range(len(bucket_list)):
    print(f"{i}: {bucket_list[i]}")

# Professionista
for i, bucket in enumerate(bucket_list, start=1):
    print(f"{i}: {bucket}")
```
""",
        "perche": """
**Questi built-in appaiono ogni giorno nel codice boto3:**

```python
# enumerate — per log numerati
for n, ist in enumerate(istanze, start=1):
    print(f"{n}/{len(istanze)} → {ist['InstanceId']}")

# zip — per abbinare due liste (es. nomi e ARN)
for nome, arn in zip(nomi_bucket, arn_list):
    print(f"{nome}: {arn}")

# sorted con key — per ordinare risorse per costo
per_costo = sorted(istanze, key=lambda x: x["costo_ora"], reverse=True)

# None safety — accesso sicuro a campi opzionali
ip = istanza.get("PublicIpAddress")
if ip is not None:
    print(f"IP: {ip}")
```
""",
        "errori_comuni": [
            {
                "titolo": "❌ Confronto con == None invece di is None",
                "testo": "`None` è un singleton — il confronto corretto è `is None`, non `== None`.",
                "codice_sbagliato": "if valore == None:  # funziona ma è scorretto",
                "codice_giusto":    "if valore is None:  # idiomatico Python",
            },
            {
                "titolo": "❌ sorted modifica la lista originale",
                "testo": "`sorted()` ritorna una nuova lista. `list.sort()` modifica in-place. Confonderli causa bug silenziosi.",
                "codice_sbagliato": "sorted(lista)  # risultato ignorato! lista non cambia",
                "codice_giusto":    "ordinata = sorted(lista)  # salva il risultato",
            },
            {
                "titolo": "❌ zip si ferma alla lista più corta",
                "testo": "`zip` si ferma alla lista più corta. Se le liste hanno lunghezze diverse, usa `itertools.zip_longest`.",
                "codice_sbagliato": "list(zip([1,2,3], ['a','b']))  # [(1,'a'),(2,'b')] — 3 perso!",
                "codice_giusto":    "from itertools import zip_longest\nlist(zip_longest([1,2,3], ['a','b'], fillvalue='?'))",
            },
        ],
        "quando_usarlo": "enumerate quando hai bisogno di indice + valore. zip per iterare su più liste in parallelo. sorted quando l'ordine conta. is None per controlli di esistenza.",
    },

    "setup_env": {
        "analogia": """
**Il venv è una stanza pulita per ogni progetto.**

Senza ambienti virtuali, tutte le librerie di tutti i tuoi progetti convivono
nella stessa stanza. La versione di boto3 che serve al progetto A rompe il progetto B.

```bash
python -m venv .venv          # crea la stanza
source .venv/bin/activate     # entra nella stanza (Linux/Mac)
.venv\\Scripts\\activate        # entra nella stanza (Windows)
pip install boto3 streamlit   # installa SOLO in questa stanza
```

Ogni progetto ha la sua stanza. Nessun conflitto.
""",
        "perche": """
**Perché venv e pip sono il primo passo — non l'ultimo.**

```bash
# Installa dipendenze
pip install -r requirements.txt

# Congela le versioni esatte (riproducibilità)
pip freeze > requirements.txt

# Versioni moderne (più veloci di pip)
pip install uv
uv pip install boto3
```

Senza requirements.txt il codice funziona sul tuo PC ma non in produzione.
Con requirements.txt il deploy è deterministico.
""",
        "errori_comuni": [
            {
                "titolo": "❌ pip install senza venv attivo",
                "testo": "Installa a livello di sistema — rompe altri progetti o richiede sudo.",
                "codice_sbagliato": "# terminale senza venv attivo\npip install boto3  # va nel Python di sistema",
                "codice_giusto":    "source .venv/bin/activate  # prima attiva\npip install boto3           # poi installa",
            },
            {
                "titolo": "❌ Committare .venv su git",
                "testo": "La cartella .venv pesa centinaia di MB e non è portabile tra sistemi.",
                "codice_sbagliato": "git add .venv  # centinaia di MB nel repo",
                "codice_giusto":    "echo '.venv/' >> .gitignore\ngit add requirements.txt  # solo questo",
            },
            {
                "titolo": "❌ requirements.txt senza versioni",
                "testo": "`pip freeze` include le versioni esatte. Senza, `pip install` prende l'ultima — che potrebbe rompere tutto.",
                "codice_sbagliato": "# requirements.txt\nboto3\nstreamlit",
                "codice_giusto":    "boto3==1.34.0\nstreamlit==1.40.0",
            },
        ],
        "quando_usarlo": "Sempre — ogni progetto Python merita il suo venv. Non è opzionale, è igiene.",
    },

    "tipi_operatori": {
        "analogia": """
**Il casting è come il cambio valuta: stesso valore, formato diverso.**

L'utente ti manda sempre stringhe. Il computer vuole numeri per fare calcoli.
`int()`, `float()`, `str()` sono i cambiavalute.

```python
eta_str = "28"          # dall'input utente
eta_int = int(eta_str)  # adesso puoi fare calcoli
print(eta_int + 1)      # 29
```
""",
        "perche": """
**Perché casting e operatori avanzati compaiono ovunque:**

```python
# Ternary — if/else in una riga
stato = "attiva" if istanza["running"] else "spenta"

# Walrus := — assegna e controlla insieme
import re
if m := re.search(r'i-\\w+', log_line):
    print(f"ID trovato: {m.group()}")

# Casting da env var (sempre stringhe)
timeout = int(os.environ.get("TIMEOUT", "30"))
max_retry = float(os.environ.get("RETRY_DELAY", "1.5"))
```
""",
        "errori_comuni": [
            {
                "titolo": "❌ int() su float-string",
                "testo": '`int("3.14")` fallisce — devi passare prima da `float()`.',
                "codice_sbagliato": 'int("3.14")   # ValueError',
                "codice_giusto":    'int(float("3.14"))  # 3',
            },
            {
                "titolo": '❌ Confondere "0" con 0',
                "testo": '`bool("0")` è `True` — la stringa non è vuota! `bool(0)` è `False`.',
                "codice_sbagliato": 'debug = os.environ.get("DEBUG", "0")\nif debug:   # True anche con "0"!',
                "codice_giusto":    'debug = os.environ.get("DEBUG", "0") == "1"',
            },
            {
                "titolo": "❌ / vs // per la divisione",
                "testo": "`/` restituisce sempre float. `//` è divisione intera. `%` è il resto.",
                "codice_sbagliato": "pagine = 100 / 10   # 10.0 (float)\nrange(pagine)       # TypeError",
                "codice_giusto":    "pagine = 100 // 10  # 10 (int)\nrange(pagine)       # ok",
            },
        ],
        "quando_usarlo": "Ogni volta che leggi dati dall'esterno (input utente, env var, file) devi castare. Il ternary quando l'if/else è semplice e stai assegnando un valore.",
    },

    "scope_closures": {
        "analogia": """
**LEGB è come cercare le chiavi di casa.**

Prima guardi le tue tasche (Local), poi la borsa (Enclosing), poi il cassetto (Global), poi lo zaino comune (Built-in).
Python fa lo stesso con i nomi delle variabili.

```python
x = "globale"

def outer():
    x = "enclosing"
    def inner():
        x = "locale"
        print(x)   # cerca Local → trova "locale"
    inner()
    print(x)       # cerca Local → non c'è → Enclosing → trova "enclosing"

outer()
print(x)           # cerca Global → trova "globale"
```
""",
        "perche": """
**Closures e lambda sono usati ogni giorno:**

```python
# Lambda — funzione anonima in una riga
istanze_ordinate = sorted(istanze, key=lambda x: x["costo_ora"])

# Closure — una funzione che ricorda il suo ambiente
def make_tagger(prefisso):
    def tagger(risorsa):
        return f"{prefisso}-{risorsa}"
    return tagger

prod_tag = make_tagger("prod")
print(prod_tag("web-server"))   # prod-web-server
```
""",
        "errori_comuni": [
            {
                "titolo": "❌ Modificare una globale senza `global`",
                "testo": "Dentro una funzione, assegnare a un nome crea sempre una variabile locale — non modifica la globale.",
                "codice_sbagliato": "contatore = 0\ndef incrementa():\n    contatore += 1   # UnboundLocalError!",
                "codice_giusto":    "contatore = 0\ndef incrementa():\n    global contatore\n    contatore += 1",
            },
            {
                "titolo": "❌ Lambda con side effect",
                "testo": "Lambda è per espressioni semplici. Se hai bisogno di più righe o side effect, usa `def`.",
                "codice_sbagliato": "fn = lambda x: print(x); return x  # SyntaxError",
                "codice_giusto":    "def fn(x):\n    print(x)\n    return x",
            },
            {
                "titolo": "❌ Closure che cattura variabile del loop",
                "testo": "La closure cattura il *riferimento* alla variabile, non il valore al momento della creazione.",
                "codice_sbagliato": "funzioni = [lambda: i for i in range(3)]\nprint([f() for f in funzioni])  # [2, 2, 2]",
                "codice_giusto":    "funzioni = [lambda i=i: i for i in range(3)]\nprint([f() for f in funzioni])  # [0, 1, 2]",
            },
        ],
        "quando_usarlo": "Lambda per key= in sorted/map/filter quando l'espressione è breve. global/nonlocal raramente — preferisci classi o return. Closure quando vuoi incapsulare stato senza una classe.",
    },

    "tuple_immutabilita": {
        "analogia": """
**La tupla è cemento. La lista è argilla.**

Argilla (lista) — puoi aggiungere, togliere, modificare.
Cemento (tupla) — una volta solidificato, non cambia più. Ma è più solido, più veloce, più sicuro da condividere.

```python
lista  = [1, 2, 3]   # argilla: modificabile
lista[0] = 99        # ok

tupla  = (1, 2, 3)   # cemento: immutabile
tupla[0] = 99        # TypeError!
```
""",
        "perche": """
**Quando usare tuple e perché copy/deepcopy importano:**

```python
# Tuple unpacking — elegante e diretto
latitudine, longitudine = (45.07, 7.69)
nome, *resto = ("Lorenzo", "dev", "Torino")

# Chiave di dizionario (le liste non possono esserlo)
cache = {}
cache[(45.07, 7.69)] = "Torino"  # tupla come chiave

# copy vs deepcopy
import copy
originale = {"lista": [1, 2, 3]}
superficiale = copy.copy(originale)
profonda     = copy.deepcopy(originale)

superficiale["lista"].append(4)  # modifica ANCHE originale!
profonda["lista"].append(5)      # non tocca originale
```
""",
        "errori_comuni": [
            {
                "titolo": "❌ Tupla da un elemento senza virgola",
                "testo": "`(42)` è solo `42` tra parentesi. `(42,)` è una tupla con un elemento.",
                "codice_sbagliato": "t = (42)\nprint(type(t))  # <class 'int'>",
                "codice_giusto":    "t = (42,)\nprint(type(t))  # <class 'tuple'>",
            },
            {
                "titolo": "❌ Modificare un elemento mutabile dentro una tupla",
                "testo": "La tupla è immutabile, ma se contiene una lista, la lista è ancora modificabile.",
                "codice_sbagliato": "t = ([1, 2], 'ok')\nt[0].append(3)  # funziona! t[0] è ancora [1,2,3]",
                "codice_giusto":    "# Usa tuple di soli immutabili se hai bisogno di vera immutabilità",
            },
            {
                "titolo": "❌ copy() su strutture annidate",
                "testo": "`copy.copy()` è superficiale: copia il container ma condivide gli oggetti interni.",
                "codice_sbagliato": "a = {'k': [1,2,3]}\nb = copy.copy(a)\nb['k'].append(4)  # modifica anche a['k']!",
                "codice_giusto":    "b = copy.deepcopy(a)  # indipendente a tutti i livelli",
            },
        ],
        "quando_usarlo": "Tuple per dati che non devono cambiare (coordinate, chiavi composite, ritorni multipli). deepcopy quando devi clonare strutture annidate senza rischi.",
    },

    "controllo_avanzato": {
        "analogia": """
**break è l'uscita d'emergenza. continue è il filtraggio. else è la conferma.**

```python
# break — esci appena trovi quello che cerchi
for ist in istanze:
    if ist["stato"] == "running":
        prima_running = ist
        break   # inutile continuare

# continue — salta i casi non interessanti
for ist in istanze:
    if ist["stato"] == "stopped":
        continue   # non mi interessa
    processa(ist)

# for/else — else esegue SOLO se il loop non ha fatto break
for ist in istanze:
    if ist["id"] == target_id:
        print("Trovato!")
        break
else:
    print("Non trovato — cercalo in un'altra regione")
```
""",
        "perche": """
**match/case — Python 3.10+ — per classificare strutture:**

```python
# Classifica risposte HTTP
def gestisci(codice):
    match codice:
        case 200: return "OK"
        case 404: return "Non trovato"
        case 403: return "Accesso negato"
        case c if c >= 500: return f"Errore server ({c})"
        case _: return "Codice sconosciuto"

# Match su strutture boto3
match risposta.get("State", {}).get("Name"):
    case "running":  avvia_monitoraggio()
    case "stopped":  notifica_team()
    case _:          log_stato_insolito()
```
""",
        "errori_comuni": [
            {
                "titolo": "❌ break fuori da un loop",
                "testo": "`break` e `continue` funzionano solo dentro for/while.",
                "codice_sbagliato": "if condizione:\n    break  # SyntaxError fuori da loop",
                "codice_giusto":    "for x in lista:\n    if condizione:\n        break",
            },
            {
                "titolo": "❌ continue in while senza aggiornare la variabile",
                "testo": "`continue` salta il resto del corpo — se aggiorni la variabile in fondo, il loop diventa infinito.",
                "codice_sbagliato": "n = 0\nwhile n < 5:\n    if n == 3: continue\n    n += 1   # non raggiunto quando n==3 → loop infinito",
                "codice_giusto":    "n = 0\nwhile n < 5:\n    n += 1\n    if n == 3: continue\n    print(n)",
            },
            {
                "titolo": "❌ for/else male interpretato",
                "testo": "Il `else` del for NON significa 'se il for è vuoto'. Esegue SEMPRE tranne se è avvenuto un break.",
                "codice_sbagliato": "# pensando che else = 'lista vuota'\nfor x in []:  # else esegue\n    pass\nelse:\n    print('Vuota')  # esegue, ma anche se la lista ha elementi!",
                "codice_giusto":    "# else = 'non è avvenuto break'\n# Per lista vuota: if not lista:",
            },
        ],
        "quando_usarlo": "break per uscire appena trovi. continue per saltare casi non interessanti (più leggibile di if annidati). for/else per ricerche. match/case per classificare valori o strutture (Python 3.10+).",
    },

    "generatori": {
        "analogia": """
**Il generatore è un nastro trasportatore lazy.**

Una lista carica tutto in memoria subito.
Un generatore produce un elemento alla volta — solo quando richiesto.

```python
# Lista — carica TUTTO in memoria
tutti = [x**2 for x in range(1_000_000)]  # 8 MB di RAM

# Generatore — produce uno alla volta
gen = (x**2 for x in range(1_000_000))    # quasi 0 RAM
primo = next(gen)                          # 0, poi 1, poi 4...
```

boto3 usa questo pattern per la paginazione: non scarichi 10.000 oggetti in una lista.
""",
        "perche": """
**yield e itertools dominano il codice professionale:**

```python
# Simula boto3 paginator
def pagina_bucket(client, bucket, prefix):
    paginator = client.get_paginator("list_objects_v2")
    for pagina in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in pagina.get("Contents", []):
            yield obj["Key"]   # un file alla volta, non tutti in memoria

# Uso: come se fosse una lista normale
for chiave in pagina_bucket(s3, "mio-bucket", "logs/"):
    processa(chiave)

# itertools — strumenti per iteratori
from itertools import islice, chain, groupby
prime_10 = list(islice(generatore_infinito(), 10))
```
""",
        "errori_comuni": [
            {
                "titolo": "❌ Iterare due volte un generatore esaurito",
                "testo": "Un generatore si esaurisce dopo il primo passaggio. Non puoi iterarci di nuovo.",
                "codice_sbagliato": "gen = (x for x in range(3))\nprint(list(gen))  # [0, 1, 2]\nprint(list(gen))  # [] — esaurito!",
                "codice_giusto":    "# Se ti serve iterare più volte, usa una lista\ndati = list(range(3))\nprint(dati)\nprint(dati)  # ok",
            },
            {
                "titolo": "❌ return con valore in un generatore",
                "testo": "In una funzione con yield, `return valore` lancia `StopIteration` — il valore è perso.",
                "codice_sbagliato": "def gen():\n    yield 1\n    return 42   # 42 non viene mai ricevuto",
                "codice_giusto":    "def gen():\n    yield 1\n    yield 42   # se vuoi emettere 42",
            },
            {
                "titolo": "❌ list() su un generatore infinito",
                "testo": "Un generatore infinito non si converte in lista — occupa memoria infinita e il processo si blocca.",
                "codice_sbagliato": "def infinito():\n    n = 0\n    while True:\n        yield n; n += 1\n\nlist(infinito())  # mai finisce",
                "codice_giusto":    "from itertools import islice\nlist(islice(infinito(), 10))  # solo i primi 10",
            },
        ],
        "quando_usarlo": "Quando lavori con grandi dataset, stream di dati, o API paginate. Se non hai bisogno di tutti gli elementi contemporaneamente, un generatore è più efficiente di una lista.",
    },

    "oop_base": {
        "analogia": """
**La classe è il progetto architettonico. L'istanza è l'edificio costruito.**

```python
class EC2Instance:          # progetto
    def __init__(self, id, tipo):
        self.id   = id      # ogni edificio ha il suo ID
        self.tipo = tipo

server1 = EC2Instance("i-001", "t3.micro")   # edificio 1
server2 = EC2Instance("i-002", "m5.large")   # edificio 2
```

`self` è il riferimento all'edificio specifico su cui stai lavorando.
""",
        "perche": """
**OOP organizza codice boto3 complesso:**

```python
class AWSResource:
    def __init__(self, id, regione):
        self.id      = id
        self.regione = regione

    def arn(self):
        return f"arn:aws::::{self.regione}:{self.id}"

class EC2(AWSResource):
    def __init__(self, id, regione, tipo):
        super().__init__(id, regione)   # inizializza il genitore
        self.tipo = tipo

    def costo_mensile(self, prezzo_ora):
        return prezzo_ora * 730

server = EC2("i-001", "eu-west-1", "t3.micro")
print(server.arn())           # eredita dal genitore
print(server.costo_mensile(0.023))  # metodo proprio
```
""",
        "errori_comuni": [
            {
                "titolo": "❌ Dimenticare self nei metodi",
                "testo": "Ogni metodo deve avere `self` come primo parametro — Python lo passa automaticamente.",
                "codice_sbagliato": "class Foo:\n    def saluta():  # manca self\n        print('ciao')\n\nFoo().saluta()  # TypeError",
                "codice_giusto":    "class Foo:\n    def saluta(self):\n        print('ciao')",
            },
            {
                "titolo": "❌ Attributo di classe vs istanza",
                "testo": "Un attributo definito nel corpo della classe è condiviso da tutte le istanze. Usalo solo per costanti.",
                "codice_sbagliato": "class Risorsa:\n    tags = []   # CONDIVISO tra tutte le istanze!\n\na = Risorsa(); a.tags.append('prod')\nb = Risorsa(); print(b.tags)  # ['prod'] — bug!",
                "codice_giusto":    "class Risorsa:\n    def __init__(self):\n        self.tags = []  # ogni istanza ha la sua lista",
            },
            {
                "titolo": "❌ super() senza argomenti in Python 3",
                "testo": "In Python 3 `super()` non ha bisogno di argomenti. `super(Classe, self)` è lo stile Python 2.",
                "codice_sbagliato": "class Figlio(Genitore):\n    def __init__(self):\n        super(Figlio, self).__init__()  # Python 2 style",
                "codice_giusto":    "class Figlio(Genitore):\n    def __init__(self):\n        super().__init__()  # Python 3",
            },
        ],
        "quando_usarlo": "Quando hai più oggetti dello stesso tipo con stato e comportamento. Per modellare risorse AWS (EC2Instance, S3Bucket, LambdaFunction) con metodi come costo(), start(), stop().",
    },

    "oop_avanzata": {
        "analogia": """
**I metodi dunder sono il vocabolario che Python usa per parlare con i tuoi oggetti.**

Quando scrivi `print(obj)`, Python chiama `obj.__str__()`.
Quando scrivi `len(obj)`, Python chiama `obj.__len__()`.
Quando scrivi `a == b`, Python chiama `a.__eq__(b)`.

Implementando questi metodi, i tuoi oggetti si comportano come oggetti nativi Python.
""",
        "perche": """
**@property, @classmethod e dataclasses nel codice reale:**

```python
from dataclasses import dataclass, field

@dataclass
class EC2Instance:
    id:      str
    tipo:    str
    regione: str = "eu-west-1"
    tags:    list = field(default_factory=list)

    @property
    def arn(self):   # accesso come attributo, non chiamata
        return f"arn:aws:ec2:{self.regione}::{self.id}"

    @classmethod
    def from_boto3(cls, risposta):
        return cls(
            id=risposta["InstanceId"],
            tipo=risposta["InstanceType"],
        )

    def __str__(self):
        return f"EC2({self.id}, {self.tipo})"
```
""",
        "errori_comuni": [
            {
                "titolo": "❌ @property senza setter quando serve modifica",
                "testo": "Una property senza setter è read-only. Tentare di assegnarle un valore lancia AttributeError.",
                "codice_sbagliato": "class Foo:\n    @property\n    def val(self): return self._val\n\nf = Foo(); f.val = 10  # AttributeError",
                "codice_giusto":    "@val.setter\ndef val(self, v): self._val = v",
            },
            {
                "titolo": "❌ Mutable default in dataclass",
                "testo": "In `@dataclass`, i default mutabili (liste, dict) devono usare `field(default_factory=...)`.",
                "codice_sbagliato": "@dataclass\nclass Foo:\n    items: list = []  # ValueError",
                "codice_giusto":    "from dataclasses import field\n@dataclass\nclass Foo:\n    items: list = field(default_factory=list)",
            },
            {
                "titolo": "❌ __eq__ senza __hash__",
                "testo": "Se ridefinisci `__eq__`, Python azzera `__hash__`. L'oggetto non può più essere usato come chiave di dict o elemento di set.",
                "codice_sbagliato": "class Risorsa:\n    def __eq__(self, altro): return self.id == altro.id\n# ora non può stare in un set",
                "codice_giusto":    "class Risorsa:\n    def __eq__(self, altro): return self.id == altro.id\n    def __hash__(self): return hash(self.id)",
            },
        ],
        "quando_usarlo": "@property per attributi calcolati (non vuoi parentesi). @classmethod per factory method (costruttore alternativo). dataclass quando hai solo dati + pochi metodi. Dunder quando vuoi che l'oggetto si comporti come un nativo Python.",
    },

    "decoratori": {
        "analogia": """
**Il decoratore è l'imballaggio di una funzione.**

Prendi una funzione, la avvolgi in un'altra funzione che aggiunge comportamento
prima/dopo, e restituisci la versione migliorata.

```python
def log_chiamata(func):
    def wrapper(*args, **kwargs):
        print(f"Chiamo {func.__name__}")
        risultato = func(*args, **kwargs)
        print(f"Fine {func.__name__}")
        return risultato
    return wrapper

@log_chiamata          # zucchero sintattico per: crea_bucket = log_chiamata(crea_bucket)
def crea_bucket(nome):
    print(f"Bucket {nome} creato")
```
""",
        "perche": """
**I decoratori standard che userai ogni giorno:**

```python
import functools

# @functools.lru_cache — memoization gratuita
@functools.lru_cache(maxsize=128)
def get_ami_id(regione):
    # chiamata boto3 costosa
    return ec2.describe_images(...)["Images"][0]["ImageId"]

# @property — già visto in OOP
# @staticmethod, @classmethod — già visti

# Retry decorator custom
def retry(n=3):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for tentativo in range(n):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if tentativo == n - 1: raise
            return wrapper
        return decorator
    return decorator

@retry(n=3)
def chiama_api():
    ...
```
""",
        "errori_comuni": [
            {
                "titolo": "❌ Dimenticare @functools.wraps",
                "testo": "Senza `@wraps`, il nome e la docstring della funzione originale vengono persi.",
                "codice_sbagliato": "def decorator(func):\n    def wrapper(*a, **kw): return func(*a, **kw)\n    return wrapper\n\n@decorator\ndef mia_funzione(): pass\nprint(mia_funzione.__name__)  # 'wrapper' — sbagliato!",
                "codice_giusto":    "from functools import wraps\ndef decorator(func):\n    @wraps(func)\n    def wrapper(*a, **kw): return func(*a, **kw)\n    return wrapper",
            },
            {
                "titolo": "❌ Chiamare il decoratore invece di passarlo",
                "testo": "`@decorator()` richiede che `decorator` ritorni un decoratore. `@decorator` usa `decorator` direttamente.",
                "codice_sbagliato": "@log_chiamata()   # errore se log_chiamata non accetta argomenti",
                "codice_giusto":    "@log_chiamata    # senza parentesi se non ha parametri",
            },
            {
                "titolo": "❌ lru_cache su funzione con argomenti non hashable",
                "testo": "`lru_cache` richiede argomenti hashable. Liste e dizionari non lo sono.",
                "codice_sbagliato": "@lru_cache\ndef f(lista): ...  # TypeError: lista non è hashable",
                "codice_giusto":    "@lru_cache\ndef f(tupla): ...  # ok, tuple sono hashable",
            },
        ],
        "quando_usarlo": "Logging, timing, retry, autenticazione, caching — ogni comportamento trasversale che si ripete su più funzioni. @lru_cache per funzioni pure con input ripetuti.",
    },

    "moduli_package": {
        "analogia": """
**Il modulo è un capitolo. Il package è il libro.**

`import boto3` carica il capitolo boto3 nel tuo script.
`from datetime import date` estrae solo la pagina `date` dal capitolo `datetime`.

```
mio_progetto/
├── __init__.py       # questo è un package
├── aws_utils.py      # questo è un modulo
└── config.py         # questo è un modulo
```

```python
from mio_progetto.aws_utils import crea_client
```
""",
        "perche": """
**logging e collections: due librerie standard indispensabili:**

```python
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

logger.info("Avvio script")
logger.warning("Credenziali scadono tra 7 giorni")
logger.error("Connessione fallita: %s", errore)

# collections
from collections import Counter, defaultdict

# Counter — conta occorrenze
errori = Counter(["NameError", "KeyError", "NameError", "TypeError"])
print(errori.most_common(2))  # [('NameError', 2), ('KeyError', 1)]

# defaultdict — dict con valore di default automatico
per_regione = defaultdict(list)
for ist in istanze:
    per_regione[ist["regione"]].append(ist["id"])
```
""",
        "errori_comuni": [
            {
                "titolo": "❌ Codice eseguito all'import senza guardia __name__",
                "testo": "Tutto il codice a livello modulo gira all'import. Senza guardia, il tuo script si esegue anche quando lo importi.",
                "codice_sbagliato": "# script.py\nresult = calcola_tutto()  # gira anche con 'import script'",
                "codice_giusto":    "if __name__ == '__main__':\n    result = calcola_tutto()",
            },
            {
                "titolo": "❌ print() invece di logging",
                "testo": "`print()` non ha livelli, non ha timestamp, non è filtrabile. In produzione usa sempre `logging`.",
                "codice_sbagliato": "print('Errore:', e)  # invisibile nei log di CloudWatch",
                "codice_giusto":    "logger.error('Errore: %s', e)  # CloudWatch lo cattura",
            },
            {
                "titolo": "❌ Import circolare",
                "testo": "Se A importa B e B importa A, Python si blocca in un loop. Spezza la dipendenza con un terzo modulo.",
                "codice_sbagliato": "# a.py: from b import qualcosa\n# b.py: from a import qualcosa  ← circolare",
                "codice_giusto":    "# Sposta le dipendenze comuni in c.py\n# a.py e b.py importano da c.py",
            },
        ],
        "quando_usarlo": "logging sempre invece di print nei progetti seri. __name__ guard in ogni script che potrebbe anche essere importato. collections quando conti o aggreghi dati.",
    },

    "eccezioni_avanzate": {
        "analogia": """
**`raise` è come il campanello d'allarme. Le eccezioni custom sono i cartelli che spiegano quale allarme suona.**

```python
class BudgetSuperatoError(Exception):
    def __init__(self, budget, spesa):
        self.budget = budget
        self.spesa  = spesa
        super().__init__(f"Spesa {spesa:.2f}€ supera il budget {budget:.2f}€")

def verifica_costo(costo, budget):
    if costo > budget:
        raise BudgetSuperatoError(budget, costo)
```

Ora chi chiama la funzione può catturare `BudgetSuperatoError` con informazioni precise.
""",
        "perche": """
**assert, contextlib e chaining nel codice reale:**

```python
# assert — pre/post condizioni (disabilitabile con -O)
def divide(a, b):
    assert b != 0, "Il divisore non può essere zero"
    return a / b

# contextlib — context manager senza classe
from contextlib import contextmanager

@contextmanager
def sessione_aws(regione):
    logger.info(f"Apertura sessione {regione}")
    try:
        yield boto3.Session(region_name=regione)
    finally:
        logger.info("Sessione chiusa")

with sessione_aws("eu-west-1") as sess:
    s3 = sess.client("s3")

# Exception chaining
try:
    dati = json.loads(risposta_raw)
except json.JSONDecodeError as e:
    raise ValueError("Risposta API non valida") from e
```
""",
        "errori_comuni": [
            {
                "titolo": "❌ Usare assert per validazione di input utente",
                "testo": "`assert` è disabilitato con `python -O`. Non usarlo per validazione — usa `raise` con eccezione esplicita.",
                "codice_sbagliato": "assert len(nome) > 0, 'Nome obbligatorio'  # disabilitato in produzione!",
                "codice_giusto":    "if not nome:\n    raise ValueError('Nome obbligatorio')",
            },
            {
                "titolo": "❌ raise senza from perde il contesto",
                "testo": "Quando rilanchi un'eccezione dentro un except, usa `raise ... from e` per preservare la traccia originale.",
                "codice_sbagliato": "try:\n    op()\nexcept SomeError:\n    raise AltroError()  # traccia originale persa",
                "codice_giusto":    "except SomeError as e:\n    raise AltroError() from e  # catena visibile",
            },
            {
                "titolo": "❌ contextmanager senza try/finally",
                "testo": "Il codice dopo `yield` non gira se viene lanciata un'eccezione. Il `finally` garantisce la pulizia.",
                "codice_sbagliato": "@contextmanager\ndef apri():\n    risorsa = acquisisci()\n    yield risorsa\n    rilascia(risorsa)  # non gira se c'è eccezione!",
                "codice_giusto":    "@contextmanager\ndef apri():\n    risorsa = acquisisci()\n    try:\n        yield risorsa\n    finally:\n        rilascia(risorsa)",
            },
        ],
        "quando_usarlo": "raise per comunicare errori con significato. Eccezioni custom per errori di dominio (BudgetSuperatoError, ResourceNotFoundError). assert solo per invarianti di sviluppo. contextlib per gestire risorse in modo pulito.",
    },
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# APPROCCIO ANALITICO — domande, pattern, checklist per modulo
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

APPROCCIO = {
    "variabili": {
        "domanda_chiave": "Cosa sto etichettando e perché mi servirà dopo?",
        "prima_di_codificare": [
            "Che tipo di valore devo conservare? (testo, numero, vero/falso?)",
            "Lo userò più di una volta nel codice?",
            "Il valore è fisso o può cambiare nel tempo?",
            "Che nome lo descrive meglio? (evita: x, a, val, temp)",
        ],
        "pattern": [
            "Definisci prima → usa dopo. Mai il contrario.",
            "Calcola → salva in variabile → riusa la variabile",
            "Costanti di configurazione all'inizio del file, in MAIUSCOLO",
        ],
        "checklist": [
            "Il nome è descrittivo (non x, a, dato)?",
            "Definita PRIMA di essere usata?",
            "Uso `=` per assegnare e `==` per confrontare?",
            "Il tipo è quello giusto? (stringa vs numero vs booleano)",
        ],
    },
    "stringhe": {
        "domanda_chiave": "Ho bisogno di costruire, estrarre o trasformare questo testo?",
        "prima_di_codificare": [
            "Devo costruire testo dinamico? → f-string",
            "Devo estrarre una parte? → slicing `[inizio:fine]` o `.split()`",
            "Devo trasformare? → `.upper()`, `.lower()`, `.replace()`",
            "Il confronto è case-sensitive? Normalizza con `.lower()` prima",
        ],
        "pattern": [
            "ARN → `arn.split(':')[3]` per estrarre la regione",
            "Testo dinamico → `f'Bucket: {nome}'`",
            "Cerca dentro → `'ERROR' in riga`",
            "Pulisci spazi → `.strip()` prima di confrontare",
        ],
        "checklist": [
            "Le virgolette sono bilanciate?",
            "Sto confrontando con lo stesso case?",
            "Le f-string hanno le graffe `{}`?",
            "Stringhe immutabili: `.upper()` non modifica — crea una nuova stringa",
        ],
    },
    "condizioni": {
        "domanda_chiave": "Quante strade può prendere il codice? Le ho gestite tutte?",
        "prima_di_codificare": [
            "Quante situazioni distinte esistono? (2, 3, N?)",
            "Le condizioni si escludono a vicenda? → elif. Indipendenti? → if separati",
            "Ho un caso 'tutto il resto'? → else",
            "L'ordine dei rami importa? (dal più specifico al più generico)",
        ],
        "pattern": [
            "Due casi → `if / else`",
            "Più casi mutuamente esclusivi → `if / elif / elif / else`",
            "Più controlli indipendenti → `if` separati (non elif)",
            "Soglie: ordina dal valore più alto al più basso",
        ],
        "checklist": [
            "Due punti `:` dopo ogni if/elif/else?",
            "Indentazione di 4 spazi sotto ogni ramo?",
            "Uso `==` per confrontare, non `=` per assegnare?",
            "Qual è l'output se nessuna condizione è vera?",
        ],
    },
    "cicli": {
        "domanda_chiave": "Cosa devo costruire/raccogliere? Inizializzalo vuoto PRIMA del loop.",
        "prima_di_codificare": [
            "Quante volte si ripete? (numero fisso → `range`, sequenza → `for`, condizione → `while`)",
            "Ho bisogno dell'indice o solo del valore?",
            "Devo raccogliere risultati? → inizializza `[]` o `0` prima del loop",
            "C'è un caso in cui il loop non dovrebbe girare?",
        ],
        "pattern": [
            "Itera valori → `for x in lista`",
            "Itera con indice → `for i, x in enumerate(lista)`",
            "Accumula → `totale = 0` prima, `totale += x` dentro",
            "Filtra → `if condizione:` dentro il for",
            "Trasforma → `risultati.append(f(x))` o list comprehension `[f(x) for x in lista]`",
        ],
        "checklist": [
            "`range(n)` va da 0 a n-1. Per 1→n: `range(1, n+1)`",
            "Nel while: aggiorno la variabile di controllo?",
            "Sto modificando la lista su cui sto iterando? (usa list comprehension invece)",
            "Il loop termina sempre? (no loop infinito?)",
        ],
    },
    "funzioni": {
        "domanda_chiave": "Se questo codice cambia domani, quanti posti devo modificare?",
        "prima_di_codificare": [
            "Questo codice lo riscriverò più di una volta? → fai una funzione",
            "Quanti input riceve? (parametri) Quali hanno senso come default?",
            "Cosa restituisce? (`return` valore) o solo stampa?",
            "Ha una responsabilità sola? Se fa N cose → N funzioni",
        ],
        "pattern": [
            "Nome che descrive l'azione: `calcola_`, `ottieni_`, `verifica_`, `salva_`",
            "Una funzione = una responsabilità sola",
            "Default parameters per valori comuni: `def f(regione='eu-west-1')`",
            "Testa con input semplici prima di usarla in contesti complessi",
        ],
        "checklist": [
            "Ha `return` se deve dare un valore?",
            "I parametri hanno nomi descrittivi?",
            "Fa una sola cosa?",
            "L'ho chiamata con input limite? (0, lista vuota, None)",
        ],
    },
    "liste_dizionari": {
        "domanda_chiave": "Cosa entra? (lista/dict) Cosa devo ottenere? Filtrare, trasformare o navigare?",
        "prima_di_codificare": [
            "Sequenza ordinata? → lista. Coppie chiave-valore? → dizionario",
            "Devo cercare per posizione o per nome?",
            "La risposta boto3: è una lista di dict o un dict con liste annidate?",
            "Devo filtrare, trasformare, o solo iterare?",
        ],
        "pattern": [
            "Filtra → `[x for x in lista if condizione]`",
            "Trasforma → `[f(x) for x in lista]`",
            "Naviga boto3 → `risposta['Reservations'][0]['Instances']`",
            "Accesso sicuro → `dict.get('chiave', default)` evita KeyError",
        ],
        "checklist": [
            "La lista può essere vuota? Ho gestito quel caso?",
            "La chiave del dict esiste sempre? Se no, uso `.get()`?",
            "boto3: la risposta è una lista o un singolo elemento?",
            "Sto modificando la lista mentre ci itero? (usa list comprehension)",
        ],
    },
    "automazione": {
        "domanda_chiave": "Cosa può andare storto con file e path? (non esiste, permessi, path errato)",
        "prima_di_codificare": [
            "Il file esiste già? Cosa succede se non esiste?",
            "Devo leggere (`r`), sovrascrivere (`w`) o aggiungere (`a`)?",
            "Il path è assoluto o relativo? Funziona su altre macchine?",
            "Devo creare la directory prima di creare il file?",
        ],
        "pattern": [
            "Sempre `with open(...)` — si chiude automaticamente",
            "Costruisci path con `os.path.join()` non con `+`",
            "Crea directory con `exist_ok=True`",
            "Leggi → processa → scrivi (non mescolare lettura e scrittura dello stesso file)",
        ],
        "checklist": [
            "Ho usato `with open(...)` (non `f = open(...)` senza close)?",
            "La modalità è giusta? `w` sovrascrive tutto!",
            "Ho gestito il caso 'file non esiste'?",
            "Il path funziona anche su un'altra macchina?",
        ],
    },
    "errori": {
        "domanda_chiave": "Cosa faccio quando il mondo reale non si comporta come mi aspetto?",
        "prima_di_codificare": [
            "Cosa può andare storto? (rete, file, tipo sbagliato, chiave mancante, permessi)",
            "Se va storto, il programma deve fermarsi o continuare?",
            "Devo comunicare l'errore all'utente o solo loggarlo?",
            "C'è qualcosa che deve succedere sempre, anche in caso di errore? → `finally`",
        ],
        "pattern": [
            "Cattura eccezioni SPECIFICHE, non `except Exception:` generico",
            "Boto3: `except ClientError as e` → `e.response['Error']['Code']`",
            "Logga sempre: almeno un `print(e)` o `logging.error(e)`",
            "`finally`: chiudi connessioni e file — esegue sempre",
        ],
        "checklist": [
            "Ho identificato le eccezioni specifiche che possono accadere?",
            "Il blocco except gestisce l'errore o lo nasconde?",
            "C'è un `finally` per le risorse da chiudere?",
            "Il messaggio di errore è utile per il debug?",
        ],
    },
    "boto3_intro": {
        "domanda_chiave": "Cosa restituisce questa API? Stampa sempre la risposta raw la prima volta.",
        "prima_di_codificare": [
            "In che regione si trovano le risorse? (sempre `region_name` esplicito)",
            "Quali permessi IAM servono per questa operazione?",
            "La risposta è paginata? (liste grandi → usa paginator)",
            "Cosa faccio se la risorsa non esiste? Se non ho i permessi?",
        ],
        "pattern": [
            "Client → chiama API → naviga risposta (dizionario annidato)",
            "Sempre try/except ClientError intorno alle chiamate API",
            "Usa `.get()` per campi opzionali delle risorse",
            "Testa su risorse staging prima di toccare produzione",
        ],
        "checklist": [
            "Ho specificato `region_name` esplicitamente?",
            "Ho gestito `ClientError`?",
            "Ho stampato la risposta raw per capirne la struttura?",
            "Il codice funziona con 0 risorse, 1 risorsa, N risorse?",
        ],
    },

    "kwargs_unpacking": {
        "domanda_chiave": "Sto costruendo questa chiamata staticamente o dinamicamente in base a condizioni?",
        "prima_di_codificare": [
            "I parametri sono sempre gli stessi o variano in base alla logica?",
            "Stai leggendo codice boto3 con `**params`? → stai vedendo un dict spacchettato",
            "La funzione deve essere flessibile? → considera `**kwargs`",
            "Devo includere parametri opzionali solo se presenti? → costruisci dict e usa `**`",
        ],
        "pattern": [
            "`params = {}; if cond: params['K'] = v` → poi `f(**params)` (chiamata dinamica)",
            "`def f(**kwargs): kwargs.get('k', default)` per accesso sicuro ai parametri",
            "`*lista` spacchetta come argomenti posizionali",
            "`**dict` spacchetta come keyword arguments",
        ],
        "checklist": [
            "Ho usato `**` (doppio) per dict e `*` (singolo) per liste?",
            "Le chiavi del dict corrispondono ai nomi dei parametri della funzione?",
            "Il dict non ha chiavi extra non accettate dalla funzione?",
            "boto3: ho verificato quali parametri sono obbligatori vs opzionali nella doc?",
        ],
    },

    "json_env": {
        "domanda_chiave": "Questo dato viene dall'esterno (file, API, env)? → devo deserializzarlo. Va fuori? → devo serializzarlo.",
        "prima_di_codificare": [
            "Ho una stringa da convertire in dict? → `json.loads(stringa)`",
            "Ho un dict da convertire in stringa? → `json.dumps(dict)`",
            "Sto leggendo da file? → `json.load(file_obj)` (senza la s)",
            "Le credenziali devono stare in env var, non nel codice",
        ],
        "pattern": [
            "`os.environ.get('CHIAVE', 'default')` — sempre con default, mai KeyError",
            "`json.dumps(obj, indent=2)` per output leggibile",
            "Config: JSON file per defaults + env var per override in produzione",
            "boto3 legge `AWS_*` env var automaticamente",
        ],
        "checklist": [
            "Sto usando `json.loads` per stringhe o `json.load` per file?",
            "Tutte le env var hanno un default sicuro con `.get()`?",
            "Nessuna credenziale hardcodata nel codice?",
            "Il JSON che genero è valido? Posso verificarlo con `json.loads(json.dumps(obj))`?",
        ],
    },

    "comprehensions": {
        "domanda_chiave": "Cosa devo ottenere? (lista/dict/set) Da cosa parto? Quali elementi filtro o trasformo?",
        "prima_di_codificare": [
            "Sto costruendo una lista? → list comprehension `[...]`",
            "Sto costruendo un mapping? → dict comprehension `{k: v ...}`",
            "La logica è semplice (1 filtro, 1 trasformazione)? → comprehension OK",
            "La logica è complessa (2+ condizioni, side effect)? → loop esplicito",
        ],
        "pattern": [
            "Filtra: `[x for x in lista if condizione]`",
            "Trasforma: `[f(x) for x in lista]`",
            "Filtra+trasforma: `[f(x) for x in lista if condizione]`",
            "Dict: `{x['id']: x['stato'] for x in lista}`",
            "Generator (lazy, no lista in RAM): `sum(x for x in lista)`",
        ],
        "checklist": [
            "L'`if` di filtro sta DOPO il `for`, non prima dell'espressione?",
            "Sto creando una struttura dati o eseguendo azioni? (loop per azioni)",
            "La comprehension è leggibile in una riga? Se no, usa loop",
            "Il tipo è giusto? `[...]` lista, `{...}` set o dict, `(...)` generator",
        ],
    },

    "builtins": {
        "domanda_chiave": "Ho bisogno di indice + valore? (enumerate) Di iterare su più liste? (zip) Di ordine? (sorted)",
        "prima_di_codificare": [
            "Ho bisogno dell'indice E del valore? → `enumerate(lista)`",
            "Devo abbinare elementi di due liste? → `zip(lista1, lista2)`",
            "Devo ordinare per un campo specifico? → `sorted(lista, key=lambda x: x['campo'])`",
            "Un valore potrebbe essere `None`? → usa `is None`, non `== None`",
        ],
        "pattern": [
            "`for i, val in enumerate(lista, start=1)` — numerazione da 1",
            "`for a, b in zip(lista1, lista2)` — parallelo",
            "`sorted(lista, key=lambda x: x['k'], reverse=True)` — decrescente",
            "`val = obj.get('campo')` → `if val is not None: usa(val)`",
        ],
        "checklist": [
            "Ho salvato il risultato di `sorted()`? (non modifica in-place)",
            "Le due liste di `zip` hanno la stessa lunghezza?",
            "Sto controllando `None` con `is None` (non `== None`)?",
            "Ho usato `enumerate` invece di `range(len(lista))`?",
        ],
    },

    "setup_env": {
        "domanda_chiave": "Questo progetto ha un ambiente isolato con le dipendenze fisse?",
        "prima_di_codificare": [
            "Ho creato un venv per questo progetto?",
            "Ho attivato il venv prima di installare?",
            "Ho un requirements.txt aggiornato?",
            "Il .gitignore esclude .venv/?",
        ],
        "pattern": [
            "`python -m venv .venv && source .venv/bin/activate` — crea e attiva",
            "`pip install -r requirements.txt` — installa dipendenze da file",
            "`pip freeze > requirements.txt` — congela versioni correnti",
            "`python -m pip install --upgrade pip` — aggiorna pip prima di tutto",
        ],
        "checklist": [
            "Il terminale mostra (.venv) davanti al prompt?",
            "requirements.txt include le versioni esatte (==)?",
            ".venv è nel .gitignore?",
            "Ho testato `pip install -r requirements.txt` in un venv pulito?",
        ],
    },

    "tipi_operatori": {
        "domanda_chiave": "Questo valore viene dall'esterno? → va castato. Sto assegnando in base a una condizione? → considera il ternario.",
        "prima_di_codificare": [
            "Il valore arriva come stringa (env var, input, file)? → cast esplicito",
            "Il risultato è uno dei due valori? → ternario `x if cond else y`",
            "Sto assegnando e verificando in un if? → walrus `:=`",
            "Sto dividendo per ottenere un intero? → `//` non `/`",
        ],
        "pattern": [
            "`int(os.environ.get('N', '10'))` — env var → int con default",
            "`val = a if condizione else b` — ternario per assegnazione",
            "`while chunk := f.read(1024):` — walrus per loop di lettura",
            "`bool('0')` è True — usa `== '1'` per flag stringa",
        ],
        "checklist": [
            "Ho gestito il caso in cui il cast fallisce (ValueError)?",
            "Il ternario è leggibile in una riga, o è meglio un if/else?",
            "Il walrus è in un contesto dove l'assegnazione è ovvia?",
            "La divisione con `/` ritorna float — è quello che voglio?",
        ],
    },

    "scope_closures": {
        "domanda_chiave": "Da dove viene questo nome? (Local → Enclosing → Global → Built-in)",
        "prima_di_codificare": [
            "La variabile è definita nella funzione corrente? → Local",
            "È in una funzione esterna che la racchiude? → Enclosing",
            "È al top del modulo? → Global",
            "Devo modificare una globale? → dichiara `global` all'inizio della funzione",
        ],
        "pattern": [
            "Lambda per key semplici: `sorted(lista, key=lambda x: x['campo'])`",
            "Closure factory: `def make_fn(param): def fn(x): return param + x; return fn`",
            "`nonlocal` per modificare variabili di funzioni esterne (non globali)",
            "Lambda con default `lambda i=i: i` per catturare valore del loop",
        ],
        "checklist": [
            "Se ottengo UnboundLocalError, ho dimenticato `global`?",
            "La lambda è leggibile in una riga? Se no, usa `def`",
            "La closure cattura il valore o il riferimento?",
            "Sto usando `global` più di una volta? → forse serve una classe",
        ],
    },

    "tuple_immutabilita": {
        "domanda_chiave": "Questi dati devono cambiare? Se no, usa una tupla — è più sicura e più veloce.",
        "prima_di_codificare": [
            "I dati cambiano dopo la creazione? Lista. Non cambiano? Tupla.",
            "Devo usarlo come chiave di dict o in un set? → deve essere hashable → tupla",
            "Sto clonando una struttura annidata? → deepcopy, non copy",
            "Sto facendo unpacking multiplo? → `a, b, *resto = collezione`",
        ],
        "pattern": [
            "`a, b = b, a` — swap elegante con tuple implicita",
            "`x, y, z = punto_3d` — unpacking diretto",
            "`lat, lon = (45.07, 7.69)` — coordinate come tupla",
            "`import copy; clone = copy.deepcopy(obj)` — copia indipendente",
        ],
        "checklist": [
            "La tupla da 1 elemento ha la virgola finale: `(42,)`?",
            "Ho usato deepcopy se la struttura ha liste o dict annidati?",
            "Sto usando tuple come chiave di dict? → solo con elementi immutabili",
            "Ho bisogno di named fields? → considera `namedtuple` o `dataclass`",
        ],
    },

    "controllo_avanzato": {
        "domanda_chiave": "Sto cercando qualcosa? (break+else) Sto filtrando? (continue) Sto classificando? (match/case)",
        "prima_di_codificare": [
            "Esco appena trovo il primo match? → break",
            "Salto elementi non interessanti? → continue (più leggibile di if annidato)",
            "Ho bisogno di sapere se il loop è finito senza trovare? → for/else",
            "Sto classificando un valore in N casi? → match/case (Python 3.10+)",
        ],
        "pattern": [
            "`for x in lista: if cond: risultato = x; break` + `else: risultato = None`",
            "`for x in lista: if not cond: continue; processa(x)` — filtraggio",
            "`match valore: case A: ... case B: ... case _: ...` — default con `_`",
            "`case c if c >= 500:` — guard condition in match",
        ],
        "checklist": [
            "Il for/else è chiaro? Se confonde, usa una variabile booleana `trovato`",
            "Il continue riduce l'indentazione? → allora è utile",
            "match/case: ho il caso `_` come default?",
            "Il while con continue aggiorna la variabile PRIMA del continue?",
        ],
    },

    "generatori": {
        "domanda_chiave": "Ho bisogno di tutti i valori in memoria o li consumo uno alla volta?",
        "prima_di_codificare": [
            "I dati sono enormi o potenzialmente infiniti? → generatore",
            "Sto iterando una risposta boto3 paginata? → usare paginator + yield",
            "Aggrego (sum, max, any)? → generator expression, non list",
            "Ho bisogno di iterare due volte? → list(), perché i generatori si esauriscono",
        ],
        "pattern": [
            "`def gen(): for x in src: yield trasforma(x)` — pipeline lazy",
            "`sum(x**2 for x in range(n))` — aggregazione senza lista",
            "`from itertools import islice; list(islice(gen, 10))` — prendi solo N",
            "`yield from sotto_generatore` — delegare a un sotto-generatore",
        ],
        "checklist": [
            "Ho tenuto conto che il generatore si esaurisce?",
            "Se itero più volte, ho convertito in lista?",
            "Il generatore infinito usa islice o condizione di uscita?",
            "Sto usando `yield from` invece di un loop `for x in sub: yield x`?",
        ],
    },

    "oop_base": {
        "domanda_chiave": "Ho più oggetti dello stesso tipo con stato e comportamento? → classe.",
        "prima_di_codificare": [
            "Cosa rappresenta questa classe? (una risorsa, un client, un risultato?)",
            "Quali dati ha ogni istanza? → attributi in `__init__`",
            "Quali azioni può fare? → metodi",
            "Condivide attributi/metodi con un'altra classe? → ereditarietà",
        ],
        "pattern": [
            "`def __init__(self, *args): self.x = x` — inizializza attributi",
            "`super().__init__(...)` — delega al genitore",
            "Attributi di classe solo per costanti: `REGIONE_DEFAULT = 'eu-west-1'`",
            "Metodi che non usano self → `@staticmethod`",
        ],
        "checklist": [
            "Ogni metodo ha `self` come primo parametro?",
            "Gli attributi mutabili (liste) sono in `__init__`, non nella classe?",
            "Ho chiamato `super().__init__()` nel figlio?",
            "La classe fa UNA cosa? Se fa troppo, spezzala",
        ],
    },

    "oop_avanzata": {
        "domanda_chiave": "Voglio che Python tratti il mio oggetto come un nativo? → implementa i dunder giusti.",
        "prima_di_codificare": [
            "Voglio `print(obj)` leggibile? → `__str__`",
            "Voglio `repr(obj)` per debug? → `__repr__`",
            "Voglio `len(obj)`? → `__len__`",
            "Voglio `obj == altro`? → `__eq__` (e poi `__hash__`)",
        ],
        "pattern": [
            "`@property` per attributi calcolati (senza parentesi)",
            "`@classmethod def from_dict(cls, d)` — factory costruttore alternativo",
            "`@dataclass` elimina `__init__`, `__repr__`, `__eq__` boilerplate",
            "`field(default_factory=list)` per attributi mutabili in dataclass",
        ],
        "checklist": [
            "Ho definito `__hash__` dopo aver definito `__eq__`?",
            "La property ha setter se è modificabile?",
            "Il @classmethod ha `cls` come primo parametro (non `self`)?",
            "Il dataclass usa `field(default_factory=...)` per liste/dict?",
        ],
    },

    "decoratori": {
        "domanda_chiave": "Questo comportamento si ripete su più funzioni? → decoratore.",
        "prima_di_codificare": [
            "Il decoratore aggiunge logging/timing/retry/auth? → pattern classico",
            "Il decoratore ha parametri? → serve una funzione che ritorna un decoratore",
            "Sto preservando il nome e la docstring? → `@functools.wraps`",
            "La funzione ha sempre gli stessi input? → considera `@lru_cache`",
        ],
        "pattern": [
            "`def dec(func): @wraps(func) def wrapper(*a,**kw): ...; return func(*a,**kw); return wrapper`",
            "`def dec(n): def decorator(func): ... return decorator` — con parametri",
            "`@lru_cache(maxsize=None)` — cache illimitata per funzioni pure",
            "`functools.partial(f, arg=val)` — funzione con argomenti parziali",
        ],
        "checklist": [
            "Ho usato `@functools.wraps(func)` nel wrapper?",
            "Il decoratore con parametri ha tre livelli di nesting?",
            "Se uso `@lru_cache`, gli argomenti sono hashable?",
            "Il decoratore ritorna `wrapper`, non `wrapper()`?",
        ],
    },

    "moduli_package": {
        "domanda_chiave": "Questo codice verrà importato o eseguito direttamente? → `__name__` guard.",
        "prima_di_codificare": [
            "Il modulo può essere sia importato che eseguito? → `if __name__ == '__main__':`",
            "Sto loggando eventi? → `logging`, non `print`",
            "Conto occorrenze? → `Counter`. Aggrego in liste/dict? → `defaultdict`",
            "Importo da un package interno? → import relativo `from . import modulo`",
        ],
        "pattern": [
            "`logger = logging.getLogger(__name__)` — logger per modulo",
            "`logging.basicConfig(level=logging.INFO)` — configurazione base",
            "`Counter(lista).most_common(n)` — top N elementi",
            "`defaultdict(list); d[chiave].append(val)` — senza KeyError",
        ],
        "checklist": [
            "Lo script ha `if __name__ == '__main__':` per il codice eseguibile?",
            "Sto usando `logger.info/warning/error` invece di `print`?",
            "Il format del log include timestamp e livello?",
            "Ho evitato import circolari (A importa B, B importa A)?",
        ],
    },

    "eccezioni_avanzate": {
        "domanda_chiave": "Sto comunicando un errore di dominio? → eccezione custom. Sto garantendo cleanup? → contextmanager.",
        "prima_di_codificare": [
            "L'eccezione porta informazioni strutturate? → classe custom con attributi",
            "Devo preservare la causa originale? → `raise NuovoErrore() from e`",
            "L'assert è per invarianti di sviluppo o validazione utente? → solo invarianti",
            "Ho una risorsa da rilasciare sempre? → contextmanager con finally",
        ],
        "pattern": [
            "`class MioErrore(Exception): def __init__(self, msg, dati): super().__init__(msg); self.dati = dati`",
            "`raise ValueError('messaggio') from causa_originale`",
            "`@contextmanager def risorsa(): ...; yield r; finally: cleanup()`",
            "`assert condizione, 'messaggio'` — solo per invarianti, mai per validazione",
        ],
        "checklist": [
            "L'eccezione custom estende la classe giusta (ValueError, RuntimeError, ecc.)?",
            "Ho usato `raise ... from e` per preservare il contesto?",
            "Il contextmanager ha `try/finally` intorno allo yield?",
            "L'assert è disabilitabile senza rompere la logica?",
        ],
    },
}

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

def _ol(out: str) -> set[str]:
    """Righe normalizzate (strip) dell'output, vuote escluse. Per check esatti su singole righe."""
    return {l.strip() for l in out.strip().splitlines() if l.strip()}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CURRICULUM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CURRICULUM = [
    {
        "id": "variabili", "title": "Variabili e Tipi",
        "icon": "📦", "world": "🌱 Foresta del Principiante",
        "teoria": """
### Cos'è una variabile?
Una variabile è una **scatola con un'etichetta** dove conservi un valore.

```python
nome    = "Lorenzo"   # stringa (testo)
eta     = 28          # intero
altezza = 1.78        # decimale (float)
attivo  = True        # booleano (vero/falso)
```

Python capisce da solo il tipo — non devi dichiararlo.

**Funzioni utili:** `type(x)` · `print(x)`
""",
        "esempio": 'nome = "Lorenzo"\neta = 28\nprint(f"Ciao {nome}, hai {eta} anni")\nprint(type(eta))\nprint(type(nome))',
        "esercizi": [
            {
                "testo": 'Crea una variabile `marca` con il valore `"Triumph"` e stampala.',
                "placeholder": '# Scrivi qui\nmarca = ...\nprint(...)',
                "check": lambda out, err, vs: err is None and out.strip() == "Triumph",
                "feedback": lambda out, err: 'Scrivi `marca = "Triumph"` e poi `print(marca)`',
                "hint": 'marca = "Triumph"\nprint(marca)',
                "xp_bonus": 0,
            },
            {
                "testo": "Crea `a = 10` e `b = 3`, poi stampa la loro **somma**, **differenza** e **divisione** su righe separate.",
                "placeholder": "a = 10\nb = 3\n# tre print()",
                "check": lambda out, err, vs: err is None and "13" in _ol(out) and "7" in _ol(out) and any("3.3" in l for l in _ol(out)),
                "feedback": lambda out, err: (
                    "Manca la somma (13)" if "13" not in out else
                    "Manca la differenza (7)" if "7" not in out else
                    "La divisione deve mostrare 3.3 — `print(a/b)` stampa il risultato decimale"
                ),
                "hint": "print(a+b)\nprint(a-b)\nprint(a/b)",
                "xp_bonus": 0,
            },
            {
                "testo": "🏆 **BOSS**: Crea `nome`, `eta` e `professione` e stampa: `Lorenzo ha 28 anni ed è Cloud Engineer` usando una f-string.",
                "placeholder": 'nome = "..."\neta = ...\nprofessione = "..."\nprint(f"...")',
                "check": lambda out, err, vs: err is None and "anni" in out and "ed è" in out and len(out.strip()) > 10,
                "feedback": lambda out, err: 'La frase deve contenere "anni" e "ed è" — usa `f"{nome} ha {eta} anni ed è {professione}"`',
                "hint": 'print(f"{nome} ha {eta} anni ed è {professione}")',
                "xp_bonus": 10,
            },
            {
                "tipo": "predict",
                "testo": "🔍 **PREVEDI**: Cosa stamperà questo codice? Ragiona senza eseguirlo, poi verifica.",
                "codice": "x = 10\ny = x\nx = 99\nprint(y)\nprint(x)",
                "expected": "10\n99",
                "hint": "`y = x` copia il VALORE di x in quel momento. Poi x cambia, ma y non ne sa nulla.",
                "xp_bonus": 5,
            },
        ],
    },
    {
        "id": "stringhe", "title": "Stringhe",
        "icon": "✏️", "world": "🌿 Grotta del Testo",
        "teoria": """
### Lavorare con il testo
```python
s = "hello world"
print(s.upper())               # HELLO WORLD
print(s.capitalize())          # Hello world
print(s.replace("world","py")) # hello py
print(len(s))                  # 11
print(s[0])                    # h
print(s[-1])                   # d
print(s[0:5])                  # hello (slice)
```

**f-string:**
```python
print(f"Ciao {nome}, sei di {citta}!")
```
""",
        "esempio": 'cert = "aws cloud practitioner"\nprint(cert.upper())\nprint(cert.title())\nprint(f"Lunghezza: {len(cert)} caratteri")',
        "esercizi": [
            {
                "testo": 'Data `testo = "python è fantastico"`, stampala in **maiuscolo** e con la **prima lettera maiuscola**.',
                "placeholder": 'testo = "python è fantastico"\n# .upper() e .capitalize()',
                "check": lambda out, err, vs: err is None and "PYTHON" in out and "Python" in out,
                "feedback": lambda out, err: (
                    "Manca la versione in maiuscolo — usa `.upper()`" if "PYTHON" not in out else
                    "Manca la versione con prima lettera maiuscola — usa `.capitalize()`"
                ),
                "hint": "print(testo.upper())\nprint(testo.capitalize())",
                "xp_bonus": 0,
            },
            {
                "testo": 'Con `bucket_name = "mio-bucket-lorenzo"`, stampa: `Bucket S3: mio-bucket-lorenzo` usando una f-string.',
                "placeholder": 'bucket_name = "mio-bucket-lorenzo"\n# f-string',
                "check": lambda out, err, vs: err is None and "Bucket S3: mio-bucket-lorenzo" in out.strip(),
                "feedback": lambda out, err: 'L\'output deve essere esattamente `Bucket S3: mio-bucket-lorenzo` — controlla spazi e maiuscole',
                "hint": 'print(f"Bucket S3: {bucket_name}")',
                "xp_bonus": 0,
            },
            {
                "testo": '🏆 **BOSS**: Data `"  Hello AWS World  "`, stampa: versione senza spazi laterali + versione invertita (`.strip()` e `[::-1]`).',
                "placeholder": 's = "  Hello AWS World  "\n# strip e inverti',
                "check": lambda out, err, vs: err is None and "Hello AWS World" in out and "dlroW" in out,
                "feedback": lambda out, err: (
                    "Usa `.strip()` per rimuovere gli spazi laterali" if "Hello AWS World" not in out else
                    "Per invertire usa lo slicing `[::-1]`"
                ),
                "hint": "print(s.strip())\nprint(s.strip()[::-1])",
                "xp_bonus": 10,
            },
        ],
    },
    {
        "id": "condizioni", "title": "Condizioni",
        "icon": "🔀", "world": "🌳 Bivio delle Scelte",
        "teoria": """
### if / elif / else
```python
eta = 20
if eta >= 18:
    print("Maggiorenne")
elif eta >= 13:
    print("Adolescente")
else:
    print("Bambino")
```

| Operatore | Significato |
|-----------|-------------|
| `==` | uguale | `!=` | diverso |
| `>` `<` | maggiore/minore | `>=` `<=` | maggiore-uguale/minore-uguale |

**Logici:** `and` · `or` · `not`
""",
        "esempio": 'credito_aws = 150\nif credito_aws > 100:\n    print("Credito abbondante")\nelif credito_aws > 0:\n    print("Credito limitato")\nelse:\n    print("Nessun credito!")',
        "esercizi": [
            {
                "testo": 'Se `temperatura = 38.5` è > 37.5 stampa `"Febbre"`, altrimenti `"OK"`.',
                "placeholder": "temperatura = 38.5\n# if / else",
                "check": lambda out, err, vs: err is None and out.strip() == "Febbre",
                "feedback": lambda out, err: 'Con 38.5 la condizione `> 37.5` è vera → devi stampare "Febbre"',
                "hint": 'if temperatura > 37.5:\n    print("Febbre")\nelse:\n    print("OK")',
                "xp_bonus": 0,
            },
            {
                "testo": 'Con `ruolo = "admin"` e `attivo = True`, stampa `"Accesso consentito"` solo se **entrambe** vere.',
                "placeholder": 'ruolo = "admin"\nattivo = True\n# usa and',
                "check": lambda out, err, vs: err is None and out.strip() == "Accesso consentito",
                "feedback": lambda out, err: 'Usa `and` per combinare le due condizioni: `if ruolo == "admin" and attivo:`',
                "hint": 'if ruolo == "admin" and attivo:\n    print("Accesso consentito")',
                "xp_bonus": 0,
            },
            {
                "testo": '🏆 **BOSS**: `score = 820` → se ≥900 `"Outstanding"`, ≥800 `"Pass"`, ≥700 `"Borderline"`, altrimenti `"Fail"`.',
                "placeholder": "score = 820\n# if / elif / elif / else",
                "check": lambda out, err, vs: err is None and "Pass" in _ol(out),
                "feedback": lambda out, err: "Con score=820 il risultato deve essere 'Pass' — controlla l'ordine delle condizioni",
                "hint": 'if score >= 900:\n    print("Outstanding")\nelif score >= 800:\n    print("Pass")\nelif score >= 700:\n    print("Borderline")\nelse:\n    print("Fail")',
                "xp_bonus": 10,
            },
            {
                "tipo": "debug",
                "testo": "🐛 **DEBUG**: Questo codice dovrebbe stampare solo i numeri positivi, ma ha 2 bug di sintassi. Trovali e correggili.",
                "placeholder": "numeri = [3, -1, 7, -4, 2]\nfor n in numeri\n    if n > 0\n        print(n)",
                "check": lambda out, err, vs: err is None and {"3","7","2"}.issubset(_ol(out)) and not {"-1","-4"} & _ol(out),
                "feedback": lambda out, err: "In Python `for` e `if` devono finire con `:` — controlla entrambe le righe",
                "hint": "Aggiungi `:` dopo `for n in numeri` e dopo `if n > 0`",
                "xp_bonus": 0,
            },
        ],
    },
    {
        "id": "cicli", "title": "Cicli",
        "icon": "🔁", "world": "🏔️ Montagna della Ripetizione",
        "teoria": """
### for e while
```python
for r in ["eu-west-1", "us-east-1"]:
    print(r)

for i in range(5):   # 0,1,2,3,4
    print(i)

n = 0
while n < 3:
    print(f"Step {n}")
    n += 1
```
""",
        "esempio": 'regioni = ["eu-west-1", "us-east-1", "ap-southeast-1"]\nfor r in regioni:\n    print(f"Regione: {r}")',
        "esercizi": [
            {
                "testo": "Stampa i numeri da 1 a 5 usando `range()`.",
                "placeholder": "# for + range",
                "check": lambda out, err, vs: err is None and {str(i) for i in range(1, 6)}.issubset(_ol(out)),
                "feedback": lambda out, err: "Usa `range(1, 6)` — il secondo valore è escluso, quindi 6 per arrivare a 5",
                "hint": "for i in range(1, 6):\n    print(i)",
                "xp_bonus": 0,
            },
            {
                "testo": "Con `numeri = [1,2,3,4,5]`, stampa solo i **pari** (`n % 2 == 0`).",
                "placeholder": "numeri = [1, 2, 3, 4, 5]\nfor n in numeri:\n    pass",
                "check": lambda out, err, vs: err is None and {"2","4"}.issubset(_ol(out)) and not {"1","3","5"} & _ol(out),
                "feedback": lambda out, err: "Dentro il for aggiungi `if n % 2 == 0:` prima del print",
                "hint": "for n in numeri:\n    if n % 2 == 0:\n        print(n)",
                "xp_bonus": 0,
            },
            {
                "testo": "🏆 **BOSS**: Stampa la **tavola del 7** da 1 a 10 nel formato `7 x 1 = 7`.",
                "placeholder": "# for loop con range(1, 11)",
                "check": lambda out, err, vs: err is None and "7 x 1 = 7" in out and "7 x 10 = 70" in out,
                "feedback": lambda out, err: "Usa `print(f'7 x {i} = {7*i}')` dentro `for i in range(1, 11)`",
                "hint": "for i in range(1, 11):\n    print(f'7 x {i} = {7*i}')",
                "xp_bonus": 10,
            },
            {
                "tipo": "predict",
                "testo": "🔍 **PREVEDI**: Tracci la variabile `totale` passo per passo. Cosa stamperà questo codice?",
                "codice": "totale = 0\nfor i in range(1, 5):\n    totale += i\n    print(totale)",
                "expected": "1\n3\n6\n10",
                "hint": "range(1,5) genera 1,2,3,4. Traccia: 0+1=1, 1+2=3, 3+3=6, 6+4=10. Stampa ad ogni passo.",
                "xp_bonus": 5,
            },
        ],
    },
    {
        "id": "funzioni", "title": "Funzioni",
        "icon": "⚙️", "world": "🏛️ Tempio della Riusabilità",
        "teoria": """
### Riusa il codice
```python
def saluta(nome):
    return f"Ciao, {nome}!"

print(saluta("Lorenzo"))   # Ciao, Lorenzo!
```

**Parametri di default:**
```python
def connetti(regione="eu-west-1", porta=443):
    print(f"→ {regione}:{porta}")
```
""",
        "esempio": 'def calcola_costo_ec2(ore, prezzo_orario=0.023):\n    totale = ore * prezzo_orario\n    return round(totale, 4)\n\nprint(calcola_costo_ec2(24))\nprint(calcola_costo_ec2(730))',
        "esercizi": [
            {
                "testo": "Scrivi `doppio(n)` che restituisce il doppio di `n`. Stampa `doppio(7)`.",
                "placeholder": "def doppio(n):\n    pass\n\nprint(doppio(7))",
                "check": lambda out, err, vs: err is None and "14" in _ol(out),
                "feedback": lambda out, err: "La funzione deve `return n * 2` — `pass` non fa nulla",
                "hint": "def doppio(n):\n    return n * 2\n\nprint(doppio(7))",
                "xp_bonus": 0,
            },
            {
                "testo": 'Scrivi `saluta_utente(nome, servizio="AWS")` che stampa `"Benvenuto Lorenzo su AWS"`.',
                "placeholder": 'def saluta_utente(nome, servizio="AWS"):\n    pass\n\nsaluta_utente("Lorenzo")',
                "check": lambda out, err, vs: err is None and "Lorenzo" in out and "AWS" in out,
                "feedback": lambda out, err: 'Dentro la funzione: `print(f"Benvenuto {nome} su {servizio}")`',
                "hint": 'def saluta_utente(nome, servizio="AWS"):\n    print(f"Benvenuto {nome} su {servizio}")\n\nsaluta_utente("Lorenzo")',
                "xp_bonus": 0,
            },
            {
                "testo": "🏆 **BOSS**: Scrivi `calcola_sconto(prezzo, sconto_pct=10)` che restituisce il prezzo scontato. Stampa il prezzo di 200€ con sconto 25%.",
                "placeholder": "def calcola_sconto(prezzo, sconto_pct=10):\n    pass\n\nprint(calcola_sconto(200, 25))",
                "check": lambda out, err, vs: err is None and "150" in out,
                "feedback": lambda out, err: "200 con sconto 25% = 150. Formula: `prezzo * (1 - sconto_pct/100)`",
                "hint": "def calcola_sconto(prezzo, sconto_pct=10):\n    return prezzo * (1 - sconto_pct/100)\n\nprint(calcola_sconto(200, 25))",
                "xp_bonus": 10,
            },
        ],
    },
    {
        "id": "liste_dizionari", "title": "Liste e Dizionari",
        "icon": "📋", "world": "🗂️ Archivio dei Dati",
        "teoria": """
### Liste
```python
bucket = ["log-bucket", "data-bucket"]
bucket.append("new-bucket")
print(bucket[0])      # primo elemento
```

### Dizionari — chiave → valore
```python
istanza = {"id": "i-0abc123", "tipo": "t3.micro"}
print(istanza["tipo"])       # t3.micro
istanza["stato"] = "running" # aggiunge chiave
```

> ⚡ Tutte le risposte boto3 sono **dizionari**.
""",
        "esempio": 'ist = {"id": "i-0abc123", "tipo": "t3.micro", "regione": "eu-west-1"}\nfor k, v in ist.items():\n    print(f"{k}: {v}")',
        "esercizi": [
            {
                "testo": 'Crea `servizi = ["EC2", "S3", "Lambda"]`, aggiungi `"RDS"` con `.append()` e stampa.',
                "placeholder": 'servizi = ["EC2", "S3", "Lambda"]\n# append e print',
                "check": lambda out, err, vs: err is None and "RDS" in out and "EC2" in out,
                "feedback": lambda out, err: (
                    "Usa `servizi.append('RDS')` prima del print" if "RDS" not in out else
                    "Stampa la lista con `print(servizi)`"
                ),
                "hint": 'servizi.append("RDS")\nprint(servizi)',
                "xp_bonus": 0,
            },
            {
                "testo": "Crea un dizionario `utente` con chiavi `nome`, `ruolo`, `regione`. Stampa solo il valore di `ruolo`.",
                "placeholder": 'utente = {\n    "nome": "...",\n    "ruolo": "...",\n    "regione": "..."\n}\nprint(...)',
                "check": lambda out, err, vs: err is None and len(out.strip()) > 0,
                "feedback": lambda out, err: 'Accedi con `utente["ruolo"]`',
                "hint": 'print(utente["ruolo"])',
                "xp_bonus": 0,
            },
            {
                "testo": "🏆 **BOSS**: Lista di dizionari con 3 servizi AWS (chiavi: `nome`, `costo_mensile`). Stampa solo quelli con costo > 50.",
                "placeholder": 'servizi = [\n    {"nome": "EC2", "costo_mensile": 80},\n    {"nome": "S3",  "costo_mensile": 5},\n    {"nome": "RDS", "costo_mensile": 120},\n]\n# filtra e stampa',
                "check": lambda out, err, vs: err is None and ("EC2" in out or "RDS" in out) and "S3" not in out,
                "feedback": lambda out, err: 'Loop sulla lista: `for s in servizi: if s["costo_mensile"] > 50: print(s["nome"])`',
                "hint": 'for s in servizi:\n    if s["costo_mensile"] > 50:\n        print(s["nome"])',
                "xp_bonus": 10,
            },
            {
                "tipo": "debug",
                "testo": "🐛 **DEBUG**: Questo codice vuole stampare il costo di ogni servizio e il totale, ma ha 2 bug. Trovali.",
                "placeholder": (
                    'servizi = [\n'
                    '    {"nome": "EC2", "costo": 70},\n'
                    '    {"nome": "RDS", "costo": 105},\n'
                    ']\n'
                    'totale = 0\n'
                    'for s in servizi:\n'
                    '    print(f"{s[nome]}: ${s[\'costo\']}")  # BUG 1\n'
                    '    totale =+ s["costo"]               # BUG 2\n'
                    'print(f"Totale: ${totale}")\n'
                ),
                "check": lambda out, err, vs: err is None and "EC2" in out.strip() and "175" in out,
                "feedback": lambda out, err: "BUG 1: `s[nome]` → `s['nome']` (mancano le virgolette). BUG 2: `=+` non esiste → usa `+=`",
                "hint": "Correggi: `s['nome']` e `totale += s['costo']`",
                "xp_bonus": 0,
            },
            {
                "testo": "🏆 **BOSS**: Usa una **list comprehension** per ottenere i quadrati dei numeri pari da 1 a 10. Stampa il risultato.",
                "placeholder": "numeri = list(range(1, 11))\nquadrati_pari = [...]  # una riga sola\nprint(quadrati_pari)",
                "check": lambda out, err, vs: err is None and all(s in out for s in ["4","16","36","64","100"]),
                "feedback": lambda out, err: "Formato: `[x**2 for x in numeri if x % 2 == 0]`",
                "hint": "[x**2 for x in numeri if x % 2 == 0]",
                "xp_bonus": 15,
            },
        ],
    },
    {
        "id": "automazione", "title": "Automazione e File",
        "icon": "🤖", "world": "🏭 Fabbrica dell'Automazione",
        "teoria": """
### File
```python
with open("output.txt", "w") as f:
    f.write("Log\\n")
with open("output.txt", "r") as f:
    print(f.read())
```

### os
```python
import os
print(os.getcwd())
os.makedirs("backup", exist_ok=True)
for f in os.listdir("."):
    if f.endswith(".log"):
        print(f"Archivia: {f}")
```
""",
        "esempio": 'import os\nfiles = ["report.csv", "log_jan.log", "data.json", "backup.log"]\nfor f in files:\n    tag = "[ARCHIVIA]" if f.endswith(".log") else "[MANTIENI] "\n    print(f"{tag} {f}")',
        "esercizi": [
            {
                "testo": "Usa `os.getcwd()` per stampare la directory corrente.",
                "placeholder": "import os\nprint(...)",
                "check": lambda out, err, vs: err is None and len(out.strip()) > 0,
                "feedback": lambda out, err: "Scrivi `print(os.getcwd())` dopo l'import",
                "hint": "print(os.getcwd())",
                "xp_bonus": 0,
            },
            {
                "testo": 'Data `nomi = ["Mario", "Luigi", "Peach"]`, stampali tutti in **maiuscolo** con un ciclo.',
                "placeholder": 'nomi = ["Mario", "Luigi", "Peach"]\nfor n in nomi:\n    print(...)',
                "check": lambda out, err, vs: err is None and "MARIO" in out and "LUIGI" in out and "PEACH" in out,
                "feedback": lambda out, err: "Dentro il for usa `print(n.upper())`",
                "hint": "print(n.upper())",
                "xp_bonus": 0,
            },
            {
                "testo": "🏆 **BOSS**: Conta quanti `.log`, `.csv` e `.json` ci sono nella lista e stampa il report.",
                "placeholder": 'files = ["app.log","data.csv","run.log","config.json","err.log","report.csv"]\n# conta per estensione',
                "check": lambda out, err, vs: err is None and "3" in out and "2" in out and "1" in out,
                "feedback": lambda out, err: 'Usa un dizionario contatore o `collections.Counter` sulle estensioni',
                "hint": 'from collections import Counter\nexts = [f.split(".")[-1] for f in files]\nfor ext, n in Counter(exts).items():\n    print(f"{ext}: {n}")',
                "xp_bonus": 10,
            },
        ],
    },
    {
        "id": "errori", "title": "Gestione Errori",
        "icon": "🛡️", "world": "⚔️ Dungeon degli Errori",
        "teoria": """
### try / except — difenditi dagli imprevisti
Il codice reale fallisce. La rete cade, il file non esiste, la chiave manca.
`try/except` ti permette di gestirlo invece di crashare.

```python
try:
    risultato = 10 / 0
except ZeroDivisionError:
    print("Impossibile dividere per zero")
```

### Cattura eccezioni specifiche
```python
try:
    valore = diz["chiave_che_non_esiste"]
except KeyError as e:
    print(f"Chiave mancante: {e}")
except TypeError as e:
    print(f"Tipo sbagliato: {e}")
```

### finally — esegue sempre
```python
try:
    f = open("file.txt")
    dati = f.read()
except FileNotFoundError:
    print("File non trovato")
finally:
    print("Operazione terminata")  # gira sempre
```

### In boto3 — il pattern fondamentale
```python
from botocore.exceptions import ClientError

try:
    s3.get_object(Bucket="mio-bucket", Key="file.txt")
except ClientError as e:
    codice = e.response["Error"]["Code"]
    if codice == "NoSuchKey":
        print("File non esiste")
    elif codice == "AccessDenied":
        print("Permessi insufficienti")
```
""",
        "esempio": (
            'def dividi(a, b):\n'
            '    try:\n'
            '        return a / b\n'
            '    except ZeroDivisionError:\n'
            '        print("Errore: divisione per zero!")\n'
            '        return None\n'
            '\n'
            'print(dividi(10, 2))   # 5.0\n'
            'print(dividi(10, 0))   # gestito\n'
            'print(dividi(10, 4))   # 2.5'
        ),
        "esercizi": [
            {
                "testo": "Scrivi un `try/except` che prova ad accedere a `dati[\"nome\"]` e stampa `\"Chiave non trovata\"` se la chiave manca.",
                "placeholder": 'dati = {"eta": 28}\n\ntry:\n    print(dati["nome"])\nexcept ...:\n    print("Chiave non trovata")',
                "check": lambda out, err, vs: err is None and "Chiave non trovata" in out.strip(),
                "feedback": lambda out, err: "Usa `except KeyError:` per catturare un accesso a chiave mancante",
                "hint": 'except KeyError:\n    print("Chiave non trovata")',
                "xp_bonus": 0,
            },
            {
                "tipo": "debug",
                "testo": "🐛 **DEBUG**: Questo codice ha l'eccezione sbagliata — non cattura mai l'errore reale. Correggi.",
                "placeholder": (
                    'numeri = [10, 0, 5]\n'
                    'for n in numeri:\n'
                    '    try:\n'
                    '        print(100 / n)\n'
                    '    except ValueError:    # BUG: eccezione sbagliata\n'
                    '        print(f"Impossibile dividere per {n}")\n'
                ),
                "check": lambda out, err, vs: err is None and "Impossibile dividere per 0" in out.strip() and "10.0" in _ol(out),
                "feedback": lambda out, err: "La divisione per zero lancia `ZeroDivisionError`, non `ValueError`",
                "hint": "Cambia `ValueError` in `ZeroDivisionError`",
                "xp_bonus": 0,
            },
            {
                "tipo": "predict",
                "testo": "🔍 **PREVEDI**: Questo codice itera su valori di tipo diverso. Cosa stamperà? Ragiona su ogni iterazione.",
                "codice": (
                    'for v in [5, "ciao", 0, 2]:\n'
                    '    try:\n'
                    '        print(f"OK: {10 / v:.1f}")\n'
                    '    except ZeroDivisionError:\n'
                    '        print("ZERO")\n'
                    '    except TypeError:\n'
                    '        print("TIPO SBAGLIATO")\n'
                ),
                "expected": "OK: 2.0\nTIPO SBAGLIATO\nZERO\nOK: 5.0",
                "hint": "5→ok (2.0), 'ciao'→TypeError, 0→ZeroDivision, 2→ok (5.0). Quale except scatta in ogni caso?",
                "xp_bonus": 5,
            },
            {
                "testo": '🏆 **BOSS**: Funzione `accedi_bucket(nome)` — usa try/except con 2 eccezioni distinte + finally che stampa sempre `"Connessione chiusa"`.',
                "placeholder": (
                    'def accedi_bucket(nome):\n'
                    '    db = {"prod-logs": "dati critici", "dev-logs": "dati test"}\n'
                    '    try:\n'
                    '        pass\n'
                    '    except KeyError:\n'
                    '        pass\n'
                    '    finally:\n'
                    '        pass\n'
                    '\n'
                    'accedi_bucket("prod-logs")\n'
                    'accedi_bucket("bucket-inesistente")\n'
                ),
                "check": lambda out, err, vs: (
                    err is None
                    and out.lower().count("connessione chiusa") >= 2
                    and ("dati" in out.lower() or "prod" in out.lower())
                    and ("non esiste" in out.lower() or "trovato" in out.lower() or "inesistente" in out.lower())
                ),
                "feedback": lambda out, err: "Il finally deve stampare 'Connessione chiusa' 2 volte (una per ogni chiamata). Aggiungi messaggi per bucket trovato e non trovato.",
                "hint": (
                    'def accedi_bucket(nome):\n'
                    '    db = {"prod-logs": "dati critici", "dev-logs": "dati test"}\n'
                    '    try:\n'
                    '        print(f"Accesso OK: {db[nome]}")\n'
                    '    except KeyError:\n'
                    '        print(f"Bucket non esiste: {nome}")\n'
                    '    finally:\n'
                    '        print("Connessione chiusa")\n'
                    '\n'
                    'accedi_bucket("prod-logs")\n'
                    'accedi_bucket("bucket-inesistente")\n'
                ),
                "xp_bonus": 10,
            },
        ],
    },
    {
        "id": "setup_env", "title": "Setup e Ambiente",
        "icon": "🖥️", "world": "🏗️ Cantiere di Setup",
        "teoria": """
### Virtual environment — stanza isolata per ogni progetto
```bash
python -m venv .venv                  # crea l'ambiente
source .venv/bin/activate             # attiva (Linux/Mac)
.venv\\Scripts\\activate               # attiva (Windows)
```

### pip — installa librerie
```bash
pip install boto3 streamlit           # installa
pip freeze > requirements.txt        # congela versioni
pip install -r requirements.txt      # installa da file
```

### requirements.txt
```
boto3==1.34.0
streamlit==1.40.0
requests==2.31.0
```

### Strumenti moderni
```bash
pip install uv        # pip alternativo, molto più veloce
uv pip install boto3  # stesso interfaccia di pip
```

### Controllare l'ambiente da Python
```python
import sys
print(sys.version)        # 3.11.5
print(sys.executable)     # /path/to/.venv/bin/python
print(sys.version_info)   # sys.version_info(major=3, minor=11, ...)
```
""",
        "esempio": (
            'import sys\n'
            '\n'
            'print(f"Python {sys.version_info.major}.{sys.version_info.minor}")\n'
            'print(f"Eseguibile: {sys.executable}")\n'
            '\n'
            'if sys.version_info >= (3, 8):\n'
            '    print("Versione supportata")\n'
            'else:\n'
            '    print("Aggiorna Python!")'
        ),
        "esercizi": [
            {
                "testo": "Stampa la versione Python corrente nel formato `Python X.Y` usando `sys.version_info`.",
                "placeholder": "import sys\nprint(f\"Python {sys.version_info...}\")",
                "check": lambda out, err, vs: err is None and "Python 3." in out.strip(),
                "feedback": lambda out, err: "Usa sys.version_info.major e sys.version_info.minor",
                "hint": "print(f\"Python {sys.version_info.major}.{sys.version_info.minor}\")",
                "xp_bonus": 0,
            },
            {
                "testo": "Verifica che la versione Python sia ≥ 3.8. Stampa `OK` se sì, `Aggiorna` se no.",
                "placeholder": "import sys\nif sys.version_info >= (3, 8):\n    print(...)\nelse:\n    print(...)",
                "check": lambda out, err, vs: err is None and ("OK" in out.strip() or "Aggiorna" in out.strip()),
                "feedback": lambda out, err: "sys.version_info >= (3, 8) ritorna True/False",
                "hint": "if sys.version_info >= (3, 8): print('OK')",
                "xp_bonus": 0,
            },
            {
                "testo": "Simula la creazione di un `requirements.txt`: scrivi una lista di pacchetti con versioni (`boto3==1.34.0`, `streamlit==1.40.0`, `requests==2.31.0`) e stampali uno per riga.",
                "placeholder": "pacchetti = [\n    \"boto3==1.34.0\",\n    # aggiungi gli altri\n]\nfor p in pacchetti:\n    print(p)",
                "check": lambda out, err, vs: err is None and "boto3" in out and "streamlit" in out and "==" in out,
                "feedback": lambda out, err: "Stampa ogni pacchetto con la versione usando ==",
                "hint": 'pacchetti = [\n    "boto3==1.34.0",\n    "streamlit==1.40.0",\n    "requests==2.31.0",\n]\nfor p in pacchetti:\n    print(p)',
                "xp_bonus": 0,
            },
            {
                "tipo": "predict",
                "testo": "🔍 **PREVEDI**: Cosa stamperà questo codice? Attenzione al tipo di `sys.version_info`.",
                "codice": (
                    'import sys\n'
                    'info = sys.version_info\n'
                    'print(type(info).__name__)\n'
                    'print(info.major)\n'
                    'print(info >= (3, 10))\n'
                ),
                "expected": "version_info\n3\nTrue",
                "hint": "sys.version_info è una namedtuple: ha campi con nome come .major (sempre 3 in Python 3). Il confronto con la tupla (3, 10) dà True su Python 3.10+.",
                "xp_bonus": 5,
            },
            {
                "testo": "🏆 **BOSS**: Scrivi `verifica_ambiente()` che controlla: (1) Python ≥ 3.8, (2) se `boto3` è importabile. Stampa un report con OK/MANCANTE per ogni check.",
                "placeholder": (
                    'import sys\n'
                    '\n'
                    'def verifica_ambiente():\n'
                    '    # check 1: versione Python\n'
                    '    py_ok = sys.version_info >= (3, 8)\n'
                    '    print(f"Python 3.8+: {\'OK\' if py_ok else \'AGGIORNA\'}")\n'
                    '    \n'
                    '    # check 2: boto3 importabile\n'
                    '    try:\n'
                    '        import boto3\n'
                    '        print("boto3: OK")\n'
                    '    except ImportError:\n'
                    '        print("boto3: MANCANTE")\n'
                    '\n'
                    'verifica_ambiente()'
                ),
                "check": lambda out, err, vs: err is None and "Python 3.8+" in out and ("OK" in out or "MANCANTE" in out),
                "feedback": lambda out, err: "La funzione deve stampare il risultato di ogni check",
                "hint": "try: import boto3; print('boto3: OK') except ImportError: print('boto3: MANCANTE')",
                "xp_bonus": 10,
            },
        ],
    },
    {
        "id": "tipi_operatori", "title": "Tipi, Casting e Operatori",
        "icon": "🔢", "world": "⚗️ Laboratorio dei Tipi",
        "teoria": """
### Casting — conversione di tipo
```python
int("42")        # 42
float("3.14")    # 3.14
str(100)         # "100"
bool(0)          # False — 0, "", [], {}, None sono falsy
bool("0")        # True  — stringa non vuota!
int(float("3.9")) # 3  — int() tronca, non arrotonda
```

### Operatore ternario
```python
# x = valore_se_vero if condizione else valore_se_falso
stato = "attiva" if credito > 0 else "bloccata"
etichetta = nome if nome else "Anonimo"
```

### Walrus operator `:=` (Python 3.8+)
```python
# Assegna E verifica in un'unica espressione
import re
if m := re.search(r'ERROR: (.+)', riga_log):
    print(f"Errore trovato: {m.group(1)}")

while chunk := file.read(8192):
    processa(chunk)
```

### Divisione
```python
10 / 3    # 3.3333  (float sempre)
10 // 3   # 3       (intero)
10 % 3    # 1       (resto)
```
""",
        "esempio": (
            'import os\n'
            '\n'
            '# Env var → numeri con default\n'
            'timeout   = int(os.environ.get("TIMEOUT", "30"))\n'
            'max_retry = int(os.environ.get("MAX_RETRY", "3"))\n'
            '\n'
            'print(f"Timeout: {timeout}s, Retry: {max_retry}")\n'
            '\n'
            '# Ternary\n'
            'credito = 15.0\n'
            'stato = "OK" if credito > 0 else "ESAURITO"\n'
            'print(f"Credito AWS: {stato}")\n'
            '\n'
            '# Divisione intera\n'
            'pagine = 150 // 20\n'
            'print(f"Pagine da richiedere: {pagine}")'
        ),
        "esercizi": [
            {
                "testo": 'Converti la stringa `"42"` in intero, sommala a `8`, e stampa il risultato.',
                "placeholder": 'n = "42"\nrisultato = int(...) + 8\nprint(risultato)',
                "check": lambda out, err, vs: err is None and "50" in _ol(out),
                "feedback": lambda out, err: "int('42') converte la stringa in intero, poi somma normalmente",
                "hint": "int(n) + 8",
                "xp_bonus": 0,
            },
            {
                "testo": 'Con `nome = ""`, usa il ternario per stampare `"Utente"` se nome è vuoto, altrimenti il nome stesso.',
                "placeholder": 'nome = ""\nresult = nome if nome else "Utente"\nprint(result)',
                "check": lambda out, err, vs: err is None and out.strip() == "Utente",
                "feedback": lambda out, err: 'nome if nome else "Utente" — stringa vuota è falsy',
                "hint": 'print(nome if nome else "Utente")',
                "xp_bonus": 0,
            },
            {
                "testo": "Hai `100` oggetti S3 da listare a `20` per pagina. Calcola il numero di pagine intere con divisione intera.",
                "placeholder": 'totale = 100\nper_pagina = 20\npagine = ...\nprint(f"Pagine: {pagine}")',
                "check": lambda out, err, vs: err is None and "5" in _ol(out),
                "feedback": lambda out, err: "100 // 20 = 5 pagine esatte",
                "hint": "totale // per_pagina",
                "xp_bonus": 0,
            },
            {
                "tipo": "predict",
                "testo": '🔍 **PREVEDI**: Cosa stamperà questo codice? Attenzione ai valori falsy.',
                "codice": (
                    'valori = [0, 1, "", "0", [], [1], None, False, True]\n'
                    'for v in valori:\n'
                    '    print(bool(v))\n'
                ),
                "expected": "False\nTrue\nFalse\nTrue\nFalse\nTrue\nFalse\nFalse\nTrue",
                "hint": "Falsy: 0, '', [], {}, None, False. Tutto il resto è truthy — anche '0' e [0]!",
                "xp_bonus": 5,
            },
            {
                "testo": '🏆 **BOSS**: Scrivi `parse_config(d)` che legge da un dict di stringhe e ritorna i valori castati: `timeout` → int, `rate` → float, `debug` → bool (`"1"` = True).',
                "placeholder": (
                    'def parse_config(d):\n'
                    '    return {\n'
                    '        "timeout": int(d.get("timeout", "30")),\n'
                    '        "rate":    float(d.get("rate", "1.5")),\n'
                    '        "debug":   d.get("debug", "0") == "1",\n'
                    '    }\n'
                    '\n'
                    'cfg = parse_config({"timeout": "60", "debug": "1"})\n'
                    'print(cfg["timeout"], type(cfg["timeout"]).__name__)\n'
                    'print(cfg["debug"],   type(cfg["debug"]).__name__)'
                ),
                "check": lambda out, err, vs: err is None and "60 int" in out and "True bool" in out,
                "feedback": lambda out, err: "Il cast deve produrre int per timeout e bool True per debug='1'",
                "hint": 'd.get("debug", "0") == "1"  →  True quando il valore è la stringa "1"',
                "xp_bonus": 10,
            },
        ],
    },
    {
        "id": "scope_closures", "title": "Scope, Lambda e Closures",
        "icon": "🔍", "world": "🧅 Labirinto degli Scope",
        "teoria": """
### LEGB — ordine di ricerca dei nomi
Python cerca un nome in questo ordine:
1. **L**ocal — dentro la funzione corrente
2. **E**nclosing — funzione esterna che la racchiude
3. **G**lobal — livello del modulo
4. **B**uilt-in — `len`, `print`, `range`, ...

```python
x = "globale"

def outer():
    x = "enclosing"
    def inner():
        print(x)   # trova "enclosing" (E)
    inner()

outer()
print(x)           # trova "globale" (G)
```

### global e nonlocal
```python
contatore = 0

def incrementa():
    global contatore   # modifica la globale
    contatore += 1
```

### Lambda — funzione anonima
```python
doppio = lambda x: x * 2
print(doppio(5))   # 10

# Usata come key per sorted
istanze = sorted(istanze, key=lambda x: x["costo_ora"])
```

### Closures
```python
def make_moltiplicatore(n):
    def moltiplica(x):
        return x * n   # cattura `n` dall'Enclosing
    return moltiplica

doppio = make_moltiplicatore(2)
triplo = make_moltiplicatore(3)
print(doppio(5))  # 10
print(triplo(5))  # 15
```
""",
        "esempio": (
            '# Lambda + sorted\n'
            'risorse = [\n'
            '    {"nome": "db",  "costo": 0.192},\n'
            '    {"nome": "web", "costo": 0.096},\n'
            '    {"nome": "worker", "costo": 0.023},\n'
            ']\n'
            '\n'
            'per_costo = sorted(risorse, key=lambda r: r["costo"], reverse=True)\n'
            'for r in per_costo:\n'
            '    print(f"{r[\'nome\']}: ${r[\'costo\']}")\n'
            '\n'
            '# Closure factory\n'
            'def make_tagger(prefisso):\n'
            '    def tagger(nome):\n'
            '        return f"{prefisso}-{nome}"\n'
            '    return tagger\n'
            '\n'
            'tag_prod = make_tagger("prod")\n'
            'print(tag_prod("web-server"))'
        ),
        "esercizi": [
            {
                "testo": "Scrivi una lambda `quadrato` che calcola il quadrato di un numero. Stampa `quadrato(7)`.",
                "placeholder": "quadrato = lambda x: ...\nprint(quadrato(7))",
                "check": lambda out, err, vs: err is None and "49" in _ol(out),
                "feedback": lambda out, err: "lambda x: x ** 2",
                "hint": "quadrato = lambda x: x ** 2\nprint(quadrato(7))",
                "xp_bonus": 0,
            },
            {
                "testo": "Ordina `nomi = ['banana', 'Mela', 'ciliegia', 'Arancia']` in ordine alfabetico ignorando maiuscole/minuscole. Stampa la lista ordinata.",
                "placeholder": 'nomi = ["banana", "Mela", "ciliegia", "Arancia"]\nordinati = sorted(nomi, key=lambda s: ...)\nprint(ordinati)',
                "check": lambda out, err, vs: err is None and "Arancia" in out and out.index("Arancia") < out.index("banana"),
                "feedback": lambda out, err: "key=lambda s: s.lower() rende il confronto case-insensitive",
                "hint": 'nomi = ["banana", "Mela", "ciliegia", "Arancia"]\nordinati = sorted(nomi, key=lambda s: s.lower())\nprint(ordinati)',
                "xp_bonus": 0,
            },
            {
                "testo": "Scrivi `make_moltiplicatore(n)` che ritorna una funzione che moltiplica per `n`. Crea `triplo` e stampa `triplo(7)`.",
                "placeholder": "def make_moltiplicatore(n):\n    def fn(x):\n        return ...\n    return fn\n\ntriplo = make_moltiplicatore(3)\nprint(triplo(7))",
                "check": lambda out, err, vs: err is None and "21" in _ol(out),
                "feedback": lambda out, err: "La funzione interna deve usare `n` dall'Enclosing scope: `return x * n`",
                "hint": "return x * n",
                "xp_bonus": 0,
            },
            {
                "tipo": "predict",
                "testo": "🔍 **PREVEDI**: Cosa stamperà questo codice? Traccia quale `x` usa ogni funzione.",
                "codice": (
                    'x = 10\n'
                    '\n'
                    'def f():\n'
                    '    x = 20\n'
                    '    def g():\n'
                    '        print(x)\n'
                    '    g()\n'
                    '    x = 30\n'
                    '    g()\n'
                    '\n'
                    'f()\n'
                    'print(x)\n'
                ),
                "expected": "20\n30\n10",
                "hint": "g() legge la x di f() nel momento in cui viene ESEGUITA, non quando è definita. 1ª g(): x vale 20. Poi x diventa 30 → 2ª g(): stampa 30. Infine print(x) usa la x globale: 10.",
                "xp_bonus": 5,
            },
            {
                "testo": '🏆 **BOSS**: Scrivi `make_filtro(soglia)` che ritorna una funzione `filtra(lista)`. `filtra` deve restituire solo gli elementi maggiori della soglia. Testa con soglia=50.',
                "placeholder": (
                    'def make_filtro(soglia):\n'
                    '    def filtra(lista):\n'
                    '        return [x for x in lista if x > soglia]\n'
                    '    return filtra\n'
                    '\n'
                    'filtra_50 = make_filtro(50)\n'
                    'print(filtra_50([20, 60, 40, 80, 10, 70]))'
                ),
                "check": lambda out, err, vs: err is None and "60" in out and "80" in out and "70" in out and "20" not in out,
                "feedback": lambda out, err: "La closure deve catturare `soglia` e usarla nella list comprehension",
                "hint": "return [x for x in lista if x > soglia]",
                "xp_bonus": 10,
            },
        ],
    },
    {
        "id": "tuple_immutabilita", "title": "Tuple e Mutabilità",
        "icon": "🔒", "world": "🏛️ Tempio dell'Immutabilità",
        "teoria": """
### Tuple — sequenze immutabili
```python
punto = (45.07, 7.69)   # non modificabile
lat, lon = punto        # unpacking

# Tupla da 1 elemento: la virgola è obbligatoria!
singolo = (42,)         # tuple
non_tupla = (42)        # solo int tra parentesi
```

### Quando usare tuple vs lista
| Lista `[]` | Tupla `()` |
|-----------|-----------|
| Modificabile | Immutabile |
| Elementi omogenei | Elementi eterogenei |
| Iterare, aggiungere | Dati fissi, chiavi dict |

### Mutabilità — cosa può cambiare
```python
lista = [1, 2, 3]    # mutabile
lista[0] = 99        # ok

tupla = (1, 2, 3)    # immutabile
tupla[0] = 99        # TypeError!
```

### copy vs deepcopy
```python
import copy

originale = {"lista": [1, 2, 3]}

superficiale = copy.copy(originale)
superficiale["lista"].append(4)   # modifica ANCHE originale!

profonda = copy.deepcopy(originale)
profonda["lista"].append(5)       # originale intatto
```
""",
        "esempio": (
            'import copy\n'
            '\n'
            '# Tuple unpacking elegante\n'
            'nome, eta, ruolo = ("Lorenzo", 28, "Cloud Engineer")\n'
            'print(f"{nome}, {eta} anni, {ruolo}")\n'
            '\n'
            '# Swap con tupla\n'
            'a, b = 10, 20\n'
            'a, b = b, a\n'
            'print(f"a={a}, b={b}")\n'
            '\n'
            '# deepcopy\n'
            'config = {"regioni": ["eu-west-1", "us-east-1"]}\n'
            'config_prod = copy.deepcopy(config)\n'
            'config_prod["regioni"].append("ap-southeast-1")\n'
            'print("originale:", config["regioni"])\n'
            'print("prod:     ", config_prod["regioni"])'
        ),
        "esercizi": [
            {
                "testo": "Crea una tupla `coordinate = (45.07, 7.69)` e fai unpacking in `lat` e `lon`. Stampa entrambe.",
                "placeholder": "coordinate = (45.07, 7.69)\nlat, lon = ...\nprint(lat, lon)",
                "check": lambda out, err, vs: err is None and "45.07" in out and "7.69" in out,
                "feedback": lambda out, err: "lat, lon = coordinate  — unpacking diretto",
                "hint": "lat, lon = coordinate",
                "xp_bonus": 0,
            },
            {
                "testo": "Usa la sintassi tupla per fare swap: `a = 10, b = 20`. Dopo lo swap stampa `a=20, b=10`.",
                "placeholder": "a, b = 10, 20\na, b = ...\nprint(f\"a={a}, b={b}\")",
                "check": lambda out, err, vs: err is None and "a=20, b=10" in out.strip(),
                "feedback": lambda out, err: "a, b = b, a  — Python crea una tupla temporanea",
                "hint": "a, b = b, a",
                "xp_bonus": 0,
            },
            {
                "testo": "Dimostra la differenza tra `copy.copy` e `copy.deepcopy` su `{'tags': ['prod']}`. Aggiungi `'dev'` alla copia superficiale e mostra che l'originale è cambiato.",
                "placeholder": (
                    'import copy\n'
                    'orig = {"tags": ["prod"]}\n'
                    'sup  = copy.copy(orig)\n'
                    'sup["tags"].append("dev")\n'
                    'print("orig:", orig["tags"])\n'
                    'print("sup: ", sup["tags"])'
                ),
                "check": lambda out, err, vs: err is None and "dev" in out.split("orig:")[1].split("\n")[0],
                "feedback": lambda out, err: "copy.copy condivide la lista interna — modificarla cambia anche l'originale",
                "hint": "La prima riga dopo 'orig:' deve contenere 'dev'",
                "xp_bonus": 0,
            },
            {
                "tipo": "debug",
                "testo": "🐛 **DEBUG**: Questo codice ha 2 bug legati a tuple e mutabilità.",
                "placeholder": (
                    'import copy\n'
                    '\n'
                    't = (42)          # BUG 1: non è una tupla\n'
                    'print(type(t).__name__)\n'
                    '\n'
                    'originale = [1, 2, 3]\n'
                    'copia = copy.copy(originale)\n'
                    'copia.append(4)\n'
                    'print(originale)  # BUG 2: non cambia con liste flat — ma stampa "Non modificato"'
                ),
                "check": lambda out, err, vs: err is None and "tuple" in out and "Non modificato" in out,
                "feedback": lambda out, err: "BUG 1: (42,) non (42). BUG 2: per liste flat copy.copy è ok — aggiungi print('Non modificato')",
                "hint": "t = (42,)  e  print('Non modificato')",
                "xp_bonus": 0,
            },
            {
                "tipo": "predict",
                "testo": "🔍 **PREVEDI**: Cosa stamperà questo codice? Attenzione a cosa condivide copy.copy.",
                "codice": (
                    'import copy\n'
                    'a = {"k": [1, 2]}\n'
                    'b = copy.copy(a)\n'
                    'b["k"].append(3)\n'
                    'b["nuovo"] = "x"\n'
                    'print(a["k"])\n'
                    'print("nuovo" in a)\n'
                ),
                "expected": "[1, 2, 3]\nFalse",
                "hint": "copy.copy condivide gli oggetti interni (la lista). Ma aggiungere una chiave al dict copia non tocca il dict originale.",
                "xp_bonus": 5,
            },
        ],
    },
    {
        "id": "controllo_avanzato", "title": "Controllo Avanzato",
        "icon": "🔀", "world": "🌲 Foresta delle Decisioni",
        "teoria": """
### break e continue
```python
# break — esci subito dal loop
for ist in istanze:
    if ist["stato"] == "running":
        prima_running = ist
        break   # non serve continuare

# continue — salta questa iterazione
for ist in istanze:
    if ist["stato"] == "stopped":
        continue   # non interessano
    print(f"Attiva: {ist['id']}")
```

### for/else e while/else
```python
# else esegue SOLO se il loop non ha fatto break
for ist in istanze:
    if ist["id"] == target:
        print("Trovato!")
        break
else:
    print("Non trovato — cerca in un'altra regione")
```

### match/case (Python 3.10+)
```python
def classifica_http(codice):
    match codice:
        case 200:
            return "OK"
        case 404:
            return "Non trovato"
        case c if c >= 500:
            return f"Errore server ({c})"
        case _:
            return "Sconosciuto"
```
""",
        "esempio": (
            'istanze = [\n'
            '    {"id": "i-001", "stato": "stopped"},\n'
            '    {"id": "i-002", "stato": "running"},\n'
            '    {"id": "i-003", "stato": "running"},\n'
            ']\n'
            '\n'
            '# Trova la prima running\n'
            'prima = None\n'
            'for ist in istanze:\n'
            '    if ist["stato"] == "running":\n'
            '        prima = ist\n'
            '        break\n'
            'else:\n'
            '    print("Nessuna istanza running!")\n'
            '\n'
            'if prima:\n'
            '    print(f"Prima running: {prima[\'id\']}")'
        ),
        "esercizi": [
            {
                "testo": "Con `numeri = [3, 7, 2, 9, 1, 6]`, usa `break` per trovare il primo numero maggiore di 8 e stampalo.",
                "placeholder": "numeri = [3, 7, 2, 9, 1, 6]\nfor n in numeri:\n    if n > 8:\n        print(n)\n        break",
                "check": lambda out, err, vs: err is None and "9" in _ol(out),
                "feedback": lambda out, err: "Il primo numero > 8 è 9. Stampa e break.",
                "hint": "if n > 8: print(n); break",
                "xp_bonus": 0,
            },
            {
                "testo": "Con la stessa lista, usa `continue` per stampare solo i numeri pari. Non usare if/else — solo continue.",
                "placeholder": "numeri = [3, 7, 2, 9, 1, 6]\nfor n in numeri:\n    if n % 2 != 0:\n        continue\n    print(n)",
                "check": lambda out, err, vs: err is None and {"2","6"}.issubset(_ol(out)) and not {"3","7","9","1"} & _ol(out),
                "feedback": lambda out, err: "continue salta i dispari — rimangono 2 e 6",
                "hint": "if n % 2 != 0: continue",
                "xp_bonus": 0,
            },
            {
                "testo": "Cerca `'i-005'` nella lista di istanze con `for/else`. Stampa `'Trovato'` se esiste, `'Non trovato'` altrimenti.",
                "placeholder": (
                    'istanze = ["i-001", "i-002", "i-003"]\n'
                    'target = "i-005"\n'
                    'for ist in istanze:\n'
                    '    if ist == target:\n'
                    '        print("Trovato")\n'
                    '        break\n'
                    'else:\n'
                    '    print("Non trovato")'
                ),
                "check": lambda out, err, vs: err is None and out.strip() == "Non trovato",
                "feedback": lambda out, err: "i-005 non è nella lista → il for non fa break → else esegue",
                "hint": "else del for esegue quando non c'è stato break",
                "xp_bonus": 0,
            },
            {
                "testo": "Usa `match/case` per classificare uno status HTTP: `200`→`'OK'`, `404`→`'Non trovato'`, `403`→`'Vietato'`, qualsiasi altro ≥500→`'Errore server'`.",
                "placeholder": (
                    'def classifica(codice):\n'
                    '    match codice:\n'
                    '        case 200: return "OK"\n'
                    '        case 404: return "Non trovato"\n'
                    '        case 403: return "Vietato"\n'
                    '        case c if c >= 500: return "Errore server"\n'
                    '        case _: return "Sconosciuto"\n'
                    '\n'
                    'print(classifica(200))\n'
                    'print(classifica(503))\n'
                    'print(classifica(404))'
                ),
                "check": lambda out, err, vs: err is None and "OK" in out and "Errore server" in out and "Non trovato" in out,
                "feedback": lambda out, err: "Verifica che tutti e tre i print producano l'output corretto",
                "hint": "case c if c >= 500: return 'Errore server'",
                "xp_bonus": 0,
            },
            {
                "testo": "🏆 **BOSS**: Scrivi `cerca_istanza(lista, target_id)` che usa for/break/else e ritorna l'istanza trovata o `None`. Testa con ID presente e assente.",
                "placeholder": (
                    'istanze = [\n'
                    '    {"id": "i-001", "stato": "running"},\n'
                    '    {"id": "i-002", "stato": "stopped"},\n'
                    ']\n'
                    '\n'
                    'def cerca_istanza(lista, target_id):\n'
                    '    for ist in lista:\n'
                    '        if ist["id"] == target_id:\n'
                    '            return ist\n'
                    '    return None\n'
                    '\n'
                    'print(cerca_istanza(istanze, "i-001"))\n'
                    'print(cerca_istanza(istanze, "i-999"))'
                ),
                "check": lambda out, err, vs: err is None and "i-001" in out and "None" in out,
                "feedback": lambda out, err: "La funzione deve trovare i-001 e ritornare None per i-999",
                "hint": "return ist quando trovato, return None dopo il loop",
                "xp_bonus": 10,
            },
        ],
    },
    {
        "id": "generatori", "title": "Generatori e Iteratori",
        "icon": "⚡", "world": "🌊 Fiume dei Dati",
        "teoria": """
### yield — genera valori uno alla volta
```python
def conta(n):
    for i in range(n):
        yield i   # pausa, ritorna i, riprende dopo

for x in conta(3):
    print(x)   # 0, 1, 2
```

### Generatori vs Liste
```python
# Lista — tutto in memoria subito
lista = [x**2 for x in range(1_000_000)]   # ~8 MB

# Generatore — un valore alla volta
gen   = (x**2 for x in range(1_000_000))   # ~200 bytes
```

### Generator expression
```python
totale = sum(b["size_gb"] * 0.023 for b in buckets)
```

### itertools
```python
from itertools import islice, chain, groupby

# Prendi solo i primi 5 da un generatore
for x in islice(generatore_infinito(), 5):
    print(x)

# Concatena più iterabili
tutti = list(chain([1, 2], [3, 4], [5]))
```

### Pattern boto3 — paginazione lazy
```python
def leggi_oggetti(s3, bucket):
    paginatore = s3.get_paginator("list_objects_v2")
    for pagina in paginatore.paginate(Bucket=bucket):
        for obj in pagina.get("Contents", []):
            yield obj["Key"]
```
""",
        "esempio": (
            'from itertools import islice\n'
            '\n'
            'def pari_infiniti():\n'
            '    n = 0\n'
            '    while True:\n'
            '        yield n\n'
            '        n += 2\n'
            '\n'
            '# Prendi solo i primi 5 pari\n'
            'print(list(islice(pari_infiniti(), 5)))\n'
            '\n'
            '# Generator expression per aggregazione\n'
            'costi = [0.096, 0.023, 0.192, 0.048]\n'
            'totale_mensile = sum(c * 730 for c in costi)\n'
            'print(f"Costo mensile: ${totale_mensile:.2f}")'
        ),
        "esercizi": [
            {
                "testo": "Scrivi un generatore `quadrati(n)` che produce i quadrati di 0, 1, ..., n-1. Stampa i primi 5.",
                "placeholder": "def quadrati(n):\n    for i in range(n):\n        yield ...\n\nprint(list(quadrati(5)))",
                "check": lambda out, err, vs: err is None and "[0, 1, 4, 9, 16]" in out.strip(),
                "feedback": lambda out, err: "yield i**2 dentro il for loop",
                "hint": "yield i**2",
                "xp_bonus": 0,
            },
            {
                "testo": "Usa una generator expression per calcolare la somma dei quadrati da 1 a 10.",
                "placeholder": "totale = sum(... for i in range(1, 11))\nprint(totale)",
                "check": lambda out, err, vs: err is None and "385" in _ol(out),
                "feedback": lambda out, err: "sum(i**2 for i in range(1, 11)) = 385",
                "hint": "totale = sum(i**2 for i in range(1, 11))\nprint(totale)",
                "xp_bonus": 0,
            },
            {
                "tipo": "predict",
                "testo": "🔍 **PREVEDI**: Cosa stamperà questo codice? Attenzione all'esaurimento del generatore.",
                "codice": (
                    'gen = (x * 2 for x in range(3))\n'
                    'print(list(gen))\n'
                    'print(list(gen))\n'
                    'print(next(gen, "ESAURITO"))\n'
                ),
                "expected": "[0, 2, 4]\n[]\nESAURITO",
                "hint": "Il generatore si esaurisce dopo il primo list(). Il secondo list() è vuoto. next() con default ritorna 'ESAURITO'.",
                "xp_bonus": 5,
            },
            {
                "testo": "Usa `itertools.islice` per prendere solo i primi 5 elementi da un generatore infinito di numeri dispari.",
                "placeholder": (
                    'from itertools import islice\n'
                    '\n'
                    'def dispari_infiniti():\n'
                    '    n = 1\n'
                    '    while True:\n'
                    '        yield n\n'
                    '        n += 2\n'
                    '\n'
                    'print(list(islice(dispari_infiniti(), 5)))'
                ),
                "check": lambda out, err, vs: err is None and "[1, 3, 5, 7, 9]" in out.strip(),
                "feedback": lambda out, err: "islice(generatore, n) prende i primi n elementi",
                "hint": "list(islice(dispari_infiniti(), 5))",
                "xp_bonus": 0,
            },
            {
                "testo": "🏆 **BOSS**: Scrivi `leggi_log(righe)` generatore che riceve una lista di stringhe e produce solo le righe che contengono `'ERROR'`, senza caricarle tutte in memoria.",
                "placeholder": (
                    'def leggi_log(righe):\n'
                    '    for riga in righe:\n'
                    '        if "ERROR" in riga:\n'
                    '            yield riga\n'
                    '\n'
                    'log = [\n'
                    '    "INFO avvio",\n'
                    '    "ERROR timeout connessione",\n'
                    '    "INFO ok",\n'
                    '    "ERROR disco pieno",\n'
                    '    "WARNING cpu alta",\n'
                    ']\n'
                    '\n'
                    'for errore in leggi_log(log):\n'
                    '    print(errore)'
                ),
                "check": lambda out, err, vs: err is None and "timeout" in out and "disco" in out and "INFO" not in out,
                "feedback": lambda out, err: "Il generatore deve filtrare solo le righe ERROR e non stampare le INFO",
                "hint": "if 'ERROR' in riga: yield riga",
                "xp_bonus": 10,
            },
        ],
    },
    {
        "id": "oop_base", "title": "OOP Base",
        "icon": "🏗️", "world": "🏛️ Accademia degli Oggetti",
        "teoria": """
### Classe e istanza
```python
class AWSResource:
    SERVIZI = ["EC2", "S3", "RDS"]   # attributo di classe

    def __init__(self, id, regione):
        self.id      = id            # attributo di istanza
        self.regione = regione

    def arn(self):
        return f"arn:aws:::{self.regione}:{self.id}"

# Crea istanze
server = AWSResource("i-001", "eu-west-1")
db     = AWSResource("db-001", "us-east-1")

print(server.arn())   # ogni istanza ha il suo ARN
```

### Ereditarietà
```python
class EC2(AWSResource):
    def __init__(self, id, regione, tipo):
        super().__init__(id, regione)   # chiama il genitore
        self.tipo = tipo

    def costo_mensile(self, prezzo_ora):
        return round(prezzo_ora * 730, 2)

server = EC2("i-001", "eu-west-1", "t3.micro")
print(server.arn())            # ereditato
print(server.costo_mensile(0.023))  # 16.79
```
""",
        "esempio": (
            'class Istanza:\n'
            '    def __init__(self, id, tipo, stato="stopped"):\n'
            '        self.id    = id\n'
            '        self.tipo  = tipo\n'
            '        self.stato = stato\n'
            '\n'
            '    def avvia(self):\n'
            '        self.stato = "running"\n'
            '        print(f"{self.id} avviata")\n'
            '\n'
            '    def info(self):\n'
            '        return f"{self.id} ({self.tipo}) → {self.stato}"\n'
            '\n'
            'server = Istanza("i-001", "t3.micro")\n'
            'print(server.info())\n'
            'server.avvia()\n'
            'print(server.info())'
        ),
        "esercizi": [
            {
                "testo": "Crea una classe `Bucket` con `__init__(self, nome, regione)` e un metodo `uri()` che ritorna `s3://{nome}`. Stampa `uri()` per un bucket `logs` in `eu-west-1`.",
                "placeholder": (
                    'class Bucket:\n'
                    '    def __init__(self, nome, regione):\n'
                    '        self.nome   = nome\n'
                    '        self.regione = regione\n'
                    '\n'
                    '    def uri(self):\n'
                    '        return f"s3://{self.nome}"\n'
                    '\n'
                    'b = Bucket("logs", "eu-west-1")\n'
                    'print(b.uri())'
                ),
                "check": lambda out, err, vs: err is None and "s3://logs" in out.strip(),
                "feedback": lambda out, err: "uri() deve ritornare f's3://{self.nome}'",
                "hint": 'return f"s3://{self.nome}"',
                "xp_bonus": 0,
            },
            {
                "testo": "Aggiungi a `Bucket` un metodo `aggiungi_tag(self, chiave, valore)` che salva i tag in un dizionario `self.tags`. Aggiungi `env=prod` e stampa `b.tags`.",
                "placeholder": (
                    'class Bucket:\n'
                    '    def __init__(self, nome, regione):\n'
                    '        self.nome    = nome\n'
                    '        self.regione = regione\n'
                    '        self.tags    = {}\n'
                    '\n'
                    '    def aggiungi_tag(self, chiave, valore):\n'
                    '        self.tags[chiave] = valore\n'
                    '\n'
                    'b = Bucket("logs", "eu-west-1")\n'
                    'b.aggiungi_tag("env", "prod")\n'
                    'print(b.tags)'
                ),
                "check": lambda out, err, vs: err is None and "env" in out and "prod" in out,
                "feedback": lambda out, err: "self.tags[chiave] = valore aggiunge al dizionario",
                "hint": "self.tags[chiave] = valore",
                "xp_bonus": 0,
            },
            {
                "testo": "Crea `EC2(Bucket)` che estende `Bucket` e aggiunge `tipo_istanza`. Usa `super().__init__()`. Stampa `uri()` (ereditato) e `tipo_istanza`.",
                "placeholder": (
                    'class Bucket:\n'
                    '    def __init__(self, nome, regione):\n'
                    '        self.nome    = nome\n'
                    '        self.regione = regione\n'
                    '    def uri(self): return f"s3://{self.nome}"\n'
                    '\n'
                    'class EC2(Bucket):\n'
                    '    def __init__(self, nome, regione, tipo_istanza):\n'
                    '        super().__init__(nome, regione)\n'
                    '        self.tipo_istanza = tipo_istanza\n'
                    '\n'
                    'vm = EC2("web-server", "eu-west-1", "t3.micro")\n'
                    'print(vm.uri())\n'
                    'print(vm.tipo_istanza)'
                ),
                "check": lambda out, err, vs: err is None and "s3://web-server" in out and "t3.micro" in out,
                "feedback": lambda out, err: "super().__init__() inizializza il genitore, poi aggiunge tipo_istanza",
                "hint": "super().__init__(nome, regione)",
                "xp_bonus": 0,
            },
            {
                "tipo": "predict",
                "testo": "🔍 **PREVEDI**: Cosa stamperà questo codice? Attenzione agli attributi di classe vs istanza.",
                "codice": (
                    'class Counter:\n'
                    '    totale = 0\n'
                    '    def __init__(self, nome):\n'
                    '        self.nome = nome\n'
                    '        Counter.totale += 1\n'
                    '\n'
                    'a = Counter("a")\n'
                    'b = Counter("b")\n'
                    'c = Counter("c")\n'
                    'print(Counter.totale)\n'
                    'print(a.totale)\n'
                ),
                "expected": "3\n3",
                "hint": "`totale` è un attributo di classe condiviso. Ogni __init__ lo incrementa. Sia Counter.totale che a.totale puntano allo stesso valore.",
                "xp_bonus": 5,
            },
            {
                "testo": "🏆 **BOSS**: Crea `AWSResource` base con `id, regione, tipo`. Aggiungi `EC2` e `S3Bucket` come sottoclassi con metodo `costo_mensile()` diverso. Stampa i costi di 2 istanze.",
                "placeholder": (
                    'class AWSResource:\n'
                    '    def __init__(self, id, regione, tipo):\n'
                    '        self.id      = id\n'
                    '        self.regione = regione\n'
                    '        self.tipo    = tipo\n'
                    '    def costo_mensile(self):\n'
                    '        raise NotImplementedError\n'
                    '\n'
                    'class EC2(AWSResource):\n'
                    '    def __init__(self, id, regione, prezzo_ora):\n'
                    '        super().__init__(id, regione, "EC2")\n'
                    '        self.prezzo_ora = prezzo_ora\n'
                    '    def costo_mensile(self):\n'
                    '        return round(self.prezzo_ora * 730, 2)\n'
                    '\n'
                    'class S3Bucket(AWSResource):\n'
                    '    def __init__(self, id, regione, gb):\n'
                    '        super().__init__(id, regione, "S3")\n'
                    '        self.gb = gb\n'
                    '    def costo_mensile(self):\n'
                    '        return round(self.gb * 0.023, 2)\n'
                    '\n'
                    'server = EC2("i-001", "eu-west-1", 0.096)\n'
                    'bucket = S3Bucket("logs", "eu-west-1", 500)\n'
                    'print(f"EC2: ${server.costo_mensile()}")\n'
                    'print(f"S3:  ${bucket.costo_mensile()}")'
                ),
                "check": lambda out, err, vs: err is None and "EC2:" in out and "S3:" in out and "$" in out,
                "feedback": lambda out, err: "Le due sottoclassi devono avere costo_mensile() con logiche diverse",
                "hint": "EC2: prezzo_ora * 730. S3: gb * 0.023",
                "xp_bonus": 15,
            },
        ],
    },
    {
        "id": "oop_avanzata", "title": "OOP Avanzata",
        "icon": "🏛️", "world": "⚗️ Laboratorio degli Oggetti",
        "teoria": """
### Metodi dunder — il vocabolario Python
```python
class Risorsa:
    def __init__(self, id, costo):
        self.id    = id
        self.costo = costo

    def __str__(self):           # print(obj)
        return f"Risorsa({self.id})"

    def __repr__(self):          # repr(obj) / debug
        return f"Risorsa(id={self.id!r}, costo={self.costo})"

    def __eq__(self, altro):     # obj1 == obj2
        return self.id == altro.id

    def __lt__(self, altro):     # sorted(), <
        return self.costo < altro.costo
```

### @property
```python
class EC2:
    def __init__(self, prezzo_ora):
        self._prezzo_ora = prezzo_ora

    @property
    def costo_mensile(self):     # accesso: ist.costo_mensile (no parentesi)
        return self._prezzo_ora * 730

    @costo_mensile.setter
    def costo_mensile(self, val):
        self._prezzo_ora = val / 730
```

### @dataclass
```python
from dataclasses import dataclass, field

@dataclass
class Istanza:
    id:      str
    tipo:    str
    regione: str = "eu-west-1"
    tags:    list = field(default_factory=list)
    # __init__, __repr__, __eq__ generati automaticamente
```
""",
        "esempio": (
            'from dataclasses import dataclass, field\n'
            '\n'
            '@dataclass\n'
            'class Bucket:\n'
            '    nome:    str\n'
            '    regione: str = "eu-west-1"\n'
            '    size_gb: float = 0.0\n'
            '    tags:    list = field(default_factory=list)\n'
            '\n'
            '    @property\n'
            '    def costo_mensile(self):\n'
            '        return round(self.size_gb * 0.023, 4)\n'
            '\n'
            '    def __str__(self):\n'
            '        return f"s3://{self.nome} ({self.size_gb}GB)"\n'
            '\n'
            'b = Bucket("prod-logs", size_gb=500)\n'
            'b.tags.append("env:prod")\n'
            'print(b)\n'
            'print(f"Costo: ${b.costo_mensile}")'
        ),
        "esercizi": [
            {
                "testo": "Aggiungi `__str__` a una classe `Istanza(id, tipo)` che ritorna `'EC2 i-001 (t3.micro)'`. Stampa l'istanza con `print()`.",
                "placeholder": (
                    'class Istanza:\n'
                    '    def __init__(self, id, tipo):\n'
                    '        self.id   = id\n'
                    '        self.tipo = tipo\n'
                    '\n'
                    '    def __str__(self):\n'
                    '        return f"EC2 {self.id} ({self.tipo})"\n'
                    '\n'
                    'ist = Istanza("i-001", "t3.micro")\n'
                    'print(ist)'
                ),
                "check": lambda out, err, vs: err is None and "EC2 i-001 (t3.micro)" in out.strip(),
                "feedback": lambda out, err: "__str__ deve ritornare la stringa formattata",
                "hint": 'return f"EC2 {self.id} ({self.tipo})"',
                "xp_bonus": 0,
            },
            {
                "testo": "Crea una classe `Conto` con `@property saldo` (read-only) e metodo `deposita(n)`. Il saldo inizia a 0.",
                "placeholder": (
                    'class Conto:\n'
                    '    def __init__(self):\n'
                    '        self._saldo = 0\n'
                    '\n'
                    '    @property\n'
                    '    def saldo(self):\n'
                    '        return self._saldo\n'
                    '\n'
                    '    def deposita(self, n):\n'
                    '        self._saldo += n\n'
                    '\n'
                    'c = Conto()\n'
                    'c.deposita(100)\n'
                    'c.deposita(50)\n'
                    'print(c.saldo)'
                ),
                "check": lambda out, err, vs: err is None and "150" in _ol(out),
                "feedback": lambda out, err: "deposita incrementa _saldo, saldo lo espone come property",
                "hint": "self._saldo += n",
                "xp_bonus": 0,
            },
            {
                "testo": "Riscrivi `Istanza(id, tipo, regione='eu-west-1')` come `@dataclass`. Verifica che `__repr__` sia generato automaticamente.",
                "placeholder": (
                    'from dataclasses import dataclass\n'
                    '\n'
                    '@dataclass\n'
                    'class Istanza:\n'
                    '    id:      str\n'
                    '    tipo:    str\n'
                    '    regione: str = "eu-west-1"\n'
                    '\n'
                    'ist = Istanza("i-001", "t3.micro")\n'
                    'print(repr(ist))\n'
                    'print(ist.id)'
                ),
                "check": lambda out, err, vs: err is None and "i-001" in out and "t3.micro" in out,
                "feedback": lambda out, err: "@dataclass genera __repr__ automaticamente — deve contenere i valori",
                "hint": "@dataclass genera repr come Istanza(id='i-001', tipo='t3.micro', regione='eu-west-1')",
                "xp_bonus": 0,
            },
            {
                "tipo": "debug",
                "testo": "🐛 **DEBUG**: Questo dataclass ha 2 bug.",
                "placeholder": (
                    'from dataclasses import dataclass\n'
                    '\n'
                    '@dataclass\n'
                    'class Config:\n'
                    '    nome: str\n'
                    '    tags: list = []     # BUG 1: mutable default\n'
                    '    @property\n'
                    '    def etichetta(self):\n'
                    '        return self.nome.upper()\n'
                    '    def etichetta(self, val):  # BUG 2: setter senza decoratore\n'
                    '        self.nome = val.lower()\n'
                    '\n'
                    'c = Config("test")\n'
                    'print(c.etichetta)'
                ),
                "check": lambda out, err, vs: err is None and "TEST" in out.strip(),
                "feedback": lambda out, err: "BUG 1: field(default_factory=list). BUG 2: il setter deve avere @etichetta.setter",
                "hint": "from dataclasses import field  →  tags: list = field(default_factory=list)  |  @etichetta.setter",
                "xp_bonus": 0,
            },
            {
                "testo": "🏆 **BOSS**: Classe `Portfolio` con lista di `Istanza` (dataclass). Aggiungi `__len__` (numero istanze), `__str__` (lista nomi), `costo_totale` come property. Stampa tutto.",
                "placeholder": (
                    'from dataclasses import dataclass, field\n'
                    '\n'
                    '@dataclass\n'
                    'class Istanza:\n'
                    '    id:         str\n'
                    '    costo_ora:  float\n'
                    '\n'
                    'class Portfolio:\n'
                    '    def __init__(self):\n'
                    '        self.istanze = []\n'
                    '    def aggiungi(self, ist): self.istanze.append(ist)\n'
                    '    def __len__(self): return len(self.istanze)\n'
                    '    def __str__(self): return ", ".join(i.id for i in self.istanze)\n'
                    '    @property\n'
                    '    def costo_totale(self): return sum(i.costo_ora * 730 for i in self.istanze)\n'
                    '\n'
                    'p = Portfolio()\n'
                    'p.aggiungi(Istanza("i-001", 0.096))\n'
                    'p.aggiungi(Istanza("i-002", 0.023))\n'
                    'print(len(p))\n'
                    'print(str(p))\n'
                    'print(f"Costo: ${p.costo_totale:.2f}")'
                ),
                "check": lambda out, err, vs: err is None and "2" in _ol(out) and "i-001" in out and "Costo:" in out,
                "feedback": lambda out, err: "len(p) deve dare 2, str(p) i nomi, costo_totale la somma",
                "hint": "sum(i.costo_ora * 730 for i in self.istanze)",
                "xp_bonus": 15,
            },
        ],
    },
    {
        "id": "decoratori", "title": "Decoratori",
        "icon": "🎭", "world": "🎁 Magazzino degli Imballaggi",
        "teoria": """
### Cos'è un decoratore
Un decoratore è una funzione che riceve una funzione e ne ritorna una versione migliorata.

```python
def log(func):
    def wrapper(*args, **kwargs):
        print(f"→ chiamo {func.__name__}")
        risultato = func(*args, **kwargs)
        print(f"← fine {func.__name__}")
        return risultato
    return wrapper

@log                          # equivale a: crea = log(crea)
def crea_bucket(nome):
    print(f"Bucket {nome} creato")
```

### @functools.wraps — preserva i metadati
```python
from functools import wraps

def log(func):
    @wraps(func)   # FONDAMENTALE: preserva __name__, __doc__
    def wrapper(*args, **kwargs):
        ...
    return wrapper
```

### @functools.lru_cache — memoization gratuita
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_prezzo(regione, tipo):
    # chiamata costosa — eseguita solo la prima volta per ogni combo
    return fetch_ec2_price(regione, tipo)
```

### Decoratore con parametri
```python
def retry(n=3, delay=1.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(n):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if i == n - 1: raise
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(n=3, delay=0.5)
def chiama_api(): ...
```
""",
        "esempio": (
            'from functools import wraps, lru_cache\n'
            '\n'
            'def log_chiamata(func):\n'
            '    @wraps(func)\n'
            '    def wrapper(*args, **kwargs):\n'
            '        print(f"→ {func.__name__}({args[0] if args else \'\'!r})")\n'
            '        res = func(*args, **kwargs)\n'
            '        print(f"← OK")\n'
            '        return res\n'
            '    return wrapper\n'
            '\n'
            '@log_chiamata\n'
            'def calcola_costo(ore, prezzo=0.096):\n'
            '    return round(ore * prezzo, 2)\n'
            '\n'
            'print(calcola_costo(730))'
        ),
        "esercizi": [
            {
                "testo": "Scrivi un decoratore `stampa_prima_e_dopo` che stampa `'Inizio'` prima e `'Fine'` dopo la chiamata. Applicalo a `saluta(nome)` che stampa `'Ciao {nome}'`.",
                "placeholder": (
                    'def stampa_prima_e_dopo(func):\n'
                    '    def wrapper(*args, **kwargs):\n'
                    '        print("Inizio")\n'
                    '        func(*args, **kwargs)\n'
                    '        print("Fine")\n'
                    '    return wrapper\n'
                    '\n'
                    '@stampa_prima_e_dopo\n'
                    'def saluta(nome):\n'
                    '    print(f"Ciao {nome}")\n'
                    '\n'
                    'saluta("Lorenzo")'
                ),
                "check": lambda out, err, vs: err is None and "Inizio" in out and "Lorenzo" in out and "Fine" in out,
                "feedback": lambda out, err: "L'output deve avere Inizio, poi Ciao Lorenzo, poi Fine",
                "hint": 'print("Inizio"); func(*args, **kwargs); print("Fine")',
                "xp_bonus": 0,
            },
            {
                "testo": "Aggiungi `@wraps(func)` al decoratore precedente. Verifica che `saluta.__name__` stampi `'saluta'` e non `'wrapper'`.",
                "placeholder": (
                    'from functools import wraps\n'
                    '\n'
                    'def stampa_prima_e_dopo(func):\n'
                    '    @wraps(func)\n'
                    '    def wrapper(*args, **kwargs):\n'
                    '        print("Inizio")\n'
                    '        func(*args, **kwargs)\n'
                    '        print("Fine")\n'
                    '    return wrapper\n'
                    '\n'
                    '@stampa_prima_e_dopo\n'
                    'def saluta(nome):\n'
                    '    print(f"Ciao {nome}")\n'
                    '\n'
                    'print(saluta.__name__)'
                ),
                "check": lambda out, err, vs: err is None and "saluta" in _ol(out),
                "feedback": lambda out, err: "@wraps(func) preserva __name__ — senza di esso stamperebbe 'wrapper'",
                "hint": "@wraps(func) sopra def wrapper",
                "xp_bonus": 0,
            },
            {
                "testo": "Usa `@functools.lru_cache` su `fibonacci(n)` per memoizzarlo. Stampa `fibonacci(10)`.",
                "placeholder": (
                    'from functools import lru_cache\n'
                    '\n'
                    '@lru_cache(maxsize=None)\n'
                    'def fibonacci(n):\n'
                    '    if n <= 1: return n\n'
                    '    return fibonacci(n-1) + fibonacci(n-2)\n'
                    '\n'
                    'print(fibonacci(10))'
                ),
                "check": lambda out, err, vs: err is None and "55" in _ol(out),
                "feedback": lambda out, err: "fibonacci(10) = 55. Con lru_cache ogni risultato viene memorizzato.",
                "hint": "@lru_cache(maxsize=None)",
                "xp_bonus": 0,
            },
            {
                "tipo": "predict",
                "testo": "🔍 **PREVEDI**: In che ordine vengono applicati i decoratori? Cosa stamperà?",
                "codice": (
                    'def a(func):\n'
                    '    def w(*args, **kw):\n'
                    '        print("A inizio")\n'
                    '        func(*args, **kw)\n'
                    '        print("A fine")\n'
                    '    return w\n'
                    '\n'
                    'def b(func):\n'
                    '    def w(*args, **kw):\n'
                    '        print("B inizio")\n'
                    '        func(*args, **kw)\n'
                    '        print("B fine")\n'
                    '    return w\n'
                    '\n'
                    '@a\n'
                    '@b\n'
                    'def f():\n'
                    '    print("f")\n'
                    '\n'
                    'f()\n'
                ),
                "expected": "A inizio\nB inizio\nf\nB fine\nA fine",
                "hint": "@a @b f è uguale a a(b(f)). Il decoratore più esterno (a) avvolge tutto. B è dentro A.",
                "xp_bonus": 5,
            },
            {
                "testo": "🏆 **BOSS**: Scrivi `@retry(n)` che ritenta la funzione fino a `n` volte se lancia un'eccezione. Testalo su una funzione che fallisce le prime 2 volte.",
                "placeholder": (
                    'from functools import wraps\n'
                    '\n'
                    'def retry(n=3):\n'
                    '    def decorator(func):\n'
                    '        @wraps(func)\n'
                    '        def wrapper(*args, **kwargs):\n'
                    '            for tentativo in range(n):\n'
                    '                try:\n'
                    '                    return func(*args, **kwargs)\n'
                    '                except Exception as e:\n'
                    '                    print(f"Tentativo {tentativo+1} fallito")\n'
                    '                    if tentativo == n - 1: raise\n'
                    '        return wrapper\n'
                    '    return decorator\n'
                    '\n'
                    'tentativi = [0]\n'
                    '\n'
                    '@retry(n=3)\n'
                    'def chiama():\n'
                    '    tentativi[0] += 1\n'
                    '    if tentativi[0] < 3:\n'
                    '        raise ValueError("non ancora pronto")\n'
                    '    print("Successo!")\n'
                    '\n'
                    'chiama()'
                ),
                "check": lambda out, err, vs: err is None and "Successo!" in out and "fallito" in out,
                "feedback": lambda out, err: "Il decoratore deve ritentare e stampare i fallimenti, poi Successo al terzo tentativo",
                "hint": "for tentativo in range(n): try: return func(...) except: if tentativo == n-1: raise",
                "xp_bonus": 15,
            },
        ],
    },
    {
        "id": "moduli_package", "title": "Moduli, Logging e Collections",
        "icon": "📦", "world": "📚 Biblioteca Standard",
        "teoria": """
### import e __name__
```python
# Nel file mio_modulo.py
def calcola(): ...

if __name__ == "__main__":
    # Eseguito solo quando lo script è avviato direttamente
    # NON quando è importato da un altro modulo
    calcola()
```

### logging — il modo professionale di loggare
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

logger.debug("Dettaglio per debug")     # solo con level=DEBUG
logger.info("Script avviato")
logger.warning("Credenziali in scadenza")
logger.error("Connessione fallita: %s", e)
```

### collections.Counter
```python
from collections import Counter

log_levels = ["ERROR", "INFO", "ERROR", "WARNING", "ERROR"]
contatore = Counter(log_levels)
print(contatore.most_common(2))  # [('ERROR', 3), ('INFO', 1)]
```

### collections.defaultdict
```python
from collections import defaultdict

per_regione = defaultdict(list)
for ist in istanze:
    per_regione[ist["regione"]].append(ist["id"])
# Nessun KeyError — crea lista vuota automaticamente
```
""",
        "esempio": (
            'import logging\n'
            'from collections import Counter, defaultdict\n'
            '\n'
            'logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")\n'
            'logger = logging.getLogger(__name__)\n'
            '\n'
            'log_simulato = ["ERROR timeout", "INFO ok", "ERROR disco", "WARNING cpu", "ERROR rete"]\n'
            '\n'
            'livelli = Counter(riga.split()[0] for riga in log_simulato)\n'
            'logger.info("Log analizzati: %d", len(log_simulato))\n'
            'print("Top errori:", livelli.most_common(2))'
        ),
        "esercizi": [
            {
                "testo": "Usa `logging` per registrare 3 messaggi: INFO `'Script avviato'`, WARNING `'Memoria alta'`, ERROR `'Connessione persa'`. Configura il formato come `LIVELLO: messaggio`.",
                "placeholder": (
                    'import logging\n'
                    'logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")\n'
                    'logger = logging.getLogger(__name__)\n'
                    '\n'
                    'logger.info("Script avviato")\n'
                    'logger.warning("Memoria alta")\n'
                    'logger.error("Connessione persa")'
                ),
                "check": lambda out, err, vs: err is None and "Script avviato" in out and "Memoria alta" in out,
                "feedback": lambda out, err: "basicConfig con il formato giusto. I messaggi logger vanno su stderr — lo vedi nel blocco output.",
                "hint": 'logger.info("Script avviato")',
                "xp_bonus": 0,
            },
            {
                "testo": "Con `parole = ['boto3','python','boto3','aws','python','boto3']`, usa `Counter` per trovare la parola più frequente e quante volte compare.",
                "placeholder": (
                    'from collections import Counter\n'
                    'parole = ["boto3","python","boto3","aws","python","boto3"]\n'
                    'c = Counter(parole)\n'
                    'parola, freq = c.most_common(1)[0]\n'
                    'print(f"{parola}: {freq}")'
                ),
                "check": lambda out, err, vs: err is None and "boto3: 3" in out.strip(),
                "feedback": lambda out, err: "Counter conta le occorrenze. most_common(1) ritorna la più frequente.",
                "hint": "c.most_common(1)[0] → ('boto3', 3)",
                "xp_bonus": 0,
            },
            {
                "testo": "Con `defaultdict(list)`, raggruppa le istanze per `stato` da una lista di dict. Stampa quante istanze ha ogni stato.",
                "placeholder": (
                    'from collections import defaultdict\n'
                    '\n'
                    'istanze = [\n'
                    '    {"id": "i-001", "stato": "running"},\n'
                    '    {"id": "i-002", "stato": "stopped"},\n'
                    '    {"id": "i-003", "stato": "running"},\n'
                    '    {"id": "i-004", "stato": "stopped"},\n'
                    ']\n'
                    '\n'
                    'per_stato = defaultdict(list)\n'
                    'for ist in istanze:\n'
                    '    per_stato[ist["stato"]].append(ist["id"])\n'
                    '\n'
                    'for stato, ids in per_stato.items():\n'
                    '    print(f"{stato}: {len(ids)}")'
                ),
                "check": lambda out, err, vs: err is None and "running: 2" in out and "stopped: 2" in out,
                "feedback": lambda out, err: "defaultdict(list) crea automaticamente la lista quando accedi a una chiave nuova",
                "hint": "per_stato[ist['stato']].append(ist['id'])",
                "xp_bonus": 0,
            },
            {
                "tipo": "predict",
                "testo": "🔍 **PREVEDI**: Cosa stamperà questo codice? Attenzione al valore di `__name__`.",
                "codice": (
                    'def esegui():\n'
                    '    print("Funzione eseguita")\n'
                    '\n'
                    'print(f"__name__ = {__name__!r}")\n'
                    '\n'
                    'if __name__ == "__main__":\n'
                    '    esegui()\n'
                ),
                "expected": "__name__ = '__main__'\nFunzione eseguita",
                "hint": "Quando uno script è eseguito direttamente, __name__ è '__main__'. Quindi il if è True e esegui() viene chiamato.",
                "xp_bonus": 5,
            },
            {
                "testo": "🏆 **BOSS**: Scrivi `analizza_log(righe)` che usa `Counter` per contare i livelli, `logging` per loggare il risultato, e ritorna il dict dei conteggi.",
                "placeholder": (
                    'import logging\n'
                    'from collections import Counter\n'
                    '\n'
                    'logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")\n'
                    'logger = logging.getLogger(__name__)\n'
                    '\n'
                    'def analizza_log(righe):\n'
                    '    livelli = Counter(r.split()[0] for r in righe if r.strip())\n'
                    '    for livello, n in livelli.most_common():\n'
                    '        logger.info("%s: %d occorrenze", livello, n)\n'
                    '    return dict(livelli)\n'
                    '\n'
                    'log = ["ERROR x","INFO y","ERROR z","WARNING w","INFO a"]\n'
                    'risultato = analizza_log(log)\n'
                    'print(risultato["ERROR"])'
                ),
                "check": lambda out, err, vs: err is None and "2" in _ol(out),
                "feedback": lambda out, err: "Counter conta ERROR=2, INFO=2, WARNING=1. Il print finale deve dare 2.",
                "hint": "Counter(r.split()[0] for r in righe)",
                "xp_bonus": 15,
            },
        ],
    },
    {
        "id": "eccezioni_avanzate", "title": "Eccezioni Avanzate",
        "icon": "🚨", "world": "🔥 Sala di Crisi",
        "teoria": """
### raise — lancia un'eccezione
```python
def dividi(a, b):
    if b == 0:
        raise ValueError("Il divisore non può essere zero")
    return a / b
```

### Eccezioni personalizzate
```python
class BudgetSuperatoError(Exception):
    def __init__(self, budget, spesa):
        self.budget = budget
        self.spesa  = spesa
        super().__init__(f"Spesa {spesa:.2f} supera il budget {budget:.2f}")

try:
    raise BudgetSuperatoError(100, 150)
except BudgetSuperatoError as e:
    print(f"Budget: {e.budget}, Spesa: {e.spesa}")
```

### Exception chaining
```python
try:
    dati = json.loads(testo_malformato)
except json.JSONDecodeError as e:
    raise ValueError("Risposta API non valida") from e
    # Il traceback mostra ENTRAMBE le eccezioni
```

### assert
```python
def calcola(n):
    assert n > 0, f"n deve essere positivo, ricevuto {n}"
    return n * 2
```

### contextlib.contextmanager
```python
from contextlib import contextmanager

@contextmanager
def sessione(nome):
    print(f"Apertura: {nome}")
    try:
        yield nome
    finally:
        print(f"Chiusura: {nome}")

with sessione("db") as s:
    print(f"Uso: {s}")
```
""",
        "esempio": (
            'from contextlib import contextmanager\n'
            '\n'
            'class RisorsaOccupataError(Exception):\n'
            '    pass\n'
            '\n'
            '@contextmanager\n'
            'def lock_risorsa(nome):\n'
            '    print(f"Acquisisco: {nome}")\n'
            '    try:\n'
            '        yield nome\n'
            '    except RisorsaOccupataError:\n'
            '        print(f"Risorsa {nome} occupata!")\n'
            '    finally:\n'
            '        print(f"Rilascio: {nome}")\n'
            '\n'
            'with lock_risorsa("prod-db") as r:\n'
            '    print(f"Lavoro su {r}")'
        ),
        "esercizi": [
            {
                "testo": "Scrivi `valida_eta(eta)` che lancia `ValueError('Età non valida')` se `eta < 0` o `eta > 150`. Testa con `valida_eta(-5)` dentro un try/except.",
                "placeholder": (
                    'def valida_eta(eta):\n'
                    '    if eta < 0 or eta > 150:\n'
                    '        raise ValueError("Età non valida")\n'
                    '    return eta\n'
                    '\n'
                    'try:\n'
                    '    valida_eta(-5)\n'
                    'except ValueError as e:\n'
                    '    print(f"Errore: {e}")'
                ),
                "check": lambda out, err, vs: err is None and "Età non valida" in out.strip(),
                "feedback": lambda out, err: "raise ValueError('Età non valida') deve essere catturato dal try/except",
                "hint": "raise ValueError('Età non valida')",
                "xp_bonus": 0,
            },
            {
                "testo": "Crea `BudgetSuperatoError(Exception)` con attributi `budget` e `spesa`. Lanciala con `budget=100, spesa=150` e catturala stampando entrambi i valori.",
                "placeholder": (
                    'class BudgetSuperatoError(Exception):\n'
                    '    def __init__(self, budget, spesa):\n'
                    '        self.budget = budget\n'
                    '        self.spesa  = spesa\n'
                    '        super().__init__(f"Spesa {spesa} supera {budget}")\n'
                    '\n'
                    'try:\n'
                    '    raise BudgetSuperatoError(100, 150)\n'
                    'except BudgetSuperatoError as e:\n'
                    '    print(f"Budget: {e.budget}, Spesa: {e.spesa}")'
                ),
                "check": lambda out, err, vs: err is None and "Budget: 100" in out and "Spesa: 150" in out,
                "feedback": lambda out, err: "L'eccezione custom deve avere budget e spesa come attributi accessibili",
                "hint": "print(f'Budget: {e.budget}, Spesa: {e.spesa}')",
                "xp_bonus": 0,
            },
            {
                "testo": "Usa `assert` per verificare che una lista di istanze non sia vuota prima di processarla. Gestisci `AssertionError` con un messaggio chiaro.",
                "placeholder": (
                    'istanze = []\n'
                    '\n'
                    'try:\n'
                    '    assert len(istanze) > 0, "Lista istanze vuota"\n'
                    '    print("Processo", len(istanze), "istanze")\n'
                    'except AssertionError as e:\n'
                    '    print(f"Attenzione: {e}")'
                ),
                "check": lambda out, err, vs: err is None and "Lista istanze vuota" in out.strip(),
                "feedback": lambda out, err: "AssertionError viene lanciato perché la lista è vuota",
                "hint": "assert len(istanze) > 0, 'Lista istanze vuota'",
                "xp_bonus": 0,
            },
            {
                "testo": "Scrivi un context manager `timer()` con `contextlib.contextmanager` che stampa `'Inizio'` prima e `'Fine'` dopo il blocco with.",
                "placeholder": (
                    'from contextlib import contextmanager\n'
                    '\n'
                    '@contextmanager\n'
                    'def timer():\n'
                    '    print("Inizio")\n'
                    '    try:\n'
                    '        yield\n'
                    '    finally:\n'
                    '        print("Fine")\n'
                    '\n'
                    'with timer():\n'
                    '    print("Operazione in corso")'
                ),
                "check": lambda out, err, vs: err is None and "Inizio" in out and "Fine" in out and "Operazione" in out,
                "feedback": lambda out, err: "Il contextmanager deve stampare Inizio, poi il corpo del with, poi Fine",
                "hint": "print('Inizio'); try: yield; finally: print('Fine')",
                "xp_bonus": 0,
            },
            {
                "testo": "🏆 **BOSS**: Crea una gerarchia: `AWSError(Exception)` base, `PermissionError(AWSError)`, `ResourceNotFoundError(AWSError)`. Scrivi `accedi(risorsa)` che lancia l'errore giusto. Cattura con except AWSError.",
                "placeholder": (
                    'class AWSError(Exception):\n'
                    '    pass\n'
                    '\n'
                    'class PermessoNegatoError(AWSError):\n'
                    '    pass\n'
                    '\n'
                    'class RisorsaAssente(AWSError):\n'
                    '    pass\n'
                    '\n'
                    'def accedi(risorsa):\n'
                    '    if risorsa == "segreto":\n'
                    '        raise PermessoNegatoError(f"Accesso negato a {risorsa}")\n'
                    '    if risorsa == "inesistente":\n'
                    '        raise RisorsaAssente(f"Risorsa non trovata: {risorsa}")\n'
                    '    print(f"Accesso OK: {risorsa}")\n'
                    '\n'
                    'for r in ["prod-bucket", "segreto", "inesistente"]:\n'
                    '    try:\n'
                    '        accedi(r)\n'
                    '    except AWSError as e:\n'
                    '        print(f"AWS Error: {e}")'
                ),
                "check": lambda out, err, vs: err is None and "Accesso OK" in out and "Accesso negato" in out and "non trovata" in out,
                "feedback": lambda out, err: "Ogni risorsa deve produrre l'output corretto: OK, negato, non trovata",
                "hint": "except AWSError cattura sia PermessoNegatoError che RisorsaAssente",
                "xp_bonus": 15,
            },
        ],
    },
    {
        "id": "kwargs_unpacking", "title": "Unpacking e kwargs",
        "icon": "📦", "world": "🔧 Officina dei Parametri",
        "teoria": """
### *args e **kwargs
Le funzioni possono accettare un numero variabile di argomenti.

```python
def saluta(*nomi):           # tupla di positional
    for n in nomi:
        print(f"Ciao {n}!")

def configura(**opzioni):    # dizionario di keyword
    for k, v in opzioni.items():
        print(f"{k} = {v}")

configura(regione="eu-west-1", debug=True)
```

### Spacchettare con * e **
```python
numeri = [1, 2, 3]
print(*numeri)            # stampa: 1 2 3

params = {"Bucket": "log", "Key": "file.txt"}
s3.get_object(**params)   # equivale a s3.get_object(Bucket="log", Key="file.txt")
```

### Pattern boto3 — chiamata dinamica
```python
params = {"Bucket": bucket}
if versione:
    params["VersionId"] = versione   # aggiunge solo se serve

risposta = s3.get_object(**params)
```
""",
        "esempio": (
            'def descrivi_risorsa(tipo, **dettagli):\n'
            '    print(f"Risorsa: {tipo}")\n'
            '    for k, v in dettagli.items():\n'
            '        print(f"  {k}: {v}")\n'
            '\n'
            'descrivi_risorsa("EC2", id="i-001", stato="running", regione="eu-west-1")\n'
            'print("---")\n'
            'params = {"id": "i-002", "stato": "stopped"}\n'
            'descrivi_risorsa("RDS", **params)'
        ),
        "esercizi": [
            {
                "testo": "Scrivi `stampa_config(**kwargs)` che stampa ogni parametro nel formato `chiave: valore`. Chiamala con `regione`, `servizio` e `timeout`.",
                "placeholder": (
                    'def stampa_config(**kwargs):\n'
                    '    for k, v in kwargs.items():\n'
                    '        pass  # stampa k: v\n'
                    '\n'
                    'stampa_config(regione="eu-west-1", servizio="s3", timeout=30)'
                ),
                "check": lambda out, err, vs: err is None and "regione" in out and "eu-west-1" in out and "timeout" in out,
                "feedback": lambda out, err: 'Usa `print(f"{k}: {v}")` dentro il for loop',
                "hint": 'print(f"{k}: {v}")',
                "xp_bonus": 0,
            },
            {
                "testo": 'Hai `params = {"Bucket": "logs", "Prefisso": "jan-2024"}`. Chiama `scarica(**kwargs)` (già scritta) usando **unpacking sul dizionario.',
                "placeholder": (
                    'def scarica(**kwargs):\n'
                    '    bucket = kwargs.get("Bucket", "?")\n'
                    '    print(f"Scarico da: {bucket}")\n'
                    '\n'
                    'params = {"Bucket": "logs", "Prefisso": "jan-2024"}\n'
                    '# chiama scarica con **unpacking'
                ),
                "check": lambda out, err, vs: err is None and "Scarico da: logs" in out.strip(),
                "feedback": lambda out, err: "Chiama `scarica(**params)` — i ** spaccchettano il dict in keyword arguments",
                "hint": "scarica(**params)",
                "xp_bonus": 0,
            },
            {
                "tipo": "debug",
                "testo": "🐛 **DEBUG**: Il codice chiama una funzione boto3 simulata ma ha 2 bug con unpacking.",
                "placeholder": (
                    'def get_object(Bucket, Key, VersionId=None):\n'
                    '    print(f"Leggo s3://{Bucket}/{Key}")\n'
                    '    if VersionId:\n'
                    '        print(f"Versione: {VersionId}")\n'
                    '\n'
                    'params = {"Bucket": "dati", "Key": "report.csv"}\n'
                    'get_object(params)        # BUG 1\n'
                    'get_object(*params)       # BUG 2: * su dict spacchetta le chiavi'
                ),
                "check": lambda out, err, vs: err is None and "Leggo s3://dati/report.csv" in out,
                "feedback": lambda out, err: "BUG 1: `get_object(params)` → `get_object(**params)`. BUG 2: `*params` → `**params`",
                "hint": "Usa sempre ** (doppio asterisco) per spacchettare dizionari",
                "xp_bonus": 0,
            },
            {
                "tipo": "predict",
                "testo": "🔍 **PREVEDI**: Cosa stamperà questo codice? Traccia cosa riceve `f` in ogni chiamata.",
                "codice": (
                    'def f(*args, **kwargs):\n'
                    '    print(f"args={args}")\n'
                    '    print(f"kwargs={kwargs}")\n'
                    '\n'
                    'f(1, 2, nome="Lorenzo", ruolo="admin")'
                ),
                "expected": "args=(1, 2)\nkwargs={'nome': 'Lorenzo', 'ruolo': 'admin'}",
                "hint": "1 e 2 sono positional → tupla in args. nome e ruolo sono keyword → dict in kwargs.",
                "xp_bonus": 5,
            },
            {
                "testo": "🏆 **BOSS**: Scrivi `crea_filtri(**criteri)` che costruisce una lista `Filters` boto3 dal formato `[{'Name': k, 'Values': [v]}]`. Testa con 2 chiamate diverse.",
                "placeholder": (
                    'def crea_filtri(**criteri):\n'
                    '    filters = []\n'
                    '    # per ogni criterio, aggiungi il dict boto3\n'
                    '    return filters\n'
                    '\n'
                    'print(crea_filtri(stato="running"))\n'
                    'print(crea_filtri(stato="stopped", tipo="t3.micro"))'
                ),
                "check": lambda out, err, vs: (
                    err is None and "running" in out and "stopped" in out
                    and "t3.micro" in out and "Name" in out
                ),
                "feedback": lambda out, err: 'for k, v in criteri.items(): filters.append({"Name": k, "Values": [v]})',
                "hint": 'for k, v in criteri.items():\n    filters.append({"Name": k, "Values": [v]})',
                "xp_bonus": 10,
            },
        ],
    },
    {
        "id": "json_env", "title": "JSON e Variabili d'Ambiente",
        "icon": "🔐", "world": "🌍 Portale della Configurazione",
        "teoria": """
### Modulo json
```python
import json

# Stringa → dict
testo = '{"nome": "Lorenzo", "eta": 28}'
dati  = json.loads(testo)
print(dati["nome"])          # Lorenzo

# Dict → stringa
print(json.dumps(dati, indent=2))

# File → dict
with open("config.json") as f:
    cfg = json.load(f)       # json.load, non json.loads
```

### os.environ — variabili d'ambiente
```python
import os

regione = os.environ.get("AWS_REGION", "eu-west-1")  # default sicuro
debug   = os.environ.get("DEBUG", "false") == "true"
```

### Credenziali AWS — la regola d'oro
```bash
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_DEFAULT_REGION="eu-west-1"
```
```python
import boto3
s3 = boto3.client("s3")  # legge le env var automaticamente
```
> ⚠️ **Mai** scrivere credenziali nel codice sorgente.
""",
        "esempio": (
            'import json, os\n'
            '\n'
            'risposta_raw = \'{"Buckets": [{"Name": "prod-logs"}, {"Name": "dev-data"}]}\'\n'
            'risposta = json.loads(risposta_raw)\n'
            '\n'
            'for b in risposta["Buckets"]:\n'
            '    print(b["Name"])\n'
            '\n'
            'regione = os.environ.get("AWS_REGION", "eu-west-1")\n'
            'print(f"Regione: {regione}")'
        ),
        "esercizi": [
            {
                "testo": 'Parsa la stringa JSON `\'{"istanza": "i-001", "stato": "running", "costo_ora": 0.096}\'` e stampa solo il valore di `stato`.',
                "placeholder": (
                    'import json\n'
                    '\n'
                    'raw = \'{"istanza": "i-001", "stato": "running", "costo_ora": 0.096}\'\n'
                    'dati = ...\n'
                    'print(...)'
                ),
                "check": lambda out, err, vs: err is None and out.strip() == "running",
                "feedback": lambda out, err: 'dati = json.loads(raw)  poi  print(dati["stato"])',
                "hint": 'dati = json.loads(raw)\nprint(dati["stato"])',
                "xp_bonus": 0,
            },
            {
                "testo": "Serializza un dizionario AWS con 3 chiavi (`regione`, `servizio`, `costo`) usando `json.dumps` con `indent=2` e stampalo.",
                "placeholder": (
                    'import json\n'
                    '\n'
                    'config = {"regione": "eu-west-1", "servizio": "EC2", "costo": 70.08}\n'
                    'print(...)'
                ),
                "check": lambda out, err, vs: err is None and "  " in out and "regione" in out and "70.08" in out,
                "feedback": lambda out, err: "Usa json.dumps(config, indent=2)",
                "hint": "print(json.dumps(config, indent=2))",
                "xp_bonus": 0,
            },
            {
                "testo": "Leggi la regione da `os.environ.get('AWS_REGION', 'eu-west-1')`. Poiché non è impostata, deve stampare il default.",
                "placeholder": (
                    'import os\n'
                    '\n'
                    'regione = os.environ.get("AWS_REGION", "eu-west-1")\n'
                    'print(f"Regione: {regione}")'
                ),
                "check": lambda out, err, vs: err is None and "eu-west-1" in out.strip(),
                "feedback": lambda out, err: "Il codice è già corretto — il default 'eu-west-1' appare perché AWS_REGION non è impostata",
                "hint": "os.environ.get('KEY', 'default') ritorna il default se la variabile non esiste",
                "xp_bonus": 0,
            },
            {
                "tipo": "predict",
                "testo": "🔍 **PREVEDI**: Cosa stamperà questo codice? Attenzione ai tipi restituiti da json.loads.",
                "codice": (
                    'import json\n'
                    '\n'
                    'raw = \'{"attivo": true, "costo": 42, "nome": "prod"}\'\n'
                    'dati = json.loads(raw)\n'
                    'print(type(dati["attivo"]).__name__)\n'
                    'print(type(dati["costo"]).__name__)\n'
                    'print(dati["attivo"] is True)\n'
                ),
                "expected": "bool\nint\nTrue",
                "hint": "JSON true → Python bool. Numeri interi JSON → Python int. `is True` confronta identità, non solo valore.",
                "xp_bonus": 5,
            },
            {
                "testo": "🏆 **BOSS**: Scrivi `carica_config(json_str)` che parsa il JSON, poi sovrascrive `regione` e `debug` con le env var se presenti. Stampa il risultato con indent=2.",
                "placeholder": (
                    'import json, os\n'
                    '\n'
                    'DEFAULT = \'{"regione": "eu-west-1", "timeout": 30, "debug": false}\'\n'
                    '\n'
                    'def carica_config(json_str):\n'
                    '    cfg = json.loads(json_str)\n'
                    '    if os.environ.get("AWS_REGION"):\n'
                    '        cfg["regione"] = os.environ["AWS_REGION"]\n'
                    '    # aggiungi override per timeout\n'
                    '    return cfg\n'
                    '\n'
                    'print(json.dumps(carica_config(DEFAULT), indent=2))'
                ),
                "check": lambda out, err, vs: err is None and "regione" in out and "timeout" in out and "  " in out,
                "feedback": lambda out, err: "La funzione deve caricare il JSON e sovrascrivere con os.environ.get() per ogni chiave override",
                "hint": 'cfg["timeout"] = int(os.environ.get("TIMEOUT", cfg["timeout"]))',
                "xp_bonus": 10,
            },
        ],
    },
    {
        "id": "comprehensions", "title": "Comprehensions",
        "icon": "⚡", "world": "🏎️ Circuito della Velocità",
        "teoria": """
### List comprehension
```python
# Filtra
running = [i["id"] for i in istanze if i["stato"] == "running"]

# Trasforma
nomi_upper = [n.upper() for n in nomi]

# Filtra + trasforma
costi = [i["costo_ora"] * 730 for i in istanze if i["tipo"] == "EC2"]
```

### Dict e Set comprehension
```python
# Dict — mappa id → stato
stati = {i["id"]: i["stato"] for i in istanze}
print(stati["i-001"])   # "running"

# Set — valori unici
regioni_usate = {i["regione"] for i in istanze}
```

### Generator expression (lazy)
```python
# Non crea una lista in memoria — utile per somme su grandi dataset
totale = sum(b["size_gb"] * 0.023 for b in buckets)
```

| Tipo | Sintassi | Usa quando |
|------|----------|------------|
| List | `[expr for x in it if cond]` | vuoi una lista |
| Dict | `{k: v for x in it}` | vuoi un mapping |
| Set  | `{expr for x in it}` | vuoi valori unici |
| Gen  | `(expr for x in it)` | stai solo aggregando |
""",
        "esempio": (
            'istanze = [\n'
            '    {"id": "i-001", "stato": "running",  "costo": 0.096},\n'
            '    {"id": "i-002", "stato": "stopped",  "costo": 0.023},\n'
            '    {"id": "i-003", "stato": "running",  "costo": 0.048},\n'
            ']\n'
            '\n'
            'running_ids = [i["id"] for i in istanze if i["stato"] == "running"]\n'
            'print("Running:", running_ids)\n'
            '\n'
            'mappa_stato = {i["id"]: i["stato"] for i in istanze}\n'
            'print("Mappa:", mappa_stato)\n'
            '\n'
            'costo_totale = sum(i["costo"] for i in istanze if i["stato"] == "running")\n'
            'print(f"Costo running: ${costo_totale:.3f}/ora")'
        ),
        "esercizi": [
            {
                "testo": 'Con `numeri = [1,2,3,4,5,6,7,8,9,10]`, usa una list comprehension per ottenere solo i dispari.',
                "placeholder": 'numeri = [1,2,3,4,5,6,7,8,9,10]\ndispari = [...]\nprint(dispari)',
                "check": lambda out, err, vs: err is None and all(s in out for s in ["1","3","5","7","9"]) and not any(s in out for s in ["2","4","6","8","10"]),
                "feedback": lambda out, err: "[x for x in numeri if x % 2 != 0]",
                "hint": "[x for x in numeri if x % 2 != 0]",
                "xp_bonus": 0,
            },
            {
                "testo": "Con la lista di istanze, crea un **dizionario** `{id: costo}` usando dict comprehension.",
                "placeholder": (
                    'istanze = [\n'
                    '    {"id": "i-001", "costo": 0.096},\n'
                    '    {"id": "i-002", "costo": 0.023},\n'
                    '    {"id": "i-003", "costo": 0.048},\n'
                    ']\n'
                    'costi = {...}\n'
                    'print(costi)'
                ),
                "check": lambda out, err, vs: err is None and "i-001" in out and "0.096" in out and "{" in out,
                "feedback": lambda out, err: '{i["id"]: i["costo"] for i in istanze}',
                "hint": '{i["id"]: i["costo"] for i in istanze}',
                "xp_bonus": 0,
            },
            {
                "testo": "Usa una **set comprehension** per ottenere le regioni uniche da una lista di istanze.",
                "placeholder": (
                    'istanze = [\n'
                    '    {"id": "i-001", "regione": "eu-west-1"},\n'
                    '    {"id": "i-002", "regione": "us-east-1"},\n'
                    '    {"id": "i-003", "regione": "eu-west-1"},\n'
                    ']\n'
                    'regioni = {...}\n'
                    'print(len(regioni))  # deve essere 2, non 3'
                ),
                "check": lambda out, err, vs: err is None and "2" in _ol(out),
                "feedback": lambda out, err: '{i["regione"] for i in istanze} — le chiavi doppie vengono eliminate',
                "hint": '{i["regione"] for i in istanze}',
                "xp_bonus": 0,
            },
            {
                "tipo": "debug",
                "testo": "🐛 **DEBUG**: Questa comprehension vuole i quadrati dei numeri positivi, ma ha 2 bug.",
                "placeholder": (
                    'numeri = [-3, -1, 0, 2, 4, 6]\n'
                    'quadrati = [if x > 0: x**2 for x in numeri]  # BUG 1\n'
                    'print(quadraati)                               # BUG 2'
                ),
                "check": lambda out, err, vs: err is None and all(s in out for s in ["4","16","36"]),
                "feedback": lambda out, err: "BUG 1: `[x**2 for x in numeri if x > 0]` — il `if` va DOPO il `for`. BUG 2: typo `quadraati`",
                "hint": "[x**2 for x in numeri if x > 0]",
                "xp_bonus": 0,
            },
            {
                "tipo": "predict",
                "testo": "🔍 **PREVEDI**: Cosa stamperà questo codice? Traccia la comprehension passo per passo.",
                "codice": (
                    'dati = [{"n": "EC2", "c": 80}, {"n": "S3", "c": 5}, {"n": "RDS", "c": 120}]\n'
                    'risultato = {d["n"]: d["c"] * 12 for d in dati if d["c"] > 10}\n'
                    'print(risultato)'
                ),
                "expected": "{'EC2': 960, 'RDS': 1440}",
                "hint": "Filtra solo c > 10 (EC2=80, RDS=120, S3=5 escluso). Moltiplica per 12. Risultato è un dict.",
                "xp_bonus": 5,
            },
            {
                "testo": "🏆 **BOSS**: Da una lista di log (stringhe), estrai con comprehension: (1) lista delle righe ERROR, (2) dict `{timestamp: messaggio}` solo per WARNING.",
                "placeholder": (
                    'logs = [\n'
                    '    "2024-01-15 ERROR connection timeout",\n'
                    '    "2024-01-15 INFO instance started",\n'
                    '    "2024-01-16 WARNING high cpu usage",\n'
                    '    "2024-01-16 ERROR disk full",\n'
                    '    "2024-01-17 WARNING memory low",\n'
                    ']\n'
                    '\n'
                    'errori   = [...]   # righe che contengono ERROR\n'
                    'warnings = {...}   # {timestamp: messaggio} solo WARNING\n'
                    '\n'
                    'print(f"Errori: {len(errori)}")\n'
                    'print(f"Warning: {len(warnings)}")'
                ),
                "check": lambda out, err, vs: err is None and "Errori: 2" in out.strip() and "Warning: 2" in out.strip(),
                "feedback": lambda out, err: (
                    '[l for l in logs if "ERROR" in l]\n'
                    '{l.split()[0]: l.split(None,2)[2] for l in logs if "WARNING" in l}'
                ),
                "hint": '[l for l in logs if "ERROR" in l]',
                "xp_bonus": 15,
            },
        ],
    },
    {
        "id": "builtins", "title": "Strumenti Built-in",
        "icon": "🛠️", "world": "🧰 Cassetta degli Attrezzi",
        "teoria": """
### enumerate — indice + valore
```python
bucket_list = ["logs", "backup", "data"]

for i, nome in enumerate(bucket_list, start=1):
    print(f"{i}/{len(bucket_list)}: {nome}")
# 1/3: logs
# 2/3: backup
# 3/3: data
```

### zip — itera su più liste in parallelo
```python
nomi  = ["prod", "staging", "dev"]
costi = [120.5,  15.0,      5.0]

for nome, costo in zip(nomi, costi):
    print(f"{nome}: ${costo}")
```

### sorted — ordina senza modificare
```python
istanze = [{"id": "i-1", "costo": 0.096}, {"id": "i-2", "costo": 0.023}]

per_costo = sorted(istanze, key=lambda x: x["costo"], reverse=True)
```

### None safety
```python
ip = istanza.get("PublicIpAddress")   # ritorna None se mancante
if ip is not None:                    # is None, non == None
    print(f"IP: {ip}")

# oppure con or
label = istanza.get("Name") or "senza-nome"
```

### Type hints (Python 3.9+)
```python
def calcola_costo(ore: int, prezzo: float = 0.023) -> float:
    return ore * prezzo
```
Non cambiano il comportamento, ma rendono il codice più leggibile e
aiutano i tool di analisi statica.
""",
        "esempio": (
            'risorse = [\n'
            '    {"nome": "web-server",  "costo_ora": 0.096, "stato": "running"},\n'
            '    {"nome": "db-primary",  "costo_ora": 0.192, "stato": "running"},\n'
            '    {"nome": "worker-dev",  "costo_ora": 0.023, "stato": "stopped"},\n'
            ']\n'
            '\n'
            '# enumerate — log numerato\n'
            'for i, r in enumerate(risorse, start=1):\n'
            '    print(f"{i}. {r[\'nome\']} ({r[\'stato\']})")\n'
            '\n'
            '# sorted — ordina per costo decrescente\n'
            'per_costo = sorted(risorse, key=lambda x: x["costo_ora"], reverse=True)\n'
            'print(f"\\nPiù costosa: {per_costo[0][\'nome\']}")'
        ),
        "esercizi": [
            {
                "testo": "Usa `enumerate(servizi, start=1)` per stampare ogni servizio nel formato `1. EC2`, `2. S3`, ecc.",
                "placeholder": (
                    'servizi = ["EC2", "S3", "Lambda", "RDS"]\n'
                    'for i, s in enumerate(servizi, start=1):\n'
                    '    pass  # stampa il formato richiesto'
                ),
                "check": lambda out, err, vs: err is None and "1. EC2" in out.strip() and "4. RDS" in out.strip(),
                "feedback": lambda out, err: 'print(f"{i}. {s}")',
                "hint": 'print(f"{i}. {s}")',
                "xp_bonus": 0,
            },
            {
                "testo": "Hai due liste parallele `nomi` e `costi`. Usa `zip` per stampare ogni coppia nel formato `EC2: $70.08`.",
                "placeholder": (
                    'nomi  = ["EC2", "S3", "RDS"]\n'
                    'costi = [70.08, 1.50, 105.84]\n'
                    '\n'
                    'for nome, costo in zip(nomi, costi):\n'
                    '    pass  # stampa il formato richiesto'
                ),
                "check": lambda out, err, vs: err is None and "EC2: $70.08" in out.strip() and "RDS: $105.84" in out.strip(),
                "feedback": lambda out, err: 'print(f"{nome}: ${costo}")',
                "hint": 'print(f"{nome}: ${costo}")',
                "xp_bonus": 0,
            },
            {
                "testo": "Ordina la lista di istanze per `costo_ora` decrescente con `sorted` e stampa i nomi in quell'ordine.",
                "placeholder": (
                    'istanze = [\n'
                    '    {"nome": "web",  "costo_ora": 0.048},\n'
                    '    {"nome": "db",   "costo_ora": 0.192},\n'
                    '    {"nome": "worker","costo_ora": 0.023},\n'
                    ']\n'
                    'ordinate = sorted(...)\n'
                    'for i in ordinate:\n'
                    '    print(i["nome"])'
                ),
                "check": lambda out, err, vs: err is None and list(_ol(out)) != [] and list(out.strip().splitlines())[0].strip() == "db",
                "feedback": lambda out, err: 'sorted(istanze, key=lambda x: x["costo_ora"], reverse=True)',
                "hint": 'sorted(istanze, key=lambda x: x["costo_ora"], reverse=True)',
                "xp_bonus": 0,
            },
            {
                "tipo": "debug",
                "testo": "🐛 **DEBUG**: Questo codice gestisce `None` ma ha 2 bug sottili.",
                "placeholder": (
                    'istanza = {"id": "i-001", "stato": "running"}\n'
                    '\n'
                    'ip = istanza.get("PublicIpAddress")\n'
                    'if ip == None:              # BUG 1: confronto sbagliato\n'
                    '    print("Nessun IP")\n'
                    '\n'
                    'nome = istanza.get("Tag_Name")\n'
                    'label = nome if nome else None  # BUG 2: default inutile\n'
                    'print(f"Label: {label}")'
                ),
                "check": lambda out, err, vs: err is None and "Nessun IP" in out and "Label:" in out,
                "feedback": lambda out, err: "BUG 1: usa `is None` non `== None`. BUG 2: `label = nome or 'senza-nome'` per un default utile",
                "hint": "if ip is None:  e  label = nome or 'senza-nome'",
                "xp_bonus": 0,
            },
            {
                "testo": "🏆 **BOSS**: Combina `enumerate`, `sorted` e None-safety: stampa le istanze ordinate per costo, numerate, mostrando `N/A` se il campo `tag` è `None`.",
                "placeholder": (
                    'istanze = [\n'
                    '    {"nome": "web",    "costo": 0.096, "tag": "prod"},\n'
                    '    {"nome": "worker", "costo": 0.023, "tag": None},\n'
                    '    {"nome": "db",     "costo": 0.192, "tag": "prod"},\n'
                    ']\n'
                    '\n'
                    '# ordina per costo decrescente, enumera da 1\n'
                    '# formato: "1. db ($0.192) [prod]" oppure "[N/A]"'
                ),
                "check": lambda out, err, vs: (
                    err is None
                    and "1. db" in out
                    and "N/A" in out
                    and "3. worker" in out
                ),
                "feedback": lambda out, err: (
                    'ordinate = sorted(istanze, key=lambda x: x["costo"], reverse=True)\n'
                    'for i, ist in enumerate(ordinate, start=1):\n'
                    '    tag = ist["tag"] or "N/A"\n'
                    '    print(f"{i}. {ist[\'nome\']} (${ist[\'costo\']}) [{tag}]")'
                ),
                "hint": 'tag = ist["tag"] or "N/A"',
                "xp_bonus": 15,
            },
        ],
    },
    {
        "id": "boto3_intro", "title": "Intro boto3 (AWS)",
        "icon": "☁️", "world": "🌌 Nuvola AWS",
        "teoria": """
### boto3 — la libreria ufficiale AWS per Python
```bash
pip install boto3
aws configure
```

```python
import boto3
s3 = boto3.client("s3")
for b in s3.list_buckets()["Buckets"]:
    print(b["Name"])
```

```python
ec2 = boto3.client("ec2", region_name="eu-west-1")
for res in ec2.describe_instances()["Reservations"]:
    for ist in res["Instances"]:
        print(ist["InstanceId"], ist["State"]["Name"])
```

> 💡 La risposta è sempre un **dizionario** — il modulo 6 non era un caso!
""",
        "esempio": (
            'risposta = {\n'
            '    "Buckets": [\n'
            '        {"Name": "mio-bucket-logs",   "CreationDate": "2024-01-15"},\n'
            '        {"Name": "mio-bucket-backup", "CreationDate": "2024-03-20"},\n'
            '    ]\n'
            '}\nfor b in risposta["Buckets"]:\n'
            '    print(f"→ {b[\'Name\']}  ({b[\'CreationDate\']})")'
        ),
        "esercizi": [
            {
                "testo": 'Filtra le istanze EC2 simulate e stampa solo gli `InstanceId` con stato `"running"`.',
                "placeholder": 'istanze = [\n    {"InstanceId": "i-001", "State": "running"},\n    {"InstanceId": "i-002", "State": "stopped"},\n    {"InstanceId": "i-003", "State": "running"},\n]\n# filtra e stampa',
                "check": lambda out, err, vs: err is None and "i-001" in out and "i-003" in out and "i-002" not in out,
                "feedback": lambda out, err: (
                    "i-002 è 'stopped', non deve apparire" if "i-002" in out else
                    'Filtra con `if i["State"] == "running"` dentro il for loop'
                ),
                "hint": 'for i in istanze:\n    if i["State"] == "running":\n        print(i["InstanceId"])',
                "xp_bonus": 0,
            },
            {
                "testo": '🏆 **BOSS**: Calcola il costo totale S3 (`0.023 $/GB × size_gb`) e stampa `Costo totale: $X.XX`.',
                "placeholder": 'buckets = [\n    {"Name": "logs",   "size_gb": 120},\n    {"Name": "backup", "size_gb": 500},\n    {"Name": "data",   "size_gb": 80},\n]\nPREZZO = 0.023\n# calcola e stampa',
                "check": lambda out, err, vs: err is None and "Costo totale" in out and "$" in out,
                "feedback": lambda out, err: 'Somma `b["size_gb"] * PREZZO` per ogni bucket e stampa con `f"Costo totale: ${totale:.2f}"`',
                "hint": 'totale = sum(b["size_gb"] * PREZZO for b in buckets)\nprint(f"Costo totale: ${totale:.2f}")',
                "xp_bonus": 15,
            },
        ],
    },

    # ═══════════════════════════════════════════════════════════════════
    # FASE 4 — CODICE PROFESSIONALE
    # ═══════════════════════════════════════════════════════════════════
    {
        "id": "type_hints", "title": "Type Hints & Annotazioni",
        "icon": "🏷️", "world": "🏢 Distretto del Codice Pulito",
        "teoria": """
### Type hints: dichiarare i tipi
Python non ti *obbliga* a dichiarare i tipi, ma puoi **annotarli** per rendere il codice leggibile e far lavorare l'editor per te.

```python
def saluta(nome: str, volte: int = 1) -> str:
    return f"Ciao {nome}! " * volte

eta: int = 28
prezzi: list[float] = [1.5, 2.0]
utente: dict[str, int] = {"eta": 28}
```

- `nome: str` → il parametro è una stringa
- `-> str` → la funzione restituisce una stringa
- `int | None` → o un intero o `None` (opzionale)

**Importante:** le annotazioni **non sono controllate a runtime** — sono documentazione + aiuto per l'IDE e per `mypy`. Passare il tipo sbagliato non solleva errori da solo.
""",
        "esempio": 'def area(base: float, altezza: float) -> float:\n    return base * altezza / 2\n\nrisultato: float = area(10, 4)\nprint(f"Area: {risultato}")',
        "esercizi": [
            {
                "testo": "Scrivi una funzione tipizzata `somma(a: int, b: int) -> int` che restituisce la somma. Stampa `somma(3, 4)`.",
                "placeholder": "def somma(a: int, b: int) -> int:\n    pass\n\nprint(somma(3, 4))",
                "check": lambda out, err, vs: err is None and "7" in _ol(out),
                "feedback": lambda out, err: "Il corpo deve fare `return a + b`, poi `print(somma(3, 4))`.",
                "hint": "def somma(a: int, b: int) -> int:\n    return a + b\n\nprint(somma(3, 4))",
                "xp_bonus": 0,
            },
            {
                "testo": "Scrivi `primi_n(n: int) -> list[int]` che restituisce la lista `[0, 1, ..., n-1]`. Stampa `primi_n(4)`.",
                "placeholder": "def primi_n(n: int) -> list[int]:\n    pass\n\nprint(primi_n(4))",
                "check": lambda out, err, vs: err is None and "[0, 1, 2, 3]" in out,
                "feedback": lambda out, err: "Usa `return list(range(n))`.",
                "hint": "def primi_n(n: int) -> list[int]:\n    return list(range(n))\n\nprint(primi_n(4))",
                "xp_bonus": 10,
            },
            {
                "tipo": "predict",
                "testo": "🔍 **PREVEDI**: le annotazioni sono controllate a runtime? Cosa stampa?",
                "codice": 'def doppio(n: int) -> int:\n    return n * 2\n\nprint(doppio("ab"))\n',
                "expected": "abab",
                "hint": "Le annotazioni NON sono enforce a runtime: `n` riceve la stringa 'ab', e `'ab' * 2` è 'abab'. Python non si lamenta del tipo.",
                "xp_bonus": 5,
            },
            {
                "testo": "🏆 **BOSS**: Scrivi `trova(d: dict[str, int], chiave: str) -> int | None` che restituisce il valore o `None`. Stampa `trova({'a': 1}, 'x')`.",
                "placeholder": "def trova(d: dict[str, int], chiave: str) -> int | None:\n    pass\n\nprint(trova({'a': 1}, 'x'))",
                "check": lambda out, err, vs: err is None and out.strip() == "None",
                "feedback": lambda out, err: "Usa `return d.get(chiave)` — `dict.get` restituisce `None` se la chiave manca.",
                "hint": "def trova(d: dict[str, int], chiave: str) -> int | None:\n    return d.get(chiave)\n\nprint(trova({'a': 1}, 'x'))",
                "xp_bonus": 15,
            },
        ],
    },
    {
        "id": "testing", "title": "Testing (assert & pytest)",
        "icon": "✅", "world": "🧪 Laboratorio dei Test",
        "teoria": """
### Testare il codice
Un test verifica che il codice faccia quello che deve. Il mattone base è `assert`:

```python
def somma(a, b):
    return a + b

assert somma(2, 3) == 5          # passa in silenzio
assert somma(2, 3) == 99, "ops"  # solleva AssertionError: ops
```

Se l'assert è vero, non succede niente. Se è falso → **AssertionError**.

**pytest** è lo strumento standard: scrivi funzioni che iniziano con `test_` e le lanci da terminale:
```python
# test_calc.py
def test_somma():
    assert somma(2, 3) == 5
```
```bash
pytest        # trova ed esegue tutti i test_*
```

**Pattern AAA**: *Arrange* (prepara) → *Act* (esegui) → *Assert* (verifica).
""",
        "esempio": 'def is_pari(n):\n    return n % 2 == 0\n\nassert is_pari(4) is True\nassert is_pari(7) is False\nprint("Tutti i test passati!")',
        "esercizi": [
            {
                "testo": "Scrivi `triplo(n)` che restituisce `n*3`. Poi un `assert` che verifica `triplo(5) == 15` e stampa `OK`.",
                "placeholder": "def triplo(n):\n    pass\n\n# assert + print('OK')",
                "check": lambda out, err, vs: err is None and "OK" in out,
                "feedback": lambda out, err: "Se l'assert passa, il codice continua fino al print. Se va in AssertionError, controlla la funzione.",
                "hint": "def triplo(n):\n    return n * 3\n\nassert triplo(5) == 15\nprint('OK')",
                "xp_bonus": 0,
            },
            {
                "testo": "Scrivi `dividi(a, b)` che restituisce `a/b`. Aggiungi `assert dividi(10, 2) == 5, 'errore'` e stampa `Test passato`.",
                "placeholder": "def dividi(a, b):\n    pass\n\n# assert con messaggio + print",
                "check": lambda out, err, vs: err is None and "Test passato" in out,
                "feedback": lambda out, err: "`return a / b`, poi l'assert con la virgola e il messaggio, poi il print.",
                "hint": "def dividi(a, b):\n    return a / b\n\nassert dividi(10, 2) == 5, 'errore'\nprint('Test passato')",
                "xp_bonus": 10,
            },
            {
                "tipo": "predict",
                "testo": "🔍 **PREVEDI**: Cosa stampa? Gli assert passano?",
                "codice": "def maggiore(a, b):\n    return a if a > b else b\n\nassert maggiore(3, 8) == 8\nassert maggiore(10, 2) == 10\nprint('verde')\n",
                "expected": "verde",
                "hint": "Entrambi gli assert sono veri (8 e 10), quindi non sollevano nulla e si arriva al print: 'verde'.",
                "xp_bonus": 5,
            },
            {
                "testo": "🏆 **BOSS**: Scrivi `valida_eta(e)` → `True` se `0 <= e <= 120`, altrimenti `False`. Verifica con 3 assert (valido, negativo, troppo grande) e stampa `3/3`.",
                "placeholder": "def valida_eta(e):\n    pass\n\n# 3 assert + print('3/3')",
                "check": lambda out, err, vs: err is None and "3/3" in out,
                "feedback": lambda out, err: "`return 0 <= e <= 120`. Poi assert su 30 (True), -5 (False), 200 (False).",
                "hint": "def valida_eta(e):\n    return 0 <= e <= 120\n\nassert valida_eta(30) is True\nassert valida_eta(-5) is False\nassert valida_eta(200) is False\nprint('3/3')",
                "xp_bonus": 15,
            },
        ],
    },
    {
        "id": "logging", "title": "Logging",
        "icon": "📜", "world": "📜 Sala dei Registri",
        "teoria": """
### Logging invece di print
`print` va bene per giocare, ma nel codice vero si usa **logging**: puoi filtrare per importanza, aggiungere timestamp, scrivere su file — senza toccare il codice.

**Livelli** (dal meno al più grave): `DEBUG` < `INFO` < `WARNING` < `ERROR` < `CRITICAL`.

```python
import logging, sys
logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                    format="%(levelname)s: %(message)s")

logging.debug("dettaglio")     # NON appare (sotto INFO)
logging.info("avvio")          # INFO: avvio
logging.warning("memoria 80%") # WARNING: memoria 80%
```

`level=logging.INFO` → mostra da INFO in su; il `DEBUG` viene filtrato.

(Qui usiamo `stream=sys.stdout` per vedere l'output; di default il logging va su *stderr*.)
""",
        "esempio": 'import logging, sys\nlogging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(levelname)s: %(message)s")\nlogging.info("Server avviato")\nlogging.warning("Disco quasi pieno")',
        "esercizi": [
            {
                "testo": "Configura il logging su stdout a livello INFO e registra un messaggio INFO `Deploy completato`.",
                "placeholder": 'import logging, sys\nlogging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(levelname)s: %(message)s")\n# logga qui',
                "check": lambda out, err, vs: err is None and "Deploy completato" in out and "INFO" in out,
                "feedback": lambda out, err: "Dopo basicConfig usa `logging.info('Deploy completato')`.",
                "hint": 'import logging, sys\nlogging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(levelname)s: %(message)s")\nlogging.info("Deploy completato")',
                "xp_bonus": 0,
            },
            {
                "testo": "Imposta il livello a `WARNING`. Logga un `info()` (NON deve apparire) e un `warning('Attenzione')`. Solo il warning deve uscire.",
                "placeholder": 'import logging, sys\nlogging.basicConfig(level=logging.WARNING, stream=sys.stdout, format="%(levelname)s: %(message)s")\n# un info e un warning',
                "check": lambda out, err, vs: err is None and "Attenzione" in out and "INFO" not in out,
                "feedback": lambda out, err: "Con level=WARNING, `logging.info(...)` è filtrato. Solo `logging.warning('Attenzione')` appare.",
                "hint": 'import logging, sys\nlogging.basicConfig(level=logging.WARNING, stream=sys.stdout, format="%(levelname)s: %(message)s")\nlogging.info("non si vede")\nlogging.warning("Attenzione")',
                "xp_bonus": 10,
            },
            {
                "tipo": "predict",
                "testo": "🔍 **PREVEDI**: Quali righe appaiono in output?",
                "codice": 'import logging, sys\nlogging.basicConfig(level=logging.WARNING, stream=sys.stdout, format="%(levelname)s:%(message)s")\nlogging.info("a")\nlogging.warning("b")\nlogging.error("c")\n',
                "expected": "WARNING:b\nERROR:c",
                "hint": "Il livello è WARNING: `info('a')` è sotto soglia e sparisce. Restano warning ('b') ed error ('c').",
                "xp_bonus": 5,
            },
            {
                "testo": "🏆 **BOSS**: Logga un `ERROR` che include una variabile: `bucket = 'logs'` e registra `Connessione fallita al bucket logs` con una f-string.",
                "placeholder": 'import logging, sys\nlogging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(levelname)s: %(message)s")\nbucket = "logs"\n# logga un error con f-string',
                "check": lambda out, err, vs: err is None and "ERROR" in out and "bucket logs" in out,
                "feedback": lambda out, err: 'Usa `logging.error(f"Connessione fallita al bucket {bucket}")`.',
                "hint": 'import logging, sys\nlogging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(levelname)s: %(message)s")\nbucket = "logs"\nlogging.error(f"Connessione fallita al bucket {bucket}")',
                "xp_bonus": 15,
            },
        ],
    },
    {
        "id": "stdlib_pro", "title": "Standard Library (collections, itertools, functools)",
        "icon": "🧰", "world": "🧰 Magazzino degli Strumenti",
        "teoria": """
### Gli strumenti già pronti
La *standard library* ti regala strutture e funzioni che non devi reinventare.

**collections**
```python
from collections import Counter, defaultdict
Counter("aws s3 aws".split())            # Counter({'aws': 2, 's3': 1})
d = defaultdict(list); d["x"].append(1)  # niente KeyError
```

**itertools**
```python
import itertools
list(itertools.chain([1, 2], [3, 4]))    # [1, 2, 3, 4]
```

**functools**
```python
from functools import reduce, lru_cache
reduce(lambda a, b: a + b, [1, 2, 3, 4])  # 10
@lru_cache
def fib(n): ...                            # memoizza i risultati
```
""",
        "esempio": 'from collections import Counter\nparole = "aws s3 aws ec2 s3 aws".split()\nc = Counter(parole)\nprint(c["aws"])\nprint(c.most_common(1))',
        "esercizi": [
            {
                "testo": "Usa `Counter` per contare le lettere di `'mississippi'` e stampa quante volte appare `'s'`.",
                "placeholder": "from collections import Counter\n# conta e stampa il numero di 's'",
                "check": lambda out, err, vs: err is None and "4" in _ol(out),
                "feedback": lambda out, err: "`Counter('mississippi')['s']` vale 4.",
                "hint": "from collections import Counter\nc = Counter('mississippi')\nprint(c['s'])",
                "xp_bonus": 0,
            },
            {
                "testo": "Usa `defaultdict(list)` per raggruppare `['ec2', 'eip', 's3', 'sqs']` per lettera iniziale. Stampa la lista sotto la chiave `'s'`.",
                "placeholder": "from collections import defaultdict\nservizi = ['ec2', 'eip', 's3', 'sqs']\ngruppi = defaultdict(list)\n# raggruppa e stampa gruppi['s']",
                "check": lambda out, err, vs: err is None and "['s3', 'sqs']" in out,
                "feedback": lambda out, err: "Cicla i servizi e fai `gruppi[s[0]].append(s)`, poi `print(gruppi['s'])`.",
                "hint": "from collections import defaultdict\nservizi = ['ec2', 'eip', 's3', 'sqs']\ngruppi = defaultdict(list)\nfor s in servizi:\n    gruppi[s[0]].append(s)\nprint(gruppi['s'])",
                "xp_bonus": 10,
            },
            {
                "testo": "Usa `functools.reduce` per calcolare il prodotto di `[1, 2, 3, 4, 5]` e stampalo.",
                "placeholder": "from functools import reduce\n# prodotto di 1..5 e stampa",
                "check": lambda out, err, vs: err is None and "120" in _ol(out),
                "feedback": lambda out, err: "`reduce(lambda a, b: a * b, [1,2,3,4,5])` vale 120.",
                "hint": "from functools import reduce\nprint(reduce(lambda a, b: a * b, [1, 2, 3, 4, 5]))",
                "xp_bonus": 10,
            },
            {
                "tipo": "predict",
                "testo": "🔍 **PREVEDI**: Cosa stampa?",
                "codice": "import itertools\nr = itertools.chain([1, 2], [3, 4], [5])\nprint(list(r))\n",
                "expected": "[1, 2, 3, 4, 5]",
                "hint": "`chain` concatena gli iterabili uno dopo l'altro: [1,2] + [3,4] + [5] → [1, 2, 3, 4, 5].",
                "xp_bonus": 5,
            },
        ],
    },

    # ═══════════════════════════════════════════════════════════════════
    # FASE 5 — IL MONDO REALE
    # ═══════════════════════════════════════════════════════════════════
    {
        "id": "regex", "title": "Espressioni Regolari (re)",
        "icon": "🔎", "world": "🔎 Sala dei Pattern",
        "teoria": """
### Cercare pattern nel testo
Le *regex* descrivono un pattern e lo cercano in una stringa. Modulo: `re`.

```python
import re
re.findall(r"\\d+", "ho 3 mele e 12 pere")   # ['3', '12']  tutti i numeri
re.search(r"@(.+)", "a@b.com").group(1)       # 'b.com'      primo match + gruppo
re.sub(r"\\d", "X", "id 42")                   # 'id XX'      sostituzione
```

**Mattoni:** `\\d` cifra · `\\w` lettera/cifra · `.` qualsiasi · `+` uno o più · `*` zero o più · `()` gruppo da catturare.
""",
        "esempio": 'import re\ntesto = "Errore alle 14:30 e 09:05"\norari = re.findall(r"\\d{2}:\\d{2}", testo)\nprint(orari)',
        "esercizi": [
            {
                "testo": "Usa `re.findall` per estrarre tutti i numeri da `'ho 3 istanze e 12 volumi'`. Stampa la lista.",
                "placeholder": 'import re\ntesto = "ho 3 istanze e 12 volumi"\n# findall dei numeri e stampa',
                "check": lambda out, err, vs: err is None and "['3', '12']" in out,
                "feedback": lambda out, err: "Usa `re.findall(r'\\\\d+', testo)`.",
                "hint": 'import re\ntesto = "ho 3 istanze e 12 volumi"\nprint(re.findall(r"\\d+", testo))',
                "xp_bonus": 0,
            },
            {
                "testo": "Estrai il dominio da `'lorenzo@aws.com'` (tutto ciò che segue la `@`) con `re.search` e un gruppo. Stampa `aws.com`.",
                "placeholder": 'import re\nemail = "lorenzo@aws.com"\n# search con gruppo (.+) dopo @',
                "check": lambda out, err, vs: err is None and out.strip() == "aws.com",
                "feedback": lambda out, err: "Usa `re.search(r'@(.+)', email).group(1)`.",
                "hint": 'import re\nemail = "lorenzo@aws.com"\nprint(re.search(r"@(.+)", email).group(1))',
                "xp_bonus": 10,
            },
            {
                "tipo": "predict",
                "testo": "🔍 **PREVEDI**: Cosa restituisce findall con due gruppi?",
                "codice": 'import re\nprint(re.findall(r"(\\d+)-(\\d+)", "1-2 3-4"))\n',
                "expected": "[('1', '2'), ('3', '4')]",
                "hint": "Con più gruppi, `findall` restituisce una lista di tuple: una tupla per ogni match, un elemento per gruppo.",
                "xp_bonus": 5,
            },
            {
                "testo": "🏆 **BOSS**: Maschera tutte le cifre di `'id 4521'` con `X` usando `re.sub`. Stampa `id XXXX`.",
                "placeholder": 'import re\ntesto = "id 4521"\n# sostituisci ogni cifra con X',
                "check": lambda out, err, vs: err is None and "id XXXX" in out,
                "feedback": lambda out, err: "Usa `re.sub(r'\\\\d', 'X', testo)`.",
                "hint": 'import re\ntesto = "id 4521"\nprint(re.sub(r"\\d", "X", testo))',
                "xp_bonus": 15,
            },
        ],
    },
    {
        "id": "pathlib_mod", "title": "Pathlib — percorsi moderni",
        "icon": "🗺️", "world": "🗺️ Cartografia dei File",
        "teoria": """
### Gestire i percorsi con pathlib
`pathlib.Path` rende i percorsi oggetti, non stringhe da concatenare a mano.

```python
from pathlib import Path
p = Path("/home/lore/dati/report.csv")
p.name      # 'report.csv'   nome file
p.stem      # 'report'       senza estensione
p.suffix    # '.csv'         estensione
p.parent    # /home/lore/dati
Path("data") / "raw" / "f.json"   # data/raw/f.json  (operatore /)
p.with_suffix(".txt")             # report.txt
```

Niente più `"a/" + "b/" + "c"`: usi `/` e funziona su ogni sistema.
""",
        "esempio": 'from pathlib import Path\np = Path("/home/lore/dati/report.csv")\nprint(p.name)\nprint(p.stem)\nprint(p.suffix)\nprint(p.parent)',
        "esercizi": [
            {
                "testo": "Crea `Path('backup/logs/app.log')` e stampa solo il nome del file (`app.log`).",
                "placeholder": "from pathlib import Path\np = Path('backup/logs/app.log')\n# stampa il nome del file",
                "check": lambda out, err, vs: err is None and out.strip() == "app.log",
                "feedback": lambda out, err: "Usa `p.name`.",
                "hint": "from pathlib import Path\np = Path('backup/logs/app.log')\nprint(p.name)",
                "xp_bonus": 0,
            },
            {
                "testo": "Costruisci con l'operatore `/` il percorso `data/raw/file.json` partendo da `Path('data')`. Stampalo.",
                "placeholder": "from pathlib import Path\n# Path('data') / ... / ...",
                "check": lambda out, err, vs: err is None and "data/raw/file.json" in out,
                "feedback": lambda out, err: "Usa `Path('data') / 'raw' / 'file.json'`.",
                "hint": "from pathlib import Path\np = Path('data') / 'raw' / 'file.json'\nprint(p)",
                "xp_bonus": 10,
            },
            {
                "tipo": "predict",
                "testo": "🔍 **PREVEDI**: Cosa stampano `.suffix` e `.stem` su un doppio suffisso?",
                "codice": 'from pathlib import Path\np = Path("archivio.tar.gz")\nprint(p.suffix)\nprint(p.stem)\n',
                "expected": ".gz\narchivio.tar",
                "hint": "`.suffix` prende solo l'ultima estensione (`.gz`); `.stem` toglie solo quella (`archivio.tar`).",
                "xp_bonus": 5,
            },
            {
                "testo": "🏆 **BOSS**: Cambia l'estensione di `Path('report.txt')` in `.md` con `with_suffix` e stampa `report.md`.",
                "placeholder": "from pathlib import Path\np = Path('report.txt')\n# cambia estensione e stampa",
                "check": lambda out, err, vs: err is None and "report.md" in out,
                "feedback": lambda out, err: "Usa `p.with_suffix('.md')`.",
                "hint": "from pathlib import Path\np = Path('report.txt')\nprint(p.with_suffix('.md'))",
                "xp_bonus": 15,
            },
        ],
    },
    {
        "id": "context_manager", "title": "Context Manager (with)",
        "icon": "🚪", "world": "🚪 Soglia delle Risorse",
        "teoria": """
### `with`: apri e chiudi in sicurezza
Un *context manager* garantisce la pulizia (chiusura file, connessioni) anche se qualcosa va storto.

```python
with open("f.txt") as f:   # f viene chiuso da solo all'uscita
    dati = f.read()
```

Puoi crearne uno con una classe (`__enter__` / `__exit__`):
```python
class Sessione:
    def __enter__(self):
        print("apro"); return self
    def __exit__(self, *args):
        print("chiudo")

with Sessione():
    print("uso")   # → apro / uso / chiudo
```

O con `@contextmanager` di `contextlib` (più conciso, con `yield`).
""",
        "esempio": 'from contextlib import contextmanager\n\n@contextmanager\ndef tag(nome):\n    print(f"<{nome}>")\n    yield\n    print(f"</{nome}>")\n\nwith tag("p"):\n    print("ciao")',
        "esercizi": [
            {
                "testo": "Crea una classe `Sessione` con `__enter__` che stampa `apro` e `__exit__` che stampa `chiudo`. Usala con un `with` che stampa `uso`.",
                "placeholder": "class Sessione:\n    def __enter__(self):\n        pass\n    def __exit__(self, *args):\n        pass\n\n# with Sessione(): ...",
                "check": lambda out, err, vs: err is None and "apro" in out and "uso" in out and "chiudo" in out and out.index("apro") < out.index("uso") < out.index("chiudo"),
                "feedback": lambda out, err: "`__enter__` deve `return self` e stampare 'apro'; `__exit__` stampa 'chiudo'. Dentro il with: print('uso').",
                "hint": "class Sessione:\n    def __enter__(self):\n        print('apro')\n        return self\n    def __exit__(self, *args):\n        print('chiudo')\n\nwith Sessione():\n    print('uso')",
                "xp_bonus": 10,
            },
            {
                "tipo": "predict",
                "testo": "🔍 **PREVEDI**: In che ordine vengono stampate le righe?",
                "codice": 'class CM:\n    def __enter__(self):\n        print("A")\n        return self\n    def __exit__(self, *a):\n        print("C")\n\nwith CM():\n    print("B")\n',
                "expected": "A\nB\nC",
                "hint": "`__enter__` (A) gira all'ingresso, poi il corpo del with (B), infine `__exit__` (C) all'uscita.",
                "xp_bonus": 5,
            },
            {
                "testo": "Usa `@contextmanager` per creare `blocco()` che stampa `--inizio--`, poi `yield`, poi `--fine--`. Usalo con un `with` che stampa `dentro`.",
                "placeholder": "from contextlib import contextmanager\n\n@contextmanager\ndef blocco():\n    pass\n\n# with blocco(): print('dentro')",
                "check": lambda out, err, vs: err is None and "--inizio--" in out and "dentro" in out and "--fine--" in out and out.index("--inizio--") < out.index("--fine--"),
                "feedback": lambda out, err: "Prima del `yield` stampa '--inizio--', dopo stampa '--fine--'.",
                "hint": "from contextlib import contextmanager\n\n@contextmanager\ndef blocco():\n    print('--inizio--')\n    yield\n    print('--fine--')\n\nwith blocco():\n    print('dentro')",
                "xp_bonus": 10,
            },
            {
                "testo": "🏆 **BOSS**: Crea un CM `Contatore` con metodo `conta()`; `__exit__` stampa `totale: N`. Chiama `conta()` 3 volte e ottieni `totale: 3`.",
                "placeholder": "class Contatore:\n    def __enter__(self):\n        self.n = 0\n        return self\n    def conta(self):\n        pass\n    def __exit__(self, *args):\n        pass\n\n# with Contatore() as c: ...",
                "check": lambda out, err, vs: err is None and "totale: 3" in out,
                "feedback": lambda out, err: "`conta` fa `self.n += 1`; `__exit__` stampa `f'totale: {self.n}'`.",
                "hint": "class Contatore:\n    def __enter__(self):\n        self.n = 0\n        return self\n    def conta(self):\n        self.n += 1\n    def __exit__(self, *args):\n        print(f'totale: {self.n}')\n\nwith Contatore() as c:\n    c.conta()\n    c.conta()\n    c.conta()",
                "xp_bonus": 15,
            },
        ],
    },
    {
        "id": "sqlite_mod", "title": "Database con SQLite",
        "icon": "🗄️", "world": "🗄️ Archivio SQL",
        "teoria": """
### Un database vero, incluso in Python
`sqlite3` è nella standard library: un DB SQL completo, anche solo in memoria.

```python
import sqlite3
con = sqlite3.connect(":memory:")   # DB in RAM (o un file: "dati.db")
cur = con.cursor()
cur.execute("CREATE TABLE servizi (nome TEXT, costo REAL)")
cur.execute("INSERT INTO servizi VALUES ('ec2', 0.5)")
cur.executemany("INSERT INTO servizi VALUES (?, ?)", [("s3", 0.02), ("rds", 0.9)])

for riga in cur.execute("SELECT * FROM servizi WHERE costo > 0.1"):
    print(riga)
print(cur.execute("SELECT COUNT(*) FROM servizi").fetchone()[0])
```

`?` sono **placeholder** sicuri (mai concatenare valori nelle query!). `fetchone()`/`fetchall()` leggono i risultati.
""",
        "esempio": 'import sqlite3\ncon = sqlite3.connect(":memory:")\ncur = con.cursor()\ncur.execute("CREATE TABLE t (nome TEXT)")\ncur.execute("INSERT INTO t VALUES (\'ec2\')")\nfor r in cur.execute("SELECT nome FROM t"):\n    print(r[0])',
        "esercizi": [
            {
                "testo": "Crea una tabella `t(nome TEXT)`, inserisci `'ec2'`, poi leggi e stampa il nome (`ec2`).",
                "placeholder": 'import sqlite3\ncon = sqlite3.connect(":memory:")\ncur = con.cursor()\n# crea, inserisci, seleziona, stampa',
                "check": lambda out, err, vs: err is None and "ec2" in out,
                "feedback": lambda out, err: "CREATE TABLE, INSERT, poi `for r in cur.execute('SELECT nome FROM t'): print(r[0])`.",
                "hint": 'import sqlite3\ncon = sqlite3.connect(":memory:")\ncur = con.cursor()\ncur.execute("CREATE TABLE t (nome TEXT)")\ncur.execute("INSERT INTO t VALUES (\'ec2\')")\nfor r in cur.execute("SELECT nome FROM t"):\n    print(r[0])',
                "xp_bonus": 0,
            },
            {
                "testo": "Inserisci i numeri `1, 2, 3` con `executemany` e stampa quante righe ci sono con `SELECT COUNT(*)`.",
                "placeholder": 'import sqlite3\ncon = sqlite3.connect(":memory:")\ncur = con.cursor()\ncur.execute("CREATE TABLE t (x INTEGER)")\n# executemany + COUNT(*)',
                "check": lambda out, err, vs: err is None and "3" in _ol(out),
                "feedback": lambda out, err: "`cur.executemany('INSERT INTO t VALUES (?)', [(1,), (2,), (3,)])`, poi `print(cur.execute('SELECT COUNT(*) FROM t').fetchone()[0])`.",
                "hint": 'import sqlite3\ncon = sqlite3.connect(":memory:")\ncur = con.cursor()\ncur.execute("CREATE TABLE t (x INTEGER)")\ncur.executemany("INSERT INTO t VALUES (?)", [(1,), (2,), (3,)])\nprint(cur.execute("SELECT COUNT(*) FROM t").fetchone()[0])',
                "xp_bonus": 10,
            },
            {
                "tipo": "predict",
                "testo": "🔍 **PREVEDI**: Cosa stampa la query con WHERE?",
                "codice": 'import sqlite3\ncon = sqlite3.connect(":memory:")\ncur = con.cursor()\ncur.execute("CREATE TABLE s (nome TEXT, costo REAL)")\ncur.executemany("INSERT INTO s VALUES (?, ?)", [("ec2", 5.0), ("s3", 0.5)])\nprint(cur.execute("SELECT nome FROM s WHERE costo > 1").fetchall())\n',
                "expected": "[('ec2',)]",
                "hint": "Solo 'ec2' ha costo > 1. `fetchall` restituisce una lista di tuple: `[('ec2',)]` (tupla con un solo campo).",
                "xp_bonus": 5,
            },
            {
                "testo": "🏆 **BOSS**: Inserisci i GB `120, 500, 80` e stampa la somma totale con `SELECT SUM(gb)` (= `700`).",
                "placeholder": 'import sqlite3\ncon = sqlite3.connect(":memory:")\ncur = con.cursor()\ncur.execute("CREATE TABLE c (gb INTEGER)")\n# inserisci e somma',
                "check": lambda out, err, vs: err is None and "700" in _ol(out),
                "feedback": lambda out, err: "executemany con [(120,), (500,), (80,)], poi `SELECT SUM(gb)` e `.fetchone()[0]`.",
                "hint": 'import sqlite3\ncon = sqlite3.connect(":memory:")\ncur = con.cursor()\ncur.execute("CREATE TABLE c (gb INTEGER)")\ncur.executemany("INSERT INTO c VALUES (?)", [(120,), (500,), (80,)])\nprint(cur.execute("SELECT SUM(gb) FROM c").fetchone()[0])',
                "xp_bonus": 15,
            },
        ],
    },
    {
        "id": "api_http", "title": "API HTTP & JSON (requests)",
        "icon": "🌐", "world": "🌐 Porto delle API",
        "teoria": """
### Parlare con un'API
Quasi ogni app moderna chiede dati a un server via HTTP. Libreria standard di fatto: `requests`.

```python
import requests
r = requests.get("https://api.example.com/istanze")
print(r.status_code)    # 200 = OK
dati = r.json()         # converte la risposta JSON in dict/list Python
print(dati["nome"])
```

Il cuore non è la chiamata, è **navigare il JSON** che torna (dict e liste annidate).
Negli esercizi qui sotto **simuliamo** quella risposta con `json.loads(...)` — la struttura è identica a quella che `r.json()` ti darebbe, così impari la parte che conta senza dipendere dalla rete.
""",
        "esempio": 'import json\nrisposta = \'{"servizio": "ec2", "stato": "running", "costo": 0.5}\'\ndati = json.loads(risposta)\nprint(dati["stato"])\nprint(dati["costo"])',
        "esercizi": [
            {
                "testo": "Una API ha risposto con `'{\"servizio\": \"ec2\", \"stato\": \"running\"}'`. Convertila e stampa il valore di `stato`.",
                "placeholder": 'import json\nrisposta = \'{"servizio": "ec2", "stato": "running"}\'\n# json.loads e stampa lo stato',
                "check": lambda out, err, vs: err is None and out.strip() == "running",
                "feedback": lambda out, err: "`dati = json.loads(risposta)` poi `print(dati['stato'])`.",
                "hint": 'import json\nrisposta = \'{"servizio": "ec2", "stato": "running"}\'\ndati = json.loads(risposta)\nprint(dati["stato"])',
                "xp_bonus": 0,
            },
            {
                "testo": "La risposta `'{\"region\": \"eu-west-1\", \"istanze\": [{\"id\": \"i-1\"}, {\"id\": \"i-2\"}]}'` contiene una lista. Stampa quante istanze ci sono.",
                "placeholder": 'import json\nrisposta = \'{"region": "eu-west-1", "istanze": [{"id": "i-1"}, {"id": "i-2"}]}\'\n# conta gli elementi di istanze',
                "check": lambda out, err, vs: err is None and "2" in _ol(out),
                "feedback": lambda out, err: "`len(dati['istanze'])`.",
                "hint": 'import json\nrisposta = \'{"region": "eu-west-1", "istanze": [{"id": "i-1"}, {"id": "i-2"}]}\'\ndati = json.loads(risposta)\nprint(len(dati["istanze"]))',
                "xp_bonus": 10,
            },
            {
                "tipo": "predict",
                "testo": "🔍 **PREVEDI**: Cosa stampa, navigando il JSON?",
                "codice": 'import json\nr = json.loads(\'{"items": [10, 20, 30]}\')\nprint(sum(r["items"]))\n',
                "expected": "60",
                "hint": "`r['items']` è la lista [10, 20, 30]; `sum(...)` la somma → 60.",
                "xp_bonus": 5,
            },
            {
                "testo": "🏆 **BOSS**: Dalla risposta `'{\"buckets\": [{\"name\": \"logs\"}, {\"name\": \"data\"}, {\"name\": \"backup\"}]}'` estrai la lista dei soli nomi e stampala (`['logs', 'data', 'backup']`).",
                "placeholder": 'import json\nrisposta = \'{"buckets": [{"name": "logs"}, {"name": "data"}, {"name": "backup"}]}\'\n# list comprehension sui nomi',
                "check": lambda out, err, vs: err is None and "['logs', 'data', 'backup']" in out,
                "feedback": lambda out, err: "`[b['name'] for b in dati['buckets']]`.",
                "hint": 'import json\nrisposta = \'{"buckets": [{"name": "logs"}, {"name": "data"}, {"name": "backup"}]}\'\ndati = json.loads(risposta)\nprint([b["name"] for b in dati["buckets"]])',
                "xp_bonus": 15,
            },
        ],
    },

    # ═══════════════════════════════════════════════════════════════════
    # FASE 6 — AVANZATO
    # ═══════════════════════════════════════════════════════════════════
    {
        "id": "asyncio_mod", "title": "Async / Await (asyncio)",
        "icon": "⚡", "world": "⚡ Dimensione Asincrona",
        "teoria": """
### Fare più cose mentre si aspetta
`asyncio` serve quando il codice **aspetta** (rete, disco, API): invece di stare fermo, fa altro.

```python
import asyncio

async def scarica(nome):       # coroutine: definita con async def
    await asyncio.sleep(0)     # await = "qui posso cedere il controllo"
    return f"{nome} pronto"

async def main():
    # gather lancia più coroutine "insieme" e raccoglie i risultati in ordine
    risultati = await asyncio.gather(scarica("a"), scarica("b"))
    print(risultati)

asyncio.run(main())            # avvia il loop asincrono
```

⚠️ Serve per attese **I/O-bound**, non per calcoli pesanti (CPU). `gather` preserva l'ordine dei risultati.
""",
        "esempio": 'import asyncio\n\nasync def saluta(nome):\n    await asyncio.sleep(0)\n    return f"Ciao {nome}"\n\nasync def main():\n    print(await saluta("Lorenzo"))\n\nasyncio.run(main())',
        "esercizi": [
            {
                "testo": "Scrivi una coroutine `async def numero()` che ritorna `42`. Eseguila con `asyncio.run(...)` e stampa il risultato.",
                "placeholder": "import asyncio\n\nasync def numero():\n    pass\n\n# asyncio.run e stampa",
                "check": lambda out, err, vs: err is None and "42" in _ol(out),
                "feedback": lambda out, err: "`return 42` nella coroutine, poi `print(asyncio.run(numero()))`.",
                "hint": "import asyncio\n\nasync def numero():\n    return 42\n\nprint(asyncio.run(numero()))",
                "xp_bonus": 0,
            },
            {
                "testo": "Usa `asyncio.gather` per eseguire `quadrato(2)`, `quadrato(3)`, `quadrato(4)` insieme e stampa la lista dei risultati (`[4, 9, 16]`).",
                "placeholder": "import asyncio\n\nasync def quadrato(n):\n    return n * n\n\nasync def main():\n    pass\n\nasyncio.run(main())",
                "check": lambda out, err, vs: err is None and "[4, 9, 16]" in out,
                "feedback": lambda out, err: "`risultati = await asyncio.gather(quadrato(2), quadrato(3), quadrato(4))` poi `print(risultati)`.",
                "hint": "import asyncio\n\nasync def quadrato(n):\n    return n * n\n\nasync def main():\n    risultati = await asyncio.gather(quadrato(2), quadrato(3), quadrato(4))\n    print(risultati)\n\nasyncio.run(main())",
                "xp_bonus": 10,
            },
            {
                "tipo": "predict",
                "testo": "🔍 **PREVEDI**: In che ordine vengono stampate le righe?",
                "codice": 'import asyncio\n\nasync def f():\n    print("dentro")\n    return 1\n\nasync def main():\n    print("prima")\n    await f()\n    print("dopo")\n\nasyncio.run(main())\n',
                "expected": "prima\ndentro\ndopo",
                "hint": "`await f()` esegue subito f() (stampa 'dentro') prima di proseguire: prima → dentro → dopo.",
                "xp_bonus": 5,
            },
            {
                "testo": "🏆 **BOSS**: `async def costo(x)` ritorna `x * 0.5`. Con `gather` calcola costo di 10, 20, 30 e stampa la **somma** dei risultati (`30.0`).",
                "placeholder": "import asyncio\n\nasync def costo(x):\n    return x * 0.5\n\nasync def main():\n    pass\n\nasyncio.run(main())",
                "check": lambda out, err, vs: err is None and "30.0" in out,
                "feedback": lambda out, err: "`valori = await asyncio.gather(costo(10), costo(20), costo(30))` poi `print(sum(valori))`.",
                "hint": "import asyncio\n\nasync def costo(x):\n    return x * 0.5\n\nasync def main():\n    valori = await asyncio.gather(costo(10), costo(20), costo(30))\n    print(sum(valori))\n\nasyncio.run(main())",
                "xp_bonus": 15,
            },
        ],
    },
    {
        "id": "packaging", "title": "Packaging & Versioning",
        "icon": "📦", "world": "📦 Cantiere dei Pacchetti",
        "teoria": """
### Da script a pacchetto installabile
Un progetto serio ha una struttura e una versione:

```
mio_pacchetto/
├── pyproject.toml      # metadati, dipendenze, versione
├── src/mio_pacchetto/
│   ├── __init__.py     # rende la cartella un package
│   └── core.py
└── tests/
```
```bash
pip install -e .        # installa in modalità "editabile"
```

**`if __name__ == "__main__":`** → il codice parte solo se esegui il file direttamente, non se lo importi.

**Semantic Versioning** `MAJOR.MINOR.PATCH` (es. `2.5.1`):
- `PATCH` → bugfix · `MINOR` → nuove feature compatibili · `MAJOR` → cambi che rompono.

⚠️ Confrontare versioni come **stringhe** è sbagliato (`"1.10" < "1.2"` è True!). Convertile in tuple di interi.
""",
        "esempio": 'versione = "2.5.1"\nmajor, minor, patch = versione.split(".")\nprint(f"major={major} minor={minor} patch={patch}")',
        "esercizi": [
            {
                "tipo": "predict",
                "testo": "🔍 **PREVEDI**: Eseguendo il file direttamente, cosa stampa?",
                "codice": 'def main():\n    print("avvio")\n\nif __name__ == "__main__":\n    main()\n',
                "expected": "avvio",
                "hint": "Eseguito direttamente, `__name__` vale `'__main__'`, quindi la condizione è vera e `main()` parte: stampa 'avvio'.",
                "xp_bonus": 5,
            },
            {
                "testo": "La versione è `'3.11.4'`. Estrai e stampa solo il numero **MAJOR** (`3`).",
                "placeholder": 'versione = "3.11.4"\n# stampa il major',
                "check": lambda out, err, vs: err is None and out.strip() == "3",
                "feedback": lambda out, err: "`versione.split('.')[0]` è la prima parte.",
                "hint": 'versione = "3.11.4"\nprint(versione.split(".")[0])',
                "xp_bonus": 10,
            },
            {
                "testo": "Confronta `'1.2.0'` e `'1.10.0'` **come tuple di interi** e stampa se la seconda è maggiore (`True`). (Come stringhe darebbe il risultato sbagliato!)",
                "placeholder": 'v1 = "1.2.0"\nv2 = "1.10.0"\n# converti in tuple di int e confronta',
                "check": lambda out, err, vs: err is None and out.strip() == "True",
                "feedback": lambda out, err: "`tuple(int(x) for x in v.split('.'))` per entrambe, poi confronta con `>`.",
                "hint": 'v1 = tuple(int(x) for x in "1.2.0".split("."))\nv2 = tuple(int(x) for x in "1.10.0".split("."))\nprint(v2 > v1)',
                "xp_bonus": 10,
            },
            {
                "testo": "🏆 **BOSS**: Incrementa il **PATCH** di `'1.4.9'` di uno e stampa la nuova versione (`1.4.10`).",
                "placeholder": 'versione = "1.4.9"\n# scomponi, incrementa il patch, ricomponi',
                "check": lambda out, err, vs: err is None and "1.4.10" in out,
                "feedback": lambda out, err: "Scomponi in interi, `patch += 1`, poi `f'{major}.{minor}.{patch}'`.",
                "hint": 'major, minor, patch = (int(x) for x in "1.4.9".split("."))\npatch += 1\nprint(f"{major}.{minor}.{patch}")',
                "xp_bonus": 15,
            },
        ],
    },
    {
        "id": "design_patterns", "title": "Design Patterns",
        "icon": "🧩", "world": "🧩 Tempio dei Pattern",
        "teoria": """
### Soluzioni collaudate a problemi ricorrenti
I *design pattern* sono schemi riutilizzabili. Tre classici:

**Factory** — una funzione che costruisce l'oggetto giusto in base a un input:
```python
def crea(tipo):
    return {"cane": Cane, "gatto": Gatto}[tipo]()
```

**Strategy** — scegli un comportamento da un dizionario di funzioni, niente `if/elif` infiniti:
```python
strategie = {"carta": paga_carta, "paypal": paga_paypal}
strategie["paypal"](50)
```

**Singleton** — una sola istanza condivisa (es. configurazione globale), via `__new__`:
```python
class Config:
    _istanza = None
    def __new__(cls):
        if cls._istanza is None:
            cls._istanza = super().__new__(cls)
        return cls._istanza
```
""",
        "esempio": 'def paga_carta(importo): return f"Carta: {importo}euro"\ndef paga_paypal(importo): return f"PayPal: {importo}euro"\n\nstrategie = {"carta": paga_carta, "paypal": paga_paypal}\nprint(strategie["paypal"](50))',
        "esercizi": [
            {
                "testo": "**Factory**: scrivi `crea_risorsa(tipo)` che mappa `ec2→Server`, `s3→Storage`, `rds→Database` (default `Sconosciuto`). Stampa `crea_risorsa('s3')`.",
                "placeholder": "def crea_risorsa(tipo):\n    pass\n\nprint(crea_risorsa('s3'))",
                "check": lambda out, err, vs: err is None and "Storage" in out,
                "feedback": lambda out, err: "Usa un dict e `.get(tipo, 'Sconosciuto')`.",
                "hint": "def crea_risorsa(tipo):\n    risorse = {'ec2': 'Server', 's3': 'Storage', 'rds': 'Database'}\n    return risorse.get(tipo, 'Sconosciuto')\n\nprint(crea_risorsa('s3'))",
                "xp_bonus": 0,
            },
            {
                "testo": "**Strategy**: dato `strategie = {'nessuno': ..., 'meta': ...}` con funzioni di sconto, applica la strategia `'meta'` a `100` e stampa (`50.0`).",
                "placeholder": "def sconto_nessuno(p):\n    return p\ndef sconto_meta(p):\n    return p / 2\n\nstrategie = {'nessuno': sconto_nessuno, 'meta': sconto_meta}\n# applica 'meta' a 100 e stampa",
                "check": lambda out, err, vs: err is None and "50.0" in out,
                "feedback": lambda out, err: "`print(strategie['meta'](100))`.",
                "hint": "def sconto_nessuno(p):\n    return p\ndef sconto_meta(p):\n    return p / 2\n\nstrategie = {'nessuno': sconto_nessuno, 'meta': sconto_meta}\nprint(strategie['meta'](100))",
                "xp_bonus": 10,
            },
            {
                "tipo": "predict",
                "testo": "🔍 **PREVEDI**: Due `Config()` sono lo stesso oggetto? Cosa stampa?",
                "codice": 'class Config:\n    _istanza = None\n    def __new__(cls):\n        if cls._istanza is None:\n            cls._istanza = super().__new__(cls)\n        return cls._istanza\n\na = Config()\nb = Config()\nprint(a is b)\n',
                "expected": "True",
                "hint": "Il Singleton via `__new__` restituisce sempre la stessa istanza: `a is b` è True.",
                "xp_bonus": 5,
            },
            {
                "testo": "🏆 **BOSS**: **Factory di classi** — `Cane.verso()→'Bau'`, `Gatto.verso()→'Miao'`. Scrivi `crea(tipo)` che istanzia la classe giusta. Stampa `crea('gatto').verso()`.",
                "placeholder": "class Cane:\n    def verso(self):\n        return 'Bau'\nclass Gatto:\n    def verso(self):\n        return 'Miao'\n\ndef crea(tipo):\n    pass\n\nprint(crea('gatto').verso())",
                "check": lambda out, err, vs: err is None and "Miao" in out,
                "feedback": lambda out, err: "`return {'cane': Cane, 'gatto': Gatto}[tipo]()` — nota le parentesi `()` per istanziare.",
                "hint": "class Cane:\n    def verso(self):\n        return 'Bau'\nclass Gatto:\n    def verso(self):\n        return 'Miao'\n\ndef crea(tipo):\n    return {'cane': Cane, 'gatto': Gatto}[tipo]()\n\nprint(crea('gatto').verso())",
                "xp_bonus": 15,
            },
        ],
    },
]


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
