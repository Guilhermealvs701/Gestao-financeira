"""
Model: Goal
"""
from datetime import datetime
from app import db


class Goal(db.Model):
    __tablename__ = 'goals'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title       = db.Column(db.String(150), nullable=False)
    target      = db.Column(db.Numeric(12, 2), nullable=False)
    current     = db.Column(db.Numeric(12, 2), default=0.0)
    deadline    = db.Column(db.Date)
    description = db.Column(db.Text)
    icon        = db.Column(db.String(60), default='fa-bullseye')
    color       = db.Column(db.String(20), default='#4f46e5')
    completed   = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def progress_percent(self):
        if self.target and float(self.target) > 0:
            return min(100, round((float(self.current) / float(self.target)) * 100, 1))
        return 0

    def __repr__(self):
        return f'<Goal {self.title}>'