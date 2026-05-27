"""Connection model - pro Like/Match"""

from models.database import get_db
import uuid

class Connection:
    """Operace s konekcemi (Like/Match)"""

    @staticmethod
    def create(sender_id: str, receiver_id: str):
        """Vytvoř novou konekci (like)"""
        db = get_db()
        try:
            connection_id = str(uuid.uuid4())
            result = db.execute('''
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
                OPTIONAL MATCH (conn2:Connection)
                WHERE (conn2)-[:INITIATED_CONNECTION]-(receiver)
                AND (conn2)-[:RECEIVED_CONNECTION]-(sender)
                AND conn2.is_match = false
                AND conn2.is_deleted = false

                FOREACH (c IN CASE WHEN conn2 IS NOT NULL THEN [conn2] ELSE [] END |
                    SET c.is_match = true,
                        conn.is_match = true
                )

                RETURN conn
            ''', conn_id=connection_id, sender_id=sender_id, receiver_id=receiver_id)
            return result[0] if result else None
        except Exception as e:
            print(f"Error creating connection: {e}")
            return None

    @staticmethod
    def exists(user1_id: str, user2_id: str) -> bool:
        """Existuje již konekce mezi dvěma uživateli?"""
        db = get_db()
        result = db.query('''
            MATCH (user1:User {id: $user1_id})
            MATCH (user2:User {id: $user2_id})
            MATCH (user1)-[:INITIATED_CONNECTION|:RECEIVED_CONNECTION]-(conn:Connection)-[:INITIATED_CONNECTION|:RECEIVED_CONNECTION]-(user2)
            WHERE conn.is_deleted = false
            RETURN conn
        ''', user1_id=user1_id, user2_id=user2_id)
        return len(result) > 0

    @staticmethod
    def delete(connection_id: str):
        """Smaž konekci (soft delete)"""
        db = get_db()
        db.execute('''
            MATCH (conn:Connection {id: $conn_id})
            SET conn.is_deleted = true, conn.deleted_at = datetime()
        ''', conn_id=connection_id)

    @staticmethod
    def get_all_for_user(user_id: str):
        """Vrať všechny konekce pro uživatele"""
        db = get_db()
        result = db.query('''
            MATCH (user:User {id: $user_id})
            MATCH (user)-[:INITIATED_CONNECTION|:RECEIVED_CONNECTION]-(conn:Connection)-[:INITIATED_CONNECTION|:RECEIVED_CONNECTION]-(other:User)
            WHERE conn.is_deleted = false
            OPTIONAL MATCH (other)-[:HAS_PROFILE]->(profile:Profile)
            RETURN conn.id as id,
                   conn.is_match as is_match,
                   conn.created_at as created_at,
                   other.id as user_id,
                   profile.nickname as nickname
            ORDER BY conn.is_match DESC, conn.created_at DESC
        ''', user_id=user_id)
        return result
