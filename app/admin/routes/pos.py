from datetime import datetime
from flask import render_template, request, redirect, url_for, current_app, flash
from .. import admin_bp
from ...extensions import db
from ...models import Table, MenuItem, Order, OrderItem, Bill, Member
from ...services import order_service as svc
from ...services.billing_service import calc, split
from ...sockets.kitchen_events import notify
from ...shared.utils import to_int, to_float
from ...services import audit_service as audit

def back(tid): return redirect(url_for("admin.table", tid=tid))

@admin_bp.route("/table/<int:tid>")
def table(tid):
    return render_template("admin/table.html", t=db.get_or_404(Table, tid), tables=Table.query.all(),
                           items=svc.active_items(tid), menu=MenuItem.query.filter_by(available=True).all())

@admin_bp.post("/table/<int:tid>/status")
def set_status(tid):
    db.get_or_404(Table, tid).status = request.form["status"]; db.session.commit(); notify(); return back(tid)

@admin_bp.post("/table/<int:tid>/add")
def add(tid):
    m = db.get_or_404(MenuItem, to_int(request.form.get("menu_id")))
    svc.create_order(tid, [(m.id, m.name, m.price, max(to_int(request.form.get("qty"), 1), 1), "")]); return back(tid)

@admin_bp.post("/item/<int:iid>")
def item(iid):
    it, act = db.get_or_404(OrderItem, iid), request.form["act"]
    if act == "inc": it.qty += 1
    elif act == "dec" and it.qty > 1: it.qty -= 1
    else: it.cancelled = True
    db.session.commit(); notify(); audit.log("แก้รายการ: " + act, f"{it.name} โต๊ะ {it.order.table_id}")
    return back(it.order.table_id)

@admin_bp.post("/table/<int:tid>/move")  # ย้ายโต๊ะ / รวมโต๊ะ
def move(tid):
    to = to_int(request.form.get("to"))
    Order.query.filter_by(table_id=tid, bill_id=None).update({"table_id": to})
    db.session.get(Table, tid).status = "free"; db.session.get(Table, to).status = "occupied"
    db.session.commit(); notify(); audit.log("ย้าย/รวมโต๊ะ", f"โต๊ะ {tid} -> {to}"); return back(to)

def _calc(sub, disc):
    c = current_app.config
    return calc(sub, disc, c["SERVICE_CHARGE"], c["VAT_RATE"])

@admin_bp.route("/table/<int:tid>/checkout", methods=["GET", "POST"])
def checkout(tid):  # เช็คบิล + แยกบิลตามรายการ (เลือกจำนวนที่จ่ายของแต่ละรายการ)
    disc = max(to_float(request.values.get("discount")), 0); people = max(to_int(request.values.get("people"), 1), 1)
    items = svc.active_items(tid)
    paid = {i.id: min(max(to_int(request.values.get(f"pay_{i.id}"), i.qty), 0), i.qty) for i in items}  # ไม่ระบุ = จ่ายทั้งหมด
    c = _calc(sum(i.price * paid[i.id] for i in items), disc)
    if request.method == "POST":
        if c["subtotal"] <= 0:
            flash("กรุณาเลือกรายการที่จะจ่ายอย่างน้อย 1 รายการ"); return redirect(url_for("admin.checkout", tid=tid))
        phone = request.form.get("phone", "").strip()
        b = Bill(table_id=tid, phone=phone, paid=datetime.now().strftime("%Y-%m-%d %H:%M"), **c); db.session.add(b); db.session.flush()
        part = Order(table_id=tid, status="served", created=datetime.now().strftime("%H:%M:%S"), bill_id=b.id); db.session.add(part); db.session.flush()
        for i in items:  # ย้ายรายการที่จ่ายไปไว้ในออเดอร์ของบิลนี้ (จ่ายไม่ครบจำนวน = แยกบรรทัด)
            n = paid[i.id]
            if n == i.qty: i.order_id = part.id
            elif n > 0:
                i.qty -= n; db.session.add(OrderItem(order_id=part.id, menu_id=i.menu_id, name=i.name, price=i.price, qty=n, note=i.note))
        db.session.flush()
        if not svc.active_items(tid):  # จ่ายครบทุกรายการแล้ว -> ปิดโต๊ะ
            Order.query.filter_by(table_id=tid, bill_id=None).update({"bill_id": b.id}); db.session.get(Table, tid).status = "free"
        if phone:
            m = Member.query.filter_by(phone=phone).first() or Member(phone=phone, points=0); db.session.add(m)
            m.points = (m.points or 0) + int(c["total"] // 10)
        db.session.commit(); notify(); audit.log("เช็คบิล", f"โต๊ะ {tid} บิล #{b.id} สุทธิ {c['total']} ({sum(paid.values())} รายการ)")
        return redirect(url_for("admin.receipt", bid=b.id))
    return render_template("admin/checkout.html", t=tid, c=c, disc=disc, people=people, per=split(c["total"], people), items=items, paid=paid)

@admin_bp.route("/receipt/<int:bid>")
def receipt(bid):
    b = db.get_or_404(Bill, bid)
    items = OrderItem.query.join(Order).filter(Order.bill_id == bid, OrderItem.cancelled.is_(False)).all()
    m = Member.query.filter_by(phone=b.phone).first() if b.phone else None
    return render_template("admin/receipt.html", b=b, items=items, m=m)
