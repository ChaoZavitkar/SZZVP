# 🚀 DEVELOPMENT PLAN - NerdMatch Aplikace

## 📋 Přehled projektu

**Aplikace:** NerdMatch - Seznamka/sociální síť pro nerdy  
**Tech Stack:** Flask (Python) + Neo4j (grafová DB) + Docker  
**Cíl:** Webová aplikace pro seznamování se zaměřením na lidi se zájmem o technologie, vědu, hry, sci-fi, fantasy, matematiku, komiksy atd.

**Zadání:** [Zadání - Vývoj webové aplikace.pdf](Zadání%20-%20Vývoj%20webové%20aplikace.pdf)

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

# 📁 Projektová struktura

```
code/
├── app.py                          # Flask aplikace (init + routing)
├── config.py                       # Konfigurace (SECRET_KEY, SESSION atd.)
├── requirements.txt                # Závislosti
│
├── models/                         # Logika pro Neo4j
│   ├── __init__.py
│   ├── database.py                # Neo4j connection, init schema
│   ├── user.py                    # User operace (registrace, login)
│   ├── profile.py                 # Profile operace
│   ├── interest.py                # Zájmy a technologie
│   └── connection.py              # Connections (likes, matches)
│
├── utils/                         # Utility funkce
│   ├── __init__.py
│   ├── validators.py              # Validace emailu, hesla
│   ├── decorators.py              # @require_login, @timeout
│   └── constants.py               # INTERESTS, TECHNOLOGIES
│
├── routes/                        # Flask blueprinty
│   ├── __init__.py
│   ├── auth.py                    # /register, /login, /logout
│   ├── dashboard.py               # /
│   ├── profile.py                 # /profile, /profile/edit
│   ├── discover.py                # /discover, /like, /skip
│   └── contacts.py                # /contacts
│
├── templates/
│   ├── base.html                  # Navbar, footer, base
│   ├── auth/login.html
│   ├── auth/register.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── discover.html
│   └── contacts.html
│
├── static/
│   ├── css/style.css              # Vlastní styly
│   └── js/main.js                 # Validace, interakce
│
└── tests/                         # Unit testy (volitelné)
    ├── test_auth.py
    └── test_models.py
```

---

# 🔧 Nové závislosti (requirements.txt)

```
Flask==3.0.0
Flask-Session==0.5.0               # Session management
py2neo==2021.2.4                    # Neo4j driver
bcrypt==4.1.0                       # Password hashing
email-validator==2.1.0             # Email validation
python-dotenv==1.0.0               # ENV variables
neo4j==5.13.0                       # Neo4j official driver (alternativa)
```

---

# 🚀 Příští kroky

1. **DNES:** Vytvoříme strukturu projektu a inicializaci Neo4j
2. **TÝDEN 1:** Implementujeme Fázi 1-3 (Autentizace, Profil, Dashboard)
3. **TÝDEN 2:** Implementujeme Fázi 4-5 (Discover, Contacts)
4. **TÝDEN 3:** Styling, testování, dokumentace

---

# ✅ Checklist - Co všechno musí fungovat

- [ ] Registrace s validací hesla
- [ ] Přihlášení se session management
- [ ] Auto-logout po 5 minutách
- [ ] Odhlášení
- [ ] Smazání účtu + všech dat
- [ ] Editace profilu (všechny pole)
- [ ] Dashboard se statistikami
- [ ] Vyhledávání s filtrováním
- [ ] Like/Dislike funk
- [ ] Detekce matchů
- [ ] Kontakty - oboustranné + jednostranné
- [ ] Smazání kontaktu
- [ ] Responsive UI
- [ ] Chybové zprávy (flashy)
- [ ] README dokumentace

