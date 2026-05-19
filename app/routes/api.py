"""
Routes: API JSON (para requisições AJAX do frontend)
"""
from datetime import date
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.services.finance_service import FinanceService

api_bp = Blueprint('api', __name__)


@api_bp.route('/summary')
@login_required
def summary():
    today = date.today()
    year  = request.args.get('year',  today.year,  type=int)
    month = request.args.get('month', today.month, type=int)
    return jsonify(FinanceService.get_monthly_summary(current_user.id, year, month))


@api_bp.route('/chart')
@login_required
def chart():
    months = request.args.get('months', 6, type=int)
    return jsonify(FinanceService.get_monthly_chart_data(current_user.id, months))


@api_bp.route('/categories')
@login_required
def categories():
    today = date.today()
    year  = request.args.get('year',  today.year,  type=int)
    month = request.args.get('month', today.month, type=int)
    return jsonify(FinanceService.get_expenses_by_category(current_user.id, year, month))


@api_bp.route('/health')
@login_required
def health():
    return jsonify(FinanceService.get_financial_health(current_user.id))


@api_bp.route('/toggle-dark', methods=['POST'])
@login_required
def toggle_dark():
    from app import db
    current_user.dark_mode = not current_user.dark_mode
    db.session.commit()
    return jsonify({'dark_mode': current_user.dark_mode})