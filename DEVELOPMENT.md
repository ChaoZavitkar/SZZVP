# 🚀 DEVELOPMENT PLAN - NerdMatch Aplikace

## 📋 Přehled projektu

**Aplikace:** NerdMatch - Seznamka/sociální síť pro nerdy  
**Tech Stack:** Flask (Python) + Neo4j (grafová DB) + Docker  
**Cíl:** Webová aplikace pro seznamování se zaměřením na lidi se zájmem o technologie, vědu, hry, sci-fi, fantasy, matematiku, komiksy atd.

**Zadání:** [Zadání - Vývoj webové aplikace.pdf](Zadání%20-%20Vývoj%20webové%20aplikace.pdf)

---

# 🎯 AKTUÁLNÍ STAV IMPLEMENTACE

## Status: ✅ MINIMÁLNÍ VIABLE PRODUCT (MVP) HOTOV

### Hotové fáze:
- ✅ **FÁZE 1** - Autentizace (registrace, login, logout, smazání účtu, session timeout 5 min)
- ✅ **FÁZE 2** - Profil uživatele (vytvoření, zobrazení, editace s zájmy a technologiemi)
- ✅ **FÁZE 3** - Dashboard (statistiky kontaktů, matchů, dostupných profilů)
- ✅ **FÁZE 4** - Vyhledávání profilů (discovery s filtrováním, like/skip, automatická detekce matchů)
- ✅ **FÁZE 5** - Kontakty (seznam vzájemných matchů a jednostranných zájmů, odebrání)

### Zbývá:
- ⏳ **FÁZE 6** - UI/UX vylepšení (je funkční, ale lze vylepšit design)
- ⏳ **Volitelné** - Notifikace, vyhledávání podle jména, preference soukromí, atd.

---

## 🧪 Testovací účty

Jsou v databázi funkční účty:

| Email | Heslo | Profil | Nerd Level | Zájmy |
|-------|-------|--------|-----------|-------|
| `alice@example.com` | `Alice123!@` | Alice | 8/10 | programování, sci-fi |
| `bob@example.com` | `Bob123!@` | Bob | 6/10 | videohry, matematika |

**Status:** Alice ❤️ Bob (Alice si lajkla Boba, ale Bob se ještě nepřihlásil)

---

## 🚀 Jak spustit a testovat aplikaci

### Spuštění:
```bash
cd /c/Users/LBao/Documents/GitHub/SZZVP
docker-compose up --build
```

Aplikace běží na: **http://localhost:5000**

### Testovací scénář:
1. **Přihlášení:** alice@example.com / Alice123!@
2. **Dashboard:** Zobrazí statistiky
3. **Profil:** Zobrazí "Alice" s bio a zájmy
4. **Objevuj:** Procházení dostupných profilů (Boba už nevidí, protože si ho lajkla)
5. **Kontakty:** Vidí "Tvůj zájem" na Bob (jednostranný like)
6. **Logout:** Odhlášení
7. **Nový účet:** Registrace s novým emailem → automaticky na vytvoření profilu

---

# 📐 DATOVÝ MODEL (Neo4j)

## Architektonická rozhodnutí

✅ **User Management:** Modulární (User + Account + Profile oddělené)  
✅ **Tagy (Zájmy):** Kombinace predefinovaných (systém) + user-defined (LinkedIn styl)  
✅ **Connections:** Uzel Connection s metadata (is_match, created_at, is_deleted)

---

## 🎯 Uzly a jejich atributy

### 1. User
```neo4j
(:User {
  id: UUID                     # Unikátní identifikátor (uuid())
  email: String                # Email (unikátní, lowercased)
  password_hash: String        # Heslo hashováno bcryptem
  created_at: DateTime         # Čas vytvoření účtu
})
```

