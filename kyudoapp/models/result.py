from kyudoapp import db
from datetime import datetime


class Result(db.Model):
    __tablename__ = 'result'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.now, onupdate=datetime.now)
    position1 = db.Column(db.Integer, default="20")
    atari1 = db.Column(db.Integer, default="3")
    position2 = db.Column(db.Integer, default="20")
    atari2 = db.Column(db.Integer, default="3")
    memo = db.Column(db.String(191), default="")
