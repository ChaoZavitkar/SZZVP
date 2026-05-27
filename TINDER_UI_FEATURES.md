# 🔥 NerdMatch Tinder-Style UI

## Přehled Nové Vizuální Identitity

NerdMatch nyní poskytuje moderní, zábavný Tinder-inspirovaný design pro discovery stránku s interaktivními gesty a animacemi.

---

## ✨ Klíčové Features

### 1. 🎴 Swipovací Karty

**Co se změnilo:**
- Jedna velká karta místo klasického layoutu
- Gradient background (purpurová → červená)
- Profesionální design s hodně bílého prostoru
- Animované swipe gesty (doleva/doprava)

**Jak funguje:**
```
User vidi velkou kartu s profilem
→ Může jí dragovat myší nebo prstem
→ Když přetáhne dost (30% obrazovky)
→ Karta se animuje a zmizí
→ Další profil se objeví
```

### 2. 👤 Avatar s Iniciálou

**Funkčnost:**
- Velký kruhový avatar (120px na desktop, 80px mobile)
- Zobrazuje první písmeno jména uživatele
- Gradient background s shadow efektem
- Positionován v levém horním rohu karty

**Příklad:**
```
User: "Milan" → Avatar ukazuje "M"
User: "Alexandra" → Avatar ukazuje "A"
```

### 3. 📊 Nerd Level Visualizace

**Co se zobrazuje:**
```
┌─────────────────────────┐
│ Milano          8/10 🧠 │
│ ████████░░░░░░░░░░░░░░ │  ← Nerd level bar
└─────────────────────────┘
```

- Číslo 0-10 v pravém horním rohu
- Progresivní bar zobrazující úroveň
- Gradient barvy (red → green)

### 4. 💭 Bio Sekce

**Stylizace:**
- Centrální pozice na kartě
- Speciální rámec s levým červeným okrajem
- Pokud uživatel nemá bio: "Tajemství mi sluší... 🤐"
- Italické, měkčí text

### 5. 🏷️ Tag Systém

**Zájmy (❤️):**
```
❤️ Zájmy
[Programování] [Hry] [Sci-Fi] [Anime]
```
- Červenožluté tagy (červená barva)
- Popis: "INTERESTS"

**Technologie (⚙️):**
```
⚙️ Technologie  
[Python] [JavaScript] [React] [PostgreSQL]
```
- Zelené tagy (zelená barva)
- Popis: "TECHNOLOGIES"

Oba mají:
- Semi-transparent background
- Malý font (13px)
- Skrytá funkce: Když nema tagy → "Žádné zájmy" / "Žádné technologie"

### 6. 🔘 Action Buttons

**Lokace:** Dolní část karty, centralizované

**Tlačítka:**
```
    👎  ❤️
  [Skip] [Like]
```

**Vlastnosti:**
- Kruhová tlačítka (70px diameter na desktop)
- Gradient background (red/green)
- Hover efekt: scale up + extra shadow
- Cursor: pointer

**Interakce:**
- Click tlačítko → Ihned swipe animace
- Keyboard: Arrow Left (← skip), Arrow Right (→ like)
- Drag gesture: Vlevo → skip, vpravo → like

### 7. ⬆️ Filter Toggle

**Design:**
- Horní část stránky (nad kartou)
- Button: "⬆️ Zobrazit filtr" / "⬇️ Skrýt filtr"
- Gradient background (purple-red)
- Smooth slide-down animation

**Funkčnost:**
```
Initial state: Filter je skrytý
User klikne: ⬆️ Zobrazit filtr
  → slideDown animation (0.3s)
  → Filter se rozbalí
  → Button změní text na "⬇️ Skrýt filtr"
  
User klikne: ⬇️ Skrýt filtr
  → Filter zmizí
  → Button změní text na "⬆️ Zobrazit filtr"
```

**Filtr obsahuje:**
- Range sliders pro Nerd level (min/max)
- Checkboxes pro zájmy (2 sloupce)
- Tlačítko "Aplikovat filtr" (gradient)
- Tlačítko "Resetovat" (transparentní)

### 8. 💫 Swipe Animace

