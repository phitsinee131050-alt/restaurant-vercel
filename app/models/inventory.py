from ..extensions import db
class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(40)); name = db.Column(db.String(80)); unit = db.Column(db.String(20)); stock = db.Column(db.Float, default=0)
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey("menu_item.id")); ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredient.id"))
    qty = db.Column(db.Float)
