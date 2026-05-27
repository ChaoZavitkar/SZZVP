"""Connection model - LIKES relationship"""

from models.database import get_db

class Connection:
    """Operace s likes (matching)"""

    @staticmethod
    def create(sender_id: str, receiver_id: str):
        """Vytvoř LIKES vztah (pokud neexistuje)"""
        db = get_db()
        try:
            # Kontrola existence
            if Connection.exists(sender_id, receiver_id):
                return {'id': receiver_id}

            result = db.execute('''
                MATCH (sender:User {id: $sender_id})
                MATCH (receiver:User {id: $receiver_id})
                CREATE (sender)-[:LIKES {created_at: datetime()}]->(receiver)
                RETURN receiver.id as id
            ''', sender_id=sender_id, receiver_id=receiver_id)
            return result[0] if result else None
        except Exception as e:
            print(f"Error creating like: {e}")
            return None

    @staticmethod
    def exists(user1_id: str, user2_id: str) -> bool:
        """Existuje již LIKES mezi dvěma uživateli?"""
        db = get_db()
        result = db.query('''
            MATCH (user1:User {id: $user1_id})-[:LIKES]->(user2:User {id: $user2_id})
            RETURN true
        ''', user1_id=user1_id, user2_id=user2_id)
        return len(result) > 0

    @staticmethod
    def is_mutual(user1_id: str, user2_id: str) -> bool:
        """Jsou si navzájem LIKES?"""
        db = get_db()
        result = db.query('''
            MATCH (u1:User {id: $u1})-[:LIKES]->(u2:User {id: $u2})
            MATCH (u2)-[:LIKES]->(u1)
            RETURN true
        ''', u1=user1_id, u2=user2_id)
        return len(result) > 0

    @staticmethod
    def delete(user1_id: str, user2_id: str):
        """Smaž LIKES vztah"""
        db = get_db()
        db.execute('''
            MATCH (user1:User {id: $u1})-[r:LIKES]->(user2:User {id: $u2})
            DELETE r
        ''', u1=user1_id, u2=user2_id)

    @staticmethod
    def get_all_for_user(user_id: str):
        """Vrať všechny kontakty (likes) pro uživatele"""
        db = get_db()
        result = db.query('''
            MATCH (user:User {id: $user_id})

            MATCH (user)-[:LIKES]->(liked_by_me:User)
            OPTIONAL MATCH (liked_by_me)-[:HAS_PROFILE]->(profile_me:Profile)
            OPTIONAL MATCH (user)-[:LIKES]-(liked_me:User)

            MATCH (others:User)
            WHERE (user)-[:LIKES]->(others) OR (others)-[:LIKES]->(user)

            OPTIONAL MATCH (others)-[:HAS_PROFILE]->(profile:Profile)
            OPTIONAL MATCH (user)-[:LIKES]->(others)
            OPTIONAL MATCH (others)-[:LIKES]->(user)

            WITH user, others, profile,
                 CASE WHEN (user)-[:LIKES]->(others) AND (others)-[:LIKES]->(user) THEN true ELSE false END as is_match,
                 CASE WHEN (user)-[:LIKES]->(others) THEN 'initiated' ELSE 'received' END as initiated_by

            RETURN DISTINCT others.id as user_id,
                   profile.nickname as nickname,
                   profile.bio as bio,
                   profile.nerd_level as nerd_level,
                   is_match,
                   initiated_by
            ORDER BY is_match DESC
        ''', user_id=user_id)
        return result