### 2. Account
```neo4j
(:Account {
  user_id: UUID                # Cizí klíč na User
  last_login: DateTime         # Poslední přihlášení
  last_activity: DateTime      # Poslední aktivita (pro timeout)
  login_attempts: Integer      # Počet pokusů o přihlášení (anti-brute force)
  is_deleted: Boolean          # Soft delete (GDPR)
  deleted_at: DateTime         # Čas smazání (pokud je_deleted)
})

VZTAH: (User)-[:HAS_ACCOUNT]->(Account)
```

### 3. Profile
```neo4j
(:Profile {
  user_id: UUID                # Cizí klíč na User
  nickname: String             # Přezdívka (unikátní, 3-50 znaků)
  bio: String                  # Krátký popis (0-500 znaků)
  nerd_level: Integer          # Úroveň nerdství (0-10)
  is_public: Boolean           # Viditelnost profilu (default: true)
  created_at: DateTime
  updated_at: DateTime
})

VZTAH: (User)-[:HAS_PROFILE]->(Profile)
```

### 4. InterestCategory (Zájmy - Systém nebo User-defined)
```neo4j
(:InterestCategory {
  name: String                 # Název zájmu (unikátní)
  type: String                 # "SYSTEM" nebo "USER"
  created_by: UUID             # ID uživatele (jen pokud type="USER")
  created_at: DateTime
})

VZTAH: (Profile)-[:INTERESTED_IN {added_at: DateTime}]->(InterestCategory)

SYSTÉMOVÉ ZÁJMY (vytvoříme při inicializaci):
- programování
- videohry
- sci-fi
- fantasy
- matematika
- AI / Machine Learning
- hardware
- komiksy
```

### 5. Technology (Technologie - Predefinované)
```neo4j
(:Technology {
  name: String                 # Název (unikátní) - "Python", "Arduino" atd.
  category: String             # "LANGUAGE", "FRAMEWORK", "TOOL", "HARDWARE"
  created_at: DateTime
})

VZTAH: (Profile)-[:LIKES_TECHNOLOGY {added_at: DateTime}]->(Technology)

SYSTÉMOVÉ TECHNOLOGIE:
JAZYKY: Python, JavaScript, Java, C++, Rust, Go, Kotlin
FRAMEWORKY: Flask, Django, React, Vue, Angular
NÁSTROJE: Docker, Git, Linux
HARDWARE: Arduino, Raspberry Pi
```

### 6. Connection (Propojení - Like/Match)
```neo4j
(:Connection {
  id: UUID                     # Unikátní identifikátor
  created_at: DateTime         # Čas vytvoření
  is_match: Boolean            # true = oboustranný, false = jednostranný
  is_deleted: Boolean          # Soft delete (když uživatel odebere)
  deleted_at: DateTime         # Čas odstranění
})

VZTAHY:
(User1)-[:INITIATED_CONNECTION]->(Connection)<-[:RECEIVED_CONNECTION]-(User2)

LOGIKA MATCHOVÁNÍ:
- User_A -> User_B = User_A dá "Zaujalo mě"
  ├─ Vytvoří se Connection s is_match=false
  
- User_B -> User_A = User_B také dá "Zaujalo mě"
  ├─ Najdeme existující Connection
  ├─ Nastavíme is_match=true (MATCH! 🔥)
```

---

## 🔗 Celkový diagram

```
USER SECTION:
┌─────────────────────────────────────────┐
│          User (email, pwd_hash)         │
├─────────────────────────────────────────┤
        │
        ├─ [:HAS_ACCOUNT] ──→ Account (last_login, is_deleted)
        │
        └─ [:HAS_PROFILE] ──→ Profile (nickname, bio, nerd_level)
                                    │
                                    ├─ [:INTERESTED_IN] ──→ InterestCategory
                                    │
                                    └─ [:LIKES_TECHNOLOGY] ──→ Technology

CONNECTION SECTION:
┌─────────────────────────────────────────┐
│      User1 ──INITIATED──→ Connection ←──RECEIVED── User2        │
│            (is_match: true/false, created_at)                    │
└─────────────────────────────────────────┘
```

