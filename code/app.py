"""NerdMatch - Hlavní Flask aplikace"""

from flask import Flask, render_template, session, redirect, url_for
from config import Config
from models.database import init_db, get_db
from routes.auth import auth_bp
from routes.profile import profile_bp
from routes.discover import discover_bp
from routes.contacts import contacts_bp
from datetime import datetime, timedelta

app = Flask(__name__)
app.config.from_object(Config)

# Inicializuj databázi
try:
    init_db(app)
    print("✅ Databáze inicializována")
except Exception as e:
    print(f"⚠️ Chyba DB: {e}")

# Registruj blueprinty
app.register_blueprint(auth_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(discover_bp)
app.register_blueprint(contacts_bp)

# Session timeout middleware
@app.before_request
def check_session_timeout():
    """Kontroluj session timeout (5 minut)"""
    session.permanent = True
    app.permanent_session_lifetime = Config.PERMANENT_SESSION_LIFETIME
    
    if 'user_id' in session:
        now = datetime.now()
        last_activity = session.get('last_activity')
        
        if last_activity:
            try:
                last_activity_time = datetime.fromisoformat(last_activity)
                if (now - last_activity_time) > timedelta(minutes=5):
                    session.pop('user_id', None)
                    return redirect(url_for('auth.login'))
            except:
                pass
        
        session['last_activity'] = now.isoformat()

@app.route('/')
def index():
    """Domovská stránka - Dashboard"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    db = get_db()

    # Počet všech kontaktů - LIKES oba směry
    total_contacts = len(db.query('''
        MATCH (user:User {id: $user_id})
        MATCH (user)-[:LIKES]-(other:User)
        RETURN DISTINCT other.id as other_id
    ''', user_id=user_id))

    # Počet vzájemných matchů - oboustranné LIKES
    matches_count = len(db.query('''
        MATCH (friend:User)-[:LIKES]->(user:User)-[:LIKES]->(friend:User)
        WHERE user.id = $user_id
        RETURN DISTINCT friend.id as friend_id
    ''', user_id=user_id))

    # Počet dostupných profilů - všichni mimo těch co si lajknul
    visible_profiles = len(db.query('''
        MATCH (user:User {id: $user_id})
        MATCH (other:User)-[:HAS_ACCOUNT]->(account)
        WHERE other.id <> user.id
        AND account.is_deleted = false
        AND NOT (user)-[:LIKES]->(other)
        RETURN DISTINCT other.id as other_id
    ''', user_id=user_id))

    stats = {
        'total_contacts': total_contacts,
        'matches_count': matches_count,
        'visible_profiles': visible_profiles
    }

    return render_template('dashboard.html', stats=stats)

@app.errorhandler(404)
def not_found(error):
    """404 error"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    """500 error"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
