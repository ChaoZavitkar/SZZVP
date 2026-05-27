# 🔥 NerdMatch - Seznamka pro Nerdy

Webová aplikace pro seznamování se zaměřením na lidi se zájmem o technologie, vědu, hry, sci-fi, fantasy a matematiku.

Vytvořeno s **Flask** (Python), **Neo4j** (grafová databází) a **Docker**.

---

## 🎯 Funkcionality

- ✅ **Autentizace** - Registrace, přihlášení, odhlášení, smazání účtu
- ✅ **Profily** - Vytvoření a editace profilu (přezdívka, bio, nerd level, zájmy, technologie)
- ✅ **Vyhledávání** - Procházení dostupných profilů s filtrováním (nerd level, zájmy)
- ✅ **Matchování** - "Líbí se mi"功能, automatická detekce vzájemného zájmu
- ✅ **Kontakty** - Seznam matchů a jednostranných zájmů
- ✅ **Dashboard** - Statistiky (počet kontaktů, matchů, dostupných profilů)

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

V databázi jsou připravené účty:

| Email | Heslo | Profil | Nerd Level | Zájmy |
|-------|-------|--------|-----------|-------|
| `alice@example.com` | `Alice123!@` | Alice | 8/10 | programování, sci-fi |
| `bob@example.com` | `Bob123!@` | Bob | 6/10 | videohry, matematika |

**Status:** Alice ❤️ Bob (Alice si lajkla Boba, ale Bob se ještě nepřihlásil)

### Testovací scénář

1. **Přihlášení:**
   ```
   Email: alice@example.com
   Heslo: Alice123!@
   ```

2. **Procházení aplikace:**
   - Dashboard: Statistiky
   - Profil: Zobrazení Alice s bio a zájmy
   - Objevuj: Procházení dostupných profilů (Boba už nevidí, protože si ho lajkla)
   - Kontakty: Vidí "Tvůj zájem" na Bob

3. **Vytvoření nového účtu:**
   - Registrace → Automaticky na vytvoření profilu
   - Vyplnění údajů → Dashboard

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
- Počet všech kontaktů
- Počet vzájemných matchů 🔥
- Počet dostupných profilů

**Objevuj (`/discover`)**
- Filtrování podle nerd levelu
- Filtrování podle zájmů
- Like/Skip profilu
- Automatická detekce matchů

**Profil (`/profile`)**
- Zobrazení profilu
- Editace (přezdívka, bio, nerd level)
- Výběr zájmů (min 1)
- Výběr technologií (volitelné)

**Kontakty (`/contacts`)**
- 🔥 Vzájemné matche
- 💭 Jednostranné zájmy
- Možnost odstranit kontakt

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

## 📚 Dokumentace

- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Detailní plán, datový model, API endpointy
- **[test_users.txt](test_users.txt)** - Lista všech testovacích účtů
- Kód je dokumentován in-line v Python souborech

---

## 🔗 Technologie

- **Backend:** Flask 3.0.0 (Python 3.10)
- **Databáze:** Neo4j (grafová databáze)
- **Driver:** py2neo 2021.2.4
- **Hešování:** bcrypt 4.1.0
- **Frontend:** Bootstrap 5, Jinja2
- **Kontejnerizace:** Docker & Docker Compose

---

## ✅ Co je hotovo (MVP)

- ✅ Autentizace (5/5 kroků)
- ✅ Profil uživatele (vytvoření, zobrazení, editace)
- ✅ Dashboard (statistiky)
- ✅ Vyhledávání (procházení, filtrování)
- ✅ Matchování (like, automatická detekce matchů)
- ✅ Kontakty (seznam matchů a zájmů)

## 📝 Zbývá (volitelné)

- Phase 6: UI/UX vylepšení (je funkční, ale design by mohl být lepší)
- Notifikace pro nové matche
- Vyhledávání podle jména
- Preference soukromí profilu
- Profilové fotografie

---

## 👨‍💻 Autor a stav

**Projekt:** NerdMatch - Seznamka pro Nerdy  
**Status:** MVP hotov, připraveno pro státnice  
**Datum:** 27.5.2026

Vytvořeno pro **SZZVP státnickou zkoušku** s podporou AI asistenta.

---

## 📄 Licence

Projekt je určen pro vzdělávací účely (státnické zkoušky SZZVP).
