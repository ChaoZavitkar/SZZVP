"""Profile model"""

from models.database import get_db
from datetime import datetime

class Profile:
    """Operace s profily"""

    @staticmethod
    def exists(user_id: str) -> bool:
        """Profil existuje?"""
        db = get_db()
        result = db.query('MATCH (p:Profile {user_id: $user_id}) RETURN p', user_id=user_id)
        return len(result) > 0

    @staticmethod
    def create(user_id: str, nickname: str, bio: str = "", nerd_level: int = 5):
        """Vytvoř profil"""
        db = get_db()
        if Profile.exists(user_id):
            return None
        try:
            result = db.execute('''
                MATCH (user:User {id: $user_id})
                CREATE (profile:Profile {
                    user_id: $user_id,
                    nickname: $nickname,
                    bio: $bio,
                    nerd_level: $nerd_level,
                    is_public: true,
                    created_at: datetime(),
                    updated_at: datetime()
                })
                CREATE (user)-[:HAS_PROFILE]->(profile)
                RETURN profile.user_id as user_id, profile.nickname as nickname
            ''', user_id=user_id, nickname=nickname, bio=bio, nerd_level=nerd_level)
            return result[0] if result else None
        except Exception as e:
            print(f"Error creating profile: {e}")
            return None

    @staticmethod
    def get_by_user_id(user_id: str):
        """Najdi profil uživatele"""
        db = get_db()
        result = db.query('''
            MATCH (profile:Profile {user_id: $user_id})
            OPTIONAL MATCH (profile)-[:INTERESTED_IN]->(interest:InterestCategory)
            OPTIONAL MATCH (profile)-[:LIKES_TECHNOLOGY]->(tech:Technology)
            RETURN profile.user_id as user_id,
                   profile.nickname as nickname,
                   profile.bio as bio,
                   profile.nerd_level as nerd_level,
                   profile.is_public as is_public,
                   collect(DISTINCT interest.name) as interests,
                   collect(DISTINCT tech.name) as technologies
        ''', user_id=user_id)
        return result[0] if result else None

    @staticmethod
    def get_by_nickname(nickname: str):
        """Najdi profil podle přezdívky"""
        db = get_db()
        result = db.query('''
            MATCH (profile:Profile {nickname: $nickname})
            OPTIONAL MATCH (profile)-[:INTERESTED_IN]->(interest:InterestCategory)
            OPTIONAL MATCH (profile)-[:LIKES_TECHNOLOGY]->(tech:Technology)
            RETURN profile.user_id as user_id,
                   profile.nickname as nickname,
                   profile.bio as bio,
                   profile.nerd_level as nerd_level,
                   collect(DISTINCT interest.name) as interests,
                   collect(DISTINCT tech.name) as technologies
        ''', nickname=nickname)
        return result[0] if result else None

    @staticmethod
    def nickname_exists(nickname: str, exclude_user_id: str = None):
        """Přezdívka již existuje?"""
        db = get_db()
        if exclude_user_id:
            result = db.query('''
                MATCH (p:Profile {nickname: $nickname})
                WHERE p.user_id <> $user_id
                RETURN p
            ''', nickname=nickname, user_id=exclude_user_id)
        else:
            result = db.query('MATCH (p:Profile {nickname: $nickname}) RETURN p', nickname=nickname)
        return len(result) > 0

    @staticmethod
    def update(user_id: str, nickname: str, bio: str, nerd_level: int, interests: list, technologies: list):
        """Aktualizuj profil"""
        db = get_db()
        try:
            # Zkontroluj, že přezdívka není obsazená (kromě tohoto uživatele)
            if Profile.nickname_exists(nickname, exclude_user_id=user_id):
                return None

            # Aktualizuj základní info a vazby
            result = db.execute('''
                MATCH (profile:Profile {user_id: $user_id})
                SET profile.nickname = $nickname,
                    profile.bio = $bio,
                    profile.nerd_level = $nerd_level,
                    profile.updated_at = datetime()

                // Odstraň staré vazby na zájmy
                OPTIONAL MATCH (profile)-[r:INTERESTED_IN]->()
                DELETE r

                // Odstraň staré vazby na technologie
                OPTIONAL MATCH (profile)-[t:LIKES_TECHNOLOGY]->()
                DELETE t

                RETURN profile
            ''', user_id=user_id, nickname=nickname, bio=bio, nerd_level=nerd_level)

            if not result:
                return None

            # Přidej nové zájmy
            if interests:
                for interest in interests:
                    db.execute('''
                        MATCH (profile:Profile {user_id: $user_id})
                        MATCH (interest:InterestCategory {name: $interest})
                        CREATE (profile)-[:INTERESTED_IN {added_at: datetime()}]->(interest)
                    ''', user_id=user_id, interest=interest)

            # Přidej nové technologie
            if technologies:
                for tech in technologies:
                    db.execute('''
                        MATCH (profile:Profile {user_id: $user_id})
                        MATCH (technology:Technology {name: $tech})
                        CREATE (profile)-[:LIKES_TECHNOLOGY {added_at: datetime()}]->(technology)
                    ''', user_id=user_id, tech=tech)

            return result[0]
        except Exception as e:
            print(f"Error updating profile: {e}")
            return None

    @staticmethod
    def get_all_interests():
        """Vrať všechny dostupné zájmy"""
        db = get_db()
        result = db.query('''
            MATCH (i:InterestCategory)
            RETURN i.name as name, i.type as type
            ORDER BY i.type DESC, i.name ASC
        ''')
        return result

    @staticmethod
    def get_all_technologies():
        """Vrať všechny dostupné technologie"""
        db = get_db()
        result = db.query('''
            MATCH (t:Technology)
            RETURN t.name as name, t.category as category
            ORDER BY t.category ASC, t.name ASC
        ''')
        return result
