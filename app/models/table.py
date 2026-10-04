from ..extensions import db
class Table(db.Model):
    __tablename__ = "dining_table"
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(40), unique=True); status = db.Column(db.String(20), default="free")
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80)); phone = db.Column(db.String(20)); time = db.Column(db.String(40)); seats = db.Column(db.Integer, default=2)
class QueueTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer); name = db.Column(db.String(80)); status = db.Column(db.String(20), default="waiting")
