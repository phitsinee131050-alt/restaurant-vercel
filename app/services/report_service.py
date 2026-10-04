from datetime import datetime
from sqlalchemy import func
from ..extensions import db
from ..models import Bill, Order, OrderItem, Table
def sales_today():
    return db.session.query(func.coalesce(func.sum(Bill.total), 0)).filter(Bill.paid.like(datetime.now().strftime("%Y-%m-%d") + "%")).scalar()
def summary():
    today = datetime.now().strftime("%Y-%m-%d") + "%"
    n = Bill.query.filter(Bill.paid.like(today)).count(); s = sales_today()
    return dict(today_sales=s, today_bills=n, avg=(s / n if n else 0),
                total=db.session.query(func.coalesce(func.sum(Bill.total), 0)).scalar(),
                open_orders=Order.query.filter(Order.bill_id.is_(None), Order.status != "served").count(),
                tables=dict(db.session.query(Table.status, func.count(Table.id)).group_by(Table.status).all()))
def daily():
    d = func.substr(Bill.paid, 1, 10).label("d")
    return db.session.query(d, func.count(Bill.id).label("n"), func.sum(Bill.total).label("s")).group_by(d).order_by(d.desc()).limit(14).all()
def best_sellers():
    n = func.sum(OrderItem.qty).label("n")
    return (db.session.query(OrderItem.name, n).join(Order).filter(OrderItem.cancelled.is_(False), Order.bill_id.isnot(None))
            .group_by(OrderItem.name).order_by(n.desc()).limit(5).all())
