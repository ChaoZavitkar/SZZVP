"""Discovery routy - procházení a lajkování profilů"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from random import choice
from config import Config
from models.database import get_db
from models.connection import Connection
from models.profile import Profile

discover_bp = Blueprint('discover', __name__)

def get_available_profiles(user_id, db, min_nerd=0, max_nerd=10, interests=None, skip_timeout_hours=None):
    """Vrať dostupné profily (které jsme si nelajkli) - podle Template logiky"""
    if skip_timeout_hours is None:
        skip_timeout_hours = Config.SKIP_TIMEOUT_HOURS

    query = '''
        MATCH (user:User {id: $user_id})
        MATCH (other:User)-[:HAS_PROFILE]->(profile:Profile)
        MATCH (other)-[:HAS_ACCOUNT]->(account)
        WHERE other.id <> user.id
        AND account.is_deleted = false
        AND profile.nerd_level >= $min_nerd
        AND profile.nerd_level <= $max_nerd
        AND NOT (user)-[:LIKES]->(other)
        AND NOT (
            EXISTS {
                MATCH (user)-[skip:SKIP]->(other)
                WHERE skip.created_at > datetime() - duration({hours: $timeout_hours})
            }
        )
    '''

    params = {'user_id': user_id, 'min_nerd': min_nerd, 'max_nerd': max_nerd, 'timeout_hours': skip_timeout_hours}

    if interests:
        # Profil MUSÍ mít VŠECHNY vybrané zájmy
        query += '''
        WITH profile, other
        MATCH (profile)-[:INTERESTED_IN]->(interest:InterestCategory)
        WHERE interest.name IN $interests
        WITH profile, other, collect(DISTINCT interest.name) as matched_interests
        WHERE size(matched_interests) = $interest_count
        '''
        params['interests'] = interests
        params['interest_count'] = len(interests)

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

    # Zobraz jen SYSTEM tagy v filtru (ne custom USER tagy)
    all_interests = Profile.get_all_interests(system_only=True)

    return render_template('discover/index.html',
                         profile=profile,
                         all_interests=all_interests,
                         selected_interests=interests,
                         min_nerd=min_nerd,
                         max_nerd=max_nerd)

@discover_bp.route('/discover/like/<target_user_id>', methods=['POST'])
def like_profile(target_user_id):
    """Lajkni profil (zachova filtry)"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    if user_id == target_user_id:
        flash("❌ Nemůžete si lajkovat sami sebe", "error")
        return redirect(url_for('discover.discover'))

    Connection.create(user_id, target_user_id)
    flash("❤️ Profil se ti líbí!", "success")

    # Zachov filtry
    min_nerd = request.form.get('min_nerd', 0, type=int)
    max_nerd = request.form.get('max_nerd', 10, type=int)
    interests = request.form.getlist('interests')

    url = url_for('discover.discover', min_nerd=min_nerd, max_nerd=max_nerd)
    if interests:
        url += f"&{'&'.join([f'interests={i}' for i in interests])}"

    return redirect(url)

@discover_bp.route('/discover/skip/<target_user_id>', methods=['POST'])
def skip_profile(target_user_id):
    """Přeskoč profil (zachova filtry a vytvori SKIP vztah)"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    # Zapiš skip
    Connection.skip(user_id, target_user_id)

    # Zachov filtry
    min_nerd = request.form.get('min_nerd', 0, type=int)
    max_nerd = request.form.get('max_nerd', 10, type=int)
    interests = request.form.getlist('interests')

    url = url_for('discover.discover', min_nerd=min_nerd, max_nerd=max_nerd)
    if interests:
        url += f"&{'&'.join([f'interests={i}' for i in interests])}"

    return redirect(url)
