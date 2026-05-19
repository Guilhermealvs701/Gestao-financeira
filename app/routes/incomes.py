"""
Routes: Receitas
"""
from datetime import date, datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import extract
from app import db
from app.models.income import Income

incomes_bp = Blueprint('incomes', __name__)


@incomes_bp.route('/')
@login_required
def index():
    today  = date.today()
    year   = int(request.args.get('year',  today.year))
    month  = int(request.args.get('month', today.month))
    type_f = request.args.get('type', '')
    search = request.args.get('search', '').strip()

    query = Income.query.filter(
        Income.user_id == current_user.id,
        extract('year',  Income.date) == year,
        extract('month', Income.date) == month,
    )
    if type_f:
        query = query.filter(Income.type == type_f)
    if search:
        query = query.filter(Income.name.ilike(f'%{search}%'))

    incomes = query.order_by(Income.date.desc(), Income.created_at.desc()).all()
    total   = sum(float(i.amount) for i in incomes)

    return render_template(
        'incomes/index.html',
        incomes      = incomes,
        total        = total,
        year         = year,
        month        = month,
        type_f       = type_f,
        search       = search,
        income_types = Income.INCOME_TYPES,
    )


@incomes_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        amount   = request.form.get('amount', 0)
        date_str = request.form.get('date', '')
        inc_type = request.form.get('type', 'Salário')
        notes    = request.form.get('notes', '').strip()

        errors = []
        if not name:
            errors.append('Nome é obrigatório.')
        try:
            amount = float(amount)
            if amount <= 0:
                errors.append('Valor deve ser maior que zero.')
        except (ValueError, TypeError):
            errors.append('Valor inválido.')
        try:
            inc_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            errors.append('Data inválida.')
            inc_date = date.today()

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('incomes/form.html',
                                   income_types=Income.INCOME_TYPES,
                                   form_data=request.form)

        income = Income(
            user_id = current_user.id,
            name    = name,
            amount  = amount,
            date    = inc_date,
            type    = inc_type,
            notes   = notes,
        )
        db.session.add(income)
        db.session.commit()
        flash(f'Receita "{name}" adicionada!', 'success')
        return redirect(url_for('incomes.index'))

    return render_template('incomes/form.html',
                           income_types=Income.INCOME_TYPES,
                           today=date.today().strftime('%Y-%m-%d'))


@incomes_bp.route('/edit/<int:income_id>', methods=['GET', 'POST'])
@login_required
def edit(income_id):
    income = Income.query.filter_by(id=income_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        income.name  = request.form.get('name', income.name).strip()
        income.type  = request.form.get('type', income.type)
        income.notes = request.form.get('notes', '').strip()
        try:
            income.amount = float(request.form.get('amount', income.amount))
        except (ValueError, TypeError):
            flash('Valor inválido.', 'danger')
        try:
            date_str = request.form.get('date', '')
            income.date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Data inválida.', 'danger')

        db.session.commit()
        flash('Receita atualizada!', 'success')
        return redirect(url_for('incomes.index'))

    return render_template('incomes/form.html',
                           income=income,
                           income_types=Income.INCOME_TYPES)


@incomes_bp.route('/delete/<int:income_id>', methods=['POST'])
@login_required
def delete(income_id):
    income = Income.query.filter_by(id=income_id, user_id=current_user.id).first_or_404()
    name = income.name
    db.session.delete(income)
    db.session.commit()
    flash(f'Receita "{name}" removida.', 'info')
    return redirect(url_for('incomes.index'))