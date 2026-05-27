#!/usr/bin/env python
"""Test zjednodušené LIKES logiky"""
import sys
sys.path.insert(0, '/code')

from app import app
from models.connection import Connection

with app.app_context():
    from models.database import get_db

    db = get_db()
    db_neo4j = db.graph

    # Zařiď test data
    print("=" * 70)
    print("TEST: Zjednodušená LIKES logika")
    print("=" * 70)

    # Vytvoř 3 uživatele
    db_neo4j.run('''
        CREATE (alice:User {id: 'alice1', email: 'alice@test.com'})
        CREATE (bob:User {id: 'bob1', email: 'bob@test.com'})
        CREATE (jiri:User {id: 'jiri1', email: 'jiri@test.com'})
    ''')

    print("\n✓ Vytvořeni uživatelé: Alice, Bob, Jiří")

    # Test 1: Alice -> Bob
    print("\n1️⃣ Alice si dá like na Boba")
    Connection.create('alice1', 'bob1')

    likes = db_neo4j.run('MATCH (a:User)-[:LIKES]->(b:User) RETURN a.email as from, b.email as to').data()
    print(f"   LIKES v DB: {len(likes)}")
    for l in likes:
        print(f"     - {l['from']} -> {l['to']}")

    # Test 2: Bob -> Alice (mutual)
    print("\n2️⃣ Bob si dá like na Alice")
    Connection.create('bob1', 'alice1')

    likes = db_neo4j.run('MATCH (a:User)-[:LIKES]->(b:User) RETURN a.email as from, b.email as to').data()
    print(f"   LIKES v DB: {len(likes)}")
    for l in likes:
        print(f"     - {l['from']} -> {l['to']}")

    # Test 3: Je mutual?
    print("\n3️⃣ Kontrola mutual like")
    is_mutual = Connection.is_mutual('alice1', 'bob1')
    print(f"   Alice <-> Bob: is_mutual={is_mutual}")

    # Test 4: Discover - Alice by měla vidět Jiřího (ne Boba)
    print("\n4️⃣ Discover pro Alice (bez filtrů)")
    result = db_neo4j.run('''
        MATCH (user:User {id: 'alice1'})
        MATCH (other:User)
        WHERE other.id <> user.id

        OPTIONAL MATCH (user)-[likes_rel:LIKES]->(other)
        WITH other
        WHERE likes_rel IS NULL

        RETURN other.email as email
    ''').data()

    print(f"   Viditelné profily pro Alice: {len(result)}")
    for r in result:
        print(f"     - {r['email']}")

    expected = sorted(['jiri@test.com'])
    actual = sorted([r['email'] for r in result])

    if actual == expected:
        print("   ✅ Správně: nevidí Boba (lajkla ho), vidí jen Jiřího")
    else:
        print(f"   ❌ Chyba: očekávám {expected}, mám {actual}")

    # Test 5: Contacts - Alice má match s Bobem
    print("\n5️⃣ Contacts pro Alice")
    result = db_neo4j.run('''
        MATCH (alice:User {id: 'alice1'})
        MATCH (alice)-[r:LIKES]-(other:User)
        WHERE other.id <> alice.id

        OPTIONAL MATCH (alice)-[:LIKES]->(other)
        OPTIONAL MATCH (other)-[:LIKES]->(alice)

        WITH DISTINCT other,
             CASE WHEN (alice)-[:LIKES]->(other) AND (other)-[:LIKES]->(alice) THEN true ELSE false END as is_match

        RETURN other.email as email, is_match
    ''').data()

    print(f"   Kontakty Alice: {len(result)}")
    for r in result:
        match_str = "👥 MATCH" if r['is_match'] else "💔 One-way"
        print(f"     - {r['email']}: {match_str}")

    matches = [r for r in result if r['is_match']]
    if len(matches) == 1 and matches[0]['email'] == 'bob@test.com':
        print("   ✅ Správně: Bob je match, Jiří není v kontaktech")
    else:
        print(f"   ❌ Chyba s matches: očekávám 1 match (Bob), mám {len(matches)} matchů")

    # Test 6: Trojúhelník - Jiří -> Bob
    print("\n6️⃣ Jiří si dá like na Boba")
    Connection.create('jiri1', 'bob1')

    result = db_neo4j.run('''
        MATCH (alice:User {id: 'alice1'})
        MATCH (alice)-[r:LIKES]-(other:User)

        OPTIONAL MATCH (alice)-[:LIKES]->(other)
        OPTIONAL MATCH (other)-[:LIKES]->(alice)

        WITH DISTINCT other,
             CASE WHEN (alice)-[:LIKES]->(other) AND (other)-[:LIKES]->(alice) THEN true ELSE false END as is_match

        RETURN other.email as email, is_match
    ''').data()

    print(f"   Alice vidí {len(result)} kontakty")
    for r in result:
        print(f"     - {r['email']}: is_match={r['is_match']}")

    print("\n" + "=" * 70)
    print("✅ TEST KOMPLETNÍ")
    print("=" * 70)