---

# 🎯 IMPLEMENTAČNÍ PLÁN

## FÁZE 1️⃣ - AUTENTIZACE (PRIORITA: VELMI VYSOKÁ)

### Požadavky ze zadání (2.1)
- Přihlášení (login)
- Registrace (email + heslo)
- Validace hesla (8+ znaků, malé+velké písmeno, číslo, speciální znak)
- Hashing hesla (bcrypt)
- Odhlášení
- Auto-logout po 5 minutách nečinnosti
- Smazání účtu + všech dat

### 1.1 Registrace (POST `/register`)

**Vstup:**
- email: string (format: xxx@xxx.xxx)
- password: string (min 8 znaků, podmínky níže)
- password_confirm: string

**Validace:**
```
✓ Email existuje?           → Error: "Email již používán"
✓ Email je platný?          → Error: "Neplatný email"
✓ Hesla se shodují?         → Error: "Hesla se neshodují"
✓ Délka hesla >= 8?         → Error
✓ Obsahuje malé písmeno?    → Error
✓ Obsahuje velké písmeno?   → Error
✓ Obsahuje číslici?         → Error
✓ Obsahuje speciální znak?  → Error
```

**Akce:**
1. Hashovat heslo (bcrypt)
2. Vytvořit User uzel
3. Vytvořit Account uzel
4. Propojit vztahem
5. Flash: "Účet vytvořen! Přihlaste se."
6. Redirect: `/login`

**Cypher:**
```cypher
CREATE (user:User {
  id: apoc.create.uuid(),
  email: $email,
  password_hash: $password_hash,
  created_at: datetime()
})
CREATE (account:Account {
  user_id: user.id,
  last_login: null,
  last_activity: null,
  login_attempts: 0,
  is_deleted: false
})
CREATE (user)-[:HAS_ACCOUNT]->(account)
RETURN user
```

### 1.2 Přihlášení (POST `/login`)

**Vstup:**
- email: string
- password: string

**Akce:**
1. Najít uživatele (User {email})
2. Ověřit heslo (bcrypt.check())
3. Kontrola is_deleted
4. Kontrola login_attempts
5. Nastavit session["user_id"] = user.id
6. Aktualizovat last_login a last_activity
7. Resetovat login_attempts = 0
8. Flash: "Přihlášeni!"
9. Redirect: `/` (dashboard)

**Cypher:**
```cypher
MATCH (user:User {email: $email})
MATCH (user)-[:HAS_ACCOUNT]->(account)
WHERE account.is_deleted = false
SET account.last_login = datetime()
SET account.last_activity = datetime()
SET account.login_attempts = 0
RETURN user
```

### 1.3 Odhlášení (GET `/logout`)

**Akce:**
1. Vymazat session["user_id"]
2. Flash: "Odhlášeni!"
3. Redirect: `/login`

### 1.4 Session Management (Middleware)

**Timeout:** 5 minut

**Logika:**
- Každý request: kontrola session["last_activity"]
- Pokud (nyní - last_activity) > 300 sekund:
  - Vymazat session
  - Flash: "Relace vypršela"
  - Redirect: `/login`
- Jinak: aktualizovat last_activity

**Implementace:**
- Decorator: `@require_login`
- Middleware: `before_request`

### 1.5 Smazání účtu (POST `/delete-account`)

**Vstup:**
- password: string (ověření)
- confirm: string = "yes" (double-check)

**Akce:**
1. Ověřit heslo
2. Ověřit checkbox
3. SET account.is_deleted = true
4. SET account.deleted_at = datetime()
5. Smazat profil
6. Vymazat session
7. Flash: "Účet smazán"
8. Redirect: `/login`

---

## FÁZE 2️⃣ - PROFIL UŽIVATELE (PRIORITA: VELMI VYSOKÁ)

