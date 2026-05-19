"""
Model: User
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    avatar_color  = db.Column(db.String(20), default='#4f46e5')
    monthly_goal  = db.Column(db.Float, default=0.0)
    dark_mode     = db.Column(db.Boolean, default=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    last_login    = db.Column(db.DateTime)
    is_active     = db.Column(db.Boolean, default=True)

    # ── Relacionamentos ────────────────────────────────────────────────────────
    expenses   = db.relationship('Expense',  backref='user', lazy='dynamic', cascade='all, delete-orphan')
    incomes    = db.relationship('Income',   backref='user', lazy='dynamic', cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='user', lazy='dynamic',
                                 foreign_keys='Category.user_id', cascade='all, delete-orphan')
    goals      = db.relationship('Goal',     backref='user', lazy='dynamic', cascade='all, delete-orphan')

    # ── Propriedades ──────────────────────────────────────────────────────────
    @property
    def password(self):
        raise AttributeError('Senha não é legível.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def initials(self):
        parts = self.name.strip().split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return self.name[:2].upper()

    def __repr__(self):
        return f'<User {self.email}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))