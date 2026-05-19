"""
Finance Control Pro - Configurações do Sistema
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ── Segurança ──────────────────────────────────────────────────────────────
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-mude-em-producao-12345')
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    # ── Banco de Dados ─────────────────────────────────────────────────────────
    DB_HOST     = os.getenv('DB_HOST', 'localhost')
    DB_PORT     = os.getenv('DB_PORT', '3306')
    DB_NAME     = os.getenv('DB_NAME', 'finance_control_pro')
    DB_USER     = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        "?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # ── Upload ─────────────────────────────────────────────────────────────────
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))

    # ── Sessão ─────────────────────────────────────────────────────────────────
    PERMANENT_SESSION_LIFETIME = 86400  # 24 horas


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,
}