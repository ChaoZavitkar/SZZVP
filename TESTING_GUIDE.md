# 🧪 TESTING GUIDE - NerdMatch

## 🎯 Scénáře pro testování

Po každém zásadním testu **očistěte databázi** a znovu vytvořte účty, aby byly výsledky konzistentní.

---

## 📋 Testovací účty

Jsou v databázi přednaimportovány:

| Email | Heslo | Profil | Nerd Level | Zájmy |
|-------|-------|--------|-----------|-------|
| `alice@example.com` | `Alice123!@` | Alice | 8/10 | programování, sci-fi |
| `bob@example.com` | `Bob123!@` | Bob | 6/10 | videohry, matematika |
| `jiri@example.com` | `Jiri123!@` | (ještě není vytvořen profil) | - | - |

---

## 🧹 Jak vyčistit databázi

Spusťte v neo4j shellu (nebo přes aplikační kontejner):

```bash
# Smazat VŠECHNY conexe
docker-compose exec -T neo4j cypher-shell -u neo4j -p adminpass "MATCH (c:Connection) DETACH DELETE c;"

# Smazat všechny profily a účty (pokud chcete úplně reset)
docker-compose exec -T neo4j cypher-shell -u neo4j -p adminpass "MATCH (a:Account) DETACH DELETE a; MATCH (p:Profile) DETACH DELETE p; MATCH (u:User) DETACH DELETE u;"
```

Nebo v aplikaci - odstraňte uživatele přes "Smazat účet" a znovu se registrujte.

---

## ✅ Test 1: Registrace a Profil (FÁZE 1-2)

### Kroky:
1. Jděte na **http://localhost:5000**
2. Klikněte na **"Registrace"**
3. Vyplňte:
   - Email: `alice@example.com`
   - Heslo: `Alice123!@` (musí mít 8+ znaků, velké/malé písmeno, číslo, speciální znak)
   - Potvrzení hesla: `Alice123!@`
4. Klikněte **"Registrovat se"**

### Očekávaný výsledek:
- ✅ Přesměrování na stránku "Vytvoření profilu"
- ✅ Formulář s poli: přezdívka, bio, nerd level (0-10), zájmy, technologie
- ✅ Výběr aspoň jednoho zájmu je povinný

### Vyplnění profilu:
1. **Přezdívka:** Alice
2. **Bio:** Mám ráda programování a sci-fi filmy
3. **Nerd level:** 8
4. **Zájmy:** Vyberte ✅ programování, ✅ sci-fi
5. **Technologie:** Vyberte ✅ Python (volitelné)
6. Klikněte **"Uložit profil"**

### Očekávaný výsledek:
- ✅ Přesměrování na dashboard
- ✅ Zobrazení tlačítka "Pokračovat v hledání"

---

## ✅ Test 2: Dashboard (FÁZE 3)

### Kroky:
1. Po vytvoření profilu jste na dashboardi
2. Klikněte na **"Můj profil"** v navigaci

### Očekávaný výsledek:
- ✅ Zobrazení profilu s všemi údaji (Alice, nerd level 8, bio, zájmy)
- ✅ Tlačítko "Upravit profil"
- ✅ Odkaz "Zpět na dashboard"

### Funkce editace:
1. Klikněte na **"Upravit profil"**
2. Změňte bio na: `Programuju v Pythonu a miluju sci-fi`
3. Změňte nerd level na 9
4. Klikněte **"Uložit"**

### Očekávaný výsledek:
- ✅ Profil aktualizován
- ✅ Nová data se zobrazují v zobrazení profilu

---

## ✅ Test 3: Discovery a Like/Skip (FÁZE 4)

### Příprava:
Nejdříve vytvořte druhý profil:
1. Registrujte se jako Bob: `bob@example.com` / `Bob123!@`
2. Vytvořte profil: Bob, bio "Programátor a hráč", nerd level 6, zájmy: videohry, matematika

