"""
Model: Expense
"""
from datetime import datetime
from app import db


class Expense(db.Model):
    __tablename__ = 'expenses'

    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    category_id    = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    name           = db.Column(db.String(150), nullable=False)
    amount         = db.Column(db.Numeric(12, 2), nullable=False)
    date           = db.Column(db.Date, nullable=False, index=True)
    payment_method = db.Column(db.String(50), default='Dinheiro')
    notes          = db.Column(db.Text)
    is_recurring   = db.Column(db.Boolean, default=False)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at     = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    PAYMENT_METHODS = [
        'Dinheiro', 'Cartão de Crédito', 'Cartão de Débito',
        'PIX', 'Transferência', 'Boleto', 'Outros'
    ]

    def to_dict(self):
        return {
            'id':             self.id,
            'name':           self.name,
            'amount':         float(self.amount),
            'date':           self.date.strftime('%Y-%m-%d'),
            'payment_method': self.payment_method,
            'notes':          self.notes,
            'category':       self.category.to_dict() if self.category else None,
        }

    def __repr__(self):
        return f'<Expense {self.name} R${self.amount}>'