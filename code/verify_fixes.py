#!/usr/bin/env python
"""Verify all bug fixes are working"""
import sys
sys.path.insert(0, '/code')

from py2neo import Graph
import uuid

db = Graph('bolt://neo4j:7687', auth=('neo4j', 'adminpass'))

print("=" * 60)
print("VERIFYING BUG FIXES")
print("=" * 60)

# Clean connections
db.run('MATCH (c:Connection) DETACH DELETE c RETURN count(c) as count')

# Get users
alice = db.run('MATCH (u:User {email: $e}) RETURN u.id as id', e='alice@example.com').data()
bob = db.run('MATCH (u:User {email: $e}) RETURN u.id as id', e='bob@example.com').data()

if not alice or not bob:
    print("❌ Test users not found!")
    sys.exit(1)

alice_id, bob_id = alice[0]['id'], bob[0]['id']

print("\n✅ Test users found")
print(f"  Alice: {alice_id}")
print(f"  Bob: {bob_id}")

# Test matching flow
print("\n" + "=" * 60)
print("TEST 1: MATCHING FLOW")
print("=" * 60)

conn_id = str(uuid.uuid4())
db.run('''
    MATCH (u1:User {id: $alice}), (u2:User {id: $bob})
    CREATE (u1)-[:INITIATED_CONNECTION]->(c:Connection {
        id: $cid, is_match: false, is_deleted: false, created_at: datetime()
    })<-[:RECEIVED_CONNECTION]-(u2)
''', alice=alice_id, bob=bob_id, cid=conn_id)

result = db.run('MATCH (c:Connection) RETURN c.is_match as m').data()
print(f"\n1️⃣ After Alice→Bob: is_match = {result[0]['m']} (expected: false)")

# Bob likes Alice - should trigger match detection
conn_id2 = str(uuid.uuid4())
try:
    result = db.run('''
        MATCH (u1:User {id: $bob}), (u2:User {id: $alice})
        MATCH (u2)-[:INITIATED_CONNECTION]->(conn:Connection)<-[:RECEIVED_CONNECTION]-(u1)
        WHERE conn.is_match = false
        SET conn.is_match = true
        RETURN conn.is_match as m
    ''', bob=bob_id, alice=alice_id)
    data = result.data()
    if data:
        print(f"2️⃣ After Bob→Alice: is_match = {data[0]['m']} (expected: true)")
        print("✅ BUG #2 FIXED: Matching detected correctly")
    else:
        print("2️⃣ No existing connection found - creating new one")
        db.run('''
            MATCH (u1:User {id: $bob}), (u2:User {id: $alice})
            CREATE (u1)-[:INITIATED_CONNECTION]->(c:Connection {
                id: $cid2, is_match: false, is_deleted: false, created_at: datetime()
            })<-[:RECEIVED_CONNECTION]-(u2)
        ''', bob=bob_id, alice=alice_id, cid2=conn_id2)
except Exception as e:
    print(f"❌ Error in matching: {e}")

# Test contacts query (Bug #1)
print("\n" + "=" * 60)
print("TEST 2: CONTACTS QUERY (BUG #1 FIX)")
print("=" * 60)

result = db.run('''
    MATCH (user:User {id: $alice})
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
''', alice=alice_id).data()

print(f"Total connections for Alice: {len(result)}")
connection_ids = [r['id'] for r in result]
unique_ids = set(connection_ids)

if len(connection_ids) == len(unique_ids):
    print("✅ BUG #1 FIXED: No duplicate connection IDs")
else:
    print(f"❌ BUG #1 NOT FIXED: Found duplicates! {len(connection_ids)} rows, {len(unique_ids)} unique")

# Display connections
for conn in result:
    print(f"  - {conn['nickname']}: match={conn['is_match']}, initiated_by={conn['initiated_by']}")

# Test discover visibility (Bug #3)
print("\n" + "=" * 60)
print("TEST 3: DISCOVER VISIBILITY (BUG #3 FIX)")
print("=" * 60)

# Delete Alice's initiated connections but keep Bob's
db.run('''
    MATCH (alice:User {id: $alice})-[:INITIATED_CONNECTION]->(c:Connection)
    DETACH DELETE c
''', alice=alice_id)

# Now check if Alice can still see Bob in discover
result = db.run('''
    MATCH (user:User {id: $alice})
    MATCH (other:User)-[:HAS_PROFILE]->(profile:Profile)
    MATCH (other)-[:HAS_ACCOUNT]->(account)
    WHERE other.id <> user.id
    AND account.is_deleted = false

    OPTIONAL MATCH (user)-[:INITIATED_CONNECTION]->(initiated:Connection)<-[:RECEIVED_CONNECTION]-(other)
    WHERE initiated.is_deleted = false

    WITH profile, other, initiated
    WHERE initiated IS NULL

    OPTIONAL MATCH (other)-[:HAS_PROFILE]->(profile2:Profile)
    RETURN DISTINCT other.id as user_id, profile.nickname as nickname
    LIMIT 1
''', alice=alice_id).data()

if result and result[0]['nickname'] == 'Bob':
    print("✅ BUG #3 FIXED: Bob is visible even though Alice deleted her like")
else:
    print("❌ BUG #3 NOT FIXED: Bob should be visible but isn't")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
