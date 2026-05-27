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
    def create_interest_if_not_exists(name: str, user_id: str):
        """Vytvoř custom zájmi (nebo vrať existující)"""
        db = get_db()
        try:
            result = db.execute('''
                MERGE (i:InterestCategory {name: $name})
                ON CREATE SET
                    i.type = "USER",
                    i.created_by = $user_id,
                    i.created_at = datetime()
                RETURN i.name as name, i.type as type
            ''', name=name, user_id=user_id)
            return result[0] if result else None
        except Exception as e:
            print(f"Error creating interest: {e}")
            return None

    @staticmethod
    def create_technology_if_not_exists(name: str, user_id: str):
        """Vytvoř custom technologii (nebo vrať existující)"""
        db = get_db()
        try:
            result = db.execute('''
                MERGE (t:Technology {name: $name})
                ON CREATE SET
                    t.created_by = $user_id,
                    t.created_at = datetime(),
                    t.category = "USER"
                RETURN t.name as name
            ''', name=name, user_id=user_id)
            return result[0] if result else None
        except Exception as e:
            print(f"Error creating technology: {e}")
            return None

    @staticmethod
    def get_all_interests(limit_user_tags: int = 5, system_only: bool = False):
        """Vrať dostupné zájmy (SYSTEM všechny, USER omezené, nebo jen SYSTEM)"""
        db = get_db()
        if system_only:
            result = db.query('''
                MATCH (i:InterestCategory {type: "SYSTEM"})
                RETURN i.name as name, i.type as type
                ORDER BY i.name ASC
            ''')
        else:
            result = db.query('''
                MATCH (i:InterestCategory)
                RETURN i.name as name, i.type as type
                ORDER BY
                    CASE WHEN i.type = "SYSTEM" THEN 0 ELSE 1 END ASC,
                    i.name ASC,
                    i.created_at DESC
            ''')

        # Rozděleme na SYSTEM a USER, limitujeme USER
        system_interests = [r for r in result if r['type'] == 'SYSTEM']
        user_interests = [r for r in result if r['type'] == 'USER'][:limit_user_tags]

        return system_interests + user_interests

    @staticmethod
    def get_all_technologies(limit_user_tags: int = 5, system_only: bool = False):
        """Vrať dostupné technologie (SYSTEM všechny, USER omezené, nebo jen SYSTEM)"""
        db = get_db()
        if system_only:
            result = db.query('''
                MATCH (t:Technology)
                WHERE t.category IS NOT NULL AND t.category <> "USER"
                RETURN t.name as name, t.category as category
                ORDER BY t.name ASC
            ''')
        else:
            result = db.query('''
                MATCH (t:Technology)
                WHERE t.category IS NOT NULL
                RETURN t.name as name, t.category as category
                ORDER BY
                    CASE WHEN t.category = "USER" THEN 1 ELSE 0 END ASC,
                    t.category ASC,
                    t.name ASC,
                    t.created_at DESC
            ''')

        # Rozděleme na SYSTEM a USER, limitujeme USER
        system_techs = [r for r in result if r['category'] != 'USER']
        user_techs = [r for r in result if r['category'] == 'USER'][:limit_user_tags]

        return system_techs + user_techs
