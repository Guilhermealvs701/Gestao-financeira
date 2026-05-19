"""
Model: Income
"""
from datetime import datetime
from app import db


class Income(db.Model):
    __tablename__ = 'incomes'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name       = db.Column(db.String(150), nullable=False)
    amount     = db.Column(db.Numeric(12, 2), nullable=False)
    date       = db.Column(db.Date, nullable=False, index=True)
    type       = db.Column(db.String(60), default='Salário')
    notes      = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    INCOME_TYPES = [
        'Salário', 'Freelance', 'Investimentos', 'Aluguel',
        'Presente', 'Bônus', 'Reembolso', 'Outros'
    ]

    def to_dict(self):
        return {
            'id':     self.id,
            'name':   self.name,
            'amount': float(self.amount),
            'date':   self.date.strftime('%Y-%m-%d'),
            'type':   self.type,
            'notes':  self.notes,
        }

    def __repr__(self):
        return f'<Income {self.name} R${self.amount}>'