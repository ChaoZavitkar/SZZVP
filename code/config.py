import os
from datetime import timedelta

class Config:
    """Základní konfigurace"""

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', False)

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=5)  # Session timeout 5 minut
    SESSION_COOKIE_SECURE = False  # True v produkci (HTTPS)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_TYPE = 'filesystem'

    # Neo4j
    NEO4J_URI = os.environ.get('NEO4J_URI', 'bolt://neo4j:7687')
    NEO4J_USER = os.environ.get('NEO4J_USER', 'neo4j')
    NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD', 'adminpass')

    # Bezpečnost
    PASSWORD_MIN_LENGTH = 8
    BCRYPT_LOG_ROUNDS = 12  # Počet iterací pro bcrypt

    # Validace
    MAX_EMAIL_LENGTH = 255
    MAX_NICKNAME_LENGTH = 50
    MIN_NICKNAME_LENGTH = 3
    MAX_BIO_LENGTH = 500
    NERD_LEVEL_MIN = 0
    NERD_LEVEL_MAX = 10
