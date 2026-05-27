"""Discovery routy - procházení a lajkování profilů"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from random import choice
from models.database import get_db
from models.connection import Connection
from models.profile import Profile

discover_bp = Blueprint('discover', __name__)

def get_available_profiles(user_id, db, min_nerd=0, max_nerd=10, interests=None):
    """Vrať dostupné profily (které jsme si nelajkli) - podle Template logiky"""
    query = '''
        MATCH (user:User {id: $user_id})
        MATCH (other:User)-[:HAS_PROFILE]->(profile:Profile)
        MATCH (other)-[:HAS_ACCOUNT]->(account)
        WHERE other.id <> user.id
        AND account.is_deleted = false
        AND profile.nerd_level >= $min_nerd
        AND profile.nerd_level <= $max_nerd
        AND NOT (user)-[:LIKES]->(other)
    '''

    params = {'user_id': user_id, 'min_nerd': min_nerd, 'max_nerd': max_nerd}

    if interests:
        query += '''
        MATCH (profile)-[:INTERESTED_IN]->(interest:InterestCategory)
        WHERE interest.name IN $interests
        '''
        params['interests'] = interests

    query += '''
        OPTIONAL MATCH (profile)-[:INTERESTED_IN]->(interest:InterestCategory)
        OPTIONAL MATCH (profile)-[:LIKES_TECHNOLOGY]->(tech:Technology)
        RETURN other.id as user_id,
               profile.nickname as nickname,
               profile.bio as bio,
               profile.nerd_level as nerd_level,
               collect(DISTINCT interest.name) as interests,
               collect(DISTINCT tech.name) as technologies
    '''

    result = db.query(query, **params)
    return result

@discover_bp.route('/discover', methods=['GET'])
def discover():
    """Stránka pro objevování profilů"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    min_nerd = request.args.get('min_nerd', 0, type=int)
    max_nerd = request.args.get('max_nerd', 10, type=int)
    interests = request.args.getlist('interests')

    db = get_db()
    available = get_available_profiles(user_id, db, min_nerd, max_nerd, interests)
    profile = choice(available) if available else None

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

    Connection.create(user_id, target_user_id)
    flash("❤️ Profil se ti líbí!", "success")
    return redirect(url_for('discover.discover'))

@discover_bp.route('/discover/skip', methods=['POST'])
def skip_profile():
    """Přeskoč profil (na další se zobrazí automaticky)"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    return redirect(url_for('discover.discover'))
