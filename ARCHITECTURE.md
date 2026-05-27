# 🏗️ Architecture - NerdMatch

Dokumentace architektuры a designu NerdMatch aplikace.

---

## 📐 Přehled Systému

```
┌─────────────────────────────────────────────────────────────────┐
│                        Browser/Client                           │
│  (HTML + CSS + JavaScript - Vanilla, no frameworks)             │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/REST
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    Flask Web Server                             │
│  (Python 3.10)                                                  │
│  ├─ Routes (Auth, Profile, Discover, Contacts)                 │
│  ├─ Session Management (5-min timeout)                         │
│  └─ Input Validation & Middleware                              │
└────────────────────────┬────────────────────────────────────────┘
                         │ Cypher/Bolt
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                  Neo4j Graph Database                           │
│  (Nodes: User, Account, Profile, InterestCategory, Technology) │
│  (Relationships: HAS_ACCOUNT, HAS_PROFILE, LIKES, SKIP, etc.)  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📂 Projektová Struktura

```
SZZVP/
├── README.md                    # Hlavní dokumentace
├── INSTALLATION.md              # Setup návod
├── ARCHITECTURE.md              # Tento soubor
├── docker-compose.yml           # Docker orchestrace
├── Dockerfile                   # Flask container
│
├── code/
│   ├── app.py                   # Flask hlavní aplikace
│   ├── config.py                # Konfigurace (Neo4j, session, atd.)
│   ├── requirements.txt         # Python dependencies
│   ├── create_test_profiles.py  # Seed script pro 20 test profilů
│   │
│   ├── models/                  # Datový model & logika
│   │   ├── database.py          # Neo4j connection + init
│   │   ├── user.py              # User operace (register, login, etc.)
│   │   ├── profile.py           # Profile CRUD + custom tags
│   │   └── connection.py        # Like/Match/Skip operace
│   │
│   ├── routes/                  # Flask blueprints (API endpointy)
│   │   ├── auth.py              # /register, /login, /logout, /delete-account
│   │   ├── profile.py           # /profile, /profile/setup, /profile/edit
│   │   ├── discover.py          # /discover, /discover/like, /discover/skip
│   │   └── contacts.py          # /contacts (matche, zájmy, obdivovatelé)
│   │
│   ├── utils/
│   │   └── validators.py        # Input validation (email, heslo, text)
│   │
│   ├── templates/               # Jinja2 HTML šablony
│   │   ├── base.html            # Base template (navbar, footer)
│   │   ├── index.html           # Dashboard/home
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── profile/
│   │   │   ├── view.html
│   │   │   ├── setup.html
│   │   │   └── edit.html
│   │   ├── discover/
│   │   │   └── index.html       # Tinder-style swipe UI
│   │   └── contacts/
│   │       └── list.html        # Matche, zájmy, obdivovatelé
│   │
│   └── static/
│       ├── css/
│       │   └── style.css        # Unified dark theme (1100+ lines)
│       │       - Navbar styling
│       │       - Form controls
│       │       - Tinder card animations
│       │       - Responsive grid layout
│       │       - Match notifications
│       │       - Empty states
│       │
│       └── js/
│           ├── main.js          # Global utilities
│           ├── tinder-swipe.js  # Swipe gesture handling (mouse, touch, keyboard)
│           └── custom-tags.js   # Autocomplete UI pro custom tags
│
├── Template/                    # Original wireframes & screenshots
├── requirements.txt             # Python dependencies (root level)
└── Dockerfile                   # Docker build config
```

---

## 🗄️ Datový Model (Neo4j)

### Uzly

#### User
```cypher
User {
  id: UUID,
  email: String,
  password_hash: String,
  created_at: DateTime
}
```

#### Account
```cypher
Account {
  is_deleted: Boolean,
  last_login: DateTime
}
```

#### Profile
```cypher
Profile {
  nickname: String,
  bio: String,
  nerd_level: Integer (0-10),
  created_at: DateTime,
  updated_at: DateTime
}
```

#### InterestCategory
```cypher
InterestCategory {
  name: String,
  type: Enum("SYSTEM" | "USER"),
  created_by: UUID,  # only for USER tags
  created_at: DateTime
}
```

#### Technology
```cypher
Technology {
  name: String,
  created_by: UUID,  # only for USER tags
  created_at: DateTime
}
```

### Vztahy (Relationships)

```cypher
User -[:HAS_ACCOUNT]-> Account
User -[:HAS_PROFILE]-> Profile
Profile -[:INTERESTED_IN]-> InterestCategory
Profile -[:LIKES_TECHNOLOGY]-> Technology

# Matchování
User -[:LIKES {created_at: DateTime}]-> User

# Skip s timeout
User -[:SKIP {created_at: DateTime}]-> User
```

### Příklady Queries

**Vytvoření profilu s custom tagy:**
```cypher
MERGE (u:User {id: $user_id})
MERGE (a:Account) ON CREATE SET a.is_deleted = false
CREATE (u)-[:HAS_ACCOUNT]->(a)
CREATE (p:Profile {nickname: $nickname, bio: $bio, nerd_level: $nerd_level, created_at: datetime()})
CREATE (u)-[:HAS_PROFILE]->(p)

