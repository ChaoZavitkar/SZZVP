# Architektura aplikace Matchomat

## 📋 Přehled projektu

**Matchomat** je webová aplikace sociální sítě inspirovaná online seznamkou (Tinder). Uživatelé se mohou vzájemně "matchovat" (dávat si likes/dislikes) a vidět své potenciální páry.

**Technologický stack:**
- **Backend:** Flask (Python)
- **Databáze:** Neo4j (grafová databáze)
- **ORM/Driver:** py2neo (Python -> Neo4j)
- **Frontend:** Jinja2 templaty + HTML
- **Orchestrace:** Docker & Docker Compose

---

## 🏗️ Architektura systému

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Compose                          │
├──────────────────────────┬──────────────────────────────────┤
│                          │                                  │
│  ┌────────────────────┐  │  ┌──────────────────────────────┐
│  │   Flask Service    │  │  │    Neo4j Database Service    │
│  │  (Container)       │  │  │  (Container)                 │
│  │                    │  │  │                              │
│  │  ┌──────────────┐  │  │  │  Port: 7687 (Bolt)           │
│  │  │  app.py      │  │  │  │  Port: 7474 (Browser)        │
│  │  │              │  │  │  │  User: neo4j                 │
│  │  │  Routes:     │  │  │  │  Pass: adminpass             │
│  │  │  /home       │  │  │  │  Healthcheck: Enabled        │
│  │  │  /search     │  │  │  │                              │
│  │  │  /matches    │  │  │  └──────────────────────────────┘
│  │  │              │  │  │
│  │  └──────────────┘  │  │
│  │                    │  │
│  │ Volume:            │  │
│  │ ./code:/code       │  │
│  │                    │  │
│  └────────────────────┘  │
│          ↓               │
│  http://localhost:5000   │
│                          │
└──────────────────────────┴──────────────────────────────────┘
```

---

## 📊 Datový model (Neo4j)

### Uzly (Nodes)

```
:Person {
  name: String          # Jméno uživatele (unikátní)
  age: Integer          # Věk
  hobbies: [String]     # Pole se zálibami
}
```

**Příklad uzlů:**
```
(Pepa:Person {name: "Pepa", age: 34, hobbies: ["programming", "running"]})
(Jana:Person {name: "Jana", age: 30, hobbies: ["cats", "running"]})
(Michal:Person {name: "Michal", age: 38, hobbies: ["partying", "cats"]})
(Alena:Person {name: "Alena", age: 32, hobbies: ["kids", "cats"]})
(Richard:Person {name: "Richard", age: 33, hobbies: ["partying", "cats"]})
```

### Vztahy (Relationships)

```
(user:Person)-[:LIKES]->(friend:Person)        # Like profil
(user:Person)-[:DISLIKES]->(friend:Person)    # Dislike profil
```

**Příklad vztahů:**
```
Pepa -[:LIKES]-> Jana
Jana -[:LIKES]-> Pepa           # Vzájemný like (MATCH!)
Michal -[:LIKES]-> Alena
Alena -[:DISLIKES]-> Michal     # One-way dislike
Alena -[:LIKES]-> Pepa
Richard -[:LIKES]-> Alena
```

### Vizualizace

```
Pepa ←──LIKES──→ Jana  ✓ MATCH (vzájemný like)
  ↑
  └─ LIKES ← Alena

Michal ──LIKES──→ Alena
            ←──DISLIKES──

Richard ──LIKES──→ Alena
```

---

## 🔄 Pracovní postup (Workflow)

### 1. Inicializace (Startup)

```python
docker-compose up --build
    ↓
Flask kontejner spuštěn (port 5000)
    ↓
Neo4j kontejner spuštěn (Bolt: 7687, Browser: 7474)
    ↓
Health check Neo4j (kontrola připojení)
    ↓
Flask čeká na Neo4j (depends_on: condition: service_healthy)
    ↓
mock_data() - vložení testovacích dat do DB
    ↓
