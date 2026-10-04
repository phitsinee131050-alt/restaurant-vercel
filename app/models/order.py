from ..extensions import db
class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey("dining_table.id"))
    status = db.Column(db.String(20), default="pending"); created = db.Column(db.String(20))
    bill_id = db.Column(db.Integer, nullable=True)
    items = db.relationship("OrderItem", backref="order")
class OrderItem(db.Model):
    __tablename__ = "order_item"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id")); menu_id = db.Column(db.Integer)
    name = db.Column(db.String(100)); price = db.Column(db.Float); qty = db.Column(db.Integer)
    note = db.Column(db.String(200), default=""); cancelled = db.Column(db.Boolean, default=False)
