# 🔥 Matchomat - Online Seznamka

Jednoduchá webová aplikace sociální sítě pro hledání "matchů" mezi uživateli, inspirovaná online seznamkami (Tinder). Vytvořeno s **Flask** a **Neo4j** grafovou databází.

## 🎯 Co je to Matchomat?

Matchomat vám umožní:
- 👤 Prohlédnout si dostupné profily
- 👍 Dávat si "like" nebo "dislike" na profily
- 🔥 Vidět, s kým máte vzájemný interesse (match)
- 📊 Sledovat statistiky vašeho profilu

---

## 🏗️ Architektura

Pro detailní popis architektury, datového modelu, API a pracovního toku viz: **[ARCHITECTURE.md](ARCHITECTURE.md)**

**Krátký přehled:**
```
Browser → Flask (Python) → Neo4j (Grafová DB)
                ↓
          Jinja2 Templates
```

---

## 🚀 Spuštění aplikace

### Požadavky
- Docker & Docker Compose
- Port 5000 (Flask) a 7687 (Neo4j) musí být volné

### Kroky

1. **Klonuj nebo otevři projekt**
```bash
cd SZZVP
```

2. **Spusť Docker Compose**
```bash
docker-compose up --build
```

Při prvním spuštění si Docker stáhne obrazy a postaví kontejnery. Počkej 10-15 sekund, až se Neo4j inicializuje.

3. **Otevři aplikaci v prohlížeči**
```
http://localhost:5000
```

4. _(Volitelně)_ Otevři Neo4j Browser
```
http://localhost:7474
Uživatel: neo4j
Heslo: adminpass
```

---

## 📖 Jak používat aplikaci

### Stránka **Domů** (`/home`)
- Zobrazí tvůj profil (jméno, věk, záliby)
- Statistiky: kolik máš matchů a kolik profilů ti zbývá projít

### Stránka **Hledej** (`/search`)
- Zobrazí náhodný dostupný profil
- Tlačítko **Like** → profil se ti líbí (vytvoří vztah LIKES)
- Tlačítko **Dislike** → profil se ti nelíbí (vytvoří vztah DISLIKES)

### Stránka **Shody** (`/matches`)
- Zobrazí seznam osob, s kterými máš **vzájemný like**
- To jsou tvoje "matche" 🔥

---

## 👥 Testovací uživatelé

Aplikace obsahuje 5 testovacích uživatelů. Přihlášen je defaultně **Pepa** (lze změnit v `code/app.py`):

| Jméno | Věk | Záliby |
|-------|-----|--------|
| Pepa | 34 | programming, running |
| Jana | 30 | cats, running |
| Michal | 38 | partying, cats |
| Alena | 32 | kids, cats |
| Richard | 33 | partying, cats |

**Počáteční state:**
- Pepa & Jana si dali vzájemný like → mají match ✓
- Ostatní vztahy jsou nastaveny pro testování

---

## 📂 Struktura projektů

```
SZZVP/
├── README.md                  ← Toto (návod na použití)
├── ARCHITECTURE.md            ← Detailní architektura
├── docker-compose.yml         ← Orchestrace služeb
├── Dockerfile                 ← Obraz pro Flask aplikaci
│
└── code/                      ← Hlavní aplikační kód
    ├── app.py                 ← Flask aplikace (routy, logika)
    ├── requirements.txt       ← Python závislosti
    │
    └── templates/             ← HTML šablony
        ├── template.html      ← Základní layout
        ├── home.html          ← Domovská stránka
        ├── search.html        ← Vyhledávání profilů
        └── matches.html       ← Vzájemné matche
```

---

## 🔧 Vývoj a modifikace

### Změna přihlášeného uživatele
V `code/app.py` (řádek 9):
```python
logged_user = "Pepa"  # ← Změní na své jméno
```

### Přidání nového uživatele
V `code/app.py`, funkce `mock_data()`:
```python
새_user = Node("Person", name="Jméno", age=25, hobbies=["zálib1", "zálib2"])
users.append(nový_user)
```

### Modifikace šablon
Soubory v `code/templates/` se automaticky znovu načtou (díky `debug=True` a `volumes` v docker-compose).

### Kontrola logu
```bash
docker-compose logs flask
```

---

## 🛑 Zastavení aplikace

```bash
docker-compose down
```

Zastaví a odebere kontejnery. Data v Neo4j budou vymazána (jsou volána `mock_data()` při startu).

---

## 🔐 Bezpečnostní poznámky

⚠️ **Toto je učební projekt!**

Obsahuje bezpečnostní rizika:
- ❌ Uživatel je hardkodován (bez AuthN)
- ❌ SQL/Cypher Injection vulnerabilita (string interpolation)
- ❌ Bez CSRF ochrany
- ❌ Bez validace vstupů

**V produkčním kódu:**
- ✅ Implementovat AuthN/AuthZ
- ✅ Parametrizované Cypher dotazy
- ✅ CSRF tokeny
- ✅ Input validation
- ✅ HTTPS

---

## 🐛 Troubleshooting

### Port 5000 je obsazen
```bash
docker-compose down  # Zastavit všechny kontejnery
```

### Neo4j se nespustil
Počkej 15-20 sekund a spusť znovu:
```bash
docker-compose restart neo4j
```

### Flask se nespustil s chybou "Connection refused"
Neo4j ještě není připravena. Healthcheck by měl vyřešit, ale zkus:
```bash
docker-compose logs neo4j
```

### HTML šablony se neaktualizují
Restartuj Flask:
```bash
docker-compose restart flask
```

---

## 📚 Další čtení

- [ARCHITECTURE.md](ARCHITECTURE.md) – Detailní dokumentace architektury, datového modelu, API
- [Flask dokumentace](https://flask.palletsprojects.com/)
- [Neo4j Cypher](https://neo4j.com/docs/cypher-manual/current/)
- [py2neo dokumentace](https://py2neo.org/)

---

## 👨‍💻 Autor

Originální řešení: **Pavel Beránek** (Cvičení 11 - NoSQL databázové systémy)

Upraveno pro: **SZZVP projekt**

---

## 📝 Licence

Tento projekt je určen pro vzdělávací účely.
