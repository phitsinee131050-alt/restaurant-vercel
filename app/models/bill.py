from ..extensions import db
class Bill(db.Model):
    __tablename__ = "bills"
    id = db.Column(db.Integer, primary_key=True); table_id = db.Column(db.Integer)
    subtotal = db.Column(db.Float); discount = db.Column(db.Float); service = db.Column(db.Float)
    vat = db.Column(db.Float); total = db.Column(db.Float); phone = db.Column(db.String(20)); paid = db.Column(db.String(20))
