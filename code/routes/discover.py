"""Discovery routy - procházení a lajkování profilů"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models.database import get_db
from models.connection import Connection
from models.profile import Profile

discover_bp = Blueprint('discover', __name__)

@discover_bp.route('/discover', methods=['GET'])
def discover():
    """Stránka pro objevování profilů"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    # Parametry filtrování
    min_nerd = request.args.get('min_nerd', 0, type=int)
    max_nerd = request.args.get('max_nerd', 10, type=int)
    interests = request.args.getlist('interests')

    db = get_db()

    # Základní dotaz
    query = '''
        MATCH (user:User {id: $user_id})
        MATCH (other:User)-[:HAS_PROFILE]->(profile:Profile)
        MATCH (other)-[:HAS_ACCOUNT]->(account)
        WHERE other.id <> user.id
        AND account.is_deleted = false
        AND profile.nerd_level >= $min_nerd
        AND profile.nerd_level <= $max_nerd
    '''

    params = {
        'user_id': user_id,
        'min_nerd': min_nerd,
        'max_nerd': max_nerd
    }

    # Filtr podle zájmů
    if interests:
        query += '''
        AND (profile)-[:INTERESTED_IN]->(interest:InterestCategory)
        AND interest.name IN $interests
        '''
        params['interests'] = interests

    # Vylučuj již ohodnocené profily
    query += '''
        OPTIONAL MATCH (existing:Connection)
        WHERE (user)-[:INITIATED_CONNECTION|:RECEIVED_CONNECTION]-(existing)-[:INITIATED_CONNECTION|:RECEIVED_CONNECTION]-(other)
        AND existing.is_deleted = false

        WITH profile, other, existing
        WHERE existing IS NULL

        OPTIONAL MATCH (profile)-[:INTERESTED_IN]->(interest:InterestCategory)
        OPTIONAL MATCH (profile)-[:LIKES_TECHNOLOGY]->(tech:Technology)

        RETURN other.id as user_id,
               profile.nickname as nickname,
               profile.bio as bio,
               profile.nerd_level as nerd_level,
               collect(DISTINCT interest.name) as interests,
               collect(DISTINCT tech.name) as technologies
        LIMIT 1
    '''

    result = db.query(query, **params)
    profile = result[0] if result else None

    # Všechny dostupné zájmy pro filtr
    all_interests = Profile.get_all_interests()

    return render_template('discover/index.html',
                         profile=profile,
                         all_interests=all_interests,
                         selected_interests=interests,
                         min_nerd=min_nerd,
                         max_nerd=max_nerd)

@discover_bp.route('/discover/like/<target_user_id>', methods=['POST'])
def like_profile(target_user_id):
    """Lajkni profil"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    if user_id == target_user_id:
        flash("❌ Nemůžete si lajkovat sami sebe", "error")
        return redirect(url_for('discover.discover'))

    # Vytvoř konekci
    connection = Connection.create(user_id, target_user_id)
    if connection:
        flash("❤️ Profil se ti líbí!", "success")
    else:
        flash("❌ Chyba při uložení", "error")

    # Vrať se na discover
    return redirect(url_for('discover.discover'))

@discover_bp.route('/discover/skip/<target_user_id>', methods=['POST'])
def skip_profile(target_user_id):
    """Přeskoč profil (na další se zobrazí automaticky)"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    # Prostě vrať na discover - zobrazí se další profil
    return redirect(url_for('discover.discover'))