**Swipe Left (Skip - 👎):**
```css
@keyframes swipeLeft {
    to {
        transform: translateX(-150%) rotate(-20deg);
        opacity: 0;
    }
}
```
- Karta se posune doleva
- Rotace -20 stupňů
- Fade out efekt
- Trvání: 0.5s

**Swipe Right (Like - ❤️):**
```css
@keyframes swipeRight {
    to {
        transform: translateX(150%) rotate(20deg);
        opacity: 0;
    }
}
```
- Karta se posune doprava
- Rotace +20 stupňů
- Fade out efekt
- Trvání: 0.5s

**Drag Animation (během táhnutí):**
- Real-time transform: `translateX(currentX) rotate(rotation)`
- Opacity: `1 - Math.abs(currentX) / windowWidth`
- Smoothness: GPU accelerated

### 9. ⌨️ Keyboard Shortcuts

| Klávesa | Akce | Popis |
|---------|------|-------|
| → | Like ❤️ | Svipe right |
| ← | Skip 👎 | Swipe left |
| Esc | Toggle Filter | Otevři/zavři filtr |

### 10. 😶 Empty State (Žádné profily)

**Design:**
```
    🤷
    
  Zkušeností jsi prošel!
  
Vyčerpal jsi seznam profilů pro tento filtr.
Zkus změnit kritéria nebo se vrať později! 😎

[🔄 Resetovat a zkusit znova]
```

**Animace:**
- Icon: Bobá nahoru-dolů (float animation, 3s)
- Button: Gradient background
- Centralizované na stránce

### 11. 💘 Match Notification

**Když se matchne:**
```
    💘 (spinning animation)
    
   JE TO MATCH!
   
Ty a [PartnerName] si vzájemně padnete!

🎉 Pojďte si psát zprávy! 🎉
```

**Animace:**
- Pop-up animation (cubic-bezier)
- 💘 emoji se točí (360°, 2s)
- Automaticky zmizí za 3 sekundy
- Fixed position (uprostřed obrazovky)

---

## 🎨 Barvy & Design

### Paleta Barev
```
Primary:        #ff6b6b  (Červená)
Success:        #51cf66  (Zelená)
Nerd Purple:    #7c3aed  (Purpura)
Dark BG:        #1a1a2e  (Tmavě modrá)
Card BG:        #16213e  (Tmavá modř)
```

### Gradienty
```
Primary Gradient:  135deg, #ff6b6b → #7c3aed
Background:        135deg, #1a1a2e → #0f3460
Interest Tag:      rgba(255, 107, 107, 0.3)
Technology Tag:    rgba(81, 207, 102, 0.3)
```

### Typography
```
Heading (jméno):      36px, bold, white
Profile Nerd Level:   14px, semi-transparent
Bio:                  16px, line-height: 1.6
Tag:                  13px, font-weight: 500
```

---

## 📱 Responsive Design

### Desktop (> 768px)
```
┌─────────────────────────────┐
│       🔥 NerdMatch 🔥       │
│  Swipuj. Matchuj. Zajímej   │
├─────────────────────────────┤
│     [⬆️ Zobrazit filtr]      │
├─────────────────────────────┤
│   ┌──────────────────────┐   │
│   │ M           8/10 🧠  │   │
│   │ Milano               │   │
│   │                      │   │
│   │ "Vývojář v srdci"    │   │
│   │                      │   │
│   │ ❤️ Zájmy             │   │
│   │ [Python] [Games]     │   │
│   │                      │   │
│   │ ⚙️ Technologie       │   │
│   │ [React] [Node]       │   │
│   │                      │   │
│   │     👎    ❤️         │   │
│   └──────────────────────┘   │
└─────────────────────────────┘
```

### Mobile (< 768px)
```
┌──────────────────────┐
│  🔥 NerdMatch 🔥    │
├──────────────────────┤
│ [⬆️ Zobrazit filtr]  │
├──────────────────────┤
│┌────────────────────┐│
││M        8/10 🧠   ││
││Milano             ││
││                   ││
││"Vývojář v srdci"  ││
││                   ││
││❤️ Zájmy           ││
││[Python] [Games]   ││
││                   ││
││  👎    ❤️         ││
│└────────────────────┘│
└──────────────────────┘
```

---

