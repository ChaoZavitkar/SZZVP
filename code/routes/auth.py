"""Autentizační routy"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.validators import validate_email_format, validate_password
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registrace"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        email_valid, email_error = validate_email_format(email)
        if not email_valid:
            flash(f"❌ {email_error}", "error")
            return redirect(url_for('auth.register'))

        password_valid, password_errors = validate_password(password)
        if not password_valid:
            for error in password_errors:
                flash(f"❌ {error}", "error")
            return redirect(url_for('auth.register'))

        if password != password_confirm:
            flash("❌ Hesla se neshodují", "error")
            return redirect(url_for('auth.register'))

        user = User.create(email, password)
        if user:
            flash("✅ Účet vytvořen! Přihlaste se.", "success")
            return redirect(url_for('auth.login'))
        else:
            flash("❌ Email již existuje", "error")
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Přihlášení"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.get_by_email(email)
        if user and User.verify_password(password, user['password_hash']):
            session.permanent = True
            session['user_id'] = user['id']
            User.update_last_login(user['id'])
            flash("✅ Přihlášeni!", "success")
            return redirect(url_for('dashboard.index'))
        else:
            flash("❌ Nesprávný email nebo heslo", "error")
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """Odhlášení"""
    session.pop('user_id', None)
    flash("✅ Odhlášeni!", "success")
    return redirect(url_for('auth.login'))

@auth_bp.route('/delete-account', methods=['GET', 'POST'])
def delete_account():
    """Smazání účtu"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        user = User.get_by_id(user_id)
        if not User.verify_password(password, user['password_hash'] if user else ''):
            flash("❌ Nesprávné heslo", "error")
            return redirect(url_for('auth.delete_account'))
        if confirm != 'on':
            flash("❌ Potvrďte smazání", "error")
            return redirect(url_for('auth.delete_account'))
        User.delete(user_id)
        session.pop('user_id', None)
        flash("✅ Účet smazán", "success")
        return redirect(url_for('auth.login'))
    return render_template('auth/delete-account.html')
