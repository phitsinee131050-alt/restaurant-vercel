from flask import render_template, redirect, url_for
from . import kitchen_bp
from ..extensions import db
from ..models import Order
from ..sockets.kitchen_events import notify

@kitchen_bp.route("/")
def display():
    orders = Order.query.filter(Order.status != "served", Order.bill_id.is_(None)).order_by(Order.id).all()
    data = [(o, [i for i in o.items if not i.cancelled]) for o in orders]
    return render_template("kitchen/display.html", data=[d for d in data if d[1]], live=True)

@kitchen_bp.post("/<int:oid>/<status>")
def advance(oid, status):
    db.get_or_404(Order, oid).status = status; db.session.commit(); notify("order:status")
    return redirect(url_for("kitchen.display"))