### Požadavky ze zadání (2.4)
- Přezdívka (editovatelná)
- Bio (editovatelné)
- Zájmy (min. 1, editovatelné)
- Technologie (volitelné, editovatelné)
- Nerd level 0-10 (editovatelné, slider)

### 2.1 GET `/profile` - Zobrazení profilu

**Cypher:**
```cypher
MATCH (user:User {id: $user_id})
MATCH (user)-[:HAS_PROFILE]->(profile:Profile)
OPTIONAL MATCH (profile)-[:INTERESTED_IN]->(interest:InterestCategory)
OPTIONAL MATCH (profile)-[:LIKES_TECHNOLOGY]->(tech:Technology)
RETURN profile, collect(interest.name) as interests, 
       collect(tech.name) as technologies
```

### 2.2 POST `/profile/edit` - Editace profilu

**Vstup:**
- nickname: string (3-50 znaků)
- bio: string (0-500 znaků)
- interests: list[string] (min 1)
- technologies: list[string] (prázdné OK)
- nerd_level: integer (0-10)

**Cypher:**
```cypher
MATCH (user:User {id: $user_id})-[:HAS_PROFILE]->(profile:Profile)
SET profile.nickname = $nickname
SET profile.bio = $bio
SET profile.nerd_level = $nerd_level
SET profile.updated_at = datetime()

OPTIONAL MATCH (profile)-[r:INTERESTED_IN]->()
DELETE r

WITH profile
UNWIND $interests as interest_name
MATCH (interest:InterestCategory {name: interest_name})
CREATE (profile)-[:INTERESTED_IN {added_at: datetime()}]->(interest)

OPTIONAL MATCH (profile)-[r:LIKES_TECHNOLOGY]->()
DELETE r

WITH profile
UNWIND $technologies as tech_name
MATCH (tech:Technology {name: tech_name})
CREATE (profile)-[:LIKES_TECHNOLOGY {added_at: datetime()}]->(tech)

RETURN profile
```

---

## FÁZE 3️⃣ - DASHBOARD (PRIORITA: STŘEDNÍ)

### Požadavky ze zadání (2.2)
- Počet navázaných kontaktů
- Počet zobrazených profilů (zatím nebudeme sledovat)
- Počet matchů
- Bonus: Grafické zobrazení

### 3.1 GET `/` - Dashboard data

**Cypher dotazy:**
```cypher
-- Počet všech kontaktů
MATCH (user:User {id: $user_id})
MATCH (conn:Connection)
WHERE (conn.sender_id = user.id OR conn.receiver_id = user.id)
AND conn.is_deleted = false
RETURN count(conn) as total_contacts

-- Počet matchů (oboustranný zájem)
MATCH (user:User {id: $user_id})
MATCH (conn:Connection)
WHERE (conn.sender_id = user.id OR conn.receiver_id = user.id)
AND conn.is_match = true
AND conn.is_deleted = false
RETURN count(conn) as matches_count

-- Počet všech viditelných uživatelů (reference)
MATCH (other:User)
MATCH (other)-[:HAS_ACCOUNT]->(account)
WHERE other.id <> $user_id
AND account.is_deleted = false
RETURN count(other) as visible_profiles
```

---

## FÁZE 4️⃣ - VYHLEDÁVÁNÍ PROFILŮ (PRIORITA: VELMI VYSOKÁ)

### Požadavky ze zadání (2.5)
- Seznam profilů s filtrováním
- Filtrování: zájmy, nerd level, technologie
- Tlačítka: "Zaujalo mě" a "Přeskočit"

### 4.1 GET `/discover` - Vyhledávání profilů

