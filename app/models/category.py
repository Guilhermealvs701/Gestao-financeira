"""
Model: Category
"""
from datetime import datetime
from app import db


class Category(db.Model):
    __tablename__ = 'categories'

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(80), nullable=False)
    icon       = db.Column(db.String(60), default='fa-tag')
    color      = db.Column(db.String(20), default='#4f46e5')
    is_default = db.Column(db.Boolean, default=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    expenses = db.relationship('Expense', backref='category', lazy='dynamic')

    def to_dict(self):
        return {
            'id':         self.id,
            'name':       self.name,
            'icon':       self.icon,
            'color':      self.color,
            'is_default': self.is_default,
        }

    def __repr__(self):
        return f'<Category {self.name}>'