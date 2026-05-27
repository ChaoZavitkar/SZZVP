#!/usr/bin/env python
"""Debug discover - test LIKES relationships and filtering"""
import sys
sys.path.insert(0, '/code')

from models.database import get_db
from routes.discover import get_available_profiles

db = get_db()

# Get all users
users = db.query('''
    MATCH (u:User)-[:HAS_PROFILE]->(p:Profile)
    RETURN u.id as id, u.email as email, p.nickname as nickname
    ORDER BY u.email
''')

print("=" * 70)
print("VŠICHNI UŽIVATELÉ V DATABÁZI")
print("=" * 70)
for u in users:
    print(f"  {u['email']:25} -> {u['nickname']:15}")

print(f"\nCelkem: {len(users)} uživatelů\n")

# Get all LIKES relationships
likes = db.query('''
    MATCH (u1:User)-[l:LIKES]->(u2:User)
    MATCH (u1)-[:HAS_PROFILE]->(p1:Profile)
    MATCH (u2)-[:HAS_PROFILE]->(p2:Profile)
    RETURN p1.nickname as from_nick, p2.nickname as to_nick
    ORDER BY p1.nickname, p2.nickname
''')

print("=" * 70)
print("VŠECHNY LIKES VZTAHY")
print("=" * 70)
for like in likes:
    print(f"  {like['from_nick']:15} → {like['to_nick']:15}")

if not likes:
    print("  (žádné lajky)")

# Get mutual matches
matches = db.query('''
    MATCH (u1:User)-[:LIKES]->(u2:User)-[:LIKES]->(u1)
    MATCH (u1)-[:HAS_PROFILE]->(p1:Profile)
    MATCH (u2)-[:HAS_PROFILE]->(p2:Profile)
    RETURN p1.nickname as nick1, p2.nickname as nick2
    ORDER BY nick1
''')

print("\n" + "=" * 70)
print("VZÁJEMNÉ MATCHE (MUTUAL LIKES)")
print("=" * 70)
for match in matches:
    print(f"  💖 {match['nick1']:15} ↔ {match['nick2']:15}")

if not matches:
    print("  (žádné matche)")

if not users:
    print("\n❌ Žádní uživatelé - nelze testovat!")
else:
    # Test MULTI-SELECT FILTERING
    print("\n" + "=" * 70)
    print("TEST: MULTI-SELECT INTEREST FILTERING")
    print("=" * 70)

    test_user = users[0]
    test_user_id = test_user['id']
    test_user_email = test_user['email']

    print(f"\nTest user: {test_user_email} ({test_user['nickname']})")

    # Test multi-interest filter
    print("\nTest 1: Filter by programování AND matematika")
    print("-" * 65)
    result = get_available_profiles(test_user_id, db, interests=['programování', 'matematika'])
    print(f"Results: {len(result)} profiles")

    all_valid = True
    for prof in result[:10]:
        has_prog = 'programování' in prof['interests']
        has_math = 'matematika' in prof['interests']
        both = has_prog and has_math
        status = "✓" if both else "✗"
        if not both:
            all_valid = False
        print(f"  {status} {prof['nickname']:15} | {', '.join(sorted(prof['interests']))}")

    if all_valid and result:
        print(f"\n✅ PASS: All {len(result)} profiles have BOTH interests")
    elif not result:
        print("\n⚠️  No profiles found (check if data exists)")
    else:
        print("\n❌ FAIL: Some profiles missing required interests!")

    # Test single interest
    print("\nTest 2: Filter by programování (single interest)")
    print("-" * 65)
    result = get_available_profiles(test_user_id, db, interests=['programování'])
    print(f"Results: {len(result)} profiles (showing first 5)")

    for prof in result[:5]:
        has_prog = 'programování' in prof['interests']
        status = "✓" if has_prog else "✗"
        print(f"  {status} {prof['nickname']:15} | {', '.join(sorted(prof['interests']))}")

    # Test nerd level filter
    print("\nTest 3: Filter by nerd level 7-9")
    print("-" * 65)
    result = get_available_profiles(test_user_id, db, min_nerd=7, max_nerd=9)
    print(f"Results: {len(result)} profiles")

    for prof in result[:5]:
        valid = 7 <= prof['nerd_level'] <= 9
        status = "✓" if valid else "✗"
        print(f"  {status} {prof['nickname']:15} | Nerd: {prof['nerd_level']}/10")

print("\n" + "=" * 70)
print("✅ DEBUG COMPLETE")
print("=" * 70)
