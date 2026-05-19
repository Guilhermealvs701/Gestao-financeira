"""
Routes: Despesas
"""
from datetime import date, datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import extract, or_
from app import db
from app.models.expense  import Expense
from app.models.category import Category

expenses_bp = Blueprint('expenses', __name__)


def _get_user_categories(user_id):
    """Retorna categorias padrão + personalizadas do usuário."""
    return Category.query.filter(
        or_(Category.is_default == True, Category.user_id == user_id)
    ).order_by(Category.name).all()


@expenses_bp.route('/')
@login_required
def index():
    today   = date.today()
    year    = int(request.args.get('year',  today.year))
    month   = int(request.args.get('month', today.month))
    cat_id  = request.args.get('category', type=int)
    search  = request.args.get('search', '').strip()
    pay_method = request.args.get('payment', '')

    query = Expense.query.filter(
        Expense.user_id == current_user.id,
        extract('year',  Expense.date) == year,
        extract('month', Expense.date) == month,
    )

    if cat_id:
        query = query.filter(Expense.category_id == cat_id)
    if search:
        query = query.filter(Expense.name.ilike(f'%{search}%'))
    if pay_method:
        query = query.filter(Expense.payment_method == pay_method)

    expenses   = query.order_by(Expense.date.desc(), Expense.created_at.desc()).all()
    total      = sum(float(e.amount) for e in expenses)
    categories = _get_user_categories(current_user.id)

    return render_template(
        'expenses/index.html',
        expenses     = expenses,
        categories   = categories,
        total        = total,
        year         = year,
        month        = month,
        cat_id       = cat_id,
        search       = search,
        pay_method   = pay_method,
        payment_methods = Expense.PAYMENT_METHODS,
    )


@expenses_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    categories = _get_user_categories(current_user.id)

    if request.method == 'POST':
        name           = request.form.get('name', '').strip()
        amount         = request.form.get('amount', 0)
        date_str       = request.form.get('date', '')
        category_id    = request.form.get('category_id', type=int)
        payment_method = request.form.get('payment_method', 'Dinheiro')
        notes          = request.form.get('notes', '').strip()
        is_recurring   = request.form.get('is_recurring') == 'on'

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
            exp_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            errors.append('Data inválida.')
            exp_date = date.today()

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('expenses/form.html', categories=categories,
                                   payment_methods=Expense.PAYMENT_METHODS,
                                   form_data=request.form)

        expense = Expense(
            user_id        = current_user.id,
            name           = name,
            amount         = amount,
            date           = exp_date,
            category_id    = category_id,
            payment_method = payment_method,
            notes          = notes,
            is_recurring   = is_recurring,
        )
        db.session.add(expense)
        db.session.commit()
        flash(f'Despesa "{name}" adicionada com sucesso!', 'success')
        return redirect(url_for('expenses.index'))

    return render_template('expenses/form.html',
                           categories=categories,
                           payment_methods=Expense.PAYMENT_METHODS,
                           today=date.today().strftime('%Y-%m-%d'))


@expenses_bp.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def edit(expense_id):
    expense    = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
    categories = _get_user_categories(current_user.id)

    if request.method == 'POST':
        expense.name           = request.form.get('name', expense.name).strip()
        expense.payment_method = request.form.get('payment_method', expense.payment_method)
        expense.notes          = request.form.get('notes', '').strip()
        expense.is_recurring   = request.form.get('is_recurring') == 'on'
        cat_id = request.form.get('category_id', type=int)
        expense.category_id = cat_id

        try:
            expense.amount = float(request.form.get('amount', expense.amount))
        except (ValueError, TypeError):
            flash('Valor inválido.', 'danger')
            return render_template('expenses/form.html', expense=expense,
                                   categories=categories,
                                   payment_methods=Expense.PAYMENT_METHODS)
        try:
            date_str = request.form.get('date', '')
            expense.date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Data inválida.', 'danger')

        db.session.commit()
        flash('Despesa atualizada!', 'success')
        return redirect(url_for('expenses.index'))

    return render_template('expenses/form.html',
                           expense=expense,
                           categories=categories,
                           payment_methods=Expense.PAYMENT_METHODS)


@expenses_bp.route('/delete/<int:expense_id>', methods=['POST'])
@login_required
def delete(expense_id):
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
    name = expense.name
    db.session.delete(expense)
    db.session.commit()
    flash(f'Despesa "{name}" removida.', 'info')
    return redirect(url_for('expenses.index'))