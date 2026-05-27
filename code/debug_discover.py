#!/usr/bin/env python
"""Debug discover query - vidíme co se vrací"""
import sys
sys.path.insert(0, '/code')

from py2neo import Graph

db = Graph('bolt://neo4j:7687', auth=('neo4j', 'adminpass'))

# Načteme všechny uživatele
users = db.run('''
    MATCH (u:User)-[:HAS_PROFILE]->(p:Profile)
    RETURN u.id as id, u.email as email, p.nickname as nickname
''').data()

print("=" * 70)
print("VŠICHNI UŽIVATELÉ V DATABÁZI")
print("=" * 70)
for u in users:
    print(f"  {u['email']:20} -> Profil: {u['nickname']:15} ID: {u['id'][:8]}...")

# Načteme všechny konekce
conns = db.run('''
    MATCH (u1:User)-[:INITIATED_CONNECTION]->(conn:Connection)<-[:RECEIVED_CONNECTION]-(u2:User)
    WHERE conn.is_deleted = false
    OPTIONAL MATCH (u1)-[:HAS_PROFILE]->(p1:Profile)
    OPTIONAL MATCH (u2)-[:HAS_PROFILE]->(p2:Profile)
    RETURN u1.email as from_email, p1.nickname as from_nick,
           u2.email as to_email, p2.nickname as to_nick,
           conn.is_match as is_match
''').data()

print("\n" + "=" * 70)
print("VŠECHNY KONEKCE (LAJKY/MATCHE)")
print("=" * 70)
for c in conns:
    match_icon = "🔥" if c['is_match'] else "❤️"
    print(f"  {match_icon} {c['from_nick']:15} → {c['to_nick']:15} (match={c['is_match']})")

if not users:
    print("❌ Žádní uživatelé!")
    sys.exit(1)

# Test discover pro každého uživatele
print("\n" + "=" * 70)
print("DISCOVER QUERY TEST - CO VIDÍ KAŽDÝ UŽIVATEL?")
print("=" * 70)

for user in users:
    user_id = user['id']
    user_email = user['email']

    print(f"\n👤 {user_email} ({user['nickname']}):")
    print("  " + "-" * 65)

    # Simulujeme discover query
    result = db.run('''
        MATCH (user:User {id: $user_id})
        MATCH (other:User)-[:HAS_PROFILE]->(profile:Profile)
        MATCH (other)-[:HAS_ACCOUNT]->(account)
        WHERE other.id <> user.id
        AND account.is_deleted = false
        AND profile.nerd_level >= 0
        AND profile.nerd_level <= 10

        OPTIONAL MATCH (user)-[:INITIATED_CONNECTION]->(initiated:Connection)<-[:RECEIVED_CONNECTION]-(other)
        WHERE initiated.is_deleted = false

        WITH user, profile, other, initiated
        WHERE initiated IS NULL

        OPTIONAL MATCH (other)-[:HAS_PROFILE]->(p2:Profile)
        OPTIONAL MATCH (p2)-[:INTERESTED_IN]->(interest:InterestCategory)

        RETURN DISTINCT other.id as user_id,
               p2.nickname as nickname,
               profile.nerd_level as nerd_level
        ORDER BY other.id
    ''', user_id=user_id).data()

    if result:
        print(f"  Vidí {len(result)} profil(ů):")
        for r in result:
            print(f"    • {r['nickname']} (nerd level: {r['nerd_level']})")
    else:
        print(f"  ❌ NIKOGO NEVIDÍ! (prázdný seznam)")

    # Také zkontrolujeme co se vyloučilo
    excluded = db.run('''
        MATCH (user:User {id: $user_id})
        MATCH (other:User)-[:HAS_PROFILE]->(profile:Profile)
        MATCH (other)-[:HAS_ACCOUNT]->(account)
        WHERE other.id <> user.id
        AND account.is_deleted = false

        OPTIONAL MATCH (user)-[:INITIATED_CONNECTION]->(initiated:Connection)<-[:RECEIVED_CONNECTION]-(other)
        WHERE initiated.is_deleted = false

        WITH user, profile, other, initiated
        WHERE initiated IS NOT NULL

        OPTIONAL MATCH (other)-[:HAS_PROFILE]->(p2:Profile)
        RETURN DISTINCT p2.nickname as nickname
        ORDER BY p2.nickname
    ''', user_id=user_id).data()

    if excluded:
        print(f"  (Vyloučení - už lajkl: {', '.join([e['nickname'] for e in excluded])})")

print("\n" + "=" * 70)