**Cypher:**
```cypher
MATCH (user:User {id: $user_id})
MATCH (other:User)-[:HAS_PROFILE]->(profile:Profile)
MATCH (other)-[:HAS_ACCOUNT]->(account)
WHERE other.id <> user.id
AND account.is_deleted = false

-- Filtrování
AND profile.nerd_level >= $min_nerd
AND profile.nerd_level <= $max_nerd
AND (profile)-[:INTERESTED_IN]->(interest:InterestCategory)
AND (interest.name IN $interests OR size($interests) = 0)

-- Vyloučení už ohodnocených
OPTIONAL MATCH (existing:Connection)
WHERE (existing.sender_id = user.id AND existing.receiver_id = other.id)
WHERE existing.is_deleted = false
WITH profile, other, existing
WHERE existing IS NULL

RETURN profile, other
LIMIT 1
```

### 4.2 POST `/discover/like` - Označit profil jako "Zaujalo mě"

**Akce:**
1. Najít existující Connection (obě strany)
2. Pokud existuje opačný like → is_match = true
3. Jinak vytvořit nový Connection s is_match = false

**Cypher:**
```cypher
CREATE (conn:Connection {
  id: apoc.create.uuid(),
  created_at: datetime(),
  is_match: false,
  is_deleted: false
})

MATCH (sender:User {id: $sender_id})
MATCH (receiver:User {id: $receiver_id})
CREATE (sender)-[:INITIATED_CONNECTION]->(conn)<-[:RECEIVED_CONNECTION]-(receiver)

-- Kontrola na oboustranný like
MATCH (conn2:Connection)
WHERE conn2.sender_id = $receiver_id
AND conn2.receiver_id = $sender_id
AND conn2.is_deleted = false
SET conn.is_match = true
SET conn2.is_match = true
RETURN conn
```

### 4.3 POST `/discover/skip` - Přeskočit profil

Zatím nebudeme nic zaznamenávat (u dalšího refresh se zobrazí jiný profil).

---

## FÁZE 5️⃣ - KONTAKTY (PRIORITA: STŘEDNÍ)

### Požadavky ze zadání (2.6)
- Seznam uživatelů s oboustranným + jednostranným zájmem
- Datum navázání
- Možnost odebrat kontakt

### 5.1 GET `/contacts` - Seznam kontaktů

**Cypher:**
```cypher
MATCH (user:User {id: $user_id})
MATCH (conn:Connection)
WHERE (conn.sender_id = user.id OR conn.receiver_id = user.id)
AND conn.is_deleted = false

OPTIONAL MATCH (other_sender:User {id: conn.sender_id})
OPTIONAL MATCH (other_receiver:User {id: conn.receiver_id})
WITH conn, 
     CASE WHEN other_sender.id = $user_id THEN other_receiver ELSE other_sender END as other_user

MATCH (other_user)-[:HAS_PROFILE]->(profile:Profile)
RETURN conn, other_user, profile
ORDER BY conn.is_match DESC, conn.created_at DESC
```

### 5.2 DELETE `/contacts/<connection_id>` - Odebrat kontakt

**Cypher:**
```cypher
MATCH (conn:Connection {id: $connection_id})
SET conn.is_deleted = true
SET conn.deleted_at = datetime()
RETURN conn
```

---

## FÁZE 6️⃣ - NAVIGACE & LAYOUT

### 6.1 Společné komponenty
- Navbar: Přehled, Objevuj, Kontakty, Profil, Odhlášení
- Footer: Copyright
- Flash messages: Chyby, úspěchy

### 6.2 Responsive design
- Bootstrap 5
- Mobile-friendly

---

# 📁 Projektová struktura (AKTUÁLNÍ)

