"""User model"""

import bcrypt
import uuid
from models.database import get_db

class User:
    """Operace s uživateli"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hashuj heslo"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Ověř heslo"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    @staticmethod
    def email_exists(email: str) -> bool:
        """Email existuje?"""
        db = get_db()
        result = db.query('MATCH (u:User {email: $email}) RETURN u', email=email.lower())
        return len(result) > 0

    @staticmethod
    def create(email: str, password: str):
        """Vytvoř uživatele"""
        db = get_db()
        if User.email_exists(email):
            return None
        password_hash = User.hash_password(password)
        user_id = str(uuid.uuid4())
        try:
            result = db.execute('''
                CREATE (user:User {id: $id, email: $email, password_hash: $password_hash, created_at: datetime()})
                CREATE (account:Account {user_id: $id, last_login: null, last_activity: null, login_attempts: 0, is_deleted: false})
                CREATE (user)-[:HAS_ACCOUNT]->(account)
                RETURN user.id as id, user.email as email
            ''', id=user_id, email=email.lower(), password_hash=password_hash)
            return result[0] if result else None
        except Exception as e:
            print(f"Error: {e}")
            return None

    @staticmethod
    def get_by_email(email: str):
        """Najdi uživatele"""
        db = get_db()
        result = db.query('''
            MATCH (user:User {email: $email})
            MATCH (user)-[:HAS_ACCOUNT]->(account)
            WHERE account.is_deleted = false
            RETURN user.id as id, user.password_hash as password_hash
        ''', email=email.lower())
        return result[0] if result else None

    @staticmethod
    def get_by_id(user_id: str):
        """Najdi podle ID"""
        db = get_db()
        result = db.query('MATCH (user:User {id: $id}) RETURN user.id as id, user.email as email', id=user_id)
        return result[0] if result else None

    @staticmethod
    def update_last_login(user_id: str):
        """Update login"""
        db = get_db()
        db.execute('''
            MATCH (user:User {id: $id})-[:HAS_ACCOUNT]->(account)
            SET account.last_login = datetime(), account.last_activity = datetime(), account.login_attempts = 0
        ''', id=user_id)

    @staticmethod
    def delete(user_id: str):
        """Smaž uživatele"""
        db = get_db()
        db.execute('''
            MATCH (user:User {id: $id})-[:HAS_ACCOUNT]->(account)
            SET account.is_deleted = true, account.deleted_at = datetime()
            OPTIONAL MATCH (user)-[:HAS_PROFILE]->(profile)
            DETACH DELETE profile
        ''', id=user_id)
