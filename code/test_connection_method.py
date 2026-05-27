#!/usr/bin/env python
"""Test actual Connection.create() method"""
import sys
sys.path.insert(0, '/code')

from app import app
from models.connection import Connection

# Initialize with Flask context
with app.app_context():
    from models.database import get_db

    db = get_db()
    db_neo4j = db.graph

    # Get users
    alice = db_neo4j.run('MATCH (u:User {email: $e}) RETURN u.id as id', e='alice@example.com').data()[0]['id']
    bob = db_neo4j.run('MATCH (u:User {email: $e}) RETURN u.id as id', e='bob@example.com').data()[0]['id']

    print("=" * 70)
    print("TEST: Actual Connection.create() Method")
    print("=" * 70)

    # Vyčistit
    db_neo4j.run('MATCH (c:Connection) DETACH DELETE c')

    # Test 1: Alice likes Bob
    print("\n1️⃣ Alice calls Connection.create(alice_id, bob_id)")
    conn1 = Connection.create(alice, bob)
    print(f"   Result: Created connection")

    # Count connections
    conns = db_neo4j.run('MATCH (c:Connection) RETURN count(c) as cnt').data()
    print(f"   Total in DB: {conns[0]['cnt']}")

    # Test 2: Bob likes Alice
    print("\n2️⃣ Bob calls Connection.create(bob_id, alice_id)")
    conn2 = Connection.create(bob, alice)
    print(f"   Result: Updated/Created connection")

    # Count connections
    conns = db_neo4j.run('MATCH (c:Connection) RETURN count(c) as cnt').data()
    print(f"   Total in DB: {conns[0]['cnt']}")

    # Check final state
    print("\n📊 FINAL STATE:")
    final = db_neo4j.run('''
        MATCH (u1:User)-[:INITIATED_CONNECTION]->(c:Connection)<-[:RECEIVED_CONNECTION]-(u2:User)
        OPTIONAL MATCH (u1)-[:HAS_PROFILE]->(p1:Profile)
        OPTIONAL MATCH (u2)-[:HAS_PROFILE]->(p2:Profile)
        RETURN p1.nickname as from_nick, p2.nickname as to_nick, c.is_match as m, c.id as cid
    ''').data()

    print(f"Total Connections: {len(final)}")
    for c in final:
        print(f"  {c['from_nick']} -> {c['to_nick']}: is_match={c['m']} (id={c['cid'][:8]}...)")

    # Check for duplicates
    alice_bob_conns = db_neo4j.run('''
        MATCH (alice:User {email: 'alice@example.com'})-[:INITIATED_CONNECTION|:RECEIVED_CONNECTION]-(c:Connection)-[:INITIATED_CONNECTION|:RECEIVED_CONNECTION]-(bob:User {email: 'bob@example.com'})
        WHERE c.is_deleted = false
        RETURN count(c) as cnt
    ''').data()

    if alice_bob_conns[0]['cnt'] == 1:
        print(f"\n✅ SUCCESS: Only 1 connection between Alice & Bob")
    else:
        print(f"\n❌ ERROR: {alice_bob_conns[0]['cnt']} connections between Alice & Bob (expected 1)")

    print("\n" + "=" * 70)
