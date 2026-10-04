from flask import jsonify
from . import api_bp
from ..models import MenuItem
@api_bp.get("/menu")
def menu(): return jsonify([dict(id=m.id, name=m.name, category=m.category, price=m.price, available=m.available) for m in MenuItem.query])