```
SZZVP/
├── code/
│   ├── app.py                      # ✅ Flask hlavní aplikace + routing
│   ├── config.py                   # ✅ Konfigurace (SECRET_KEY, SESSION, Neo4j)
│   ├── requirements.txt            # ✅ Závislosti (Flask, py2neo, bcrypt...)
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py             # ✅ Neo4j connection, init schema + indexy
│   │   ├── user.py                 # ✅ User operace (create, verify, delete)
│   │   ├── profile.py              # ✅ Profile operace (create, edit, get)
│   │   └── connection.py           # ✅ Connection operace (like, match, delete)
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── validators.py           # ✅ Validace (email, heslo, nickname, bio)
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py                 # ✅ /register, /login, /logout, /delete-account
│   │   ├── profile.py              # ✅ /profile, /profile/setup, /profile/edit
│   │   ├── discover.py             # ✅ /discover, /discover/like/<id>, /discover/skip/<id>
│   │   └── contacts.py             # ✅ /contacts, /contacts/<id>/remove
│   │
│   ├── templates/
│   │   ├── base.html               # ✅ Navbar (Přehled, Objevuj, Kontakty, Profil)
│   │   ├── dashboard.html          # ✅ Statistiky (kontakty, matche, profily)
│   │   ├── 404.html                # ✅ Chyba - stránka nenalezena
│   │   ├── 500.html                # ✅ Chyba - server error
│   │   │
│   │   ├── auth/
│   │   │   ├── login.html          # ✅ Přihlášení formulář
│   │   │   ├── register.html       # ✅ Registrace formulář
│   │   │   └── delete-account.html # ✅ Potvrzení smazání účtu
│   │   │
│   │   ├── profile/
│   │   │   ├── view.html           # ✅ Zobrazení profilu
│   │   │   ├── setup.html          # ✅ Vytvoření profilu (1. přihlášení)
│   │   │   └── edit.html           # ✅ Editace profilu
│   │   │
│   │   ├── discover/
│   │   │   └── index.html          # ✅ Procházení profilů s filtrováním
│   │   │
│   │   └── contacts/
│   │       └── list.html           # ✅ Seznam kontaktů (matche + jednostranné)
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css           # ✅ Bootstrap 5 + vlastní styly
│   │   └── js/
│   │       └── main.js             # ✅ Validace, interakce
│   │
│   └── [ostatní Python soubory]
│
├── Dockerfile                      # ✅ Python 3.10-slim kontejner
├── docker-compose.yml              # ✅ Flask + Neo4j orchestrace
├── DEVELOPMENT.md                  # ✅ Tato dokumentace
├── README.md                       # ✅ Quick start průvodce
├── ARCHITECTURE.md                 # ✅ Detailní architektura
├── test_users.txt                  # ✅ Seznam testovacích účtů
└── [ostatní kořenové soubory]
```

### Podrobný popis souborů:

**app.py**
- Inicializace Flask aplikace
- Registrace blueprintů (auth, profile, discover, contacts)
- Middleware pro session timeout (5 minut)
- Error handlery (404, 500)
- Dashboard route s Neo4j statistikami

**config.py**
- SECRET_KEY pro session
- PERMANENT_SESSION_LIFETIME = 5 minut
- Neo4j URI, user, password z ENV
- MAX_CONTENT_LENGTH = 16 MB

**models/user.py**
- `User.hash_password()` - bcrypt hashing
- `User.verify_password()` - ověření hesla
- `User.create()` - vytvoření User + Account s vztahem
- `User.get_by_email()` - přihlášení
- `User.delete()` - soft delete (is_deleted = true)

**models/profile.py**
- `Profile.create()` - vytvoření profilu
- `Profile.get_by_user_id()` - zobrazení profilu
- `Profile.update()` - editace včetně zájmů/technologií
- `Profile.get_all_interests()` - seznam dostupných zájmů
- `Profile.get_all_technologies()` - seznam dostupných technologií

**models/connection.py**
- `Connection.create()` - vytvoření Like s automatickou match detekcí
- `Connection.exists()` - kontrola existence konekce
- `Connection.delete()` - soft delete konekce
- `Connection.get_all_for_user()` - všechny konekce uživatele

**routes/auth.py**
- POST /register - registrace s validací
- POST /login - přihlášení, kontrola profilu, redirect na setup
- GET /logout - odhlášení
- GET/POST /delete-account - smazání s potvrzením

**routes/profile.py**
- GET/POST /profile/setup - vytvoření profilu na prvním loginu
- GET /profile - zobrazení svého profilu
- GET/POST /profile/edit - editace profilu

