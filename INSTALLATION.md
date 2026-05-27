# 📦 Installation Guide - NerdMatch

Pokyny pro instalaci a spuštění NerdMatch aplikace.

---

## 🐳 Instalace s Docker (Doporučeno)

### Požadavky
- **Docker:** https://docker.com/products/docker-desktop
- **Docker Compose:** Součást Docker Desktop
- Volné porty: **5000** (Flask) a **7687** (Neo4j)

### Postup

1. **Klonuj/otevři projekt**
```bash
cd C:\Users\{username}\Documents\GitHub\SZZVP
```

2. **Spusť Docker Compose**
```bash
docker-compose up --build
```

Výstup by měl obsahovat:
```
flask     | Flask server running on http://localhost:5000
neo4j     | Listening on bolt://localhost:7687
```

3. **Počkej na inicializaci**
- Neo4j vytváří indexy a schéma (~10-15 sekund)
- Sleduj logy: `docker-compose logs neo4j`

4. **Otevři aplikaci**
- 🌐 **Aplikace:** http://localhost:5000
- 📊 **Neo4j Browser:** http://localhost:7474
  - Uživatel: `neo4j`
  - Heslo: `adminpass`

### Vytvoření testovacích dat

Po spuštění aplikace, vytvoř 20 testovacích profilů:

```bash
# Option 1: V běžícím Docker kontejneru
docker-compose exec flask python code/create_test_profiles.py

# Option 2: V novém kontejneru
docker-compose run flask python code/create_test_profiles.py
```

Output:
```
✅ Creating 20 test profiles...
Profile 1: alice-tech (nerd_level: 8)
Profile 2: bob-gamer (nerd_level: 6)
...
✅ Successfully created 20 profiles
```

### Zastavení aplikace

```bash
# Zastavit služby
docker-compose down

# Zastavit a odstranit data
docker-compose down -v
```

---

## 🖥️ Instalace bez Docker (Development)

### Požadavky
- **Python 3.10+**
- **Neo4j 4.4+** (běžící samostatně)
- **pip** (Python package manager)

### Postup

#### 1. Neo4j Setup

Stáhni a spusť Neo4j:
- https://neo4j.com/download-center/

Nebo Docker:
```bash
docker run -d \
  -p 7687:7687 \
  -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/adminpass \
  neo4j:latest
```

#### 2. Python Environment

```bash
# Jdi do projekt
cd SZZVP/code

# Vytvoř virtuální prostředí
python -m venv venv

# Aktivuj (Windows)
venv\Scripts\activate

# Aktivuj (Mac/Linux)
source venv/bin/activate

# Nainstaluj závislosti
pip install -r requirements.txt
```

#### 3. Konfigurace

Otevři `code/config.py` a ověř:
```python
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "adminpass"
```

#### 4. Spuštění aplikace

```bash
python app.py
```

Output:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

Otevři http://localhost:5000

#### 5. Vytvoření testovacích dat

V novém terminálu (se zapnutým venv):
```bash
python code/create_test_profiles.py
```

---

## 🔧 Konfigurace

### Soubor `code/config.py`

```python
class Config:
    # Neo4j
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "adminpass"
    
    # Flask
    SECRET_KEY = "your-secret-key-here"
    SESSION_TIMEOUT_MINUTES = 5
    
    # Skip timeout
    SKIP_TIMEOUT_HOURS = 4
    
    # Limity
    MAX_BIO_LENGTH = 500
    MAX_TAGS_PER_PROFILE = 20
```

### Environment Variables (Docker)

Upravit v `docker-compose.yml`:
```yaml
environment:
  - NEO4J_AUTH=neo4j/TVOJE_HESLO
  - FLASK_ENV=production
```

---

## 📋 Struktura Databáze

### Automatická inicializace

Při prvním spuštění se vytvoří:

```cypher
# Indexy na klíčové pole
CREATE INDEX ON :User(id)
CREATE INDEX ON :User(email)
CREATE INDEX ON :Profile(nickname)
CREATE INDEX ON :InterestCategory(name)
CREATE INDEX ON :Technology(name)

# Systémové zájmy
CREATE (i:InterestCategory {name: "Programování", type: "SYSTEM"})
CREATE (i:InterestCategory {name: "Sci-Fi", type: "SYSTEM"})
...
```

Viz `models/database.py` v `Database.init_schema()`.

---

## 🧪 Testování aplikace

### 1. Registrace

```
URL: http://localhost:5000/register
Email: test@example.com
Heslo: Test123!@
```

### 2. Vytvoření profilu

```
Přezdívka: Testovací User
Bio: Jsem testerem aplikace
Nerd Level: 7
Zájmy: Vyberi min 1
Technologie: Vyberi (volitelné)
```

### 3. Discover

- Swipuj vlevo/vpravo (drag myší, touch, nebo šipky)
- Filtruj podle nerd levelu a zájmů
- Lajkuj profily (❤️) a vidět co se stane

### 4. Kontakty

- Vidíš matchů (když je to vzájemné)
- Vidíš "tvůj zájem" (kdy ty lajkuješ, ale oni ne)
- Vidíš "obdivovatelé" (kdy oni lajkují, ale ty ne)

---

## 🐛 Troubleshooting

### Port již používán

```bash
# Zjisti jaký proces používá port 5000
lsof -i :5000  # Mac/Linux
netstat -ano | findstr :5000  # Windows

# Zabij proces
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows

# Nebo změň port v docker-compose.yml
```

### Neo4j se nespustila

```bash
# Zkontroluj logy
docker-compose logs neo4j

# Restartuj
docker-compose restart neo4j

# Počkej 20 sekund a zkus znovu
```

### Flask chyba "address already in use"

```bash
# Zastavit všechny Docker kontejnery
docker-compose down -v

# Spustit znovu
docker-compose up --build
```

### Chyba připojení k databázi

```
Error: Could not connect to bolt://localhost:7687
```

Řešení:
1. Ověř, že Neo4j je spuštěný (`docker-compose logs neo4j`)
2. Zkontroluj credentials v `config.py`
3. Restartuj Neo4j: `docker-compose restart neo4j`

### Python ImportError

```bash
# Ujisti se, že jsi aktivoval venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows

# Reinstaluj závislosti
pip install -r requirements.txt
```

### Testovací profily se nevytvořili

```bash
# Běž logging
docker-compose logs flask

# Zkus znovu
docker-compose exec flask python code/create_test_profiles.py

# Pokud je pořád chyba, vymažete data:
docker-compose down -v
docker-compose up --build
```

---

## 📚 Další Zdroje

- **README.md** - Přehled aplikace a features
- **code/models/** - Datový model a logika
- **code/routes/** - Endpoint dokumentace
- **code/templates/** - HTML šablony
- **code/static/** - CSS a JavaScript

---

## ✅ Kontrolní seznam po instalaci

- [ ] Docker je nainstalován
- [ ] Projekt je naklonován
- [ ] `docker-compose up --build` běží bez chyb
- [ ] http://localhost:5000 se otevírá
- [ ] Testovací profily jsou vytvořeny
- [ ] Můžu se registrovat a přihlásit
- [ ] Discover funguje (swipe, filtry)
- [ ] Mohu vidět matche v /contacts

---

Hotovo! 🎉 Aplikace je připravena k použití.
