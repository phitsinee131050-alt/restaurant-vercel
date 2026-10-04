from ..extensions import db
class Member(db.Model):
    __tablename__ = "members"
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True); points = db.Column(db.Integer, default=0)