**routes/discover.py**
- GET /discover - procházení profilů s filtrováním
- POST /discover/like/<id> - like profil
- POST /discover/skip/<id> - skip profil

**routes/contacts.py**
- GET /contacts - seznam všech kontaktů
- POST /contacts/<id>/remove - odebrání kontaktu

---

# 🔧 Závislosti (requirements.txt) - FINÁLNÍ

```
Flask==3.0.0                        # Web framework
py2neo==2021.2.4                    # Neo4j driver
bcrypt==4.1.0                       # Password hashing (bcrypt)
python-dotenv==1.0.0                # ENV variables (.env)
Werkzeug==3.0.1                     # WSGI utilities
```

### Poznámky k závislostem:
- **Flask-Session**: ❌ Odstraněno (nekompatibilní s Flask 3.0, používáme Flask built-in session)
- **email-validator**: ❌ Odstraněno (nahrazeno regex validací)
- **neo4j official driver**: ❌ Odstraněno (py2neo pokrývá všechny potřeby)

### Důvody:
- Flask 3.0.0 má built-in session management → žádný Flask-Session potřebný
- Regex email validace je jednoduchá a bez dalších závislostí
- py2neo v2021.2.4 je stabilní a má všechny potřebné funkce
- bcrypt 4.1.0 je nejnovější a zabezpečený

---

# 🚀 Příští kroky (Volitelné vylepšení)

1. **Phase 6:** UI/UX vylepšení - lepší design a animace
2. **Bonus:** Notifikace pro nové matche
3. **Bonus:** Vyhledávání profilů podle přezdívky
4. **Bonus:** Preference soukromí (make profile private)
5. **Bonus:** Historie aktivit a statistik

---

# ✅ Checklist - Co všechno musí fungovat

## Implementováno a testováno ✅

- [x] Registrace s validací hesla (8+ znaků, velká/malá písmena, číslo, speciální znak)
- [x] Přihlášení se session management (Flask built-in)
- [x] Auto-logout po 5 minutách nečinnosti
- [x] Odhlášení
- [x] Smazání účtu + všech dat (soft delete)
- [x] Vytvoření profilu na prvním přihlášení
- [x] Editace profilu (přezdívka, bio, nerd level, zájmy, technologie)
- [x] Validace profilu (3-50 znaků pro přezdívku, max 500 znaků bio)
- [x] Dashboard se statistikami (kontakty, matche, dostupné profily)
- [x] Vyhledávání s filtrováním (nerd level min/max, zájmy)
- [x] Like funkce - vytváření connections
- [x] Skip funkce - přechod na další profil
- [x] Automatická detekce matchů (oboustranný like = is_match: true)
- [x] Kontakty - zobrazení oboustranných matchů
- [x] Kontakty - zobrazení jednostranných zájmů
- [x] Odebrání kontaktu (soft delete)
- [x] Responsive UI (Bootstrap 5)
- [x] Chybové zprávy (Flash messages)
- [x] Error stránky (404, 500)
- [x] Neo4j databáze s indexy
- [x] Docker container s health checks
- [x] Konfigurace (SECRET_KEY, timeout, Neo4j parametry)

## Volitelné vylepšení (Not MVP)

- [ ] Dark mode
- [ ] Notifikace pro nové matche
- [ ] Real-time updaty (WebSockets)
- [ ] Profilové obrázky
- [ ] Mapování podle lokace
- [ ] Přesný match algoritmus (na základě zájmů)
- [ ] Admin panel
- [ ] Reporting/Blocking uživatelů

---

# 📊 Git Commits

```
6327c3d - Update test users list with functional test accounts
90f264d - Implement Phase 4 & 5: Discovery and Contacts
b615a00 - Implement Phase 2: User Profile (Create/View/Edit)
8ce1c19 - Fáze 1: Struktura projektu + Autentizace
d7a8650 - Initial project setup
```

