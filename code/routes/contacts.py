"""Kontakty routy"""

from flask import Blueprint, render_template, redirect, url_for, session, flash
from models.database import get_db
from models.connection import Connection

contacts_bp = Blueprint('contacts', __name__)

def get_matches(user_id, db):
    """Vrať vzájemné matche - podle Template logiky"""
    return db.query('''
        MATCH (friend:User)-[:LIKES]->(user:User)-[:LIKES]->(friend:User)
        WHERE user.id = $user_id
        MATCH (friend)-[:HAS_PROFILE]->(profile:Profile)
        OPTIONAL MATCH (profile)-[:INTERESTED_IN]->(interest:InterestCategory)
        OPTIONAL MATCH (profile)-[:LIKES_TECHNOLOGY]->(tech:Technology)
        RETURN friend.id as user_id,
               profile.nickname as nickname,
               profile.bio as bio,
               profile.nerd_level as nerd_level,
               collect(DISTINCT interest.name) as interests,
               collect(DISTINCT tech.name) as technologies
    ''', user_id=user_id)

def get_one_way_interests(user_id, db):
    """Vrať ty, kterým se líbím (já je lajknu, ale oni ne)"""
    return db.query('''
        MATCH (user:User {id: $user_id})-[:LIKES]->(other:User)
        WHERE NOT (other)-[:LIKES]->(user)
        MATCH (other)-[:HAS_PROFILE]->(profile:Profile)
        OPTIONAL MATCH (profile)-[:INTERESTED_IN]->(interest:InterestCategory)
        OPTIONAL MATCH (profile)-[:LIKES_TECHNOLOGY]->(tech:Technology)
        RETURN other.id as user_id,
               profile.nickname as nickname,
               profile.bio as bio,
               profile.nerd_level as nerd_level,
               collect(DISTINCT interest.name) as interests,
               collect(DISTINCT tech.name) as technologies
    ''', user_id=user_id)

def get_admirers(user_id, db):
    """Vrať ty, kterí si mě lajkli (oni mě lajknou, ale já je ne)"""
    return db.query('''
        MATCH (other:User)-[:LIKES]->(user:User {id: $user_id})
        WHERE NOT (user)-[:LIKES]->(other)
        MATCH (other)-[:HAS_PROFILE]->(profile:Profile)
        OPTIONAL MATCH (profile)-[:INTERESTED_IN]->(interest:InterestCategory)
        OPTIONAL MATCH (profile)-[:LIKES_TECHNOLOGY]->(tech:Technology)
        RETURN other.id as user_id,
               profile.nickname as nickname,
               profile.bio as bio,
               profile.nerd_level as nerd_level,
               collect(DISTINCT interest.name) as interests,
               collect(DISTINCT tech.name) as technologies
    ''', user_id=user_id)

@contacts_bp.route('/contacts', methods=['GET'])
def list_contacts():
    """Seznam všech kontaktů - vzájemné matche a jednostranné zájmy"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    db = get_db()

    matches = get_matches(user_id, db)
    one_way_interests = get_one_way_interests(user_id, db)
    admirers = get_admirers(user_id, db)

    return render_template('contacts/list.html',
                         matches=matches,
                         one_way_interests=one_way_interests,
                         admiring_you=admirers)

@contacts_bp.route('/contacts/<other_user_id>/remove', methods=['POST'])
def remove_contact(other_user_id):
    """Odeber like (smaž LIKES vztah)"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    Connection.delete(user_id, other_user_id)
    flash("✅ Kontakt odstraněn", "success")

    return redirect(url_for('contacts.list_contacts'))
