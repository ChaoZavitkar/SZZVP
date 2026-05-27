#!/usr/bin/env python
"""Test matching flow and check for duplicates"""
import sys
sys.path.insert(0, '/code')

from py2neo import Graph
import uuid

# Create direct database connection
db = Graph('bolt://neo4j:7687', auth=('neo4j', 'adminpass'))

# Get test users
print("Checking test users...")
alice_result = db.run('MATCH (u:User {email: $email}) RETURN u.id as id', email='alice@example.com')
alice = alice_result.data()
if not alice:
    print("❌ Alice not found!")
    sys.exit(1)
alice_id = alice[0]['id']

bob_result = db.run('MATCH (u:User {email: $email}) RETURN u.id as id', email='bob@example.com')
bob = bob_result.data()
if not bob:
    print("❌ Bob not found!")
    sys.exit(1)
bob_id = bob[0]['id']

print(f"✅ Alice (ID: {alice_id})")
print(f"✅ Bob (ID: {bob_id})")

# Clear any existing connections
print("\nClearing existing connections...")
result = db.run('MATCH (c:Connection) DETACH DELETE c RETURN count(c) as count')
count = result.data()[0]['count']
print(f"Deleted {count} connections")

# Test 1: Alice likes Bob
print("\n=== TEST 1: Alice likes Bob ===")
conn_id = str(uuid.uuid4())
db.run('''
    MATCH (u1:User {id: $user_id_1})
    MATCH (u2:User {id: $user_id_2})
    CREATE (u1)-[:INITIATED_CONNECTION]->(conn:Connection {
        id: $conn_id,
        is_match: false,
        is_deleted: false,
        created_at: datetime()
    })<-[:RECEIVED_CONNECTION]-(u2)
''', user_id_1=alice_id, user_id_2=bob_id, conn_id=conn_id)
print(f"Connection created: {conn_id}")

result = db.run('MATCH (c:Connection)-[:INITIATED_CONNECTION]-(u1:User) MATCH (c)-[:RECEIVED_CONNECTION]-(u2:User) RETURN c.id as id, c.is_match as is_match, u1.id as initiator, u2.id as receiver')
print(f"After Alice→Bob: {result.data()}")

# Test 2: Bob likes Alice
print("\n=== TEST 2: Bob likes Alice ===")
# Check if connection already exists between Bob and Alice in EITHER direction
existing = db.run('''
    MATCH (u1:User {id: $user_id_1})
    MATCH (u2:User {id: $user_id_2})
    MATCH (u1)-[:INITIATED_CONNECTION]->(conn:Connection)<-[:RECEIVED_CONNECTION]-(u2)
    RETURN conn.id as id, u1.id as initiator
''', user_id_1=bob_id, user_id_2=alice_id).data()

# If no match, try the opposite direction
if not existing:
    existing = db.run('''
        MATCH (u1:User {id: $user_id_1})
        MATCH (u2:User {id: $user_id_2})
        MATCH (u2)-[:INITIATED_CONNECTION]->(conn:Connection)<-[:RECEIVED_CONNECTION]-(u1)
        RETURN conn.id as id, u2.id as initiator
    ''', user_id_1=bob_id, user_id_2=alice_id).data()

if existing:
    # Connection already exists, mark as match
    conn_id_existing = existing[0]['id']
    db.run('''
        MATCH (c:Connection {id: $conn_id})
        SET c.is_match = true
    ''', conn_id=conn_id_existing)
    print(f"Marked existing connection as match: {conn_id_existing}")
else:
    # Create new connection from Bob to Alice
    conn_id_2 = str(uuid.uuid4())
    db.run('''
        MATCH (u1:User {id: $user_id_1})
        MATCH (u2:User {id: $user_id_2})
        CREATE (u1)-[:INITIATED_CONNECTION]->(conn:Connection {
            id: $conn_id,
            is_match: false,
            is_deleted: false,
            created_at: datetime()
        })<-[:RECEIVED_CONNECTION]-(u2)
    ''', user_id_1=bob_id, user_id_2=alice_id, conn_id=conn_id_2)
    print(f"Created new connection: {conn_id_2}")

result = db.run('MATCH (c:Connection)-[:INITIATED_CONNECTION]-(u1:User) MATCH (c)-[:RECEIVED_CONNECTION]-(u2:User) RETURN c.id as id, c.is_match as is_match, u1.id as initiator, u2.id as receiver')
print(f"After Bob→Alice: {result.data()}")

# Test 3: Check Alice's contacts (should see Bob as match)
print("\n=== TEST 3: Alice's Contacts (should have 1 match) ===")
result = db.run('''
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
''', user_id=alice_id)

data = result.data()
print(f"Total connections: {len(data)}")
matches = [r for r in data if r['is_match']]
one_way = [r for r in data if not r['is_match']]
print(f"  Matches (is_match=true): {len(matches)}")
print(f"  One-way (is_match=false): {len(one_way)}")

for conn in data:
    print(f"  - {conn['nickname']} (match={conn['is_match']}, initiated_by={conn['initiated_by']})")

# Check for duplicate IDs
connection_ids = [r['id'] for r in data]
if len(connection_ids) != len(set(connection_ids)):
    print("❌ DUPLICATE CONNECTION IDS FOUND!")
    from collections import Counter
    dups = [id for id, count in Counter(connection_ids).items() if count > 1]
    print(f"Duplicates: {dups}")
else:
    print("✅ No duplicate connection IDs")

# Test 4: Check Bob's contacts (should see Alice as match)
print("\n=== TEST 4: Bob's Contacts (should have 1 match) ===")
result = db.run('''
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
''', user_id=bob_id)

data = result.data()
print(f"Total connections: {len(data)}")
matches = [r for r in data if r['is_match']]
one_way = [r for r in data if not r['is_match']]
print(f"  Matches (is_match=true): {len(matches)}")
print(f"  One-way (is_match=false): {len(one_way)}")

for conn in data:
    print(f"  - {conn['nickname']} (match={conn['is_match']}, initiated_by={conn['initiated_by']})")

# Check for duplicate IDs
connection_ids = [r['id'] for r in data]
if len(connection_ids) != len(set(connection_ids)):
    print("❌ DUPLICATE CONNECTION IDS FOUND!")
else:
    print("✅ No duplicate connection IDs")

print("\n=== TEST COMPLETE ===")
