"""
Dati del curriculum del Python Trainer (estratti da app.py).

Contiene:
  _ol         — helper usato dalle lambda `check` degli esercizi
  CONCETTI    — analogie / errori comuni / quando-usarlo per modulo
  APPROCCIO   — domande-guida e checklist per modulo
  CURRICULUM  — i 36 moduli con teoria, esempi ed esercizi
"""


def _ol(out: str) -> set[str]:
    """Righe normalizzate (strip) dell'output, vuote escluse. Per check esatti su singole righe."""
    return {l.strip() for l in out.strip().splitlines() if l.strip()}


CONCETTI = {'automazione': {'analogia': '\n'
                             '**Il tuo script è un robot in fabbrica.**\n'
                             '\n'
                             '`os` è il braccio che si muove tra i cassetti del filesystem.\n'
                             '`open()` è la mano che apre e chiude scatole (file).\n'
                             'Il for loop è il nastro trasportatore che porta ogni file al robot.\n'
                             '\n'
                             '```python\n'
                             'import os\n'
                             '\n'
                             'for nome_file in os.listdir("/var/log/demo"):     # nastro\n'
                             '    if nome_file.endswith(".log"):                # filtro\n'
                             '        with open(nome_file, "r") as f:           # apri scatola\n'
                             '            contenuto = f.read()                  # leggi\n'
                             '            if "ERROR" in contenuto:\n'
                             '                print(f"Problema in: {nome_file}")\n'
                             '```\n'
                             '\n'
                             'Il robot non si stanca. Processa 1 file o 10.000 con lo stesso '
                             'sforzo.\n',
                 'perche': '\n'
                           '**Perché automazione e file sono cruciali nel lavoro Cloud?**\n'
                           '\n'
                           'Scenari reali in cui userai questi strumenti:\n'
                           '\n'
                           '1. **Report di costo** — scarichi i dati di billing Python (CSV) e li '
                           'elabori con Python\n'
                           '2. **Analisi log** — leggi file di log da Disco, cerchi pattern di '
                           'errore\n'
                           '3. **Backup automatici** — crei cartelle con timestamp, sposti file\n'
                           '4. **Config management** — leggi file YAML/JSON con configurazioni di '
                           'deploy\n'
                           '\n'
                           '```python\n'
                           'import os\n'
                           'from datetime import date\n'
                           '\n'
                           '# Crea cartella backup con data odierna\n'
                           'oggi = str(date.today())\n'
                           'cartella = f"backup_{oggi}"\n'
                           'os.makedirs(cartella, exist_ok=True)\n'
                           '\n'
                           '# Salva report\n'
                           'with open(f"{cartella}/report.txt", "w") as f:\n'
                           '    f.write(f"Report del {oggi}\\n")\n'
                           '    f.write("Istanze attive: 12\\n")\n'
                           '    f.write("Costo stimato: $142.50\\n")\n'
                           '```\n',
                 'errori_comuni': [{'titolo': "❌ Non usare 'with' per aprire file",
                                    'testo': 'Senza `with`, se il codice crasha il file rimane '
                                             'aperto e bloccato.',
                                    'codice_sbagliato': "f = open('file.txt')\n"
                                                        'contenuto = f.read()\n'
                                                        '# se qui crasha, f rimane aperto',
                                    'codice_giusto': "with open('file.txt') as f:\n"
                                                     '    contenuto = f.read()\n'
                                                     '# chiuso automaticamente'},
                                   {'titolo': '❌ Modalità sbagliata',
                                    'testo': "`'r'` legge, `'w'` scrive (sovrascrive), `'a'` "
                                             "aggiunge alla fine. `'w'` cancella il contenuto "
                                             'esistente!',
                                    'codice_sbagliato': "with open('log.txt', 'w') as f:\n"
                                                        "    f.write('nuova riga')  # cancella "
                                                        'tutto il log!',
                                    'codice_giusto': "with open('log.txt', 'a') as f:\n"
                                                     "    f.write('nuova riga\\n')  # aggiunge in "
                                                     'fondo'},
                                   {'titolo': '❌ Path relativo vs assoluto',
                                    'testo': 'Un path relativo dipende da dove esegui lo script. '
                                             'Usa `os.path.join()` per costruire path portabili.',
                                    'codice_sbagliato': "open('data/file.txt')  # funziona solo se "
                                                        'esegui dalla cartella giusta',
                                    'codice_giusto': 'base = os.path.dirname(__file__)\n'
                                                     "path = os.path.join(base, 'data', "
                                                     "'file.txt')"}],
                 'quando_usarlo': 'Ogni volta che devi leggere/scrivere file, navigare cartelle, '
                                  'salvare report, leggere configurazioni. Fondamentale per '
                                  'qualsiasi script di automazione reale.'},
 'setup_env': {'analogia': '\n'
                           '**Il venv è una stanza pulita per ogni progetto.**\n'
                           '\n'
                           'Senza ambienti virtuali, tutte le librerie di tutti i tuoi progetti '
                           'convivono\n'
                           'nella stessa stanza. La versione di requests che serve al progetto A '
                           'rompe il progetto B.\n'
                           '\n'
                           '```bash\n'
                           'python -m venv .venv          # crea la stanza\n'
                           'source .venv/bin/activate     # entra nella stanza (Linux/Mac)\n'
                           '.venv\\Scripts\\activate        # entra nella stanza (Windows)\n'
                           'pip install requests streamlit   # installa SOLO in questa stanza\n'
                           '```\n'
                           '\n'
                           'Ogni progetto ha la sua stanza. Nessun conflitto.\n',
               'perche': '\n'
                         "**Perché venv e pip sono il primo passo — non l'ultimo.**\n"
                         '\n'
                         '```bash\n'
                         '# Installa dipendenze\n'
                         'pip install -r requirements.txt\n'
                         '\n'
                         '# Congela le versioni esatte (riproducibilità)\n'
                         'pip freeze > requirements.txt\n'
                         '\n'
                         '# Versioni moderne (più veloci di pip)\n'
                         'pip install uv\n'
                         'uv pip install requests\n'
                         '```\n'
                         '\n'
                         'Senza requirements.txt il codice funziona sul tuo PC ma non in '
                         'produzione.\n'
                         'Con requirements.txt il deploy è deterministico.\n',
               'errori_comuni': [{'titolo': '❌ pip install senza venv attivo',
                                  'testo': 'Installa a livello di sistema — rompe altri progetti o '
                                           'richiede sudo.',
                                  'codice_sbagliato': '# terminale senza venv attivo\n'
                                                      'pip install requests  # va nel Python di '
                                                      'sistema',
                                  'codice_giusto': 'source .venv/bin/activate  # prima attiva\n'
                                                   'pip install requests           # poi installa'},
                                 {'titolo': '❌ Committare .venv su git',
                                  'testo': 'La cartella .venv pesa centinaia di MB e non è '
                                           'portabile tra sistemi.',
                                  'codice_sbagliato': 'git add .venv  # centinaia di MB nel repo',
                                  'codice_giusto': "echo '.venv/' >> .gitignore\n"
                                                   'git add requirements.txt  # solo questo'},
                                 {'titolo': '❌ requirements.txt senza versioni',
                                  'testo': '`pip freeze` include le versioni esatte. Senza, `pip '
                                           "install` prende l'ultima — che potrebbe rompere tutto.",
                                  'codice_sbagliato': '# requirements.txt\nboto3\nstreamlit',
                                  'codice_giusto': 'requests==1.34.0\nstreamlit==1.40.0'}],
               'quando_usarlo': 'Sempre — ogni progetto Python merita il suo venv. Non è '
                                'opzionale, è igiene.'},
 'tuple_immutabilita': {'analogia': '\n'
                                    '**La tupla è cemento. La lista è argilla.**\n'
                                    '\n'
                                    'Argilla (lista) — puoi aggiungere, togliere, modificare.\n'
                                    'Cemento (tupla) — una volta solidificato, non cambia più. Ma '
                                    'è più solido, più veloce, più sicuro da condividere.\n'
                                    '\n'
                                    '```python\n'
                                    'lista  = [1, 2, 3]   # argilla: modificabile\n'
                                    'lista[0] = 99        # ok\n'
                                    '\n'
                                    'tupla  = (1, 2, 3)   # cemento: immutabile\n'
                                    'tupla[0] = 99        # TypeError!\n'
                                    '```\n',
                        'perche': '\n'
                                  '**Quando usare tuple e perché copy/deepcopy importano:**\n'
                                  '\n'
                                  '```python\n'
                                  '# Tuple unpacking — elegante e diretto\n'
                                  'latitudine, longitudine = (45.07, 7.69)\n'
                                  'nome, *resto = ("Lorenzo", "dev", "Torino")\n'
                                  '\n'
                                  '# Chiave di dizionario (le liste non possono esserlo)\n'
                                  'cache = {}\n'
                                  'cache[(45.07, 7.69)] = "Torino"  # tupla come chiave\n'
                                  '\n'
                                  '# copy vs deepcopy\n'
                                  'import copy\n'
                                  'originale = {"lista": [1, 2, 3]}\n'
                                  'superficiale = copy.copy(originale)\n'
                                  'profonda     = copy.deepcopy(originale)\n'
                                  '\n'
                                  'superficiale["lista"].append(4)  # modifica ANCHE originale!\n'
                                  'profonda["lista"].append(5)      # non tocca originale\n'
                                  '```\n',
                        'errori_comuni': [{'titolo': '❌ Tupla da un elemento senza virgola',
                                           'testo': '`(42)` è solo `42` tra parentesi. `(42,)` è '
                                                    'una tupla con un elemento.',
                                           'codice_sbagliato': 't = (42)\n'
                                                               "print(type(t))  # <class 'int'>",
                                           'codice_giusto': 't = (42,)\n'
                                                            "print(type(t))  # <class 'tuple'>"},
                                          {'titolo': '❌ Modificare un elemento mutabile dentro una '
                                                     'tupla',
                                           'testo': 'La tupla è immutabile, ma se contiene una '
                                                    'lista, la lista è ancora modificabile.',
                                           'codice_sbagliato': "t = ([1, 2], 'ok')\n"
                                                               't[0].append(3)  # funziona! t[0] è '
                                                               'ancora [1,2,3]',
                                           'codice_giusto': '# Usa tuple di soli immutabili se hai '
                                                            'bisogno di vera immutabilità'},
                                          {'titolo': '❌ copy() su strutture annidate',
                                           'testo': '`copy.copy()` è superficiale: copia il '
                                                    'container ma condivide gli oggetti interni.',
                                           'codice_sbagliato': "a = {'k': [1,2,3]}\n"
                                                               'b = copy.copy(a)\n'
                                                               "b['k'].append(4)  # modifica anche "
                                                               "a['k']!",
                                           'codice_giusto': 'b = copy.deepcopy(a)  # indipendente '
                                                            'a tutti i livelli'}],
                        'quando_usarlo': 'Tuple per dati che non devono cambiare (coordinate, '
                                         'chiavi composite, ritorni multipli). deepcopy quando '
                                         'devi clonare strutture annidate senza rischi.'},
 'controllo_avanzato': {'analogia': '\n'
                                    "**break è l'uscita d'emergenza. continue è il filtraggio. "
                                    'else è la conferma.**\n'
                                    '\n'
                                    '```python\n'
                                    '# break — esci appena trovi quello che cerchi\n'
                                    'for ist in prodotti:\n'
                                    '    if ist["stato"] == "running":\n'
                                    '        prima_running = ist\n'
                                    '        break   # inutile continuare\n'
                                    '\n'
                                    '# continue — salta i casi non interessanti\n'
                                    'for ist in prodotti:\n'
                                    '    if ist["stato"] == "stopped":\n'
                                    '        continue   # non mi interessa\n'
                                    '    processa(ist)\n'
                                    '\n'
                                    '# for/else — else esegue SOLO se il loop non ha fatto break\n'
                                    'for ist in prodotti:\n'
                                    '    if ist["id"] == target_id:\n'
                                    '        print("Trovato!")\n'
                                    '        break\n'
                                    'else:\n'
                                    '    print("Non trovato — cercalo in un\'altra regione")\n'
                                    '```\n',
                        'perche': '\n'
                                  '**match/case — Python 3.10+ — per classificare strutture:**\n'
                                  '\n'
                                  '```python\n'
                                  '# Classifica risposte HTTP\n'
                                  'def gestisci(codice):\n'
                                  '    match codice:\n'
                                  '        case 200: return "OK"\n'
                                  '        case 404: return "Non trovato"\n'
                                  '        case 403: return "Accesso negato"\n'
                                  '        case c if c >= 500: return f"Errore server ({c})"\n'
                                  '        case _: return "Codice sconosciuto"\n'
                                  '\n'
                                  '# Match su strutture requests\n'
                                  'match risposta.get("State", {}).get("Name"):\n'
                                  '    case "running":  avvia_monitoraggio()\n'
                                  '    case "stopped":  notifica_team()\n'
                                  '    case _:          log_stato_insolito()\n'
                                  '```\n',
                        'errori_comuni': [{'titolo': '❌ break fuori da un loop',
                                           'testo': '`break` e `continue` funzionano solo dentro '
                                                    'for/while.',
                                           'codice_sbagliato': 'if condizione:\n'
                                                               '    break  # SyntaxError fuori da '
                                                               'loop',
                                           'codice_giusto': 'for x in lista:\n'
                                                            '    if condizione:\n'
                                                            '        break'},
                                          {'titolo': '❌ continue in while senza aggiornare la '
                                                     'variabile',
                                           'testo': '`continue` salta il resto del corpo — se '
                                                    'aggiorni la variabile in fondo, il loop '
                                                    'diventa infinito.',
                                           'codice_sbagliato': 'n = 0\n'
                                                               'while n < 5:\n'
                                                               '    if n == 3: continue\n'
                                                               '    n += 1   # non raggiunto '
                                                               'quando n==3 → loop infinito',
                                           'codice_giusto': 'n = 0\n'
                                                            'while n < 5:\n'
                                                            '    n += 1\n'
                                                            '    if n == 3: continue\n'
                                                            '    print(n)'},
                                          {'titolo': '❌ for/else male interpretato',
                                           'testo': "Il `else` del for NON significa 'se il for è "
                                                    "vuoto'. Esegue SEMPRE tranne se è avvenuto un "
                                                    'break.',
                                           'codice_sbagliato': "# pensando che else = 'lista "
                                                               "vuota'\n"
                                                               'for x in []:  # else esegue\n'
                                                               '    pass\n'
                                                               'else:\n'
                                                               "    print('Vuota')  # esegue, ma "
                                                               'anche se la lista ha elementi!',
                                           'codice_giusto': "# else = 'non è avvenuto break'\n"
                                                            '# Per lista vuota: if not lista:'}],
                        'quando_usarlo': 'break per uscire appena trovi. continue per saltare casi '
                                         'non interessanti (più leggibile di if annidati). '
                                         'for/else per ricerche. match/case per classificare '
                                         'valori o strutture (Python 3.10+).'}}