# Vytvoř systémové zájmy
WITH p
MATCH (i:InterestCategory {name: $interest1, type: "SYSTEM"})
CREATE (p)-[:INTERESTED_IN]->(i)
```

**Vyhledání dostupných profilů (s filtrováním a skip timeout):**
```cypher
MATCH (user:User {id: $user_id})
MATCH (other:User)-[:HAS_PROFILE]->(profile:Profile)
WHERE other.id <> user.id
  AND NOT (user)-[:LIKES]->(other)
  AND NOT (
    EXISTS {
      MATCH (user)-[skip:SKIP]->(other)
      WHERE skip.created_at > datetime() - duration({hours: 4})
    }
  )
  AND profile.nerd_level >= $min_nerd
  AND profile.nerd_level <= $max_nerd

OPTIONAL MATCH (profile)-[:INTERESTED_IN]->(interest:InterestCategory)
WHERE interest.name IN $interests

RETURN other.id, profile.nickname, profile.bio, profile.nerd_level, 
       collect(DISTINCT interest.name) as interests
```

**Detekce matche:**
```cypher
MATCH (u1:User {id: $user_id})-[:LIKES]->(u2:User)
MATCH (u2)-[:LIKES]->(u1)
RETURN true
```

---

## 🔐 Bezpečnost

### Implementováno

1. **Autentizace:**
   - bcrypt hashing (12 koly)
   - Session management s timeoutem
   - Soft delete (GDPR)

2. **Validace:**
   - Email format + existence check
   - Heslo: min 8 chars, uppercase, number, special char
   - Text fields: max length, XSS prevention

3. **Databáze:**
   - Parametrizované Cypher dotazy (bez injection)
   - Indexy na klíčová pole

### Doporučeno pro produkci

- [ ] HTTPS (SSL/TLS)
- [ ] CSRF protection (Flask-WTF)
- [ ] Rate limiting (flask-limiter)
- [ ] Audit logging
- [ ] API key management
- [ ] Input sanitization (bleach library)
- [ ] Database encryption

---

## 🎨 Frontend Architektura

### CSS Struktura

Všechny styly jsou v jednom souboru: `code/static/css/style.css` (1100+ řádků)

**Sekce:**
1. **CSS Variables** - Barvy, shadows, spacing
2. **Reset & Typography** - Font, heading, paragraph styles
3. **Components** - Navbar, buttons, forms, cards, badges
4. **Discover UI** - Grid layout, tinder card, swipe animations
5. **Dashboard** - Stat cards, metrics
6. **Responsive Media Queries** - 1024px, 768px, 480px breakpoints

**Color Palette:**
```css
--primary-color: #ff6b6b      /* Červená */
--success-color: #51cf66      /* Zelená */
--nerd-purple: #7c3aed        /* Purpurová */
--dark-bg: #1a1a2e            /* Temný background */
--darker-bg: #0f3460          /* Ještě temněji */
--card-bg: #16213e            /* Card background */
```

### JavaScript

**vanilla JS** (bez frameworků - jQuery/React/Vue)

**Soubory:**
- `main.js` - Global utilities, helper functions
- `tinder-swipe.js` - Swipe gesture handling (Class: TinderSwipe)
- `custom-tags.js` - Autocomplete pro custom tags (Class: CustomTagsInput)

**Klíčové funkcionality:**
- Touch events: `touchstart`, `touchmove`, `touchend`
- Mouse events: `mousedown`, `mousemove`, `mouseup`
- Keyboard events: Arrow keys, Escape
- CSS animations (translateX, rotate, opacity)

### Templating (Jinja2)

**Base layout:**
```html
{% extends "base.html" %}
{% block title %}...{% endblock %}
{% block content %}...{% endblock %}
```

**Template helpers:**
```html
{{ user.email }}                    # Proměnné
{% for item in items %}...{% endfor %}  # Loops
{% if condition %}...{% endif %}    # Conditions
{{ url_for('route_name') }}         # URL generation
```

---

## 🚀 API Endpointy

### Autentizace

```
GET  /login              # Login form
POST /login              # Login submit
GET  /register           # Register form
POST /register           # Register submit
GET  /logout             # Logout
POST /delete-account     # Delete account
```

### Profil

```
GET  /profile            # View own profile
GET  /profile/setup      # Setup wizard (nový user)
POST /profile/setup      # Setup submit
GET  /profile/edit       # Edit form
POST /profile/edit       # Edit submit
```

### Discover

```
GET  /discover           # Main discover page
POST /discover/like/:id  # Like a profile
POST /discover/skip/:id  # Skip a profile
```

### Kontakty

```
GET  /contacts           # View all contacts/matches
GET  /contacts/:id       # View specific contact
POST /contacts/:id/delete # Remove contact
```

### Dashboard

```
GET  /                   # Dashboard/home
```

---

## 🔄 Datový Tok

### Registration Flow
```
1. User fills /register form
2. Backend validates input (email, password, etc.)
3. Create User + Account nodes
4. Redirect to /profile/setup
5. User fills profile details (nickname, bio, nerd_level, interests, techs)
6. Create Profile + relationships
7. Create custom tags if new (MERGE with type="USER")
8. Redirect to dashboard
```

### Like Flow
```
1. User on /discover sees profile
2. Click like or drag right
3. Frontend calls POST /discover/like/:id
4. Backend creates User-[:LIKES]->User relationship
5. Check if mutual (is_mutual)
6. Return success + match notification
7. Fetch next profile
8. Reload page with new profile
```

### Skip Flow
```
1. User clicks skip or drag left
2. Frontend calls POST /discover/skip/:id
3. Backend creates User-[:SKIP {created_at}]->User relationship
4. Set timeout duration (config: SKIP_TIMEOUT_HOURS = 4)
5. Return success
6. Fetch next profile (skip already-skipped in query)
```

### Discover Filter Flow
```
1. User on /discover adjusts filters (nerd_level range, interests)
2. Form submits with GET params
3. Backend queries available profiles with:
   - Nerd level range filter
   - Interest filter (AND logic - must have ALL selected)
   - Skip timeout (not skipped in last 4 hours)
   - Not already liked
