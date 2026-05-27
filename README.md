# 🔥 NerdMatch - Seznamka pro Nerdy

Webová aplikace pro seznamování se zaměřením na lidi se zájmem o technologie, vědu, hry, sci-fi, fantasy a matematiku.

Vytvořeno s **Flask** (Python), **Neo4j** (grafová databází) a **Docker**.

---

## 🎯 Funkcionality

- ✅ **Autentizace** - Registrace, přihlášení, odhlášení, smazání účtu (5-minutový timeout)
- ✅ **Profily** - Vytvoření a editace profilu (přezdívka, bio, nerd level, zájmy, technologie)
- ✅ **Custom Tags** - Vytváření vlastních zájmů a technologií (LinkedIn-style autocomplete)
- ✅ **Tinder-Style Discover** - Procházení profilů se swipe animacemi, drag & drop gesty
- ✅ **Vyhledávání** - Filtrování profilů (nerd level, zájmy) s timeout pro přeskočené profily
- ✅ **Matchování** - Lajkování profilů, automatická detekce vzájemného zájmu (MATCH)
- ✅ **Kontakty** - Seznam vzájemných matchů 🔥, jednostranných zájmů, obdivovatelů
- ✅ **Dashboard** - Statistiky (kontakty, matche, dostupné profily)

---

## 🚀 Spuštění aplikace

### Požadavky
- Docker & Docker Compose
- Porty 5000 (Flask) a 7687 (Neo4j) musí být volné

### Kroky

```bash
# 1. Jdi do projektové složky
cd SZZVP

# 2. Spusť Docker Compose
docker-compose up --build

# 3. Počkej 10-15 sekund na inicializaci Neo4j

# 4. Otevři aplikaci v prohlížeči
# http://localhost:5000

# 5. (Volitelně) Neo4j Browser
# http://localhost:7474
# Uživatel: neo4j
# Heslo: adminpass
```

### Zastavení
```bash
docker-compose down
```

---

## 📋 Testovací účty

### Připravené testovacie profily

20 testovacích profilů je automaticky vytvořeno při spuštění aplikace (viz `code/create_test_profiles.py`):

```bash
# Pokud chceš proběhnout profily znovu, zavolej:
python code/create_test_profiles.py
```

Toto vytvoří profily s různými:
- Nerd levely (0-10)
- Zájmy (věda, sci-fi, videohry, programování, atd.)
- Technologiemi (Python, JavaScript, Java, C++, Docker, atd.)

### Manuální vytvoření testovacího účtu

```
Email: test@example.com
Heslo: Test123!@
Přezdívka: Tester
Bio: Jsem testerem
Nerd Level: 7/10
Zájmy: Vyberi libovolně ze seznamu
Technologie: Python, Docker
```

### Testovací scénář

1. **Registrace a vytvoření profilu:**
   - Jdi na `/register`
   - Vyplň formulář a vytvoř si účet
   - Vyber si zájmy a technologie (včetně vlastních custom tagů!)

2. **Procházení Discover:**
   - `/discover` - Swipuj (mouse drag, touch, nebo klávesnice)
   - Filtruj podle nerd levelu a zájmů
   - Lajkuj (❤️) nebo přeskakuj (👎) profily

3. **Zobrazení Matchů:**
   - `/contacts` - Vidíš všechny matche a zájmy
   - Vzájemné matche jsou označeny 🔥

4. **Úprava Profilu:**
   - `/profile/edit` - Měň svoje údaje
   - Přidávej vlastní zájmy a technologie (autocomplete)

---

## 📊 Datový model

Aplikace používá Neo4j grafovou databázi s těmito uzly:

- **User** - Email, hashovné heslo, created_at
- **Account** - Stav účtu, last_login, is_deleted
- **Profile** - Přezdívka, bio, nerd_level, created_at
- **InterestCategory** - Systémové zájmy (programování, sci-fi, atd.)
- **Technology** - Technologie (Python, JavaScript, Docker, atd.)
- **Connection** - Vztahy mezi uživateli (Like/Match)

Viz [DEVELOPMENT.md](DEVELOPMENT.md) pro detaily.

---

## 📁 Projektová struktura