APPROCCIO = {'variabili': {'domanda_chiave': 'Cosa sto etichettando e perché mi servirà dopo?',
               'prima_di_codificare': ['Che tipo di valore devo conservare? (testo, numero, '
                                       'vero/falso?)',
                                       'Lo userò più di una volta nel codice?',
                                       'Il valore è fisso o può cambiare nel tempo?',
                                       'Che nome lo descrive meglio? (evita: x, a, val, temp)'],
               'pattern': ['Definisci prima → usa dopo. Mai il contrario.',
                           'Calcola → salva in variabile → riusa la variabile',
                           "Costanti di configurazione all'inizio del file, in MAIUSCOLO"],
               'checklist': ['Il nome è descrittivo (non x, a, dato)?',
                             'Definita PRIMA di essere usata?',
                             'Uso `=` per assegnare e `==` per confrontare?',
                             'Il tipo è quello giusto? (stringa vs numero vs booleano)']},
 'condizioni': {'domanda_chiave': 'Quante strade può prendere il codice? Le ho gestite tutte?',
                'prima_di_codificare': ['Quante situazioni distinte esistono? (2, 3, N?)',
                                        'Le condizioni si escludono a vicenda? → elif. '
                                        'Indipendenti? → if separati',
                                        "Ho un caso 'tutto il resto'? → else",
                                        "L'ordine dei rami importa? (dal più specifico al più "
                                        'generico)'],
                'pattern': ['Due casi → `if / else`',
                            'Più casi mutuamente esclusivi → `if / elif / elif / else`',
                            'Più controlli indipendenti → `if` separati (non elif)',
                            'Soglie: ordina dal valore più alto al più basso'],
                'checklist': ['Due punti `:` dopo ogni if/elif/else?',
                              'Indentazione di 4 spazi sotto ogni ramo?',
                              'Uso `==` per confrontare, non `=` per assegnare?',
                              "Qual è l'output se nessuna condizione è vera?"]},
 'cicli': {'domanda_chiave': 'Cosa devo costruire/raccogliere? Inizializzalo vuoto PRIMA del loop.',
           'prima_di_codificare': ['Quante volte si ripete? (numero fisso → `range`, sequenza → '
                                   '`for`, condizione → `while`)',
                                   "Ho bisogno dell'indice o solo del valore?",
                                   'Devo raccogliere risultati? → inizializza `[]` o `0` prima del '
                                   'loop',
                                   "C'è un caso in cui il loop non dovrebbe girare?"],
           'pattern': ['Itera valori → `for x in lista`',
                       'Itera con indice → `for i, x in enumerate(lista)`',
                       'Accumula → `totale = 0` prima, `totale += x` dentro',
                       'Filtra → `if condizione:` dentro il for',
                       'Trasforma → `risultati.append(f(x))` o list comprehension `[f(x) for x in '
                       'lista]`'],
           'checklist': ['`range(n)` va da 0 a n-1. Per 1→n: `range(1, n+1)`',
                         'Nel while: aggiorno la variabile di controllo?',
                         'Sto modificando la lista su cui sto iterando? (usa list comprehension '
                         'invece)',
                         'Il loop termina sempre? (no loop infinito?)']},
 'funzioni': {'domanda_chiave': 'Se questo codice cambia domani, quanti posti devo modificare?',
              'prima_di_codificare': ['Questo codice lo riscriverò più di una volta? → fai una '
                                      'funzione',
                                      'Quanti input riceve? (parametri) Quali hanno senso come '
                                      'default?',
                                      'Cosa restituisce? (`return` valore) o solo stampa?',
                                      'Ha una responsabilità sola? Se fa N cose → N funzioni'],
              'pattern': ["Nome che descrive l'azione: `calcola_`, `ottieni_`, `verifica_`, "
                          '`salva_`',
                          'Una funzione = una responsabilità sola',
                          "Default parameters per valori comuni: `def f(regione='nord')`",
                          'Testa con input semplici prima di usarla in contesti complessi'],
              'checklist': ['Ha `return` se deve dare un valore?',
                            'I parametri hanno nomi descrittivi?',
                            'Fa una sola cosa?',
                            "L'ho chiamata con input limite? (0, lista vuota, None)"]},
 'liste_dizionari': {'domanda_chiave': 'Cosa entra? (lista/dict) Cosa devo ottenere? Filtrare, '
                                       'trasformare o navigare?',
                     'prima_di_codificare': ['Sequenza ordinata? → lista. Coppie chiave-valore? → '
                                             'dizionario',
                                             'Devo cercare per posizione o per nome?',
                                             'La risposta requests: è una lista di dict o un dict '
                                             'con liste annidate?',
                                             'Devo filtrare, trasformare, o solo iterare?'],
                     'pattern': ['Filtra → `[x for x in lista if condizione]`',
                                 'Trasforma → `[f(x) for x in lista]`',
                                 "Naviga requests → `risposta['Reservations'][0]['Instances']`",
                                 "Accesso sicuro → `dict.get('chiave', default)` evita KeyError"],
                     'checklist': ['La lista può essere vuota? Ho gestito quel caso?',
                                   'La chiave del dict esiste sempre? Se no, uso `.get()`?',
                                   'requests: la risposta è una lista o un singolo elemento?',
                                   'Sto modificando la lista mentre ci itero? (usa list '
                                   'comprehension)']},
 'automazione': {'domanda_chiave': 'Cosa può andare storto con file e path? (non esiste, permessi, '
                                   'path errato)',
                 'prima_di_codificare': ['Il file esiste già? Cosa succede se non esiste?',
                                         'Devo leggere (`r`), sovrascrivere (`w`) o aggiungere '
                                         '(`a`)?',
                                         'Il path è assoluto o relativo? Funziona su altre '
                                         'macchine?',
                                         'Devo creare la directory prima di creare il file?'],
                 'pattern': ['Sempre `with open(...)` — si chiude automaticamente',
                             'Costruisci path con `os.path.join()` non con `+`',
                             'Crea directory con `exist_ok=True`',
                             'Leggi → processa → scrivi (non mescolare lettura e scrittura dello '
                             'stesso file)'],
                 'checklist': ['Ho usato `with open(...)` (non `f = open(...)` senza close)?',
                               'La modalità è giusta? `w` sovrascrive tutto!',
                               "Ho gestito il caso 'file non esiste'?",
                               "Il path funziona anche su un'altra macchina?"]},
 'kwargs_unpacking': {'domanda_chiave': 'Sto costruendo questa chiamata staticamente o '
                                        'dinamicamente in base a condizioni?',
                      'prima_di_codificare': ['I parametri sono sempre gli stessi o variano in '
                                              'base alla logica?',
                                              'Stai leggendo codice requests con `**params`? → '
                                              'stai vedendo un dict spacchettato',
                                              'La funzione deve essere flessibile? → considera '
                                              '`**kwargs`',
                                              'Devo includere parametri opzionali solo se '
                                              'presenti? → costruisci dict e usa `**`'],
                      'pattern': ["`params = {}; if cond: params['K'] = v` → poi `f(**params)` "
                                  '(chiamata dinamica)',
                                  "`def f(**kwargs): kwargs.get('k', default)` per accesso sicuro "
                                  'ai parametri',
                                  '`*lista` spacchetta come argomenti posizionali',
                                  '`**dict` spacchetta come keyword arguments'],
                      'checklist': ['Ho usato `**` (doppio) per dict e `*` (singolo) per liste?',
                                    'Le chiavi del dict corrispondono ai nomi dei parametri della '
                                    'funzione?',
                                    'Il dict non ha chiavi extra non accettate dalla funzione?',
                                    'requests: ho verificato quali parametri sono obbligatori vs '
                                    'opzionali nella doc?']},
 'json_env': {'domanda_chiave': "Questo dato viene dall'esterno (file, API, env)? → devo "
                                'deserializzarlo. Va fuori? → devo serializzarlo.',
              'prima_di_codificare': ['Ho una stringa da convertire in dict? → '
                                      '`json.loads(stringa)`',
                                      'Ho un dict da convertire in stringa? → `json.dumps(dict)`',
                                      'Sto leggendo da file? → `json.load(file_obj)` (senza la s)',
                                      'Le credenziali devono stare in env var, non nel codice'],
              'pattern': ["`os.environ.get('CHIAVE', 'default')` — sempre con default, mai "
                          'KeyError',
                          '`json.dumps(obj, indent=2)` per output leggibile',
                          'Config: JSON file per defaults + env var per override in produzione',
                          'requests legge `AWS_*` env var automaticamente'],
              'checklist': ['Sto usando `json.loads` per stringhe o `json.load` per file?',
                            'Tutte le env var hanno un default sicuro con `.get()`?',
                            'Nessuna credenziale hardcodata nel codice?',
                            'Il JSON che genero è valido? Posso verificarlo con '
                            '`json.loads(json.dumps(obj))`?']},
 'comprehensions': {'domanda_chiave': 'Cosa devo ottenere? (lista/dict/set) Da cosa parto? Quali '
                                      'elementi filtro o trasformo?',
                    'prima_di_codificare': ['Sto costruendo una lista? → list comprehension '
                                            '`[...]`',
                                            'Sto costruendo un mapping? → dict comprehension `{k: '
                                            'v ...}`',
                                            'La logica è semplice (1 filtro, 1 trasformazione)? → '
                                            'comprehension OK',
                                            'La logica è complessa (2+ condizioni, side effect)? → '
                                            'loop esplicito'],
                    'pattern': ['Filtra: `[x for x in lista if condizione]`',
                                'Trasforma: `[f(x) for x in lista]`',
                                'Filtra+trasforma: `[f(x) for x in lista if condizione]`',
                                "Dict: `{x['id']: x['stato'] for x in lista}`",
                                'Generator (lazy, no lista in RAM): `sum(x for x in lista)`'],
                    'checklist': ["L'`if` di filtro sta DOPO il `for`, non prima dell'espressione?",
                                  'Sto creando una struttura dati o eseguendo azioni? (loop per '
                                  'azioni)',
                                  'La comprehension è leggibile in una riga? Se no, usa loop',
                                  'Il tipo è giusto? `[...]` lista, `{...}` set o dict, `(...)` '
                                  'generator']},
 'builtins': {'domanda_chiave': 'Ho bisogno di indice + valore? (enumerate) Di iterare su più '
                                'liste? (zip) Di ordine? (sorted)',
              'prima_di_codificare': ["Ho bisogno dell'indice E del valore? → `enumerate(lista)`",
                                      'Devo abbinare elementi di due liste? → `zip(lista1, '
                                      'lista2)`',
                                      'Devo ordinare per un campo specifico? → `sorted(lista, '
                                      "key=lambda x: x['campo'])`",
                                      'Un valore potrebbe essere `None`? → usa `is None`, non `== '
                                      'None`'],
              'pattern': ['`for i, val in enumerate(lista, start=1)` — numerazione da 1',
                          '`for a, b in zip(lista1, lista2)` — parallelo',
                          "`sorted(lista, key=lambda x: x['k'], reverse=True)` — decrescente",
                          "`val = obj.get('campo')` → `if val is not None: usa(val)`"],
              'checklist': ['Ho salvato il risultato di `sorted()`? (non modifica in-place)',
                            'Le due liste di `zip` hanno la stessa lunghezza?',
                            'Sto controllando `None` con `is None` (non `== None`)?',
                            'Ho usato `enumerate` invece di `range(len(lista))`?']},
 'setup_env': {'domanda_chiave': 'Questo progetto ha un ambiente isolato con le dipendenze fisse?',
               'prima_di_codificare': ['Ho creato un venv per questo progetto?',
                                       'Ho attivato il venv prima di installare?',
                                       'Ho un requirements.txt aggiornato?',
                                       'Il .gitignore esclude .venv/?'],
               'pattern': ['`python -m venv .venv && source .venv/bin/activate` — crea e attiva',
                           '`pip install -r requirements.txt` — installa dipendenze da file',
                           '`pip freeze > requirements.txt` — congela versioni correnti',
                           '`python -m pip install --upgrade pip` — aggiorna pip prima di tutto'],
               'checklist': ['Il terminale mostra (.venv) davanti al prompt?',
                             'requirements.txt include le versioni esatte (==)?',
                             '.venv è nel .gitignore?',
                             'Ho testato `pip install -r requirements.txt` in un venv pulito?']},
 'tipi_operatori': {'domanda_chiave': "Questo valore viene dall'esterno? → va castato. Sto "
                                      'assegnando in base a una condizione? → considera il '
                                      'ternario.',
                    'prima_di_codificare': ['Il valore arriva come stringa (env var, input, file)? '
                                            '→ cast esplicito',
                                            'Il risultato è uno dei due valori? → ternario `x if '
                                            'cond else y`',
                                            'Sto assegnando e verificando in un if? → walrus `:=`',
                                            'Sto dividendo per ottenere un intero? → `//` non `/`'],
                    'pattern': ["`int(os.environ.get('N', '10'))` — env var → int con default",
                                '`val = a if condizione else b` — ternario per assegnazione',
                                '`while chunk := f.read(1024):` — walrus per loop di lettura',
                                "`bool('0')` è True — usa `== '1'` per flag stringa"],
                    'checklist': ['Ho gestito il caso in cui il cast fallisce (ValueError)?',
                                  'Il ternario è leggibile in una riga, o è meglio un if/else?',
                                  "Il walrus è in un contesto dove l'assegnazione è ovvia?",
                                  'La divisione con `/` ritorna float — è quello che voglio?']},
 'scope_closures': {'domanda_chiave': 'Da dove viene questo nome? (Local → Enclosing → Global → '
                                      'Built-in)',
                    'prima_di_codificare': ['La variabile è definita nella funzione corrente? → '
                                            'Local',
                                            'È in una funzione esterna che la racchiude? → '
                                            'Enclosing',
                                            'È al top del modulo? → Global',
                                            'Devo modificare una globale? → dichiara `global` '
                                            "all'inizio della funzione"],
                    'pattern': ['Modulo per key semplici: `sorted(lista, key=lambda x: '
                                "x['campo'])`",
                                'Closure factory: `def make_fn(param): def fn(x): return param + '
                                'x; return fn`',
                                '`nonlocal` per modificare variabili di funzioni esterne (non '
                                'globali)',
                                'Modulo con default `lambda i=i: i` per catturare valore del loop'],
                    'checklist': ['Se ottengo UnboundLocalError, ho dimenticato `global`?',
                                  'La lambda è leggibile in una riga? Se no, usa `def`',
                                  'La closure cattura il valore o il riferimento?',
                                  'Sto usando `global` più di una volta? → forse serve una '
                                  'classe']},
 'tuple_immutabilita': {'domanda_chiave': 'Questi dati devono cambiare? Se no, usa una tupla — è '
                                          'più sicura e più veloce.',
                        'prima_di_codificare': ['I dati cambiano dopo la creazione? Lista. Non '
                                                'cambiano? Tupla.',
                                                'Devo usarlo come chiave di dict o in un set? → '
                                                'deve essere hashable → tupla',
                                                'Sto clonando una struttura annidata? → deepcopy, '
                                                'non copy',
                                                'Sto facendo unpacking multiplo? → `a, b, *resto = '
                                                'collezione`'],
                        'pattern': ['`a, b = b, a` — swap elegante con tuple implicita',
                                    '`x, y, z = punto_3d` — unpacking diretto',
                                    '`lat, lon = (45.07, 7.69)` — coordinate come tupla',
                                    '`import copy; clone = copy.deepcopy(obj)` — copia '
                                    'indipendente'],
                        'checklist': ['La tupla da 1 elemento ha la virgola finale: `(42,)`?',
                                      'Ho usato deepcopy se la struttura ha liste o dict annidati?',
                                      'Sto usando tuple come chiave di dict? → solo con elementi '
                                      'immutabili',
                                      'Ho bisogno di named fields? → considera `namedtuple` o '
                                      '`dataclass`']},
 'controllo_avanzato': {'domanda_chiave': 'Sto cercando qualcosa? (break+else) Sto filtrando? '
                                          '(continue) Sto classificando? (match/case)',
                        'prima_di_codificare': ['Esco appena trovo il primo match? → break',
                                                'Salto elementi non interessanti? → continue (più '
                                                'leggibile di if annidato)',
                                                'Ho bisogno di sapere se il loop è finito senza '
                                                'trovare? → for/else',
                                                'Sto classificando un valore in N casi? → '
                                                'match/case (Python 3.10+)'],
                        'pattern': ['`for x in lista: if cond: risultato = x; break` + `else: '
                                    'risultato = None`',
                                    '`for x in lista: if not cond: continue; processa(x)` — '
                                    'filtraggio',
                                    '`match valore: case A: ... case B: ... case _: ...` — default '
                                    'con `_`',
                                    '`case c if c >= 500:` — guard condition in match'],
                        'checklist': ['Il for/else è chiaro? Se confonde, usa una variabile '
                                      'booleana `trovato`',
                                      "Il continue riduce l'indentazione? → allora è utile",
                                      'match/case: ho il caso `_` come default?',
                                      'Il while con continue aggiorna la variabile PRIMA del '
                                      'continue?']},
 'generatori': {'domanda_chiave': 'Ho bisogno di tutti i valori in memoria o li consumo uno alla '
                                  'volta?',
                'prima_di_codificare': ['I dati sono enormi o potenzialmente infiniti? → '
                                        'generatore',
                                        'Sto iterando una risposta requests paginata? → usare '
                                        'paginator + yield',
                                        'Aggrego (sum, max, any)? → generator expression, non list',
                                        'Ho bisogno di iterare due volte? → list(), perché i '
                                        'generatori si esauriscono'],
                'pattern': ['`def gen(): for x in src: yield trasforma(x)` — pipeline lazy',
                            '`sum(x**2 for x in range(n))` — aggregazione senza lista',
                            '`from itertools import islice; list(islice(gen, 10))` — prendi solo N',
                            '`yield from sotto_generatore` — delegare a un sotto-generatore'],
                'checklist': ['Ho tenuto conto che il generatore si esaurisce?',
                              'Se itero più volte, ho convertito in lista?',
                              'Il generatore infinito usa islice o condizione di uscita?',
                              'Sto usando `yield from` invece di un loop `for x in sub: yield '
                              'x`?']},
 'oop_avanzata': {'domanda_chiave': 'Voglio che Python tratti il mio oggetto come un nativo? → '
                                    'implementa i dunder giusti.',
                  'prima_di_codificare': ['Voglio `print(obj)` leggibile? → `__str__`',
                                          'Voglio `repr(obj)` per debug? → `__repr__`',
                                          'Voglio `len(obj)`? → `__len__`',
                                          'Voglio `obj == altro`? → `__eq__` (e poi `__hash__`)'],
                  'pattern': ['`@property` per attributi calcolati (senza parentesi)',
                              '`@classmethod def from_dict(cls, d)` — factory costruttore '
                              'alternativo',
                              '`@dataclass` elimina `__init__`, `__repr__`, `__eq__` boilerplate',
                              '`field(default_factory=list)` per attributi mutabili in dataclass'],
                  'checklist': ['Ho definito `__hash__` dopo aver definito `__eq__`?',
                                'La property ha setter se è modificabile?',
                                'Il @classmethod ha `cls` come primo parametro (non `self`)?',
                                'Il dataclass usa `field(default_factory=...)` per liste/dict?']},
 'decoratori': {'domanda_chiave': 'Questo comportamento si ripete su più funzioni? → decoratore.',
                'prima_di_codificare': ['Il decoratore aggiunge logging/timing/retry/auth? → '
                                        'pattern classico',
                                        'Il decoratore ha parametri? → serve una funzione che '
                                        'ritorna un decoratore',
                                        'Sto preservando il nome e la docstring? → '
                                        '`@functools.wraps`',
                                        'La funzione ha sempre gli stessi input? → considera '
                                        '`@lru_cache`'],
                'pattern': ['`def dec(func): @wraps(func) def wrapper(*a,**kw): ...; return '
                            'func(*a,**kw); return wrapper`',
                            '`def dec(n): def decorator(func): ... return decorator` — con '
                            'parametri',
                            '`@lru_cache(maxsize=None)` — cache illimitata per funzioni pure',
                            '`functools.partial(f, arg=val)` — funzione con argomenti parziali'],
                'checklist': ['Ho usato `@functools.wraps(func)` nel wrapper?',
                              'Il decoratore con parametri ha tre livelli di nesting?',
                              'Se uso `@lru_cache`, gli argomenti sono hashable?',
                              'Il decoratore ritorna `wrapper`, non `wrapper()`?']},
 'moduli_package': {'domanda_chiave': 'Questo codice verrà importato o eseguito direttamente? → '
                                      '`__name__` guard.',
                    'prima_di_codificare': ['Il modulo può essere sia importato che eseguito? → '
                                            "`if __name__ == '__main__':`",
                                            'Sto loggando eventi? → `logging`, non `print`',
                                            'Conto occorrenze? → `Counter`. Aggrego in liste/dict? '
                                            '→ `defaultdict`',
                                            'Importo da un package interno? → import relativo '
                                            '`from . import modulo`'],
                    'pattern': ['`logger = logging.getLogger(__name__)` — logger per modulo',
                                '`logging.basicConfig(level=logging.INFO)` — configurazione base',
                                '`Counter(lista).most_common(n)` — top N elementi',
                                '`defaultdict(list); d[chiave].append(val)` — senza KeyError'],
                    'checklist': ["Lo script ha `if __name__ == '__main__':` per il codice "
                                  'eseguibile?',
                                  'Sto usando `logger.info/warning/error` invece di `print`?',
                                  'Il format del log include timestamp e livello?',
                                  'Ho evitato import circolari (A importa B, B importa A)?']},
 'eccezioni_avanzate': {'domanda_chiave': 'Sto comunicando un errore di dominio? → eccezione '
                                          'custom. Sto garantendo cleanup? → contextmanager.',
                        'prima_di_codificare': ["L'eccezione porta informazioni strutturate? → "
                                                'classe custom con attributi',
                                                'Devo preservare la causa originale? → `raise '
                                                'NuovoErrore() from e`',
                                                "L'assert è per invarianti di sviluppo o "
                                                'validazione utente? → solo invarianti',
                                                'Ho una risorsa da rilasciare sempre? → '
                                                'contextmanager con finally'],
                        'pattern': ['`class MioErrore(Exception): def __init__(self, msg, dati): '
                                    'super().__init__(msg); self.dati = dati`',
                                    "`raise ValueError('messaggio') from causa_originale`",
                                    '`@contextmanager def risorsa(): ...; yield r; finally: '
                                    'cleanup()`',
                                    "`assert condizione, 'messaggio'` — solo per invarianti, mai "
                                    'per validazione'],
                        'checklist': ["L'eccezione custom estende la classe giusta (ValueError, "
                                      'RuntimeError, ecc.)?',
                                      'Ho usato `raise ... from e` per preservare il contesto?',
                                      'Il contextmanager ha `try/finally` intorno allo yield?',
                                      "L'assert è disabilitabile senza rompere la logica?"]}}


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
        "esempio": 'cert = "demo cloud practitioner"\nprint(cert.upper())\nprint(cert.title())\nprint(f"Lunghezza: {len(cert)} caratteri")',
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
                "testo": 'Con `bucket_name = "mio-scaffale-lorenzo"`, stampa: `Scaffale Disco: mio-scaffale-lorenzo` usando una f-string.',
                "placeholder": 'bucket_name = "mio-scaffale-lorenzo"\n# f-string',
                "check": lambda out, err, vs: err is None and "Scaffale Disco: mio-scaffale-lorenzo" in out.strip(),
                "feedback": lambda out, err: 'L\'output deve essere esattamente `Scaffale Disco: mio-scaffale-lorenzo` — controlla spazi e maiuscole',
                "hint": 'print(f"Scaffale Disco: {bucket_name}")',
                "xp_bonus": 0,
            },
            {
                "testo": '🏆 **BOSS**: Data `"  Hello Python World  "`, stampa: versione senza spazi laterali + versione invertita (`.strip()` e `[::-1]`).',
                "placeholder": 's = "  Hello Python World  "\n# strip e inverti',
                "check": lambda out, err, vs: err is None and "Hello Python World" in out and "dlroW" in out,
                "feedback": lambda out, err: (
                    "Usa `.strip()` per rimuovere gli spazi laterali" if "Hello Python World" not in out else
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
for r in ["nord", "sud"]:
    print(r)

for i in range(5):   # 0,1,2,3,4
    print(i)

n = 0
while n < 3:
    print(f"Step {n}")
    n += 1
```
""",
        "esempio": 'regioni = ["nord", "sud", "ap-southeast-1"]\nfor r in regioni:\n    print(f"Regione: {r}")',
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
def connetti(regione="nord", porta=443):
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
                "testo": 'Scrivi `saluta_utente(nome, servizio="Python")` che stampa `"Benvenuto Lorenzo su Python"`.',
                "placeholder": 'def saluta_utente(nome, servizio="Python"):\n    pass\n\nsaluta_utente("Lorenzo")',
                "check": lambda out, err, vs: err is None and "Lorenzo" in out and "Python" in out,
                "feedback": lambda out, err: 'Dentro la funzione: `print(f"Benvenuto {nome} su {servizio}")`',
                "hint": 'def saluta_utente(nome, servizio="Python"):\n    print(f"Benvenuto {nome} su {servizio}")\n\nsaluta_utente("Lorenzo")',
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
scaffale = ["log-scaffale", "data-scaffale"]
scaffale.append("new-scaffale")
print(scaffale[0])      # primo elemento
```

### Dizionari — chiave → valore
```python
prodotto = {"id": "i-0abc123", "tipo": "base"}
print(prodotto["tipo"])       # base
prodotto["stato"] = "running" # aggiunge chiave
```

> ⚡ Tutte le risposte requests sono **dizionari**.
""",
        "esempio": 'ist = {"id": "i-0abc123", "tipo": "base", "regione": "nord"}\nfor k, v in ist.items():\n    print(f"{k}: {v}")',
        "esercizi": [
            {
                "testo": 'Crea `servizi = ["Server", "Disco", "Modulo"]`, aggiungi `"Database"` con `.append()` e stampa.',
                "placeholder": 'servizi = ["Server", "Disco", "Modulo"]\n# append e print',
                "check": lambda out, err, vs: err is None and "Database" in out and "Server" in out,
                "feedback": lambda out, err: (
                    "Usa `servizi.append('Database')` prima del print" if "Database" not in out else
                    "Stampa la lista con `print(servizi)`"
                ),
                "hint": 'servizi.append("Database")\nprint(servizi)',
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
                "testo": "🏆 **BOSS**: Lista di dizionari con 3 servizi Python (chiavi: `nome`, `costo_mensile`). Stampa solo quelli con costo > 50.",
                "placeholder": 'servizi = [\n    {"nome": "Server", "costo_mensile": 80},\n    {"nome": "Disco",  "costo_mensile": 5},\n    {"nome": "Database", "costo_mensile": 120},\n]\n# filtra e stampa',
                "check": lambda out, err, vs: err is None and ("Server" in out or "Database" in out) and "Disco" not in out,
                "feedback": lambda out, err: 'Loop sulla lista: `for s in servizi: if s["costo_mensile"] > 50: print(s["nome"])`',
                "hint": 'for s in servizi:\n    if s["costo_mensile"] > 50:\n        print(s["nome"])',
                "xp_bonus": 10,
            },
            {
                "tipo": "debug",
                "testo": "🐛 **DEBUG**: Questo codice vuole stampare il costo di ogni servizio e il totale, ma ha 2 bug. Trovali.",
                "placeholder": (
                    'servizi = [\n'
                    '    {"nome": "Server", "costo": 70},\n'
                    '    {"nome": "Database", "costo": 105},\n'
                    ']\n'
                    'totale = 0\n'
                    'for s in servizi:\n'
                    '    print(f"{s[nome]}: ${s[\'costo\']}")  # BUG 1\n'
                    '    totale =+ s["costo"]               # BUG 2\n'
                    'print(f"Totale: ${totale}")\n'
                ),
                "check": lambda out, err, vs: err is None and "Server" in out.strip() and "175" in out,
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

### Catturare il tipo giusto di errore
```python
try:
    config = leggi_config("app.json")
except FileNotFoundError:
    print("File di configurazione mancante")
except KeyError as e:
    print(f"Campo obbligatorio assente: {e}")
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
                    'accedi_bucket("scaffale-inesistente")\n'
                ),
                "check": lambda out, err, vs: (
                    err is None
                    and out.lower().count("connessione chiusa") >= 2
                    and ("dati" in out.lower() or "prod" in out.lower())
                    and ("non esiste" in out.lower() or "trovato" in out.lower() or "inesistente" in out.lower())
                ),
                "feedback": lambda out, err: "Il finally deve stampare 'Connessione chiusa' 2 volte (una per ogni chiamata). Aggiungi messaggi per scaffale trovato e non trovato.",
                "hint": (
                    'def accedi_bucket(nome):\n'
                    '    db = {"prod-logs": "dati critici", "dev-logs": "dati test"}\n'
                    '    try:\n'
                    '        print(f"Accesso OK: {db[nome]}")\n'
                    '    except KeyError:\n'
                    '        print(f"Scaffale non esiste: {nome}")\n'
                    '    finally:\n'
                    '        print("Connessione chiusa")\n'
                    '\n'
                    'accedi_bucket("prod-logs")\n'
                    'accedi_bucket("scaffale-inesistente")\n'
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
pip install requests streamlit           # installa
pip freeze > requirements.txt        # congela versioni
pip install -r requirements.txt      # installa da file
```

### requirements.txt
```
requests==1.34.0
streamlit==1.40.0
requests==2.31.0
```

### Strumenti moderni
```bash
pip install uv        # pip alternativo, molto più veloce
uv pip install requests  # stesso interfaccia di pip
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
                "testo": "Simula la creazione di un `requirements.txt`: scrivi una lista di pacchetti con versioni (`requests==1.34.0`, `streamlit==1.40.0`, `requests==2.31.0`) e stampali uno per riga.",
                "placeholder": "pacchetti = [\n    \"requests==1.34.0\",\n    # aggiungi gli altri\n]\nfor p in pacchetti:\n    print(p)",
                "check": lambda out, err, vs: err is None and "requests" in out and "streamlit" in out and "==" in out,
                "feedback": lambda out, err: "Stampa ogni pacchetto con la versione usando ==",
                "hint": 'pacchetti = [\n    "requests==1.34.0",\n    "streamlit==1.40.0",\n    "requests==2.31.0",\n]\nfor p in pacchetti:\n    print(p)',
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
                "testo": "🏆 **BOSS**: Scrivi `verifica_ambiente()` che controlla: (1) Python ≥ 3.8, (2) se `requests` è importabile. Stampa un report con OK/MANCANTE per ogni check.",
                "placeholder": (
                    'import sys\n'
                    '\n'
                    'def verifica_ambiente():\n'
                    '    # check 1: versione Python\n'
                    '    py_ok = sys.version_info >= (3, 8)\n'
                    '    print(f"Python 3.8+: {\'OK\' if py_ok else \'AGGIORNA\'}")\n'
                    '    \n'
                    '    # check 2: requests importabile\n'
                    '    try:\n'
                    '        import requests\n'
                    '        print("requests: OK")\n'
                    '    except ImportError:\n'
                    '        print("requests: MANCANTE")\n'
                    '\n'
                    'verifica_ambiente()'
                ),
                "check": lambda out, err, vs: err is None and "Python 3.8+" in out and ("OK" in out or "MANCANTE" in out),
                "feedback": lambda out, err: "La funzione deve stampare il risultato di ogni check",
                "hint": "try: import requests; print('requests: OK') except ImportError: print('requests: MANCANTE')",
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
            'print(f"Credito Python: {stato}")\n'
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
                "testo": "Hai `100` oggetti Disco da listare a `20` per pagina. Calcola il numero di pagine intere con divisione intera.",
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
        "id": "scope_closures", "title": "Scope, Modulo e Closures",
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

### Modulo — funzione anonima
```python
doppio = lambda x: x * 2
print(doppio(5))   # 10

# Usata come key per sorted
prodotti = sorted(prodotti, key=lambda x: x["prezzo"])
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
            '# Modulo + sorted\n'
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
            'config = {"regioni": ["nord", "sud"]}\n'
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
for ist in prodotti:
    if ist["stato"] == "running":
        prima_running = ist
        break   # non serve continuare

# continue — salta questa iterazione
for ist in prodotti:
    if ist["stato"] == "stopped":
        continue   # non interessano
    print(f"Attiva: {ist['id']}")
```

### for/else e while/else
```python
# else esegue SOLO se il loop non ha fatto break
for ist in prodotti:
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
            'prodotti = [\n'
            '    {"id": "i-001", "stato": "stopped"},\n'
            '    {"id": "i-002", "stato": "running"},\n'
            '    {"id": "i-003", "stato": "running"},\n'
            ']\n'
            '\n'
            '# Trova la prima running\n'
            'prima = None\n'
            'for ist in prodotti:\n'
            '    if ist["stato"] == "running":\n'
            '        prima = ist\n'
            '        break\n'
            'else:\n'
            '    print("Nessuna prodotto running!")\n'
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
                "testo": "Cerca `'i-005'` nella lista di prodotti con `for/else`. Stampa `'Trovato'` se esiste, `'Non trovato'` altrimenti.",
                "placeholder": (
                    'prodotti = ["i-001", "i-002", "i-003"]\n'
                    'target = "i-005"\n'
                    'for ist in prodotti:\n'
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
                "testo": "🏆 **BOSS**: Scrivi `cerca_istanza(lista, target_id)` che usa for/break/else e ritorna l'prodotto trovata o `None`. Testa con ID presente e assente.",
                "placeholder": (
                    'prodotti = [\n'
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
                    'print(cerca_istanza(prodotti, "i-001"))\n'
                    'print(cerca_istanza(prodotti, "i-999"))'
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

### Pattern — lettura lazy a blocchi
```python
def leggi_righe(file_lista):
    for nome in file_lista:
        with open(nome) as f:
            for riga in f:
                yield riga.strip()
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
### Classe e prodotto
```python
class Risorsa:
    SERVIZI = ["Server", "Disco", "Database"]   # attributo di classe

    def __init__(self, id, regione):
        self.id      = id            # attributo di prodotto
        self.regione = regione

    def etichetta(self):
        return f"{self.regione}/{self.id}"

# Crea prodotti
server = Risorsa("i-001", "nord")
db     = Risorsa("db-001", "sud")

print(server.etichetta())   # ogni prodotto ha la sua etichetta
```

### Ereditarietà
```python
class Server(Risorsa):
    def __init__(self, id, regione, tipo):
        super().__init__(id, regione)   # chiama il genitore
        self.tipo = tipo

    def costo_mensile(self, prezzo_ora):
        return round(prezzo_ora * 730, 2)

server = Server("i-001", "nord", "base")
print(server.etichetta())      # ereditato
print(server.costo_mensile(0.023))  # 16.79
```
""",
        "esempio": (
            'class Prodotto:\n'
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
            'server = Prodotto("i-001", "base")\n'
            'print(server.info())\n'
            'server.avvia()\n'
            'print(server.info())'
        ),
        "esercizi": [
            {
                "testo": "Crea una classe `Scaffale` con `__init__(self, nome, regione)` e un metodo `uri()` che ritorna `item://{nome}`. Stampa `uri()` per un scaffale `logs` in `nord`.",
                "placeholder": (
                    'class Scaffale:\n'
                    '    def __init__(self, nome, regione):\n'
                    '        self.nome   = nome\n'
                    '        self.regione = regione\n'
                    '\n'
                    '    def uri(self):\n'
                    '        return f"item://{self.nome}"\n'
                    '\n'
                    'b = Scaffale("logs", "nord")\n'
                    'print(b.uri())'
                ),
                "check": lambda out, err, vs: err is None and "item://logs" in out.strip(),
                "feedback": lambda out, err: "uri() deve ritornare f'item://{self.nome}'",
                "hint": 'return f"item://{self.nome}"',
                "xp_bonus": 0,
            },
            {
                "testo": "Aggiungi a `Scaffale` un metodo `aggiungi_tag(self, chiave, valore)` che salva i tag in un dizionario `self.tags`. Aggiungi `env=prod` e stampa `b.tags`.",
                "placeholder": (
                    'class Scaffale:\n'
                    '    def __init__(self, nome, regione):\n'
                    '        self.nome    = nome\n'
                    '        self.regione = regione\n'
                    '        self.tags    = {}\n'
                    '\n'
                    '    def aggiungi_tag(self, chiave, valore):\n'
                    '        self.tags[chiave] = valore\n'
                    '\n'
                    'b = Scaffale("logs", "nord")\n'
                    'b.aggiungi_tag("env", "prod")\n'
                    'print(b.tags)'
                ),
                "check": lambda out, err, vs: err is None and "env" in out and "prod" in out,
                "feedback": lambda out, err: "self.tags[chiave] = valore aggiunge al dizionario",
                "hint": "self.tags[chiave] = valore",
                "xp_bonus": 0,
            },
            {
                "testo": "Crea `Server(Scaffale)` che estende `Scaffale` e aggiunge `tipo_istanza`. Usa `super().__init__()`. Stampa `uri()` (ereditato) e `tipo_istanza`.",
                "placeholder": (
                    'class Scaffale:\n'
                    '    def __init__(self, nome, regione):\n'
                    '        self.nome    = nome\n'
                    '        self.regione = regione\n'
                    '    def uri(self): return f"item://{self.nome}"\n'
                    '\n'
                    'class Server(Scaffale):\n'
                    '    def __init__(self, nome, regione, tipo_istanza):\n'
                    '        super().__init__(nome, regione)\n'
                    '        self.tipo_istanza = tipo_istanza\n'
                    '\n'
                    'vm = Server("web-server", "nord", "base")\n'
                    'print(vm.uri())\n'
                    'print(vm.tipo_istanza)'
                ),
                "check": lambda out, err, vs: err is None and "item://web-server" in out and "base" in out,
                "feedback": lambda out, err: "super().__init__() inizializza il genitore, poi aggiunge tipo_istanza",
                "hint": "super().__init__(nome, regione)",
                "xp_bonus": 0,
            },
            {
                "tipo": "predict",
                "testo": "🔍 **PREVEDI**: Cosa stamperà questo codice? Attenzione agli attributi di classe vs prodotto.",
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
                "testo": "🏆 **BOSS**: Crea `Risorsa` base con `id, regione, tipo`. Aggiungi `Server` e `Articolo` come sottoclassi con metodo `costo_mensile()` diverso. Stampa i costi di 2 prodotti.",
                "placeholder": (
                    'class Risorsa:\n'
                    '    def __init__(self, id, regione, tipo):\n'
                    '        self.id      = id\n'
                    '        self.regione = regione\n'
                    '        self.tipo    = tipo\n'
                    '    def costo_mensile(self):\n'
                    '        raise NotImplementedError\n'
                    '\n'
                    'class Server(Risorsa):\n'
                    '    def __init__(self, id, regione, prezzo_ora):\n'
                    '        super().__init__(id, regione, "Server")\n'
                    '        self.prezzo_ora = prezzo_ora\n'
                    '    def costo_mensile(self):\n'
                    '        return round(self.prezzo_ora * 730, 2)\n'
                    '\n'
                    'class Articolo(Risorsa):\n'
                    '    def __init__(self, id, regione, gb):\n'
                    '        super().__init__(id, regione, "Disco")\n'
                    '        self.gb = gb\n'
                    '    def costo_mensile(self):\n'
                    '        return round(self.gb * 0.023, 2)\n'
                    '\n'
                    'server = Server("i-001", "nord", 0.096)\n'
                    'scaffale = Articolo("logs", "nord", 500)\n'
                    'print(f"Server: ${server.costo_mensile()}")\n'
                    'print(f"Disco:  ${scaffale.costo_mensile()}")'
                ),
                "check": lambda out, err, vs: err is None and "Server:" in out and "Disco:" in out and "$" in out,
                "feedback": lambda out, err: "Le due sottoclassi devono avere costo_mensile() con logiche diverse",
                "hint": "Server: prezzo_ora * 730. Disco: gb * 0.023",
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
class Server:
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
class Prodotto:
    id:      str
    tipo:    str
    regione: str = "nord"
    tags:    list = field(default_factory=list)
    # __init__, __repr__, __eq__ generati automaticamente
```
""",
        "esempio": (
            'from dataclasses import dataclass, field\n'
            '\n'
            '@dataclass\n'
            'class Scaffale:\n'
            '    nome:    str\n'
            '    regione: str = "nord"\n'
            '    size_gb: float = 0.0\n'
            '    tags:    list = field(default_factory=list)\n'
            '\n'
            '    @property\n'
            '    def costo_mensile(self):\n'
            '        return round(self.size_gb * 0.023, 4)\n'
            '\n'
            '    def __str__(self):\n'
            '        return f"item://{self.nome} ({self.size_gb}GB)"\n'
            '\n'
            'b = Scaffale("prod-logs", size_gb=500)\n'
            'b.tags.append("env:prod")\n'
            'print(b)\n'
            'print(f"Costo: ${b.costo_mensile}")'
        ),
        "esercizi": [
            {
                "testo": "Aggiungi `__str__` a una classe `Prodotto(id, tipo)` che ritorna `'Server i-001 (base)'`. Stampa l'prodotto con `print()`.",
                "placeholder": (
                    'class Prodotto:\n'
                    '    def __init__(self, id, tipo):\n'
                    '        self.id   = id\n'
                    '        self.tipo = tipo\n'
                    '\n'
                    '    def __str__(self):\n'
                    '        return f"Server {self.id} ({self.tipo})"\n'
                    '\n'
                    'ist = Prodotto("i-001", "base")\n'
                    'print(ist)'
                ),
                "check": lambda out, err, vs: err is None and "Server i-001 (base)" in out.strip(),
                "feedback": lambda out, err: "__str__ deve ritornare la stringa formattata",
                "hint": 'return f"Server {self.id} ({self.tipo})"',
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
                "testo": "Riscrivi `Prodotto(id, tipo, regione='nord')` come `@dataclass`. Verifica che `__repr__` sia generato automaticamente.",
                "placeholder": (
                    'from dataclasses import dataclass\n'
                    '\n'
                    '@dataclass\n'
                    'class Prodotto:\n'
                    '    id:      str\n'
                    '    tipo:    str\n'
                    '    regione: str = "nord"\n'
                    '\n'
                    'ist = Prodotto("i-001", "base")\n'
                    'print(repr(ist))\n'
                    'print(ist.id)'
                ),
                "check": lambda out, err, vs: err is None and "i-001" in out and "base" in out,
                "feedback": lambda out, err: "@dataclass genera __repr__ automaticamente — deve contenere i valori",
                "hint": "@dataclass genera repr come Prodotto(id='i-001', tipo='base', regione='nord')",
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
                "testo": "🏆 **BOSS**: Classe `Portfolio` con lista di `Prodotto` (dataclass). Aggiungi `__len__` (numero prodotti), `__str__` (lista nomi), `costo_totale` come property. Stampa tutto.",
                "placeholder": (
                    'from dataclasses import dataclass, field\n'
                    '\n'
                    '@dataclass\n'
                    'class Prodotto:\n'
                    '    id:         str\n'
                    '    prezzo:  float\n'
                    '\n'
                    'class Portfolio:\n'
                    '    def __init__(self):\n'
                    '        self.prodotti = []\n'
                    '    def aggiungi(self, ist): self.prodotti.append(ist)\n'
                    '    def __len__(self): return len(self.prodotti)\n'
                    '    def __str__(self): return ", ".join(i.id for i in self.prodotti)\n'
                    '    @property\n'
                    '    def costo_totale(self): return sum(i.prezzo * 730 for i in self.prodotti)\n'
                    '\n'
                    'p = Portfolio()\n'
                    'p.aggiungi(Prodotto("i-001", 0.096))\n'
                    'p.aggiungi(Prodotto("i-002", 0.023))\n'
                    'print(len(p))\n'
                    'print(str(p))\n'
                    'print(f"Costo: ${p.costo_totale:.2f}")'
                ),
                "check": lambda out, err, vs: err is None and "2" in _ol(out) and "i-001" in out and "Costo:" in out,
                "feedback": lambda out, err: "len(p) deve dare 2, str(p) i nomi, costo_totale la somma",
                "hint": "sum(i.prezzo * 730 for i in self.prodotti)",
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
    print(f"Scaffale {nome} creato")
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
for ist in prodotti:
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
                "testo": "Con `parole = ['requests','python','requests','demo','python','requests']`, usa `Counter` per trovare la parola più frequente e quante volte compare.",
                "placeholder": (
                    'from collections import Counter\n'
                    'parole = ["requests","python","requests","demo","python","requests"]\n'
                    'c = Counter(parole)\n'
                    'parola, freq = c.most_common(1)[0]\n'
                    'print(f"{parola}: {freq}")'
                ),
                "check": lambda out, err, vs: err is None and "requests: 3" in out.strip(),
                "feedback": lambda out, err: "Counter conta le occorrenze. most_common(1) ritorna la più frequente.",
                "hint": "c.most_common(1)[0] → ('requests', 3)",
                "xp_bonus": 0,
            },
            {
                "testo": "Con `defaultdict(list)`, raggruppa le prodotti per `stato` da una lista di dict. Stampa quante prodotti ha ogni stato.",
                "placeholder": (
                    'from collections import defaultdict\n'
                    '\n'
                    'prodotti = [\n'
                    '    {"id": "i-001", "stato": "running"},\n'
                    '    {"id": "i-002", "stato": "stopped"},\n'
                    '    {"id": "i-003", "stato": "running"},\n'
                    '    {"id": "i-004", "stato": "stopped"},\n'
                    ']\n'
                    '\n'
                    'per_stato = defaultdict(list)\n'
                    'for ist in prodotti:\n'
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
                "testo": "Usa `assert` per verificare che una lista di prodotti non sia vuota prima di processarla. Gestisci `AssertionError` con un messaggio chiaro.",
                "placeholder": (
                    'prodotti = []\n'
                    '\n'
                    'try:\n'
                    '    assert len(prodotti) > 0, "Lista prodotti vuota"\n'
                    '    print("Processo", len(prodotti), "prodotti")\n'
                    'except AssertionError as e:\n'
                    '    print(f"Attenzione: {e}")'
                ),
                "check": lambda out, err, vs: err is None and "Lista prodotti vuota" in out.strip(),
                "feedback": lambda out, err: "AssertionError viene lanciato perché la lista è vuota",
                "hint": "assert len(prodotti) > 0, 'Lista prodotti vuota'",
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
                "testo": "🏆 **BOSS**: Crea una gerarchia: `AppError(Exception)` base, `PermissionError(AppError)`, `ResourceNotFoundError(AppError)`. Scrivi `accedi(risorsa)` che lancia l'errore giusto. Cattura con except AppError.",
                "placeholder": (
                    'class AppError(Exception):\n'
                    '    pass\n'
                    '\n'
                    'class PermessoNegatoError(AppError):\n'
                    '    pass\n'
                    '\n'
                    'class RisorsaAssente(AppError):\n'
                    '    pass\n'
                    '\n'
                    'def accedi(risorsa):\n'
                    '    if risorsa == "segreto":\n'
                    '        raise PermessoNegatoError(f"Accesso negato a {risorsa}")\n'
                    '    if risorsa == "inesistente":\n'
                    '        raise RisorsaAssente(f"Risorsa non trovata: {risorsa}")\n'
                    '    print(f"Accesso OK: {risorsa}")\n'
                    '\n'
                    'for r in ["prod-scaffale", "segreto", "inesistente"]:\n'
                    '    try:\n'
                    '        accedi(r)\n'
                    '    except AppError as e:\n'
                    '        print(f"Python Error: {e}")'
                ),
                "check": lambda out, err, vs: err is None and "Accesso OK" in out and "Accesso negato" in out and "non trovata" in out,
                "feedback": lambda out, err: "Ogni risorsa deve produrre l'output corretto: OK, negato, non trovata",
                "hint": "except AppError cattura sia PermessoNegatoError che RisorsaAssente",
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

configura(regione="nord", debug=True)
```

### Spacchettare con * e **
```python
numeri = [1, 2, 3]
print(*numeri)            # stampa: 1 2 3

params = {"nome": "report", "formato": "pdf"}
genera(**params)          # equivale a genera(nome="report", formato="pdf")
```

### Pattern — chiamata dinamica
```python
params = {"nome": nome}
if versione:
    params["versione"] = versione   # aggiunge solo se serve

risultato = genera(**params)
```
""",
        "esempio": (
            'def descrivi_risorsa(tipo, **dettagli):\n'
            '    print(f"Risorsa: {tipo}")\n'
            '    for k, v in dettagli.items():\n'
            '        print(f"  {k}: {v}")\n'
            '\n'
            'descrivi_risorsa("Server", id="i-001", stato="running", regione="nord")\n'
            'print("---")\n'
            'params = {"id": "i-002", "stato": "stopped"}\n'
            'descrivi_risorsa("Database", **params)'
        ),
        "esercizi": [
            {
                "testo": "Scrivi `stampa_config(**kwargs)` che stampa ogni parametro nel formato `chiave: valore`. Chiamala con `citta`, `reparto` e `timeout`.",
                "placeholder": (
                    'def stampa_config(**kwargs):\n'
                    '    for k, v in kwargs.items():\n'
                    '        pass  # stampa k: v\n'
                    '\n'
                    'stampa_config(citta="nord", reparto="cucina", timeout=30)'
                ),
                "check": lambda out, err, vs: err is None and "citta" in out and "nord" in out and "timeout" in out,
                "feedback": lambda out, err: 'Usa `print(f"{k}: {v}")` dentro il for loop',
                "hint": 'print(f"{k}: {v}")',
                "xp_bonus": 0,
            },
            {
                "testo": 'Hai `params = {"Scaffale": "logs", "Prefisso": "jan-2024"}`. Chiama `scarica(**kwargs)` (già scritta) usando **unpacking sul dizionario.',
                "placeholder": (
                    'def scarica(**kwargs):\n'
                    '    scaffale = kwargs.get("Scaffale", "?")\n'
                    '    print(f"Scarico da: {scaffale}")\n'
                    '\n'
                    'params = {"Scaffale": "logs", "Prefisso": "jan-2024"}\n'
                    '# chiama scarica con **unpacking'
                ),
                "check": lambda out, err, vs: err is None and "Scarico da: logs" in out.strip(),
                "feedback": lambda out, err: "Chiama `scarica(**params)` — i ** spaccchettano il dict in keyword arguments",
                "hint": "scarica(**params)",
                "xp_bonus": 0,
            },
            {
                "tipo": "debug",
                "testo": "🐛 **DEBUG**: Il codice chiama una funzione requests simulata ma ha 2 bug con unpacking.",
                "placeholder": (
                    'def get_object(Scaffale, Key, VersionId=None):\n'
                    '    print(f"Leggo item://{Scaffale}/{Key}")\n'
                    '    if VersionId:\n'
                    '        print(f"Versione: {VersionId}")\n'
                    '\n'
                    'params = {"Scaffale": "dati", "Key": "report.csv"}\n'
                    'get_object(params)        # BUG 1\n'
                    'get_object(*params)       # BUG 2: * su dict spacchetta le chiavi'
                ),
                "check": lambda out, err, vs: err is None and "Leggo item://dati/report.csv" in out,
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
                "testo": "🏆 **BOSS**: Scrivi `crea_filtri(**criteri)` che costruisce una lista `Filters` requests dal formato `[{'Name': k, 'Values': [v]}]`. Testa con 2 chiamate diverse.",
                "placeholder": (
                    'def crea_filtri(**criteri):\n'
                    '    filters = []\n'
                    '    # per ogni criterio, aggiungi il dict requests\n'
                    '    return filters\n'
                    '\n'
                    'print(crea_filtri(stato="running"))\n'
                    'print(crea_filtri(stato="stopped", tipo="base"))'
                ),
                "check": lambda out, err, vs: (
                    err is None and "running" in out and "stopped" in out
                    and "base" in out and "Name" in out
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

regione = os.environ.get("APP_CITTA", "nord")  # default sicuro
debug   = os.environ.get("DEBUG", "false") == "true"
```

### Segreti e credenziali — la regola d'oro
```bash
export APP_TOKEN="..."
export APP_CITTA="nord"
```
```python
import os
token = os.environ["APP_TOKEN"]  # letto dall'ambiente, non dal codice
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
            'regione = os.environ.get("APP_CITTA", "nord")\n'
            'print(f"Regione: {regione}")'
        ),
        "esercizi": [
            {
                "testo": 'Parsa la stringa JSON `\'{"prodotto": "i-001", "stato": "running", "prezzo": 0.096}\'` e stampa solo il valore di `stato`.',
                "placeholder": (
                    'import json\n'
                    '\n'
                    'raw = \'{"prodotto": "i-001", "stato": "running", "prezzo": 0.096}\'\n'
                    'dati = ...\n'
                    'print(...)'
                ),
                "check": lambda out, err, vs: err is None and out.strip() == "running",
                "feedback": lambda out, err: 'dati = json.loads(raw)  poi  print(dati["stato"])',
                "hint": 'dati = json.loads(raw)\nprint(dati["stato"])',
                "xp_bonus": 0,
            },
            {
                "testo": "Serializza un dizionario Python con 3 chiavi (`regione`, `servizio`, `costo`) usando `json.dumps` con `indent=2` e stampalo.",
                "placeholder": (
                    'import json\n'
                    '\n'
                    'config = {"regione": "nord", "servizio": "Server", "costo": 70.08}\n'
                    'print(...)'
                ),
                "check": lambda out, err, vs: err is None and "  " in out and "regione" in out and "70.08" in out,
                "feedback": lambda out, err: "Usa json.dumps(config, indent=2)",
                "hint": "print(json.dumps(config, indent=2))",
                "xp_bonus": 0,
            },
            {
                "testo": "Leggi la regione da `os.environ.get('APP_CITTA', 'nord')`. Poiché non è impostata, deve stampare il default.",
                "placeholder": (
                    'import os\n'
                    '\n'
                    'regione = os.environ.get("APP_CITTA", "nord")\n'
                    'print(f"Regione: {regione}")'
                ),
                "check": lambda out, err, vs: err is None and "nord" in out.strip(),
                "feedback": lambda out, err: "Il codice è già corretto — il default 'nord' appare perché APP_CITTA non è impostata",
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
                    'DEFAULT = \'{"regione": "nord", "timeout": 30, "debug": false}\'\n'
                    '\n'
                    'def carica_config(json_str):\n'
                    '    cfg = json.loads(json_str)\n'
                    '    if os.environ.get("APP_CITTA"):\n'
                    '        cfg["regione"] = os.environ["APP_CITTA"]\n'
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
running = [i["id"] for i in prodotti if i["stato"] == "running"]

# Trasforma
nomi_upper = [n.upper() for n in nomi]

# Filtra + trasforma
costi = [i["prezzo"] * 730 for i in prodotti if i["tipo"] == "Server"]
```

### Dict e Set comprehension
```python
# Dict — mappa id → stato
stati = {i["id"]: i["stato"] for i in prodotti}
print(stati["i-001"])   # "running"

# Set — valori unici
regioni_usate = {i["regione"] for i in prodotti}
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
            'prodotti = [\n'
            '    {"id": "i-001", "stato": "running",  "costo": 0.096},\n'
            '    {"id": "i-002", "stato": "stopped",  "costo": 0.023},\n'
            '    {"id": "i-003", "stato": "running",  "costo": 0.048},\n'
            ']\n'
            '\n'
            'running_ids = [i["id"] for i in prodotti if i["stato"] == "running"]\n'
            'print("Running:", running_ids)\n'
            '\n'
            'mappa_stato = {i["id"]: i["stato"] for i in prodotti}\n'
            'print("Mappa:", mappa_stato)\n'
            '\n'
            'costo_totale = sum(i["costo"] for i in prodotti if i["stato"] == "running")\n'
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
                "testo": "Con la lista di prodotti, crea un **dizionario** `{id: costo}` usando dict comprehension.",
                "placeholder": (
                    'prodotti = [\n'
                    '    {"id": "i-001", "costo": 0.096},\n'
                    '    {"id": "i-002", "costo": 0.023},\n'
                    '    {"id": "i-003", "costo": 0.048},\n'
                    ']\n'
                    'costi = {...}\n'
                    'print(costi)'
                ),
                "check": lambda out, err, vs: err is None and "i-001" in out and "0.096" in out and "{" in out,
                "feedback": lambda out, err: '{i["id"]: i["costo"] for i in prodotti}',
                "hint": '{i["id"]: i["costo"] for i in prodotti}',
                "xp_bonus": 0,
            },
            {
                "testo": "Usa una **set comprehension** per ottenere le regioni uniche da una lista di prodotti.",
                "placeholder": (
                    'prodotti = [\n'
                    '    {"id": "i-001", "regione": "nord"},\n'
                    '    {"id": "i-002", "regione": "sud"},\n'
                    '    {"id": "i-003", "regione": "nord"},\n'
                    ']\n'
                    'regioni = {...}\n'
                    'print(len(regioni))  # deve essere 2, non 3'
                ),
                "check": lambda out, err, vs: err is None and "2" in _ol(out),
                "feedback": lambda out, err: '{i["regione"] for i in prodotti} — le chiavi doppie vengono eliminate',
                "hint": '{i["regione"] for i in prodotti}',
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
                    'dati = [{"n": "Server", "c": 80}, {"n": "Disco", "c": 5}, {"n": "Database", "c": 120}]\n'
                    'risultato = {d["n"]: d["c"] * 12 for d in dati if d["c"] > 10}\n'
                    'print(risultato)'
                ),
                "expected": "{'Server': 960, 'Database': 1440}",
                "hint": "Filtra solo c > 10 (Server=80, Database=120, Disco=5 escluso). Moltiplica per 12. Risultato è un dict.",
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
prodotti = [{"id": "i-1", "costo": 0.096}, {"id": "i-2", "costo": 0.023}]

per_costo = sorted(prodotti, key=lambda x: x["costo"], reverse=True)
```

### None safety
```python
ip = prodotto.get("PublicIpAddress")   # ritorna None se mancante
if ip is not None:                    # is None, non == None
    print(f"IP: {ip}")

# oppure con or
label = prodotto.get("Name") or "senza-nome"
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
            '    {"nome": "web-server",  "prezzo": 0.096, "stato": "running"},\n'
            '    {"nome": "db-primary",  "prezzo": 0.192, "stato": "running"},\n'
            '    {"nome": "worker-dev",  "prezzo": 0.023, "stato": "stopped"},\n'
            ']\n'
            '\n'
            '# enumerate — log numerato\n'
            'for i, r in enumerate(risorse, start=1):\n'
            '    print(f"{i}. {r[\'nome\']} ({r[\'stato\']})")\n'
            '\n'
            '# sorted — ordina per costo decrescente\n'
            'per_costo = sorted(risorse, key=lambda x: x["prezzo"], reverse=True)\n'
            'print(f"\\nPiù costosa: {per_costo[0][\'nome\']}")'
        ),
        "esercizi": [
            {
                "testo": "Usa `enumerate(servizi, start=1)` per stampare ogni servizio nel formato `1. Server`, `2. Disco`, ecc.",
                "placeholder": (
                    'servizi = ["Server", "Disco", "Modulo", "Database"]\n'
                    'for i, s in enumerate(servizi, start=1):\n'
                    '    pass  # stampa il formato richiesto'
                ),
                "check": lambda out, err, vs: err is None and "1. Server" in out.strip() and "4. Database" in out.strip(),
                "feedback": lambda out, err: 'print(f"{i}. {s}")',
                "hint": 'print(f"{i}. {s}")',
                "xp_bonus": 0,
            },
            {
                "testo": "Hai due liste parallele `nomi` e `costi`. Usa `zip` per stampare ogni coppia nel formato `Server: $70.08`.",
                "placeholder": (
                    'nomi  = ["Server", "Disco", "Database"]\n'
                    'costi = [70.08, 1.50, 105.84]\n'
                    '\n'
                    'for nome, costo in zip(nomi, costi):\n'
                    '    pass  # stampa il formato richiesto'
                ),
                "check": lambda out, err, vs: err is None and "Server: $70.08" in out.strip() and "Database: $105.84" in out.strip(),
                "feedback": lambda out, err: 'print(f"{nome}: ${costo}")',
                "hint": 'print(f"{nome}: ${costo}")',
                "xp_bonus": 0,
            },
            {
                "testo": "Ordina la lista di prodotti per `prezzo` decrescente con `sorted` e stampa i nomi in quell'ordine.",
                "placeholder": (
                    'prodotti = [\n'
                    '    {"nome": "web",  "prezzo": 0.048},\n'
                    '    {"nome": "db",   "prezzo": 0.192},\n'
                    '    {"nome": "worker","prezzo": 0.023},\n'
                    ']\n'
                    'ordinate = sorted(...)\n'
                    'for i in ordinate:\n'
                    '    print(i["nome"])'
                ),
                "check": lambda out, err, vs: err is None and list(_ol(out)) != [] and list(out.strip().splitlines())[0].strip() == "db",
                "feedback": lambda out, err: 'sorted(prodotti, key=lambda x: x["prezzo"], reverse=True)',
                "hint": 'sorted(prodotti, key=lambda x: x["prezzo"], reverse=True)',
                "xp_bonus": 0,
            },
            {
                "tipo": "debug",
                "testo": "🐛 **DEBUG**: Questo codice gestisce `None` ma ha 2 bug sottili.",
                "placeholder": (
                    'prodotto = {"id": "i-001", "stato": "running"}\n'
                    '\n'
                    'ip = prodotto.get("PublicIpAddress")\n'
                    'if ip == None:              # BUG 1: confronto sbagliato\n'
                    '    print("Nessun IP")\n'
                    '\n'
                    'nome = prodotto.get("Tag_Name")\n'
                    'label = nome if nome else None  # BUG 2: default inutile\n'
                    'print(f"Label: {label}")'
                ),
                "check": lambda out, err, vs: err is None and "Nessun IP" in out and "Label:" in out,
                "feedback": lambda out, err: "BUG 1: usa `is None` non `== None`. BUG 2: `label = nome or 'senza-nome'` per un default utile",
                "hint": "if ip is None:  e  label = nome or 'senza-nome'",
                "xp_bonus": 0,
            },
            {
                "testo": "🏆 **BOSS**: Combina `enumerate`, `sorted` e None-safety: stampa le prodotti ordinate per costo, numerate, mostrando `N/A` se il campo `tag` è `None`.",
                "placeholder": (
                    'prodotti = [\n'
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
                    'ordinate = sorted(prodotti, key=lambda x: x["costo"], reverse=True)\n'
                    'for i, ist in enumerate(ordinate, start=1):\n'
                    '    tag = ist["tag"] or "N/A"\n'
                    '    print(f"{i}. {ist[\'nome\']} (${ist[\'costo\']}) [{tag}]")'
                ),
                "hint": 'tag = ist["tag"] or "N/A"',
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
                "testo": "🏆 **BOSS**: Logga un `ERROR` che include una variabile: `scaffale = 'logs'` e registra `Connessione fallita al scaffale logs` con una f-string.",
                "placeholder": 'import logging, sys\nlogging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(levelname)s: %(message)s")\nscaffale = "logs"\n# logga un error con f-string',
                "check": lambda out, err, vs: err is None and "ERROR" in out and "scaffale logs" in out,
                "feedback": lambda out, err: 'Usa `logging.error(f"Connessione fallita al scaffale {scaffale}")`.',
                "hint": 'import logging, sys\nlogging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(levelname)s: %(message)s")\nscaffale = "logs"\nlogging.error(f"Connessione fallita al scaffale {scaffale}")',
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
Counter("mela pera mela".split())          # Counter({'mela': 2, 'pera': 1})
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
        "esempio": 'from collections import Counter\nparole = "mela pera mela uva pera mela".split()\nc = Counter(parole)\nprint(c["mela"])\nprint(c.most_common(1))',
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
                "testo": "Usa `defaultdict(list)` per raggruppare `['mela', 'melone', 'pera', 'pesca']` per lettera iniziale. Stampa la lista sotto la chiave `'p'`.",
                "placeholder": "from collections import defaultdict\nparole = ['mela', 'melone', 'pera', 'pesca']\ngruppi = defaultdict(list)\n# raggruppa e stampa gruppi['p']",
                "check": lambda out, err, vs: err is None and "['pera', 'pesca']" in out,
                "feedback": lambda out, err: "Cicla i servizi e fai `gruppi[s[0]].append(s)`, poi `print(gruppi['s'])`.",
                "hint": "from collections import defaultdict\nparole = ['mela', 'melone', 'pera', 'pesca']\ngruppi = defaultdict(list)\nfor s in parole:\n    gruppi[s[0]].append(s)\nprint(gruppi['p'])",
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
                "testo": "Usa `re.findall` per estrarre tutti i numeri da `'ho 3 prodotti e 12 volumi'`. Stampa la lista.",
                "placeholder": 'import re\ntesto = "ho 3 prodotti e 12 volumi"\n# findall dei numeri e stampa',
                "check": lambda out, err, vs: err is None and "['3', '12']" in out,
                "feedback": lambda out, err: "Usa `re.findall(r'\\\\d+', testo)`.",
                "hint": 'import re\ntesto = "ho 3 prodotti e 12 volumi"\nprint(re.findall(r"\\d+", testo))',
                "xp_bonus": 0,
            },
            {
                "testo": "Estrai il dominio da `'lorenzo@demo.com'` (tutto ciò che segue la `@`) con `re.search` e un gruppo. Stampa `demo.com`.",
                "placeholder": 'import re\nemail = "lorenzo@demo.com"\n# search con gruppo (.+) dopo @',
                "check": lambda out, err, vs: err is None and out.strip() == "demo.com",
                "feedback": lambda out, err: "Usa `re.search(r'@(.+)', email).group(1)`.",
                "hint": 'import re\nemail = "lorenzo@demo.com"\nprint(re.search(r"@(.+)", email).group(1))',
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
cur.execute("CREATE TABLE prodotti (nome TEXT, costo REAL)")
cur.execute("INSERT INTO prodotti VALUES ('penna', 0.5)")
cur.executemany("INSERT INTO prodotti VALUES (?, ?)", [("matita", 0.02), ("gomma", 0.9)])

for riga in cur.execute("SELECT * FROM prodotti WHERE costo > 0.1"):
    print(riga)
print(cur.execute("SELECT COUNT(*) FROM prodotti").fetchone()[0])
```

`?` sono **placeholder** sicuri (mai concatenare valori nelle query!). `fetchone()`/`fetchall()` leggono i risultati.
""",
        "esempio": 'import sqlite3\ncon = sqlite3.connect(":memory:")\ncur = con.cursor()\ncur.execute("CREATE TABLE t (nome TEXT)")\ncur.execute("INSERT INTO t VALUES (\'penna\')")\nfor r in cur.execute("SELECT nome FROM t"):\n    print(r[0])',
        "esercizi": [
            {
                "testo": "Crea una tabella `t(nome TEXT)`, inserisci `'penna'`, poi leggi e stampa il nome (`penna`).",
                "placeholder": 'import sqlite3\ncon = sqlite3.connect(":memory:")\ncur = con.cursor()\n# crea, inserisci, seleziona, stampa',
                "check": lambda out, err, vs: err is None and "penna" in out,
                "feedback": lambda out, err: "CREATE TABLE, INSERT, poi `for r in cur.execute('SELECT nome FROM t'): print(r[0])`.",
                "hint": 'import sqlite3\ncon = sqlite3.connect(":memory:")\ncur = con.cursor()\ncur.execute("CREATE TABLE t (nome TEXT)")\ncur.execute("INSERT INTO t VALUES (\'penna\')")\nfor r in cur.execute("SELECT nome FROM t"):\n    print(r[0])',
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
                "codice": 'import sqlite3\ncon = sqlite3.connect(":memory:")\ncur = con.cursor()\ncur.execute("CREATE TABLE s (nome TEXT, costo REAL)")\ncur.executemany("INSERT INTO s VALUES (?, ?)", [("penna", 5.0), ("matita", 0.5)])\nprint(cur.execute("SELECT nome FROM s WHERE costo > 1").fetchall())\n',
                "expected": "[('penna',)]",
                "hint": "Solo 'penna' ha costo > 1. `fetchall` restituisce una lista di tuple: `[('penna',)]` (tupla con un solo campo).",
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
r = requests.get("https://api.example.com/prodotti")
print(r.status_code)    # 200 = OK
dati = r.json()         # converte la risposta JSON in dict/list Python
print(dati["nome"])
```

Il cuore non è la chiamata, è **navigare il JSON** che torna (dict e liste annidate).
Negli esercizi qui sotto **simuliamo** quella risposta con `json.loads(...)` — la struttura è identica a quella che `r.json()` ti darebbe, così impari la parte che conta senza dipendere dalla rete.
""",
        "esempio": 'import json\nrisposta = \'{"prodotto": "penna", "stato": "disponibile", "prezzo": 0.5}\'\ndati = json.loads(risposta)\nprint(dati["stato"])\nprint(dati["prezzo"])',
        "esercizi": [
            {
                "testo": "Una API ha risposto con `'{\"prodotto\": \"penna\", \"stato\": \"running\"}'`. Convertila e stampa il valore di `stato`.",
                "placeholder": 'import json\nrisposta = \'{"prodotto": "penna", "stato": "running"}\'\n# json.loads e stampa lo stato',
                "check": lambda out, err, vs: err is None and out.strip() == "running",
                "feedback": lambda out, err: "`dati = json.loads(risposta)` poi `print(dati['stato'])`.",
                "hint": 'import json\nrisposta = \'{"prodotto": "penna", "stato": "running"}\'\ndati = json.loads(risposta)\nprint(dati["stato"])',
                "xp_bonus": 0,
            },
            {
                "testo": "La risposta `'{\"region\": \"nord\", \"prodotti\": [{\"id\": \"i-1\"}, {\"id\": \"i-2\"}]}'` contiene una lista. Stampa quante prodotti ci sono.",
                "placeholder": 'import json\nrisposta = \'{"region": "nord", "prodotti": [{"id": "i-1"}, {"id": "i-2"}]}\'\n# conta gli elementi di prodotti',
                "check": lambda out, err, vs: err is None and "2" in _ol(out),
                "feedback": lambda out, err: "`len(dati['prodotti'])`.",
                "hint": 'import json\nrisposta = \'{"region": "nord", "prodotti": [{"id": "i-1"}, {"id": "i-2"}]}\'\ndati = json.loads(risposta)\nprint(len(dati["prodotti"]))',
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

**Singleton** — una sola prodotto condivisa (es. configurazione globale), via `__new__`:
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
                "testo": "**Factory**: scrivi `crea_risorsa(tipo)` che mappa `web→Server`, `file→Storage`, `dati→Database` (default `Sconosciuto`). Stampa `crea_risorsa('file')`.",
                "placeholder": "def crea_risorsa(tipo):\n    pass\n\nprint(crea_risorsa('file'))",
                "check": lambda out, err, vs: err is None and "Storage" in out,
                "feedback": lambda out, err: "Usa un dict e `.get(tipo, 'Sconosciuto')`.",
                "hint": "def crea_risorsa(tipo):\n    risorse = {'web': 'Server', 'file': 'Storage', 'dati': 'Database'}\n    return risorse.get(tipo, 'Sconosciuto')\n\nprint(crea_risorsa('file'))",
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
                "hint": "Il Singleton via `__new__` restituisce sempre la stessa prodotto: `a is b` è True.",
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
