#!/usr/bin/env python
"""Test Connection.create() matching logic"""
import sys
sys.path.insert(0, '/code')

from py2neo import Graph
import uuid

db = Graph('bolt://neo4j:7687', auth=('neo4j', 'adminpass'))

# Get Alice and Bob
alice = db.run('MATCH (u:User {email: $e}) RETURN u.id as id', e='alice@example.com').data()[0]['id']
bob = db.run('MATCH (u:User {email: $e}) RETURN u.id as id', e='bob@example.com').data()[0]['id']

print("=" * 70)
print("TEST: CONNECTION.CREATE() - Matching Logic")
print("=" * 70)

# Vyčistit konekce
db.run('MATCH (c:Connection) DETACH DELETE c')

# Test 1: Alice likes Bob
print("\n1️⃣ Alice likes Bob")
conn_id_1 = str(uuid.uuid4())
db.run('''
    CREATE (conn:Connection {
        id: $cid,
        created_at: datetime(),
        is_match: false,
        is_deleted: false
    })
    MATCH (sender:User {id: $sender_id})
    MATCH (receiver:User {id: $receiver_id})
    CREATE (sender)-[:INITIATED_CONNECTION]->(conn)<-[:RECEIVED_CONNECTION]-(receiver)
    RETURN conn
''', cid=conn_id_1, sender_id=alice, receiver_id=bob)

conns = db.run('MATCH (c:Connection) RETURN c.id as id, c.is_match as m').data()
print(f"   Connections in DB: {len(conns)}")
for c in conns:
    print(f"     - {c['id'][:8]}... is_match={c['m']}")

# Test 2: Bob likes Alice - simulate what Connection.create() does
print("\n2️⃣ Bob likes Alice (Connection.create simulation)")
conn_id_2 = str(uuid.uuid4())

# Toto je přesně co se dělá v Connection.create()
result = db.run('''
    CREATE (conn:Connection {
        id: $conn_id,
        created_at: datetime(),
        is_match: false,
        is_deleted: false
    })
    MATCH (sender:User {id: $sender_id})
    MATCH (receiver:User {id: $receiver_id})
    CREATE (sender)-[:INITIATED_CONNECTION]->(conn)<-[:RECEIVED_CONNECTION]-(receiver)

    // Kontrola na vzájemný like
    OPTIONAL MATCH (receiver)-[:INITIATED_CONNECTION]->(conn2:Connection)<-[:RECEIVED_CONNECTION]-(sender)
    WHERE conn2.is_match = false
    AND conn2.is_deleted = false

    FOREACH (c IN CASE WHEN conn2 IS NOT NULL THEN [conn2] ELSE [] END |
        SET c.is_match = true,
            conn.is_match = true
    )

    RETURN conn.id as new_conn_id, conn.is_match as new_is_match
''', conn_id=conn_id_2, sender_id=bob, receiver_id=alice)

data = result.data()
if data:
    print(f"   Returned: id={data[0]['new_conn_id'][:8]}... is_match={data[0]['new_is_match']}")

# Check final state
print("\n📊 FINAL STATE:")
conns = db.run('''
    MATCH (u1:User)-[:INITIATED_CONNECTION]->(c:Connection)<-[:RECEIVED_CONNECTION]-(u2:User)
    OPTIONAL MATCH (u1)-[:HAS_PROFILE]->(p1:Profile)
    OPTIONAL MATCH (u2)-[:HAS_PROFILE]->(p2:Profile)
    RETURN p1.nickname as from_nick, p2.nickname as to_nick, c.is_match as m, c.id as cid
''').data()

print(f"Total Connections: {len(conns)}")
for c in conns:
    print(f"  {c['from_nick']} -> {c['to_nick']}: is_match={c['m']} (id={c['cid'][:8]}...)")

# Check for duplicates between Alice and Bob
alice_bob_conns = db.run('''
    MATCH (alice:User {email: $alice_email})-[:INITIATED_CONNECTION|:RECEIVED_CONNECTION]-(c:Connection)-[:INITIATED_CONNECTION|:RECEIVED_CONNECTION]-(bob:User {email: $bob_email})
    WHERE c.is_deleted = false
    RETURN c.id as id, c.is_match as m
''', alice_email='alice@example.com', bob_email='bob@example.com').data()

print(f"\nConnections between Alice & Bob: {len(alice_bob_conns)}")
if len(alice_bob_conns) > 1:
    print("❌ ERROR: Multiple connections between same users!")
    for c in alice_bob_conns:
        print(f"  - {c['id'][:8]}... is_match={c['m']}")
else:
    print("✅ OK: Only 1 connection")
    if alice_bob_conns:
        print(f"  - is_match={alice_bob_conns[0]['m']}")

print("\n" + "=" * 70)
