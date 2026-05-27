"""Neo4j databázová inicializace"""

from py2neo import Graph
import logging

logger = logging.getLogger(__name__)

class Database:
    """Třída pro práci s Neo4j"""

    def __init__(self, uri: str, user: str, password: str):
        self.graph = None
        self.uri = uri
        self.user = user
        self.password = password

    def connect(self):
        """Připojit k Neo4j"""
        try:
            self.graph = Graph(self.uri, auth=(self.user, self.password))
            self.graph.run("RETURN 1")
            logger.info("✅ Připojeno k Neo4j")
            return True
        except Exception as e:
            logger.error(f"❌ Chyba: {e}")
            return False

    def init_schema(self):
        """Inicializuj schéma"""
        try:
            indexes = [
                "CREATE INDEX idx_user_id IF NOT EXISTS ON :User(id)",
                "CREATE INDEX idx_user_email IF NOT EXISTS ON :User(email)",
                "CREATE INDEX idx_profile_user_id IF NOT EXISTS ON :Profile(user_id)",
                "CREATE INDEX idx_profile_nickname IF NOT EXISTS ON :Profile(nickname)",
                "CREATE INDEX idx_account_user_id IF NOT EXISTS ON :Account(user_id)",
                "CREATE INDEX idx_interest_name IF NOT EXISTS ON :InterestCategory(name)",
                "CREATE INDEX idx_technology_name IF NOT EXISTS ON :Technology(name)",
                "CREATE INDEX idx_connection_id IF NOT EXISTS ON :Connection(id)",
            ]
            for index in indexes:
                try:
                    self.graph.run(index)
                except:
                    pass
            logger.info("✅ Schéma inicializováno")
        except Exception as e:
            logger.error(f"Chyba schématu: {e}")

    def init_system_interests(self):
        """Vytvoř systémové zájmy"""
        interests = ["programování", "videohry", "sci-fi", "fantasy", "matematika", 
                     "AI / Machine Learning", "hardware", "komiksy"]
        try:
            for interest in interests:
                self.graph.run('MERGE (i:InterestCategory {name: $name, type: "SYSTEM"}) '
                              'ON CREATE SET i.created_at = datetime()',
                              name=interest)
            logger.info(f"✅ {len(interests)} zájmů vytvořeno")
        except Exception as e:
            logger.error(f"Chyba zájmů: {e}")

    def init_system_technologies(self):
        """Vytvoř systémové technologie"""
        technologies = [
            ("Python", "LANGUAGE"), ("JavaScript", "LANGUAGE"), ("Java", "LANGUAGE"),
            ("Flask", "FRAMEWORK"), ("Django", "FRAMEWORK"), ("React", "FRAMEWORK"),
            ("Docker", "TOOL"), ("Git", "TOOL"), ("Arduino", "HARDWARE"),
        ]
        try:
            for name, category in technologies:
                self.graph.run('MERGE (t:Technology {name: $name}) '
                              'ON CREATE SET t.category = $category, t.created_at = datetime()',
                              name=name, category=category)
            logger.info(f"✅ {len(technologies)} technologií vytvořeno")
        except Exception as e:
            logger.error(f"Chyba technologií: {e}")

    def init_all(self):
        """Inicializuj vše"""
        logger.info("Inicializuji databázi...")
        self.init_schema()
        self.init_system_interests()
        self.init_system_technologies()
        logger.info("✅ Databáze OK")

    def query(self, query_str: str, **kwargs):
        """Spusť dotaz"""
        try:
            result = self.graph.run(query_str, **kwargs)
            return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Query error: {e}")
            return []

    def execute(self, query_str: str, **kwargs):
        """Spusť dotaz (zápis)"""
        try:
            result = self.graph.run(query_str, **kwargs)
            return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Execute error: {e}")
            return []

# Globální instance
db = None

def init_db(app):
    """Inicializuj s Flask"""
    global db
    db = Database(app.config['NEO4J_URI'], app.config['NEO4J_USER'], app.config['NEO4J_PASSWORD'])
    if not db.connect():
        raise RuntimeError("Nelze se připojit k Neo4j")
    db.init_all()
    return db

def get_db():
    """Vrať DB"""
    return db
