"""Kontakty routy"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.database import get_db
from models.connection import Connection

contacts_bp = Blueprint('contacts', __name__)

@contacts_bp.route('/contacts', methods=['GET'])
def list_contacts():
    """Seznam všech kontaktů (likes a matches)"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    db = get_db()

    # Vrať všechny likes (oba směry) s informací o tom, jestli je to mutual + zájmy a technologie
    result = db.query('''
        MATCH (user:User {id: $user_id})

        MATCH (user)-[r:LIKES]-(other:User)
        WHERE other.id <> user.id

        OPTIONAL MATCH (other)-[:HAS_PROFILE]->(profile:Profile)
        OPTIONAL MATCH (profile)-[:INTERESTED_IN]->(interest:InterestCategory)
        OPTIONAL MATCH (profile)-[:LIKES_TECHNOLOGY]->(tech:Technology)
        OPTIONAL MATCH (user)-[:LIKES]->(other)
        OPTIONAL MATCH (other)-[:LIKES]->(user)

        WITH other, profile,
             collect(DISTINCT interest.name) as interests,
             collect(DISTINCT tech.name) as technologies,
             CASE WHEN (user)-[:LIKES]->(other) AND (other)-[:LIKES]->(user) THEN true ELSE false END as is_match,
             CASE WHEN (user)-[:LIKES]->(other) THEN 'initiated' ELSE 'received' END as initiated_by

        RETURN DISTINCT other.id as user_id,
               profile.nickname as nickname,
               profile.bio as bio,
               profile.nerd_level as nerd_level,
               interests,
               technologies,
               is_match,
               initiated_by

        ORDER BY is_match DESC
    ''', user_id=user_id)

    # Odděluj matche od jednostranných zájmů
    matches = [c for c in result if c['is_match']]
    one_way_initiated = [c for c in result if not c['is_match'] and c['initiated_by'] == 'initiated']
    one_way_received = [c for c in result if not c['is_match'] and c['initiated_by'] == 'received']

    return render_template('contacts/list.html',
                         matches=matches,
                         one_way_interests=one_way_initiated,
                         admiring_you=one_way_received)

@contacts_bp.route('/contacts/<other_user_id>/remove', methods=['POST'])
def remove_contact(other_user_id):
    """Odeber like od mě"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    Connection.delete(user_id, other_user_id)
    flash("✅ Kontakt odstraněn", "success")

    return redirect(url_for('contacts.list_contacts'))
