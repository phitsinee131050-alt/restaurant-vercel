from flask import jsonify, request
from . import api_bp
from ..models import Order, Table, MenuItem
from ..services import order_service
@api_bp.post("/orders")
def create():
    d = request.get_json(); t = Table.query.filter_by(token=d["table_token"]).first_or_404(); lines = []
    for it in d["items"]:
        m = MenuItem.query.filter_by(id=it["menu_id"], available=True).first()
        if m: lines.append((m.id, m.name, m.price, it.get("qty", 1), it.get("note", "")))
    return jsonify(id=order_service.create_order(t.id, lines).id), 201
@api_bp.get("/orders")
def lst(): return jsonify([dict(id=o.id, table=o.table_id, status=o.status) for o in Order.query])