4. Return filtered profiles
```

---

## 📊 Custom Tags Architecture

### Purpose
Allow users to create their own interests and technologies (like LinkedIn).

### How it Works

**Storage:**
- Same nodes as system tags (InterestCategory, Technology)
- Additional field: `type: "USER"` and `created_by: UUID`

**Display:**
- System only (Discover filters): Show only 10 SYSTEM tags
- Full list (Profile edit): Show 10 SYSTEM + 5 USER (most recent) tags
- Autocomplete: All tags are searchable, but limited for UI clarity

**Creation:**
- User types in autocomplete field
- If tag doesn't exist, show "Create new: XXX" option
- Backend calls `create_interest_if_not_exists()` or `create_technology_if_not_exists()`
- Uses MERGE operation: Create only if doesn't exist

**Frontend:**
- Autocomplete class `CustomTagsInput` handles:
  - Input listening
  - Suggestion filtering
  - Tag removal (click X on badge)
  - Custom tag creation (Enter key)
  - Hidden input population (for form submission)

---

## 🧪 Testing

### Manual Test Scenarios

1. **Full Registration & Profile Setup**
   - Register new account
   - Create profile with custom tags
   - Verify tags appear for other users

2. **Discover & Matching**
   - Login as user 1
   - Discover 5 profiles
   - Like 2, skip 3
   - Logout

3. **Check Mutual Match**
   - Login as user 2 (who was liked by user 1)
   - Go to contacts
   - See that user 1 is in "Your interests"
   - Like user 1 back
   - Verify match appears for both

4. **Skip Timeout**
   - Skip a profile
   - Wait 4+ hours (or modify time in tests)
   - Verify profile appears again

### Unit Tests
- Would go in `tests/` directory
- Use pytest + Neo4j test database
- Test models (user, profile, connection)
- Test routes (auth, discover, contacts)

---

## 🚀 Deployment

### Docker Production Setup

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

**Changes for production:**
- Set `FLASK_ENV=production`
- Use stronger `SECRET_KEY`
- Enable HTTPS
- Use managed Neo4j instance (Neo4j Aura)
- Add reverse proxy (nginx)
- Enable monitoring (Prometheus, Grafana)

### Environment Variables

```
# Neo4j
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=adminpass

# Flask
FLASK_ENV=production
SECRET_KEY=<generate-strong-key>
SESSION_TIMEOUT_MINUTES=5

# Application
SKIP_TIMEOUT_HOURS=4
MAX_BIO_LENGTH=500
MAX_TAGS_PER_PROFILE=20
```

---

## 📚 Jak Přispívat

### Přidání Nové Features

1. **Vytvoř branch:** `git checkout -b feature/my-feature`
2. **Implementuj:** Dodržuj stávající patterns
3. **Test:** Ověř v /discover a /contacts
4. **Commit:** `git commit -m "Add: my feature description"`
5. **Push:** `git push origin feature/my-feature`

### Code Style

- **Python:** PEP 8 (4 spaces, snake_case)
- **JavaScript:** ES6+, vanilla (no jQuery), camelCase
- **HTML:** Semantic HTML, Jinja2 for templates
- **CSS:** CSS variables for colors, mobile-first responsive

### Dokumentace

- Update `README.md` for user-facing changes
- Update `ARCHITECTURE.md` for technical changes
- Add inline comments for complex logic

---

## 🔗 Odkazy

- **README.md** - Uživatelská dokumentace a features
- **INSTALLATION.md** - Setup návod
- **code/models/** - Model source code
- **code/routes/** - Route implementations
- **code/static/css/style.css** - All styling

---

**Poslední aktualizace:** 27.5.2026
