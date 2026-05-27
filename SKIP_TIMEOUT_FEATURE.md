# Skip Timeout Feature

## Overview
Implemented a timeout mechanism for skipped profiles. When users skip a profile in the discover view, it is temporarily hidden and reappears after a configurable period.

## How It Works

### 1. Skip Action
When a user clicks "Přeskočit" on a profile:
1. A `SKIP` relationship is created: `User -[:SKIP {created_at: datetime()}]-> User`
2. The timestamp is automatically set to the current time
3. User is redirected to discover with filters preserved

### 2. Profile Exclusion
The `get_available_profiles()` function now excludes profiles with recent SKIP relationships:
```cypher
AND NOT (
    EXISTS {
        MATCH (user)-[skip:SKIP]->(other)
        WHERE skip.created_at > datetime() - duration({hours: $timeout_hours})
    }
)
```

This checks:
- Does a SKIP relationship exist? 
- If yes, was it created after (now - timeout_hours)?
- If both true, exclude the profile (it's still within timeout)

### 3. Timeout Expiration
When the timeout period expires, the SKIP relationship is no longer "recent" and the profile reappears in the discover view.

## Configuration

### SKIP_TIMEOUT_HOURS
Set in `config.py`:
```python
SKIP_TIMEOUT_HOURS = float(os.environ.get('SKIP_TIMEOUT_HOURS', '0.083'))  # 5 minut pro testing
```

**Default:** 0.083 hours = **5 minutes** (for testing)

**Production values:**
- 24 hours: `24` (skip for a full day)
- 7 days: `168` (skip for a week)
- 30 days: `720` (skip for a month)

### Changing Timeout
Set environment variable before running:
```bash
# For 24 hours (production)
export SKIP_TIMEOUT_HOURS=24
docker-compose up

# For 1 hour (testing)
export SKIP_TIMEOUT_HOURS=1
docker-compose up
```

Or pass in docker-compose.yml:
```yaml
services:
  flask:
    environment:
      - SKIP_TIMEOUT_HOURS=24
```

## Implementation Details

### Files Modified
1. **code/config.py** - Added SKIP_TIMEOUT_HOURS configuration
2. **code/models/connection.py** - Added `skip()` method
3. **code/routes/discover.py** - Updated queries and routes
4. **code/templates/discover/index.html** - Skip form now passes target_user_id

### Skip Method
```python
Connection.skip(sender_id, receiver_id)
```
Creates a SKIP relationship with timestamp. Can be called multiple times (doesn't fail on duplicate).

### Query Pattern
The Cypher query uses `duration.between()` to calculate time elapsed:
```cypher
duration.between(skip.created_at, datetime()) < duration({hours: $timeout_hours})
```

This compares:
- How long ago the skip was created
- Against the configured timeout period

## Per-User Isolation

Skips are **per-user**:
- Alice skips Bob → Bob hidden from Alice's discover
- Alice skips Bob → Bob NOT hidden from Charlie's discover
- Charlie can still see and interact with Bob normally

Query uses: `MATCH (user)-[skip:SKIP]->(other)` where user is the current session user.

## Interaction with Other Features

### LIKES vs SKIP
- **LIKE**: Permanent connection, profile never reappears
- **SKIP**: Temporary, profile reappears after timeout

A profile can be:
1. Not yet interacted with - shows in discover
2. Skipped - hidden for timeout period
3. Liked - never shows again (in discover)
4. After skip timeout - shows again in discover (unless later liked)

### Filter Preservation
Skip timeout respects all active filters:
- Nerd level range
- Selected interests
- Filters are preserved when skipping (maintained in redirect)

## Testing

### Manual Test Flow
1. **Login** with test account
2. **Go to Discover** - see available profiles
3. **Skip Profile A** - profile disappears
4. **Refresh page** or navigate away and back - Profile A should NOT appear
5. **Wait for timeout** (5 minutes with default config)
6. **Refresh page** - Profile A should reappear

### Test Cases
- ✅ Skipped profile disappears from results
- ✅ Skip is per-user (other users still see skipped profile)
- ✅ Filters preserved when skipping
- ✅ Skipped profile reappears after timeout
- ✅ Multiple skips work correctly
- ✅ Skip doesn't affect LIKES (can still like after timeout)

### Verify Configuration
```bash
# Check current timeout setting
docker logs flask | grep SKIP_TIMEOUT_HOURS

# Or in Python:
from config import Config
print(Config.SKIP_TIMEOUT_HOURS)  # Should print 0.083 (5 minutes)
```

## Database Queries

### Check All Skips for a User
```cypher
MATCH (u:User {id: $user_id})-[skip:SKIP]->(other:User)
OPTIONAL MATCH (other)-[:HAS_PROFILE]->(p:Profile)
RETURN p.nickname, skip.created_at, duration.between(skip.created_at, datetime()) as age
```

### Check if Specific Profile is Skipped
```cypher
MATCH (u:User {id: $user_id})-[skip:SKIP]->(other:User {id: $other_id})
WHERE duration.between(skip.created_at, datetime()) < duration({hours: $timeout_hours})
RETURN true
```

## Future Enhancements

### Possible Improvements
1. **UI Feedback**: Show when a skipped profile will reappear
   - "Available again in 3 days"
   - Only shown in profile details, not in list

2. **Skip Management**: Allow users to undo skip
   - Remove SKIP relationship
   - Profile reappears immediately

3. **Skip Analytics**: Track which profiles are most-skipped
   - Helps improve profile recommendations
   - Shows profile quality/appeal metrics

4. **Smart Timeout**: Adjust timeout based on user behavior
   - Skip frequently? Use shorter timeout
   - Skip rarely? Use longer timeout

5. **Skip Categories**: Different skip reasons
   - "Not interested"
   - "Wrong location"
   - "Missing info"
   - Different timeouts per category

## Troubleshooting

### Profile Not Reappearing
1. Check timeout value: `Config.SKIP_TIMEOUT_HOURS`
2. Verify Neo4j is tracking timestamps correctly
3. Check system time (Neo4j uses server time)
4. Clear browser cache if needed

### Skip Not Working
1. Ensure Flask reloaded: check logs for "Restarting with stat"
2. Verify SKIP relationship created: 
   ```cypher
   MATCH ()-[s:SKIP]->() RETURN count(s)
   ```
3. Check Flask errors: `docker logs flask`

## Performance Considerations

### Database Impact
- **Read**: Each discover view checks for recent SKIPs (negligible impact)
- **Write**: One SKIP relationship created per skip action
- **Cleanup**: Old SKIP relationships are kept (minimal storage impact)

### Query Optimization
The query uses `EXISTS` subquery which is efficient in Neo4j:
- Stops checking as soon as one recent SKIP is found
- Doesn't require scanning all SKIP relationships
- Duration calculation is fast

## Notes
- SKIP relationships use Neo4j's built-in `datetime()` function
- Duration is calculated server-side (Neo4j) for accuracy
- Multiple skips on same profile just overwrite (new timestamp)
- Timeout is rounded to hours (0.083 hours = 5 minutes, not exact)
