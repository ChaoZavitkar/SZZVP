#!/usr/bin/env python
"""Test web flow - registrace, profil, discover, lajky"""
import sys
sys.path.insert(0, '/code')

from app import app
from models.user import User
from models.profile import Profile
from models.connection import Connection

with app.app_context():
    from models.database import get_db

    db = get_db()

    print("=" * 70)
    print("TEST: Webový flow (registrace → profil → discover → like)")
    print("=" * 70)

    # 1. Vytvoř uživatele
    print("\n1️⃣ Registrace uživatelů")
    alice = User.create('alice.web@test.com', 'heslo123')
    bob = User.create('bob.web@test.com', 'heslo123')
    jiri = User.create('jiri.web@test.com', 'heslo123')

    alice_id = alice['id'] if alice else None
    bob_id = bob['id'] if bob else None
    jiri_id = jiri['id'] if jiri else None

    print(f"   Alice: {alice_id}")
    print(f"   Bob: {bob_id}")
    print(f"   Jiří: {jiri_id}")

    # 2. Vytvoř profily
    print("\n2️⃣ Vytvoření profilů")
    Profile.create(alice_id, 'Alice', 'Miluji programování', nerd_level=8)
    Profile.create(bob_id, 'Bob', 'Zamilovaný do her', nerd_level=7)
    Profile.create(jiri_id, 'Jiří', 'Web developer', nerd_level=6)

    print("   ✓ Profily vytvořeny")

    # 3. Simuzuj discover - Alice lajkne Boba
    print("\n3️⃣ Alice discover → lajkne Boba")
    # Alice vidí Boba + Jiřího
    discover_alice = db.query('''
        MATCH (alice:User {email: $email})
        MATCH (other:User)-[:HAS_PROFILE]->(profile:Profile)
        WHERE other.id <> alice.id
        OPTIONAL MATCH (alice)-[likes:LIKES]->(other)
        WITH profile, other, likes
        WHERE likes IS NULL
        RETURN DISTINCT other.id, profile.nickname
    ''', email='alice.web@test.com')

    print(f"   Alice vidí profily: {len(discover_alice)}")
    for d in discover_alice[:3]:
        print(f"     - {d['profile.nickname']}")

    # Alice si dá like na Boba
    Connection.create(alice_id, bob_id)
    print("   ✓ Alice dala like Bobovi")

    # 4. Bob discover - vidí Alici + Jiřího
    print("\n4️⃣ Bob discover")
    discover_bob = db.query('''
        MATCH (bob:User {email: $email})
        MATCH (other:User)-[:HAS_PROFILE]->(profile:Profile)
        WHERE other.id <> bob.id
        OPTIONAL MATCH (bob)-[likes:LIKES]->(other)
        WITH profile, other, likes
        WHERE likes IS NULL
        RETURN DISTINCT other.id, profile.nickname
    ''', email='bob.web@test.com')

    print(f"   Bob vidí profily: {len(discover_bob)}")
    for d in discover_bob[:3]:
        print(f"     - {d['profile.nickname']}")

    # Bob si dá like na Alici - MUTUAL!
    Connection.create(bob_id, alice_id)
    print("   ✓ Bob dál like Alici → MUTUAL!")

    # 5. Check mutual
    print("\n5️⃣ Kontrola mutual like")
    is_mutual = Connection.is_mutual(alice_id, bob_id)
    print(f"   Alice <-> Bob: is_mutual={is_mutual}")

    if is_mutual:
        print("   ✅ Mutual like detekován!")

    # 6. Contacts - Alice vidí Boba jako match
    print("\n6️⃣ Contacts pro Alice")
    contacts = db.query('''
        MATCH (alice:User {email: $email})
        MATCH (alice)-[r:LIKES]-(other:User)
        WHERE other.id <> alice.id
        OPTIONAL MATCH (other)-[:HAS_PROFILE]->(profile:Profile)
        OPTIONAL MATCH (alice)-[:LIKES]->(other)
        OPTIONAL MATCH (other)-[:LIKES]->(alice)
        WITH DISTINCT other, profile,
             CASE WHEN (alice)-[:LIKES]->(other) AND (other)-[:LIKES]->(alice) THEN true ELSE false END as is_match
        RETURN other.id, profile.nickname, is_match
    ''', email='alice.web@test.com')

    print(f"   Kontakty: {len(contacts)}")
    for c in contacts:
        match_str = "👥 MATCH" if c['is_match'] else "💔 One-way"
        print(f"     - {c['profile.nickname']}: {match_str}")

    # 7. Discover - Alice by měla vidět jen Jiřího (ne Boba)
    print("\n7️⃣ Discover po mutual like")
    discover_after = db.query('''
        MATCH (alice:User {email: $email})
        MATCH (other:User)-[:HAS_PROFILE]->(profile:Profile)
        WHERE other.id <> alice.id
        OPTIONAL MATCH (alice)-[likes:LIKES]->(other)
        WITH profile, other, likes
        WHERE likes IS NULL
        RETURN DISTINCT profile.nickname
    ''', email='alice.web@test.com')

    print(f"   Alice vidí: {len(discover_after)}")
    for d in discover_after:
        print(f"     - {d['profile.nickname']}")

    expected = 'Jiří'
    actual = [d['profile.nickname'] for d in discover_after]

    if expected in actual and 'Bob' not in actual:
        print(f"   ✅ Správně: nevidí Boba, vidí Jiřího")
    else:
        print(f"   ❌ Chyba: očekávám {expected}, mám {actual}")

    print("\n" + "=" * 70)
    print("✅ WEB FLOW TEST KOMPLETNÍ")
    print("=" * 70)
