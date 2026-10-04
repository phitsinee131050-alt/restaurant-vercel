from datetime import datetime
from ..extensions import db
from ..models import Order, OrderItem, Table
from . import stock_service
from ..sockets.kitchen_events import notify

def create_order(tid, lines):  # lines = [(menu_id, name, price, qty, note)]
    o = Order(table_id=tid, created=datetime.now().strftime("%H:%M:%S")); db.session.add(o)
    for mid, n, p, c, note in lines:
        o.items.append(OrderItem(menu_id=mid, name=n, price=p, qty=c, note=note)); stock_service.deduct(mid, c, f"โต๊ะ {tid}")
    t = db.session.get(Table, tid)
    if t.status == "free": t.status = "occupied"
    db.session.commit(); notify("order:new"); return o

def active_items(tid):
    return (OrderItem.query.join(Order).filter(Order.table_id == tid, Order.bill_id.is_(None), OrderItem.cancelled.is_(False))
            .order_by(OrderItem.id).all())
