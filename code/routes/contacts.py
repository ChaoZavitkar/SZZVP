"""Kontakty routy"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.database import get_db
from models.connection import Connection

contacts_bp = Blueprint('contacts', __name__)

@contacts_bp.route('/contacts', methods=['GET'])
def list_contacts():
    """Seznam všech kontaktů"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    db = get_db()

    # Vrať všechny konekce s detaily
    result = db.query('''
        MATCH (user:User {id: $user_id})
        MATCH (user)-[:INITIATED_CONNECTION|:RECEIVED_CONNECTION]-(conn:Connection)-[:INITIATED_CONNECTION|:RECEIVED_CONNECTION]-(other:User)
        WHERE conn.is_deleted = false
        OPTIONAL MATCH (other)-[:HAS_PROFILE]->(profile:Profile)
        RETURN conn.id as id,
               conn.is_match as is_match,
               conn.created_at as created_at,
               other.id as user_id,
               profile.nickname as nickname,
               profile.bio as bio,
               profile.nerd_level as nerd_level
        ORDER BY conn.is_match DESC, conn.created_at DESC
    ''', user_id=user_id)

    # Odděluj matche od jednostranných zájmů
    matches = [c for c in result if c['is_match']]
    one_way = [c for c in result if not c['is_match']]

    return render_template('contacts/list.html', matches=matches, one_way_interests=one_way)

@contacts_bp.route('/contacts/<connection_id>/remove', methods=['POST'])
def remove_contact(connection_id):
    """Odeber kontakt"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    # Smaž konekci
    Connection.delete(connection_id)
    flash("✅ Kontakt odstraněn", "success")

    return redirect(url_for('contacts.list_contacts'))
