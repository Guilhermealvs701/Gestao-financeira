"""
Finance Control Pro - Serviço financeiro com lógica de negócio
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy import func, extract
from app import db
from app.models.expense  import Expense
from app.models.income   import Income
from app.models.category import Category


class FinanceService:
    """Centraliza toda lógica financeira."""

    @staticmethod
    def get_monthly_summary(user_id: int, year: int = None, month: int = None) -> dict:
        """Retorna resumo financeiro do mês especificado."""
        today = date.today()
        year  = year  or today.year
        month = month or today.month

        total_expenses = db.session.query(
            func.coalesce(func.sum(Expense.amount), 0)
        ).filter(
            Expense.user_id == user_id,
            extract('year',  Expense.date) == year,
            extract('month', Expense.date) == month
        ).scalar()

        total_incomes = db.session.query(
            func.coalesce(func.sum(Income.amount), 0)
        ).filter(
            Income.user_id == user_id,
            extract('year',  Income.date) == year,
            extract('month', Income.date) == month
        ).scalar()

        count_expenses = Expense.query.filter(
            Expense.user_id == user_id,
            extract('year',  Expense.date) == year,
            extract('month', Expense.date) == month
        ).count()

        count_incomes = Income.query.filter(
            Income.user_id == user_id,
            extract('year',  Income.date) == year,
            extract('month', Income.date) == month
        ).count()

        total_expenses = float(total_expenses)
        total_incomes  = float(total_incomes)
        balance        = total_incomes - total_expenses

        return {
            'total_expenses': total_expenses,
            'total_incomes':  total_incomes,
            'balance':        balance,
            'count_expenses': count_expenses,
            'count_incomes':  count_incomes,
            'year':           year,
            'month':          month,
        }

    @staticmethod
    def get_expenses_by_category(user_id: int, year: int = None, month: int = None) -> list:
        """Retorna gastos agrupados por categoria."""
        today = date.today()
        year  = year  or today.year
        month = month or today.month

        results = db.session.query(
            Category.name,
            Category.color,
            Category.icon,
            func.coalesce(func.sum(Expense.amount), 0).label('total')
        ).join(
            Expense, Expense.category_id == Category.id, isouter=True
        ).filter(
            Expense.user_id == user_id,
            extract('year',  Expense.date) == year,
            extract('month', Expense.date) == month
        ).group_by(Category.id).having(func.sum(Expense.amount) > 0).all()

        return [
            {'name': r.name, 'color': r.color, 'icon': r.icon, 'total': float(r.total)}
            for r in results
        ]

    @staticmethod
    def get_monthly_chart_data(user_id: int, months: int = 6) -> dict:
        """Retorna dados para gráfico de receitas x despesas dos últimos N meses."""
        labels    = []
        expenses  = []
        incomes   = []
        today     = date.today()

        for i in range(months - 1, -1, -1):
            # calcula mês retroativo
            month_date = (today.replace(day=1) - timedelta(days=i * 28)).replace(day=1)
            y, m = month_date.year, month_date.month

            exp = float(db.session.query(
                func.coalesce(func.sum(Expense.amount), 0)
            ).filter(
                Expense.user_id == user_id,
                extract('year',  Expense.date) == y,
                extract('month', Expense.date) == m
            ).scalar())

            inc = float(db.session.query(
                func.coalesce(func.sum(Income.amount), 0)
            ).filter(
                Income.user_id == user_id,
                extract('year',  Income.date) == y,
                extract('month', Income.date) == m
            ).scalar())

            month_names = ['Jan','Fev','Mar','Abr','Mai','Jun',
                           'Jul','Ago','Set','Out','Nov','Dez']
            labels.append(f"{month_names[m-1]}/{str(y)[2:]}")
            expenses.append(round(exp, 2))
            incomes.append(round(inc, 2))

        return {'labels': labels, 'expenses': expenses, 'incomes': incomes}

    @staticmethod
    def get_recent_expenses(user_id: int, limit: int = 8) -> list:
        """Últimas despesas do usuário."""
        return Expense.query.filter_by(user_id=user_id)\
            .order_by(Expense.date.desc(), Expense.created_at.desc())\
            .limit(limit).all()

    @staticmethod
    def get_financial_health(user_id: int) -> dict:
        """
        Calcula índice de saúde financeira (0-100) e sugestões.
        Baseia-se na regra 50/30/20.
        """
        today = date.today()
        summary = FinanceService.get_monthly_summary(user_id, today.year, today.month)
        income  = summary['total_incomes']
        expense = summary['total_expenses']

        if income == 0:
            return {
                'score': 0, 'label': 'Sem dados',
                'color': '#95a5a6', 'suggestions': [],
                'savings_rate': 0,
            }

        savings_rate   = ((income - expense) / income) * 100
        expenses_ratio = (expense / income) * 100

        score = 50
        if savings_rate >= 20:
            score += 30
        elif savings_rate >= 10:
            score += 15
        elif savings_rate >= 0:
            score += 5

        if income > expense:
            score += 20

        score = max(0, min(100, score))

        # Label
        if score >= 80:
            label = 'Excelente'
            color = '#2ecc71'
        elif score >= 60:
            label = 'Bom'
            color = '#3498db'
        elif score >= 40:
            label = 'Regular'
            color = '#f39c12'
        else:
            label = 'Atenção'
            color = '#e74c3c'

        # Sugestões
        suggestions = []
        if savings_rate < 10:
            suggestions.append('💡 Tente poupar ao menos 10% da sua renda mensal.')
        if expenses_ratio > 90:
            suggestions.append('⚠️ Seus gastos estão acima de 90% da renda. Revise despesas.')
        if savings_rate >= 20:
            suggestions.append('🎉 Ótima taxa de poupança! Considere investir o excedente.')

        # Categoria com mais gasto
        cats = FinanceService.get_expenses_by_category(user_id, today.year, today.month)
        if cats:
            top_cat = max(cats, key=lambda x: x['total'])
            if income > 0 and (top_cat['total'] / income) > 0.30:
                suggestions.append(
                    f"📊 {top_cat['name']} representa mais de 30% da renda. Avalie cortes.")

        return {
            'score':        score,
            'label':        label,
            'color':        color,
            'suggestions':  suggestions,
            'savings_rate': round(savings_rate, 1),
        }

    @staticmethod
    def get_expense_forecast(user_id: int) -> dict:
        """Previsão de gastos para o mês atual baseada em histórico."""
        today   = date.today()
        day_of_month = today.day
        days_in_month = 30  # aproximação

        # Gastos até hoje neste mês
        current_month_exp = float(db.session.query(
            func.coalesce(func.sum(Expense.amount), 0)
        ).filter(
            Expense.user_id == user_id,
            extract('year',  Expense.date) == today.year,
            extract('month', Expense.date) == today.month
        ).scalar())

        # Projeção simples: (gasto até hoje / dias decorridos) * dias no mês
        if day_of_month > 0:
            daily_avg  = current_month_exp / day_of_month
            forecast   = round(daily_avg * days_in_month, 2)
        else:
            forecast   = 0

        return {
            'current':   round(current_month_exp, 2),
            'forecast':  forecast,
            'daily_avg': round(daily_avg if day_of_month > 0 else 0, 2),
        }