```
SZZVP/
├── README.md                  ← Toto (návod)
├── DEVELOPMENT.md            ← Detailní dokumentace
├── docker-compose.yml        ← Docker orchestrace
├── Dockerfile                ← Flask kontejner
│
└── code/
    ├── app.py                ← Flask hlavní aplikace
    ├── config.py             ← Konfigurace
    ├── requirements.txt      ← Python závislosti
    │
    ├── models/
    │   ├── database.py       ← Neo4j connection
    │   ├── user.py           ← User operace
    │   ├── profile.py        ← Profile operace
    │   └── connection.py     ← Like/Match operace
    │
    ├── routes/
    │   ├── auth.py           ← /register, /login, /logout
    │   ├── profile.py        ← /profile, /profile/edit
    │   ├── discover.py       ← /discover (procházení)
    │   └── contacts.py       ← /contacts
    │
    ├── utils/
    │   └── validators.py     ← Validace vstupů
    │
    ├── templates/            ← HTML šablony
    │   ├── base.html         ← Navbar, footer
    │   ├── dashboard.html    ← Statistiky
    │   ├── auth/             ← Login, Register
    │   ├── profile/          ← Profil
    │   ├── discover/         ← Vyhledávání
    │   └── contacts/         ← Kontakty
    │
    └── static/
        ├── css/style.css     ← Bootstrap 5 + vlastní
        └── js/main.js        ← Validace, interakce
```

---

## 🔄 Webové rozhraní

### Navigace
- **Přehled** → Dashboard se statistikami
- **Objevuj** → Procházení dostupných profilů
- **Kontakty** → Seznam všech matchů a zájmů
- **Profil** → Zobrazení a editace profilu
- **Odhlášení** → Logout

### Key Features

**Dashboard (`/`)**
- 📊 Počet všech kontaktů
- 🔥 Počet vzájemných matchů
- 👥 Počet dostupných profilů

**Objevuj (`/discover`)**
- 🎴 Tinder-style swipable karty s animacemi
- ✋ Drag & drop ovládání (mouse, touch, klávesnice)
- 📊 Filtrování podle nerd levelu (rozsah)
- 🏷️ Filtrování podle zájmů (AND logika)
- ⏱️ Skip timeout (4 hodiny) - přeskočené profily se neukáží znovu
- 🔥 Automatická detekce matchů
- Filter sidebar na levé straně s živou náhledové karty

**Profil (`/profile`)**
- 👤 Zobrazení profilu s nerd level barem
- ✏️ Editace (přezdívka, bio, nerd level)
- 🏷️ Custom zájmy - vytváření vlastních tagů (LinkedIn-style autocomplete)
- 💾 Custom technologie - vytváření vlastních tagů
- 📌 Autocomplete s návrhy existujících tagů
- 🎯 Automatické vytváření nových tagů při zvolení

**Kontakty (`/contacts`)**
- 🔥 Vzájemné matche s informacemi
- 💭 Jednostranné "tvůj zájem" zájmy
- 👀 Obdivovatelé (oni tě lajkají, ty ne)
- 🗑️ Odebrání kontaktu

---

## 🏷️ Custom User Tags (Zájmy & Technologie)

Uživatelé mohou vytvářet **vlastní zájmy a technologie** jako na LinkedInu:

### Jak to funguje:
1. **Při vytvoření/úpravě profilu:** Napiš nový tag do autocomplete pole
2. **Návrhy se objeví:** Existující systémové i uživatelské tagy
3. **Vytvoření:** Nový tag se automaticky vytvoří a bude k dispozici pro všechny
4. **Omezení:** V UI se zobrazuje max 10 systémových + 5 nejnovějších uživatelských tagů (ostatní jsou searchable)
5. **Discover filtrování:** Discover zobrazuje pouze systémové tagy, aby se neplést UI

### Příklady custom tagů:
- Zájmy: blockchain, AI, machine learning, gamedev, robotika
- Technologie: Rust, Go, Kubernetes, GraphQL, React Native

---

## 🎨 Styling & Design

### Tinder-Style UI
- **2-Column Layout:** Filtry vlevo (sticky), karty vpravo
- **Swipe Animations:** Drag left/right s rotací a opacity efekty
- **Responsive Design:** Desktop (350px sidebar + 1fr content), Tablet (stacked), Mobile (full-width)
- **Color Palette:** 
  - Primary: `#ff6b6b` (červená)
  - Success: `#51cf66` (zelená)
  - Nerd: `#7c3aed` (purpurová)
  - Dark: `#1a1a2e` (темný pozadí)

### Keyboard Shortcuts
- **➡️ Šipka vpravo:** Lajk (❤️)
- **⬅️ Šipka vlevo:** Skip (👎)
- **Esc:** Zavři filtr
- **Mouse drag:** Swipe gesture
- **Touch drag:** Mobilní swipe

---

## 🔒 Bezpečnost

✅ **Implementováno:**
- Hešování hesel (bcrypt s 12 koly)
- Session management s 5-minutovým timeoutem
- Validace vstupů (email, heslo, text pole)
- Soft delete (GDPR compliance)
- Parametrizované Cypher dotazy (bez SQL injection)

⚠️ **Pro produkci:**
- Přidat HTTPS
- Přidat CSRF ochranu
- Přidat rate limiting
- Přidat audit logging
- Zlepšit input validation

---