Aplikace připravena (http://localhost:5000)
```

### 2. Datový tok

```
USER
  ↓
Browser (HTTP GET/POST)
  ↓
Flask Route (@app.route)
  ↓
Python Funkce (get_matches, available_matches, atd.)
  ↓
py2neo (Graph.run() s Cypher dotazy)
  ↓
Neo4j Server (Bolt protocol)
  ↓
Data ← zpět přes py2neo
  ↓
Jinja2 Renderer (vyrenderuje HTML)
  ↓
Browser (zobrazí HTML)
```

---

## 🚀 Klíčové funkce (Functions)

### 1. `get_user_node(graph, name)` – Získání uzlu uživatele
```python
def get_user_node(graph, name):
    return graph.evaluate(f"""
        MATCH (user:Person)
        WHERE user.name = '{name}'
        RETURN user
    """)
```
**Výstup:** Objekt Node s daným jménem  
**Použití:** Při vytváření nových vztahů

---

### 2. `get_logged_user_profile(graph, username)` – Profil přihlášeného uživatele
```python
def get_logged_user_profile(graph, username):
    return graph.run(f"""
        MATCH (user:Person)
        WHERE user.name = '{username}'
        RETURN user.name, user.age, user.hobbies
    """).data()[0]
```
**Výstup:** Dict s `user.name`, `user.age`, `user.hobbies`  
**Použití:** Stránka `/home`

---

### 3. `get_matches(graph, username)` – Vzájemné likes (MATCHES)
```python
def get_matches(graph, username):
    return graph.run(f"""
        MATCH (friend:Person)-[:LIKES]->(user:Person)-[:LIKES]->(friend:Person) 
        WHERE user.name = '{username}'
        RETURN friend.name, friend.age, friend.hobbies
    """).data()
```

**Cypher logika:**
```
friend ──LIKES──→ user ──LIKES──→ friend
        ← (vzájemný like) →
```

**Výstup:** Seznam osob, které si daly vzájemný like  
**Použití:** Stránka `/matches`

---

### 4. `available_matches(graph, username)` – Dostupné profily k matchování
```python
def available_matches(graph, username):
    return graph.run(f"""
        MATCH (user:Person)
        MATCH (friend:Person)
        WHERE user.name = '{username}'
        AND NOT (user:Person)-[:LIKES]->(friend:Person)           # Ještě nedal like
        AND NOT (friend:Person)-[:DISLIKES]->(user:Person)        # Neobdržel dislike
        AND NOT (user:Person)-[:DISLIKES]->(friend:Person)        # Nedat vlastní dislike
        AND NOT friend.name = '{username}'                        # Není sám sobě
        RETURN friend.name, friend.age, friend.hobbies
    """).data()
```

**Podmínky (vyfiltrovány):**
1. Uživatel ještě nedal like
2. Druhá osoba nedala dislike prvnímu
3. Uživatel neda vlastní dislike
4. Osoba není sám sobě

**Výstup:** Seznam osob k matchování  
**Použití:** Stránka `/search`

---

## 🌐 Flask Routes (API endpoints)

| Route | Metoda | Popis | Template |
|-------|--------|-------|----------|
| `/` nebo `/home` | GET | Domovská stránka - statistiky a profil | `home.html` |
| `/search` | GET | Zobrazí náhodný dostupný profil | `search.html` |
| `/search` | POST | Zaregistruje like/dislike na profil | (redirect → /search) |
| `/matches` | GET | Zobrazí všechny vzájemné matche | `matches.html` |
| `/login` | GET | Přihlašovací stránka (nemá šablonu) | `login.html` |

### Detailní popis routes

#### `/home` (GET)
```python
@app.route("/")
@app.route("/home")
def hello_world():
    logged_user_info = get_logged_user_profile(graph, logged_user)
    num_of_matches = len(get_matches(graph, logged_user))
    num_of_available_matches = len(available_matches(graph, logged_user))
    return render_template("home.html", 
        profile=logged_user_info, 
        num_of_matches=num_of_matches, 
        num_of_available_matches=num_of_available_matches
    )
```

**Data předaná do šablony:**
- `profile` – Profil přihlášeného uživatele
- `num_of_matches` – Počet vzájemných liků
- `num_of_available_matches` – Počet osob k matchování

**HTML výstup:**
```
Vítej na Matchomatu
├─ Statistiky
│  ├─ Počet lidí, se kterými se ještě můžeš seznámit: X
│  └─ Počet lidí, se kterými jsi již v páru: Y
└─ Tvůj profil
   ├─ Jméno
   ├─ Věk
   └─ Záliby (seznam)
```

---

#### `/search` (GET)
```python
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        potential_matches = available_matches(graph, logged_user)
        if potential_matches:
            random_profile = choice(potential_matches)  # Náhodný výběr
        else:
            random_profile = None
        return render_template("search.html", profile=random_profile)
```

**Logika:**
1. Získej dostupné profily
2. Vyber náhodný profil
3. Zobraz s tlačítky Like/Dislike

**HTML výstup:**
```
Hledej
├─ [Náhodný profil s Like/Dislike tlačítky]
└─ nebo "Žádný profil nenalezen"
```

---

#### `/search` (POST)
```python
else:
    date_choice = request.form.get("date_choice")      # "like" nebo "dislike"
    friend_name = request.form.get("friend_name")      # Skrytý form input
    user_node = get_user_node(graph, logged_user)
    friend_node = get_user_node(graph, friend_name)
    
    if date_choice == "like":
        new_relationship = Relationship(user_node, "LIKES", friend_node)
    elif date_choice == "dislike":
        new_relationship = Relationship(user_node, "DISLIKES", friend_node)
    
    graph.create(new_relationship)  # Vytvoř vztah v DB
    return redirect("/search")      # Vrátit se na search
```

**Postup:**
1. Formulář pošle skryté pole `friend_name`
2. Vytvoř vztah LIKES nebo DISLIKES
3. Ulož do Neo4j
4. Přesměruj na `/search` → zobraz nový profil

---

#### `/matches` (GET)
```python
@app.route("/matches")
def matches():
    matches = get_matches(graph, logged_user)
    return render_template("matches.html", profiles=matches)
```

**HTML výstup:**
```
Shody
├─ [Profil 1 - vzájemný like]
├─ [Profil 2 - vzájemný like]
└─ nebo "Bohužel nemáte žádné shody"
```

---

## 📝 HTML Šablony

### `template.html` – Základní layout
```html
<!DOCTYPE html>
<html>
<head>
    <title>Matchomat</title>
</head>
<body>
    <header><h1>Matchomat</h1></header>
    <nav>
        <ul>
            <li><a href="/home">Domů</a></li>
            <li><a href="/search">Hledej</a></li>
            <li><a href="/matches">Shody</a></li>
        </ul>
    </nav>
    <main>{% block content %}{% endblock %}</main>
    <footer>Matchomat, Beránek Pavel 2023</footer>
</body>
</html>
```

### `home.html` – Domovská stránka
- Uvítá uživatele
- Zobrazí statistiky (matchů, dostupných profilů)
- Zobrazí vlastní profil (jméno, věk, záliby)

### `search.html` – Hledání profilů
- Náhodný dostupný profil (jméno, věk, záliby)
- Tlačítka: **Like** a **Dislike**
- Skrytý input: `friend_name` (pro identifikaci profilu)

### `matches.html` – Vzájemné matche
- Cyklus přes všechny matche
- Karty s profily (jméno, věk, záliby)
- Pokud žádné matche: "Bohužel nemáte žádné shody"

---

## 🐳 Docker & Docker Compose

### Dockerfile
```dockerfile
FROM python:3.10-alpine
WORKDIR /code
COPY requirements.txt /code
RUN pip install -r requirements.txt --no-cache-dir
COPY ./code /code
CMD python app.py
```

**Kroky:**
1. Vychází z `python:3.10-alpine` (minimální obraz)
2. Pracovní adresář: `/code`
3. Instalace Python závislostí
4. Zkopírování kódu do kontejneru
5. Spuštění `app.py`

### docker-compose.yml
```yaml
version: '3'
services:
  flask:
    build: .
    container_name: flask
    ports:
      - "5000:5000"
    volumes:
      - ./code:/code          # Sdílená složka (live reload)
    depends_on:
      neo4j:
        condition: service_healthy

  neo4j:
    image: 'neo4j:latest'
    ports:
      - '7474:7474'           # Web Browser
      - '7687:7687'           # Bolt (Python connection)
    environment:
      NEO4J_AUTH: 'neo4j/adminpass'
    healthcheck:
      test: cypher-shell --username neo4j --password adminpass 'MATCH (n) RETURN COUNT(n);'
      interval: 10s
      timeout: 10s
      retries: 5
```

**Detaily:**
- **depends_on**: Flask čeká, až Neo4j projde healthcheckem
- **volumes**: `./code:/code` umožňuje live reload při úpravě souborů
- **ports**: Flask na `5000`, Neo4j Browser na `7474`, Bolt na `7687`
- **healthcheck**: Ověřuje, že Neo4j je dostupná (brání connection errorsům)

---

## 🔌 Komunikace zwischen komponentami

```
┌─────────────┐
│   Browser   │
│  (Chrome)   │
└──────┬──────┘
       │ HTTP GET/POST
       ↓
┌──────────────────────────┐
│   Flask App (Python)     │
│  - Route handlers        │
│  - DB queries            │
└──────┬───────────────────┘
       │ py2neo
       │ (Cypher queries)
       ↓
┌──────────────────────────┐
│   Neo4j (Bolt 7687)      │
│  - Graph Database        │
│  - Relationships         │
│  - Query execution       │
└──────────────────────────┘
```

---

## 🔐 Bezpečnost & Poznámky

⚠️ **Aktuální stav (učební projekt):**
- Uživatel je hardkodován: `logged_user = "Pepa"`
- SQL Injection vulnerability v Cypher dotazech (string interpolation)
- Bez CSRF ochrany
- Bez validace vstupů

✅ **V produkčním kódu:**
- Implementovat AuthN/AuthZ
- Parametrizované Cypher dotazy
- CSRF tokeny
- Input validation
- Heslo v environment variables

---

## 📦 Závislosti (requirements.txt)

| Balíček | Verze | Účel |
|---------|-------|------|
| Flask | 3.0.0 | Web framework |
| py2neo | 2021.2.4 | Neo4j driver pro Python |
| Jinja2 | 3.1.2 | Template engine |
| Werkzeug | 3.0.1 | WSGI utilities |
| click | 8.1.7 | CLI utilities |

---

## 🚦 Spouštění aplikace

```bash
# 1. Klonuj repo a naviguj do něj
cd SZZVP

# 2. Spusť Docker Compose
docker-compose up --build

# 3. Otevři v prohlížeči
http://localhost:5000

# 4. Zobraž Neo4j Browser
http://localhost:7474
# Přihlášení: neo4j / adminpass

# 5. Zobrazit logy Flask
docker-compose logs flask

# 6. Zastavit aplikaci
docker-compose down
```

---

## 📊 Testovací data

### Uživatelé
| Jméno | Věk | Záliby |
|-------|-----|--------|
| Pepa | 34 | programming, running |
| Jana | 30 | cats, running |
| Michal | 38 | partying, cats |
| Alena | 32 | kids, cats |
| Richard | 33 | partying, cats |

### Počáteční vztahy
```
Pepa LIKES Jana       +  Jana LIKES Pepa      = MATCH ✓
Michal LIKES Alena    +  Alena DISLIKES Michal
Alena LIKES Pepa
Richard LIKES Alena
```

**Výsledek:**
- Pepa: 1 match (Jana), 2 available (Michal, Richard)
- Jana: 1 match (Pepa), 3 available (Michal, Alena, Richard)
- Michal: 0 matches, 2 available (Jana, Richard)
- Alena: 0 matches (Pepa není uveden), 1 available (Jana, Richard)
- Richard: 0 matches, 3 available (Pepa, Jana, Michal)

---

## 🎯 Součásti projektu

```
SZZVP/
├── ARCHITECTURE.md            ← Toto (dokumentace)
├── Dockerfile                 ← Docker obraz
├── docker-compose.yml         ← Orchestrace
└── code/
    ├── app.py                 ← Hlavní aplikace
    ├── requirements.txt       ← Dependencies
    └── templates/
        ├── template.html      ← Base layout
        ├── home.html          ← Domů
        ├── search.html        ← Hledej
        └── matches.html       ← Shody
```

---

## 🔄 Příklad uživatelského toku

```
1. Uživatel otevře http://localhost:5000
   ↓
2. Flask spustí get_logged_user_profile("Pepa")
   ├─ Cypher: MATCH (user:Person) WHERE user.name = 'Pepa'
   ├─ Neo4j vrátí: {name: "Pepa", age: 34, hobbies: [...]}
   └─ HTML se vyrenderuje s daty
   ↓
3. Stránka zobrazí:
   ├─ Pepa (34) - programming, running
   ├─ Počet dostupných: 2
   └─ Počet matchů: 1
   ↓
4. Uživatel klikne "Hledej" → /search (GET)
   ├─ Flask spustí available_matches("Pepa")
   ├─ Neo4j vrátí: [Michal, Richard]
   ├─ choice() vybere náhodně: Michal
   └─ Zobrazí jeho profil
   ↓
5. Uživatel klikne "Like"
   ├─ Formulář pošle POST /search
   ├─ friend_name = "Michal"
   ├─ date_choice = "like"
   ├─ Flask vytvoří: Pepa -[:LIKES]-> Michal
   ├─ Neo4j uloží vztah
   └─ Přesměruj na /search → nový profil (Richard)
   ↓
6. Uživatel klikne "Matches"
   ├─ Flask spustí get_matches("Pepa")
   ├─ Cypher vrátí jenom Jana (vzájemný like)
   └─ Zobrazí Janu
```

---

## 📚 Dodatečné informace

- **Neo4j Query Language:** Cypher
- **Python ORM:** py2neo (high-level driver)
- **Web Server:** Flask development server
- **Template Engine:** Jinja2
- **Kontejnerizace:** Docker & Docker Compose

