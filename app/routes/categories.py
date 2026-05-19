"""
Routes: Categorias
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_
from app import db
from app.models.category import Category

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('/')
@login_required
def index():
    cats = Category.query.filter(
        or_(Category.is_default == True, Category.user_id == current_user.id)
    ).order_by(Category.is_default.desc(), Category.name).all()
    return render_template('categories/index.html', categories=cats)


@categories_bp.route('/add', methods=['POST'])
@login_required
def add():
    name  = request.form.get('name', '').strip()
    icon  = request.form.get('icon', 'fa-tag')
    color = request.form.get('color', '#4f46e5')

    if not name:
        flash('Nome é obrigatório.', 'danger')
    else:
        cat = Category(name=name, icon=icon, color=color,
                       user_id=current_user.id, is_default=False)
        db.session.add(cat)
        db.session.commit()
        flash(f'Categoria "{name}" criada!', 'success')

    return redirect(url_for('categories.index'))


@categories_bp.route('/delete/<int:cat_id>', methods=['POST'])
@login_required
def delete(cat_id):
    cat = Category.query.filter_by(id=cat_id, user_id=current_user.id).first_or_404()
    db.session.delete(cat)
    db.session.commit()
    flash(f'Categoria "{cat.name}" removida.', 'info')
    return redirect(url_for('categories.index'))