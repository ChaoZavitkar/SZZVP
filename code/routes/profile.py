"""Profil routy"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import User
from models.profile import Profile
from utils.validators import validate_nickname, validate_bio

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET'])
def view():
    """Zobrazit profil"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    profile = Profile.get_by_user_id(user_id)
    if not profile:
        flash("❌ Nejdříve si vytvořte profil", "error")
        return redirect(url_for('profile.setup'))

    user = User.get_by_id(user_id)
    return render_template('profile/view.html', user=user, profile=profile)

@profile_bp.route('/profile/setup', methods=['GET', 'POST'])
def setup():
    """Vytvoření profilu"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    if Profile.exists(user_id):
        return redirect(url_for('profile.view'))

    if request.method == 'POST':
        nickname = request.form.get('nickname', '').strip()
        bio = request.form.get('bio', '').strip()
        nerd_level = request.form.get('nerd_level', 5)
        interests_str = request.form.get('interests', '').strip()
        technologies_str = request.form.get('technologies', '').strip()
        interests = [i.strip() for i in interests_str.split(',') if i.strip()]
        technologies = [t.strip() for t in technologies_str.split(',') if t.strip()]

        # Validace
        nickname_valid, nickname_error = validate_nickname(nickname)
        if not nickname_valid:
            flash(f"❌ {nickname_error}", "error")
            return redirect(url_for('profile.setup'))

        bio_valid, bio_error = validate_bio(bio)
        if not bio_valid:
            flash(f"❌ {bio_error}", "error")
            return redirect(url_for('profile.setup'))

        if Profile.nickname_exists(nickname):
            flash("❌ Tato přezdívka je již obsazena", "error")
            return redirect(url_for('profile.setup'))

        if not interests:
            flash("❌ Vyberte alespoň jeden zájmi", "error")
            return redirect(url_for('profile.setup'))

        try:
            nerd_level = int(nerd_level)
            if not (0 <= nerd_level <= 10):
                nerd_level = 5
        except:
            nerd_level = 5

        # Vytvoř profil
        profile = Profile.create(user_id, nickname, bio, nerd_level)
        if profile:
            # Vytvoř custom zájmy a technologie (pokud neexistují)
            for interest in interests:
                Profile.create_interest_if_not_exists(interest, user_id)
            for tech in technologies:
                Profile.create_technology_if_not_exists(tech, user_id)

            # Aktualizuj s zájmy a technologiemi
            Profile.update(user_id, nickname, bio, nerd_level, interests, technologies)
            flash("✅ Profil vytvořen!", "success")
            return redirect(url_for('index'))
        else:
            flash("❌ Chyba při vytváření profilu", "error")

    all_interests = Profile.get_all_interests()
    all_technologies = Profile.get_all_technologies()
    return render_template('profile/setup.html', interests=all_interests, technologies=all_technologies)

@profile_bp.route('/profile/edit', methods=['GET', 'POST'])
def edit():
    """Editace profilu"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    profile = Profile.get_by_user_id(user_id)
    if not profile:
        flash("❌ Profil neexistuje", "error")
        return redirect(url_for('profile.setup'))

    if request.method == 'POST':
        nickname = request.form.get('nickname', '').strip()
        bio = request.form.get('bio', '').strip()
        nerd_level = request.form.get('nerd_level', 5)
        interests_str = request.form.get('interests', '').strip()
        technologies_str = request.form.get('technologies', '').strip()
        interests = [i.strip() for i in interests_str.split(',') if i.strip()]
        technologies = [t.strip() for t in technologies_str.split(',') if t.strip()]

        # Validace
        nickname_valid, nickname_error = validate_nickname(nickname)
        if not nickname_valid:
            flash(f"❌ {nickname_error}", "error")
            return redirect(url_for('profile.edit'))

        bio_valid, bio_error = validate_bio(bio)
        if not bio_valid:
            flash(f"❌ {bio_error}", "error")
            return redirect(url_for('profile.edit'))

        if Profile.nickname_exists(nickname, exclude_user_id=user_id):
            flash("❌ Tato přezdívka je již obsazena", "error")
            return redirect(url_for('profile.edit'))

        if not interests:
            flash("❌ Vyberte alespoň jeden zájmi", "error")
            return redirect(url_for('profile.edit'))

        try:
            nerd_level = int(nerd_level)
            if not (0 <= nerd_level <= 10):
                nerd_level = 5
        except:
            nerd_level = 5

        # Vytvoř custom zájmy a technologie (pokud neexistují)
        for interest in interests:
            Profile.create_interest_if_not_exists(interest, user_id)
        for tech in technologies:
            Profile.create_technology_if_not_exists(tech, user_id)

        # Aktualizuj profil
        result = Profile.update(user_id, nickname, bio, nerd_level, interests, technologies)
        if result:
            flash("✅ Profil aktualizován!", "success")
            return redirect(url_for('profile.view'))
        else:
            flash("❌ Chyba při aktualizaci profilu", "error")

    all_interests = Profile.get_all_interests()
    all_technologies = Profile.get_all_technologies()
    return render_template('profile/edit.html', profile=profile, interests=all_interests, technologies=all_technologies)