Pak se přihlaste zpět jako Alice.

### Kroky (Alice):
1. Na dashboardi klikněte na **"Pokračovat v hledání"** (nebo v navigaci **"Objevuj"**)
2. Měl by se zobrazit Bobův profil: Bob, nerd level 6, jeho bio a zájmy
3. Klikněte na **"❤️ Zaujalo mě"**

### Očekávaný výsledek:
- ✅ Flash zpráva "❤️ Profil se ti líbí!"
- ✅ Přesměrování zpět na Discover
- ✅ Zobrazí se další profil (pokud existuje) nebo prázdný stav

### Filtrování:
1. V discover otevřete filtr
2. Nastavte "Min nerd level" na 5
3. Vyberte zájmy: ✅ videohry
4. Klikněte **"Filtrovat"**

### Očekávaný výsledek:
- ✅ Zobrazí se jen profily s nerd level >= 5 a mající zájmy: videohry
- ✅ Pokud Bob splňuje kritéria, měl by se zobrazit

---

## ✅ Test 4: Kontakty - Jednosměrný Like (FÁZE 5)

### Kroky:
1. Přihlaste se jako Alice
2. V navigaci klikněte na **"Kontakty"** (nebo **"Moje kontakty"**)

### Očekávaný výsledek:
- ✅ Sekce **"💬 Tvůj zájem"** - zobrazí Boba (protože Alice si ho lajkla)
- ✅ Sekce **"✨ Tobě se líbíš"** - prázdná (protože Bob si ještě nelajkl Alice)
- ✅ Sekce **"🔥 Vzájemný zájem"** - prázdná

### Odebrání:
1. V sekcí "Tvůj zájem" klikněte na **"🗑️ Odebrat"** u Boba
2. Potvrzujte dialog

### Očekávaný výsledek:
- ✅ Bob zmizí ze seznamu
- ✅ Flash zpráva "✅ Kontakt odstraněn"

---

## ✅ Test 5: MATCHOVÁNÍ - Oboustranný Like (FÁZE 5)

**Klíčový test pro ověření opravy bugů #2 a #3**

### Příprava:
1. Smazat všechny konekce (vyčistit databázi)
2. Vytvořit 2 profily: Alice a Bob (viz Test 3)

### Kroky:
1. **Alice se přihlásí**
   - Na Discover zobrazit Boba
   - Klikne **"❤️ Zaujalo mě"**
   - Čekej: "Profil se ti líbí!"

2. **Alice se odhlásí** (nebo otevře nový inkognito tab)

3. **Bob se přihlásí**
   - Na Discover zobrazit Alice
   - Klikne **"❤️ Zaujalo mě"**
   - Čekej: "Profil se ti líbí!"

4. **Bob jde do Kontaktů**

### Očekávaný výsledek (BUG #2 OPRAVA):
- ✅ Sekce **"🔥 Vzájemný zájem"** - zobrazí Alice (1 kontakt)
- ✅ **DŮLEŽITÉ:** Jen 1 záznam o Alice, bez duplikátů!
- ✅ Sekce "Tobě se líbíš" - prázdná
- ✅ Sekce "Tvůj zájem" - prázdná

5. **Alice se znovu přihlásí a jde do Kontaktů**

### Očekávaný výsledek:
- ✅ Sekce **"🔥 Vzájemný zájem"** - zobrazí Boba (1 kontakt)
- ✅ **DŮLEŽITÉ:** Jen 1 záznam o Bobovi, bez duplikátů!

---

## ✅ Test 6: Discovery Filtrování (BUG #3 OPRAVA)

**Ověření, že profily těch, kdo vás lajkli, zůstanou viditelné**

### Příprava:
1. Alice i Bob se znovu přihlášili a lajkli se navzájem (Test 5)
2. Smazat pouze Aliciny lajky (ne Bobovy)

