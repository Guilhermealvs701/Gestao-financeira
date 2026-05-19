"""
Routes: Autenticação
"""
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        # Validações
        errors = []
        if not name or len(name) < 2:
            errors.append('Nome deve ter ao menos 2 caracteres.')
        if not email or '@' not in email:
            errors.append('E-mail inválido.')
        if len(password) < 6:
            errors.append('Senha deve ter ao menos 6 caracteres.')
        if password != confirm:
            errors.append('Senhas não coincidem.')
        if User.query.filter_by(email=email).first():
            errors.append('E-mail já cadastrado.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('auth/register.html', name=name, email=email)

        user = User(name=name, email=email)
        user.password = password
        db.session.add(user)
        db.session.commit()

        flash('Conta criada com sucesso! Faça login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(email=email).first()

        if user and user.verify_password(password) and user.is_active:
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            next_page = request.args.get('next')
            flash(f'Bem-vindo, {user.name.split()[0]}! 👋', 'success')
            return redirect(next_page or url_for('dashboard.index'))

        flash('E-mail ou senha incorretos.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sessão encerrada com sucesso.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            name         = request.form.get('name', '').strip()
            monthly_goal = request.form.get('monthly_goal', 0)
            avatar_color = request.form.get('avatar_color', '#4f46e5')

            if name and len(name) >= 2:
                current_user.name = name
            try:
                current_user.monthly_goal = float(monthly_goal)
            except (ValueError, TypeError):
                pass
            current_user.avatar_color = avatar_color
            db.session.commit()
            flash('Perfil atualizado!', 'success')

        elif action == 'change_password':
            current_pw = request.form.get('current_password', '')
            new_pw     = request.form.get('new_password', '')
            confirm_pw = request.form.get('confirm_password', '')

            if not current_user.verify_password(current_pw):
                flash('Senha atual incorreta.', 'danger')
            elif len(new_pw) < 6:
                flash('Nova senha deve ter ao menos 6 caracteres.', 'danger')
            elif new_pw != confirm_pw:
                flash('Senhas não coincidem.', 'danger')
            else:
                current_user.password = new_pw
                db.session.commit()
                flash('Senha alterada com sucesso!', 'success')

        elif action == 'toggle_dark':
            current_user.dark_mode = not current_user.dark_mode
            db.session.commit()

    return render_template('auth/profile.html')