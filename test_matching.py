#!/usr/bin/env python
"""Test matching flow and check for duplicates"""
import sys
sys.path.insert(0, '/code')

from models.database import get_db
from models.user import User
from models.connection import Connection
from models.profile import Profile

db = get_db()

# Verify test users exist
print("Checking test users...")
alice = User.get_by_email('alice@example.com')
bob = User.get_by_email('bob@example.com')

if not alice:
    print("❌ Alice not found!")
    sys.exit(1)
if not bob:
    print("❌ Bob not found!")
    sys.exit(1)

print(f"✅ Alice (ID: {alice['id']})")
print(f"✅ Bob (ID: {bob['id']})")

# Clear any existing connections
print("\nClearing existing connections...")
result = db.query('MATCH (c:Connection) DETACH DELETE c RETURN count(c) as count')
if result:
    print(f"Deleted {result[0]['count']} connections")

# Test 1: Alice likes Bob
print("\n=== TEST 1: Alice likes Bob ===")
conn1 = Connection.create(alice['id'], bob['id'])
print(f"Connection created: {conn1}")

result = db.query('''
    MATCH (c:Connection)-[:INITIATED_CONNECTION]-(u1:User)
    MATCH (c)-[:RECEIVED_CONNECTION]-(u2:User)
    RETURN c.id as id, c.is_match as is_match, u1.id as initiator, u2.id as receiver
''')
print(f"After Alice→Bob: {result}")

# Test 2: Bob likes Alice
print("\n=== TEST 2: Bob likes Alice ===")
conn2 = Connection.create(bob['id'], alice['id'])
print(f"Connection created: {conn2}")

result = db.query('''
    MATCH (c:Connection)-[:INITIATED_CONNECTION]-(u1:User)
    MATCH (c)-[:RECEIVED_CONNECTION]-(u2:User)
    RETURN c.id as id, c.is_match as is_match, u1.id as initiator, u2.id as receiver
''')
print(f"After Bob→Alice: {result}")

# Test 3: Check Alice's contacts (should see Bob as match)
print("\n=== TEST 3: Alice's Contacts (should have 1 match) ===")
result = db.query('''
    MATCH (user:User {id: $user_id})
    MATCH (u1:User)-[:INITIATED_CONNECTION]->(conn:Connection)<-[:RECEIVED_CONNECTION]-(u2:User)
    WHERE conn.is_deleted = false
    AND (u1.id = user.id OR u2.id = user.id)

    WITH user, conn, u1, u2,
         CASE WHEN u1.id = user.id THEN 'initiated' ELSE 'received' END as initiated_by,
         CASE WHEN u1.id = user.id THEN u2 ELSE u1 END as other

    OPTIONAL MATCH (other)-[:HAS_PROFILE]->(profile:Profile)
    RETURN DISTINCT conn.id as id,
           conn.is_match as is_match,
           conn.created_at as created_at,
           other.id as user_id,
           profile.nickname as nickname,
           initiated_by

    ORDER BY is_match DESC, created_at DESC
''', user_id=alice['id'])

print(f"Total connections: {len(result)}")
matches = [r for r in result if r['is_match']]
one_way = [r for r in result if not r['is_match']]
print(f"  Matches (is_match=true): {len(matches)}")
print(f"  One-way (is_match=false): {len(one_way)}")

for conn in result:
    print(f"  - {conn['nickname']} (match={conn['is_match']}, initiated_by={conn['initiated_by']})")

# Check for duplicate IDs
connection_ids = [r['id'] for r in result]
if len(connection_ids) != len(set(connection_ids)):
    print("❌ DUPLICATE CONNECTION IDS FOUND!")
    from collections import Counter
    dups = [id for id, count in Counter(connection_ids).items() if count > 1]
    print(f"Duplicates: {dups}")
else:
    print("✅ No duplicate connection IDs")

# Test 4: Check Bob's contacts (should see Alice as match)
print("\n=== TEST 4: Bob's Contacts (should have 1 match) ===")
result = db.query('''
    MATCH (user:User {id: $user_id})
    MATCH (u1:User)-[:INITIATED_CONNECTION]->(conn:Connection)<-[:RECEIVED_CONNECTION]-(u2:User)
    WHERE conn.is_deleted = false
    AND (u1.id = user.id OR u2.id = user.id)

    WITH user, conn, u1, u2,
         CASE WHEN u1.id = user.id THEN 'initiated' ELSE 'received' END as initiated_by,
         CASE WHEN u1.id = user.id THEN u2 ELSE u1 END as other

    OPTIONAL MATCH (other)-[:HAS_PROFILE]->(profile:Profile)
    RETURN DISTINCT conn.id as id,
           conn.is_match as is_match,
           conn.created_at as created_at,
           other.id as user_id,
           profile.nickname as nickname,
           initiated_by

    ORDER BY is_match DESC, created_at DESC
''', user_id=bob['id'])

print(f"Total connections: {len(result)}")
matches = [r for r in result if r['is_match']]
one_way = [r for r in result if not r['is_match']]
print(f"  Matches (is_match=true): {len(matches)}")
print(f"  One-way (is_match=false): {len(one_way)}")

for conn in result:
    print(f"  - {conn['nickname']} (match={conn['is_match']}, initiated_by={conn['initiated_by']})")

# Check for duplicate IDs
connection_ids = [r['id'] for r in result]
if len(connection_ids) != len(set(connection_ids)):
    print("❌ DUPLICATE CONNECTION IDS FOUND!")
else:
    print("✅ No duplicate connection IDs")

print("\n=== TEST COMPLETE ===")