### Jak smazat jen Alicin like:
```bash
# V neo4j - smazat Connection kde Alice iniciovala
docker-compose exec -T neo4j cypher-shell -u neo4j -p adminpass \
  "MATCH (alice:User {email: 'alice@example.com'})-[:INITIATED_CONNECTION]->(c:Connection) DELETE c;"
```

### Kroky:
1. **Alice se přihlásí**
2. Jde na **"Objevuj"**
3. Filtr: Min nerd level = 0, Max = 10 (bez filtrů)

### Očekávaný výsledek (BUG #3 OPRAVA):
- ✅ Profil Boba se STÁLE zobrazuje
- ✅ (DŘÍV by zmizela - chyba vyloučila všechny konekce)
- ✅ Klikněte na Boba opět "❤️ Zaujalo mě" - znovu vznikne match

---

## ✅ Test 7: Session Timeout (FÁZE 1)

### Kroky:
1. **Alice se přihlásí**
2. **Čekejte 5 minut** (session timeout)
3. Zkuste kliknout na tlačítko v aplikaci

### Očekávaný výsledek:
- ✅ Přesměrování na login stránku
- ✅ Flash zpráva o vypršení session (pokud je implementovaná)

---

## ✅ Test 8: Validace Hesel

### Kroky:
1. Jděte na **"Registrace"**
2. Email: `test@example.com`
3. Zkuste tyto hesla (měly by selhání):
   - `short` - příliš krátké (< 8 znaků)
   - `nouppercase123!` - bez velkého písmene
   - `NOLOWERCASE123!` - bez malého písmene
   - `NoSpecial123` - bez speciálního znaku

### Očekávaný výsledek:
- ✅ Každé heslo zobrazí varovnou zprávu
- ✅ Tlačítko "Registrovat se" je zakázáno

### Správné heslo:
- `Test123!@` - OK (8+ znaků, velké, malé, číslo, speciální znak)

---

## ✅ Test 9: Unikátnost Email/Přezdívka

### Kroky:
1. Alice je registrovaná
2. Zkuste se registrovat opět s emailem `alice@example.com`

### Očekávaný výsledek:
- ✅ Chybová zpráva "Tento email je již registrovaný"

### Stejně pro přezdívku:
1. Alice má přezdívku "Alice"
2. Bob si změní přezdívku na "Alice"

### Očekávaný výsledek:
- ✅ Chybová zpráva "Tato přezdívka je již obsazena"

---

## 🐛 Jak ověřit bugfix

### BUG #1 - Duplikování:
- Spustit Test 5 (matchování)
- Zkontrolovat, že v Kontaktech je jen **1 záznam** o matchovaném uživateli
- Pokud jsou 2 záznamy = **BUG**

### BUG #2 - Matchování:
- Spustit Test 5
- Zkontrolovat sekci **"🔥 Vzájemný zájem"**
- Pokud je prázdná nebo zobrazuje jen jednu stranu = **BUG**

### BUG #3 - Viditelnost profilů:
- Spustit Test 6
- Zkontrolovat, že profil člověka, který vás lajkl, je v Discover viditelný
- Pokud zmizí ze seznamu = **BUG**

---

## 📊 Checklist pro úplné testování

- [ ] Test 1: Registrace a Profil
- [ ] Test 2: Dashboard
- [ ] Test 3: Discovery a filtrování
- [ ] Test 4: Kontakty - jednosměrné
- [ ] Test 5: Matchování (BUG #2)
- [ ] Test 6: Discovery viditelnost (BUG #3)
- [ ] Test 7: Session timeout
- [ ] Test 8: Validace hesel
- [ ] Test 9: Unikátnost email/přezdívka
- [ ] Volitelně: Otestovat odhlášení
- [ ] Volitelně: Otestovat smazání účtu

---

## 🚀 Spuštění aplikace

```bash
cd C:\Users\LBao\Documents\GitHub\SZZVP
docker-compose up --build
```

Aplikace běží na: **http://localhost:5000**

Neo4j Browser: **http://localhost:7474**
