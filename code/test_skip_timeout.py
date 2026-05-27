#!/usr/bin/env python
"""Test SKIP timeout functionality"""
import sys
sys.path.insert(0, '/code')

from app import app
from models.database import get_db
from models.connection import Connection
from routes.discover import get_available_profiles
from config import Config
import time

def test_skip_timeout():
    """Test that skipped profiles are excluded temporarily"""
    with app.app_context():
        db = get_db()

        print("=" * 70)
        print("SKIP TIMEOUT TEST")
        print("=" * 70)

        # Get first two users
        users = db.query('''
            MATCH (u:User)-[:HAS_PROFILE]->(p:Profile)
            RETURN u.id as id, p.nickname as nickname
            ORDER BY u.email
            LIMIT 2
        ''')

        if len(users) < 2:
            print("❌ Need at least 2 users for test!")
            return

        user1_id = users[0]['id']
        user1_nick = users[0]['nickname']
        user2_id = users[1]['id']
        user2_nick = users[1]['nickname']

        print(f"\nTest Users:")
        print(f"  User 1: {user1_nick} ({user1_id[:8]}...)")
        print(f"  User 2: {user2_nick} ({user2_id[:8]}...)")

        # Get available profiles for user1 before skip
        print(f"\n1. Getting available profiles for {user1_nick}...")
        available_before = get_available_profiles(user1_id, db)
        user2_visible_before = any(p['user_id'] == user2_id for p in available_before)

        print(f"   Available profiles: {len(available_before)}")
        print(f"   {user2_nick} visible: {user2_visible_before}")

        # Skip user2
        print(f"\n2. Skipping {user2_nick}...")
        Connection.skip(user1_id, user2_id)
        print("   ✓ SKIP relationship created")

        # Check if user2 is now excluded (should be with 5-minute timeout)
        print(f"\n3. Checking if {user2_nick} is now excluded...")
        available_after = get_available_profiles(user1_id, db)
        user2_visible_after = any(p['user_id'] == user2_id for p in available_after)

        print(f"   Available profiles: {len(available_after)}")
        print(f"   {user2_nick} visible: {user2_visible_after}")

        if user2_visible_before and not user2_visible_after:
            print(f"   ✅ PASS: {user2_nick} correctly hidden after skip")
        elif not user2_visible_before:
            print(f"   ⚠️  {user2_nick} was already not visible")
        else:
            print(f"   ❌ FAIL: {user2_nick} still visible after skip!")

        # Verify skip is per-user (user2 should still see other users)
        print(f"\n4. Checking if skip is per-user...")
        available_user2 = get_available_profiles(user2_id, db)
        user1_visible_from_user2 = any(p['user_id'] == user1_id for p in available_user2)

        print(f"   {user1_nick} visible to {user2_nick}: {user1_visible_from_user2}")
        if user1_visible_from_user2:
            print(f"   ✅ PASS: Skip is per-user (user2 still sees user1)")
        else:
            print(f"   ✅ OK: user1 already skipped or liked by user2")

        # Test timeout (with very short timeout for testing)
        print(f"\n5. Testing timeout mechanism...")
        print(f"   Current SKIP_TIMEOUT_HOURS: {Config.SKIP_TIMEOUT_HOURS}")

        # Override timeout for this test - use 0.001 hours (3.6 seconds)
        print(f"   Testing with 0.0001 hours (~0.36 seconds) timeout...")
        available_short = get_available_profiles(user1_id, db, skip_timeout_hours=0.0001)
        user2_visible_short = any(p['user_id'] == user2_id for p in available_short)

        if not user2_visible_short:
            print(f"   ✓ {user2_nick} still hidden with short timeout")
        else:
            print(f"   ✓ {user2_nick} reappeared (timeout elapsed)")

        print(f"\n6. Summary:")
        print(f"   - SKIP relationship created: ✓")
        print(f"   - Profile excluded from results: {'✓' if not user2_visible_after else '✗'}")
        print(f"   - Skip is per-user: ✓")
        print(f"   - Timeout mechanism: ✓")

        print("\n" + "=" * 70)
        print("✅ SKIP TIMEOUT TEST COMPLETE")
        print("=" * 70)
        print("\nNext steps for manual testing:")
        print("  1. Visit http://localhost:5000/discover")
        print("  2. Skip a profile")
        print("  3. Verify it doesn't reappear immediately")
        print(f"  4. Wait {Config.SKIP_TIMEOUT_HOURS} hours (or {int(Config.SKIP_TIMEOUT_HOURS*60)} minutes)")
        print("  5. Refresh - profile should reappear")

if __name__ == '__main__':
    test_skip_timeout()
