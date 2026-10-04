from flask import current_app
from ..extensions import db
from ..models import Recipe, Ingredient
from . import inventory_client

def deduct(menu_id, qty, ref=""):  # ตัดสต็อกตามสูตร
    url = current_app.config.get("INVENTORY_URL")
    for r in Recipe.query.filter_by(menu_id=menu_id):
        ing = db.session.get(Ingredient, r.ingredient_id)
        if url and ing.sku: inventory_client.issue(url, ing.sku, r.qty * qty, ref)  # เชื่อมโปรเจกต์ 3
        else: ing.stock -= r.qty * qty                                               # ใช้สต็อกในตัวเอง
