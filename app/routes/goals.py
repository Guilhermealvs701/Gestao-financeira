"""
Routes: Metas Financeiras
"""
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.goal import Goal

goals_bp = Blueprint('goals', __name__)


@goals_bp.route('/')
@login_required
def index():
    goals = Goal.query.filter_by(user_id=current_user.id)\
        .order_by(Goal.completed, Goal.deadline).all()
    return render_template('goals/index.html', goals=goals)


@goals_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        title       = request.form.get('title', '').strip()
        target      = request.form.get('target', 0)
        current_val = request.form.get('current', 0)
        deadline    = request.form.get('deadline', '')
        description = request.form.get('description', '').strip()
        icon        = request.form.get('icon', 'fa-bullseye')
        color       = request.form.get('color', '#4f46e5')

        try:
            target      = float(target)
            current_val = float(current_val)
        except (ValueError, TypeError):
            flash('Valores inválidos.', 'danger')
            return render_template('goals/form.html')

        deadline_date = None
        if deadline:
            try:
                deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date()
            except ValueError:
                pass

        goal = Goal(
            user_id     = current_user.id,
            title       = title,
            target      = target,
            current     = current_val,
            deadline    = deadline_date,
            description = description,
            icon        = icon,
            color       = color,
        )
        db.session.add(goal)
        db.session.commit()
        flash(f'Meta "{title}" criada!', 'success')
        return redirect(url_for('goals.index'))

    return render_template('goals/form.html')


@goals_bp.route('/update/<int:goal_id>', methods=['POST'])
@login_required
def update(goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    try:
        add_val = float(request.form.get('add_value', 0))
        goal.current = float(goal.current) + add_val
        if float(goal.current) >= float(goal.target):
            goal.completed = True
            flash(f'🎉 Meta "{goal.title}" concluída!', 'success')
        else:
            flash(f'Progresso atualizado! {goal.progress_percent}% concluído.', 'info')
    except (ValueError, TypeError):
        flash('Valor inválido.', 'danger')

    db.session.commit()
    return redirect(url_for('goals.index'))


@goals_bp.route('/delete/<int:goal_id>', methods=['POST'])
@login_required
def delete(goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    flash('Meta removida.', 'info')
    return redirect(url_for('goals.index'))