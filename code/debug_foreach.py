#!/usr/bin/env python
"""Debug FOREACH in Connection.create()"""
import sys
sys.path.insert(0, '/code')

from py2neo import Graph
import uuid

db = Graph('bolt://neo4j:7687', auth=('neo4j', 'adminpass'))

alice = db.run('MATCH (u:User {email: $e}) RETURN u.id as id', e='alice@example.com').data()[0]['id']
bob = db.run('MATCH (u:User {email: $e}) RETURN u.id as id', e='bob@example.com').data()[0]['id']

print("=" * 70)
print("DEBUG: OPTIONAL MATCH v FOREACH")
print("=" * 70)

# Vyčistit
db.run('MATCH (c:Connection) DETACH DELETE c')

# Vytvoříme Connection od Alice
conn_id_1 = str(uuid.uuid4())
db.run('''
    CREATE (conn:Connection {id: $cid, created_at: datetime(), is_match: false, is_deleted: false})
    MATCH (alice:User {id: $alice}), (bob:User {id: $bob})
    CREATE (alice)-[:INITIATED_CONNECTION]->(conn)<-[:RECEIVED_CONNECTION]-(bob)
''', cid=conn_id_1, alice=alice, bob=bob)

print(f"\n✓ Vytvořena Connection od Alice k Bobovi: {conn_id_1[:8]}...")

# Teď testujeme OPTIONAL MATCH - hledáme Connection když Bob lajkne Alice
print("\nTest OPTIONAL MATCH (bob jako sender, alice jako receiver):")
test = db.run('''
    MATCH (sender:User {id: $sender_id})
    MATCH (receiver:User {id: $receiver_id})

    OPTIONAL MATCH (receiver)-[:INITIATED_CONNECTION]->(conn2:Connection)<-[:RECEIVED_CONNECTION]-(sender)
    WHERE conn2.is_match = false
    AND conn2.is_deleted = false

    RETURN
        sender.id as sender_id,
        receiver.id as receiver_id,
        conn2.id as found_conn_id,
        CASE WHEN conn2 IS NOT NULL THEN 'FOUND' ELSE 'NOT FOUND' END as result
''', sender_id=bob, receiver_id=alice).data()

print(f"Result: {test[0]}")

if test[0]['found_conn_id']:
    print(f"✓ Nástroj NAŠEL existující Connection: {test[0]['found_conn_id'][:8]}...")
else:
    print(f"✗ PROBLÉM: Nástroj NENAŠEL existující Connection!")

# Teď testujeme samotný FOREACH
print("\n" + "-" * 70)
print("Test FOREACH setování is_match:")

conn_id_2 = str(uuid.uuid4())
result = db.run('''
    CREATE (conn:Connection {
        id: $new_conn_id,
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

    WITH conn, conn2
    FOREACH (c IN CASE WHEN conn2 IS NOT NULL THEN [conn2] ELSE [] END |
        SET c.is_match = true,
            conn.is_match = true
    )

    RETURN
        conn.id as new_id,
        conn.is_match as new_match,
        CASE WHEN conn2 IS NOT NULL THEN conn2.id ELSE 'NULL' END as existing_id,
        CASE WHEN conn2 IS NOT NULL THEN conn2.is_match ELSE null END as existing_match
''', new_conn_id=conn_id_2, sender_id=bob, receiver_id=alice).data()

print(f"Result: {result[0]}")

# Finální kontrola v DB
print("\n" + "-" * 70)
print("Finální stav databáze:")

conns = db.run('''
    MATCH (u1:User)-[:INITIATED_CONNECTION]->(c:Connection)<-[:RECEIVED_CONNECTION]-(u2:User)
    RETURN u1.id as u1, u2.id as u2, c.id as id, c.is_match as m
    ORDER BY c.created_at
''').data()

print(f"Total Connections: {len(conns)}")
for c in conns:
    alice_init = "Alice-INIT" if c['u1'] == alice else "Bob-INIT"
    print(f"  {alice_init}: is_match={c['m']} (id={c['id'][:8]}...)")

print("\n" + "=" * 70)