## 🖱️ Interakce - Detailní Flow

### Scénář 1: User Liking Profile

```
1. Page loads
   → Nový profil je zobrazen na kartě
   → Filter je skrytý (default)

2. User vidí profil "Milan"
   → Přečte si bio, zájmy, technologie
   
3. User se rozhodne → Klikne ❤️ tlačítko
   → Karta dostane class "swipe-right"
   → Animace: translateX(150%) rotate(20deg)
   
4. Po 0.3s → Form se automaticky submitne
   → Backend: Connection.like_profile()
   → Pokud je match: showMatchNotification()
   
5. Nový profil se objeví
   → Cyklus se opakuje
```

### Scénář 2: User Filtering Profiles

```
1. User klikne "⬆️ Zobrazit filtr"
   → Filter sekcece se rozbalí slideDown
   
2. User změní Nerd level: 5-8
3. User vybere zájmy: Programování, Hry
4. User klikne "Aplikovat filtr"
   → GET /discover?min_nerd=5&max_nerd=8&interests=Programování&interests=Hry
   → Backend filtruje profily
   → Nová karta se zobrazí
   
5. User klikne "⬇️ Skrýt filtr"
   → Filter zmizí
```

### Scénář 3: Keyboard Swipe

```
1. Card is focused (visible on page)

2. User presses Right Arrow (→)
   → Triggers: swipeRight()
   → Card: swipe-right class
   → Animation plays
   → Form submits (like_profile)
   
3. User presses Left Arrow (←)
   → Triggers: swipeLeft()
   → Card: swipe-left class
   → Animation plays
   → Form submits (skip_profile)
   
4. User presses Escape
   → Closes filter if open
```

### Scénář 4: Touch/Mouse Drag

```
1. User mouse-down na kartě
   → isDragging = true
   → startX = event.clientX
   
2. User táhne myší doprava
   → currentX = e.clientX - startX (pozitivní)
   → applyDragTransform():
     - rotation = (currentX / windowWidth) * 20
     - opacity = 1 - Math.abs(currentX) / windowWidth
     - card.style.transform = `translateX(${currentX}px) rotate(${rotation}deg)`
     
3. User pustí myš
   → handleDragEnd():
   - Pokud currentX > 30% window width → swipeRight()
   - Pokud currentX < -30% window width → swipeLeft()
   - Jinak → vrať se na původní pozici (smooth transition)
```

---

## 🚀 Performance Optimizations

✅ **GPU Acceleration**
- Transform animace (GPU accelerated)
- Will-change: transform na kartě
- 60fps animace

✅ **Lazy Loading**
- CSS importován dynamicky
- JavaScript dělá себов registraci pouze při DOMContentLoaded

✅ **Mobile Optimizations**
- Touch events namísto mouse events na mobile
- Smaller avatar size (80px vs 120px)
- Simplified layout na malých screenech

---

## 🎭 Parodické Prvky

```
Motto:          "Swipuj. Matchuj. Zajímej se. Opakuj."
Empty State:    "Zkušeností jsi prošel!"
No Bio:         "Tajemství mi sluší... 🤐"
Match Title:    "JE TO MATCH!"
Match CTA:      "Pojďte si psát zprávy!"
Reset Link:     "🔄 Resetovat a zkusit znova"
```

---

## 📚 Soubory

| Soubor | Role | Řádky |
|--------|------|-------|
| `code/static/css/tinder-style.css` | Všechny styly (gradients, animace, layout) | 400+ |
| `code/static/js/tinder-swipe.js` | Drag gestures, swipe logika, keyboard | 150+ |
| `code/templates/discover/index.html` | HTML layout s Bootstrap integrací | 180+ |

---

## ✨ Souhrn

🎯 **Cíl:** Moderní, zábavný, interaktivní UI
✅ **Dosaženo:** Tinder-style design s vlastními prvky
🎮 **Zábava:** Swipe gesta, animace, parodické texty
📱 **Responsive:** Desktop, tablet, mobilní
⚡ **Výkon:** GPU accelerated, 60fps
🎨 **Design:** Gradient, modern, kvalitní

---

**Verzionováno:** 2026-05-27
**Commit:** d5c7c31 🔥 Implement Tinder-style UI