## 🛠️ Vývoj a modifikace

### Změna kódu
Soubory v `code/` se automaticky znovu načtou díky `debug=True`.

```bash
# Restartuj Flask, aby se změny projevily
docker-compose restart flask
```

### Prohlídka logů
```bash
docker-compose logs flask
docker-compose logs neo4j
```

### Restart jednotlivých služeb
```bash
docker-compose restart flask
docker-compose restart neo4j
```

---

## 🐛 Troubleshooting

| Problém | Řešení |
|---------|--------|
| Port 5000/7687 obsazen | `docker-compose down` a zkus znovu |
| Neo4j se nespustila | Počkej 20 sekund, restartuj: `docker-compose restart neo4j` |
| Flask se neaktualizuje | `docker-compose restart flask` |
| Chyba připojení k DB | Ověř `docker-compose logs neo4j` |

---

## 📚 Architektura a Struktura Kódu

### Datový Model (Neo4j)
```
User {id, email, password_hash, created_at}
  ↓
Account {is_deleted, last_login}
  ↓
Profile {nickname, bio, nerd_level, created_at}
  ↓
InterestCategory {name, type: "SYSTEM"|"USER", created_by}
Technology {name, created_by}

Vztahy:
- User -[:HAS_ACCOUNT]→ Account
- User -[:HAS_PROFILE]→ Profile
- Profile -[:INTERESTED_IN]→ InterestCategory
- Profile -[:LIKES_TECHNOLOGY]→ Technology
- User -[:LIKES]→ User (matchování)
- User -[:SKIP]→ User (s timestamp)
```

### Cypher Query Patterns
- **MERGE s ON CREATE:** Vytváření tagů pouze když neexistují
- **Parametrizované dotazy:** Bezpečnost proti injection
- **Sada relací:** Skip s timeout kontrolou pomocí `duration()`

### Kód je dokumentován
- In-line dokumentace v Python souborech
- Jinja2 šablony s českými komentáři
- JavaScript s JSDOC
- CSS proměnné pro konzistentní design

---

## 🔗 Technologie

### Backend
- **Framework:** Flask 3.0.0 (Python 3.10)
- **Databáze:** Neo4j 4.4+ (grafová databáze)
- **Driver:** py2neo 2021.2.4
- **Hešování:** bcrypt 4.1.0

### Frontend
- **Styling:** Bootstrap 5 + custom CSS (Tinder-style design)
- **Templating:** Jinja2
- **JavaScript:** Vanilla JS (bez frameworků)
  - Swipe gestures & animations
  - Autocomplete UI pro custom tags
  - Keyboard shortcuts

### DevOps
- **Kontejnerizace:** Docker & Docker Compose
- **Services:** Flask (port 5000) + Neo4j (port 7687)

---

## ✅ Co je hotovo

- ✅ **Autentizace** - Registrace, login, logout, soft delete
- ✅ **Profil** - Vytvoření, zobrazení, editace s custom tags
- ✅ **Custom Tags** - Autocomplete, vytváření vlastních zájmů/technologií
- ✅ **Dashboard** - Statistiky kontaktů a matchů
- ✅ **Discover** - Tinder-style procházení s filtrováním a skip timeout
- ✅ **Matchování** - Like/skip, automatická detekce matchů
- ✅ **Kontakty** - Zobrazení matchů, zájmů a obdivovatelů
- ✅ **Styling** - Jednotný Tinder-inspirovaný design

## 📝 Volitelná rozšíření

- Notifikace pro nové matche
- Vyhledávání podle jména
- Preference soukromí profilu
- Profilové fotografie
- Zprávy mezi matched uživateli
- Rated svýmch profilů (nejaktivnější, nejnovější)

---

## 🚀 Jak spustit

### Quickstart (Docker)
```bash
cd SZZVP
docker-compose up --build

# Počkej 10-15 sekund na inicializaci Neo4j
# Otevři http://localhost:5000
```

### Vytvoření testovacích dat
```bash
# Po spuštění Docker:
docker-compose exec flask python code/create_test_profiles.py

# Nebo v normálním Python prostředí:
python code/create_test_profiles.py
```

### Bez Docker (Development)
```bash
# Setup:
cd code
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt

# Ujisti se, že Neo4j běží na bolt://localhost:7687
# potom:
python app.py
```

---

## 👨‍💻 Projekt Info

**Projekt:** NerdMatch - Seznamka pro Nerdy  
**Status:** ✅ MVP + Styling hotov  
**Datum poslední aktualizace:** 27.5.2026  
**Vytvořeno pro:** SZZVP státnickou zkoušku  

Technologie: Flask + Neo4j + Docker + Vanilla JS

---

## 📄 Licence

Projekt je určen pro vzdělávací účely (státnické zkoušky SZZVP).
