"""
Routes: Dashboard
"""
from datetime import date
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.services.finance_service import FinanceService

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    today   = date.today()
    summary = FinanceService.get_monthly_summary(current_user.id, today.year, today.month)
    health  = FinanceService.get_financial_health(current_user.id)
    cats    = FinanceService.get_expenses_by_category(current_user.id, today.year, today.month)
    chart   = FinanceService.get_monthly_chart_data(current_user.id, months=6)
    recent  = FinanceService.get_recent_expenses(current_user.id, limit=8)
    forecast = FinanceService.get_expense_forecast(current_user.id)

    # Meta mensal
    goal_pct = 0
    if current_user.monthly_goal and current_user.monthly_goal > 0:
        goal_pct = min(100, round((summary['total_expenses'] / current_user.monthly_goal) * 100, 1))

    return render_template(
        'dashboard/index.html',
        summary   = summary,
        health    = health,
        cats      = cats,
        chart     = chart,
        recent    = recent,
        forecast  = forecast,
        goal_pct  = goal_pct,
        today     = today,
    )