#!/usr/bin/env python
"""Vytvoř 20 testovacích profilů"""
import sys
sys.path.insert(0, '/code')

from app import app
from models.user import User
from models.profile import Profile

test_users = [
    ("alice.web@test.com", "heslo123", "Alice", "Miluji programování", 8, ["programování", "matematika"], ["Python", "Git"]),
    ("bob.web@test.com", "heslo123", "Bob", "Zamilovaný do her", 7, ["videohry", "komiksy"], ["Git"]),
    ("jiri.web@test.com", "heslo123", "Jiří", "Web developer", 6, ["programování"], ["Python"]),
    ("eva.test@com", "heslo123", "Eva", "Data science entuziastka", 9, ["matematika", "AI / Machine Learning"], ["Python"]),
    ("david.test@com", "heslo123", "David", "Herní vývojář", 8, ["videohry", "programování"], ["Python", "Git"]),
    ("petra.test@com", "heslo123", "Petra", "DevOps inženýrka", 7, ["hardware", "programování"], ["Docker", "Git"]),
    ("lukas.test@com", "heslo123", "Lukáš", "Frontend vývojář", 6, ["programování", "sci-fi"], ["JavaScript", "Git"]),
    ("martina.test@com", "heslo123", "Martina", "Grafická návrhářka", 5, ["komiksy", "sci-fi"], ["Git"]),
    ("milan.test@com", "heslo123", "Milan", "Databázový administrátor", 8, ["matematika", "hardware"], ["Docker"]),
    ("katarina.test@com", "heslo123", "Katarina", "Testerka software", 6, ["programování", "matematika"], ["Git"]),
    ("radek.test@com", "heslo123", "Radek", "Backend developer", 7, ["programování", "hardware"], ["Python", "Docker"]),
    ("simona.test@com", "heslo123", "Simona", "UI/UX designer", 5, ["komiksy", "sci-fi"], ["Git"]),
    ("vladimir.test@com", "heslo123", "Vladimír", "Sysadmin", 8, ["hardware", "matematika"], ["Docker"]),
    ("anna.test@com", "heslo123", "Anna", "Product manažerka", 4, ["sci-fi", "videohry"], ["Git"]),
    ("petr.test@com", "heslo123", "Petr", "Cybersecurity expert", 9, ["hardware", "matematika"], ["Docker", "Git"]),
    ("michaela.test@com", "heslo123", "Michaela", "QA engineer", 6, ["programování", "komiksy"], ["Git"]),
    ("viktor.test@com", "heslo123", "Viktor", "Blockchain developer", 9, ["matematika", "AI / Machine Learning"], ["Python"]),
    ("agata.test@com", "heslo123", "Agata", "API architect", 7, ["programování", "hardware"], ["Python", "Docker"]),
    ("igor.test@com", "heslo123", "Igor", "Machine learning engineer", 9, ["AI / Machine Learning", "matematika"], ["Python"]),
    ("juliana.test@com", "heslo123", "Juliana", "Cloud architect", 8, ["hardware", "programování"], ["Docker", "Git"]),
]

with app.app_context():
    print("=" * 70)
    print("Vytváří 20 testovacích profilů")
    print("=" * 70)

    created_count = 0
    for email, password, nickname, bio, nerd_level, interests, techs in test_users:
        # Vytvoř uživatele
        user = User.create(email, password)
        if user:
            user_id = user['id']
            # Vytvoř profil
            Profile.create(user_id, nickname, bio, nerd_level)
            # Aktualizuj s zájmy a technologiemi
            Profile.update(user_id, nickname, bio, nerd_level, interests, techs)
            created_count += 1
            print(f"✓ {nickname:15} ({email})")
        else:
            print(f"❌ {nickname}: Uživatel již existuje")

    print("\n" + "=" * 70)
    print(f"✅ Vytvořeno {created_count}/20 profilů")
    print("=" * 70)
