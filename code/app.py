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

    # Počet všech kontaktů
    total_contacts = db.query('''
        MATCH (user:User {id: $user_id})
        MATCH (user)-[:INITIATED_CONNECTION|:RECEIVED_CONNECTION]-(conn:Connection)
        WHERE conn.is_deleted = false
        RETURN count(DISTINCT conn) as total_contacts
    ''', user_id=user_id)
    total_contacts = total_contacts[0]['total_contacts'] if total_contacts else 0

    # Počet matchů (oboustranný zájem)
    matches_count = db.query('''
        MATCH (user:User {id: $user_id})
        MATCH (user)-[:INITIATED_CONNECTION|:RECEIVED_CONNECTION]-(conn:Connection)
        WHERE conn.is_match = true
        AND conn.is_deleted = false
        RETURN count(DISTINCT conn) as matches_count
    ''', user_id=user_id)
    matches_count = matches_count[0]['matches_count'] if matches_count else 0

    # Počet všech viditelných uživatelů
    visible_profiles = db.query('''
        MATCH (other:User)
        MATCH (other)-[:HAS_ACCOUNT]->(account)
        WHERE other.id <> $user_id
        AND account.is_deleted = false
        RETURN count(other) as visible_profiles
    ''', user_id=user_id)
    visible_profiles = visible_profiles[0]['visible_profiles'] if visible_profiles else 0

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
