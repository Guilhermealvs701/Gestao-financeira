"""
Finance Control Pro - Application Factory
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from config import config

# ── Extensões globais ──────────────────────────────────────────────────────────
db       = SQLAlchemy()
login_manager = LoginManager()
csrf     = CSRFProtect()
migrate  = Migrate()


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # ── Inicializar extensões ──────────────────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    # ── Login Manager ──────────────────────────────────────────────────────────
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'warning'

    # ── Registrar Blueprints ───────────────────────────────────────────────────
    from app.routes.auth       import auth_bp
    from app.routes.dashboard  import dashboard_bp
    from app.routes.expenses   import expenses_bp
    from app.routes.incomes    import incomes_bp
    from app.routes.reports    import reports_bp
    from app.routes.categories import categories_bp
    from app.routes.goals      import goals_bp
    from app.routes.api        import api_bp

    app.register_blueprint(auth_bp,       url_prefix='/auth')
    app.register_blueprint(dashboard_bp,  url_prefix='/')
    app.register_blueprint(expenses_bp,   url_prefix='/expenses')
    app.register_blueprint(incomes_bp,    url_prefix='/incomes')
    app.register_blueprint(reports_bp,    url_prefix='/reports')
    app.register_blueprint(categories_bp, url_prefix='/categories')
    app.register_blueprint(goals_bp,      url_prefix='/goals')
    app.register_blueprint(api_bp,        url_prefix='/api')

    # ── Criar banco automaticamente ────────────────────────────────────────────
    with app.app_context():
        db.create_all()
        _seed_default_data()

    return app


def _seed_default_data():
    """Insere dados padrão se o banco estiver vazio."""
    from app.models.category import Category
    if Category.query.count() == 0:
        defaults = [
            Category(name='Alimentação',  icon='fa-utensils',         color='#e74c3c', is_default=True),
            Category(name='Transporte',   icon='fa-car',              color='#3498db', is_default=True),
            Category(name='Contas',       icon='fa-file-invoice',     color='#e67e22', is_default=True),
            Category(name='Saúde',        icon='fa-heartbeat',        color='#2ecc71', is_default=True),
            Category(name='Lazer',        icon='fa-gamepad',          color='#9b59b6', is_default=True),
            Category(name='Investimentos',icon='fa-chart-line',       color='#1abc9c', is_default=True),
            Category(name='Educação',     icon='fa-graduation-cap',   color='#f39c12', is_default=True),
            Category(name='Outros',       icon='fa-ellipsis-h',       color='#95a5a6', is_default=True),
        ]
        from app import db
        db.session.add_all(defaults)
        db.session.commit()