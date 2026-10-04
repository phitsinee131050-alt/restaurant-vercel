from flask import render_template, request, redirect, url_for, session, abort
from . import customer_bp
from ..models import MenuItem, MenuOption, Table, Order
from ..services import order_service
from ..shared.utils import to_int

@customer_bp.route("/<token>", methods=["GET", "POST"])
def menu(token):
    t = Table.query.filter_by(token=token).first_or_404()
    if request.method == "POST":
        lines, f = [], request.form
        for m in MenuItem.query.filter_by(available=True):
            n = to_int(f.get(f"qty_{m.id}"))
            if n < 1: continue
            price, opts = m.price, []
            for o in MenuOption.query.filter_by(menu_id=m.id):  # รับเฉพาะตัวเลือกที่แอดมินตั้งให้เมนูนี้
                v = f.get(f"opt_{o.id}")
                if o.kind == "choice" and v in o.choices.split(","): opts.append(f"{o.name}: {v}")
                elif o.kind == "addon" and v: opts.append(o.name); price += o.price
            lines.append((m.id, m.name, price, n, " / ".join(opts)))
        if lines: order_service.create_order(t.id, lines)
        return redirect(url_for("customer.status", token=token))
    opts = {}
    for o in MenuOption.query.order_by(MenuOption.id): opts.setdefault(o.menu_id, []).append(o)
    return render_template("customer/menu.html", t=t, opts=opts, menu=MenuItem.query.order_by(MenuItem.category, MenuItem.id).all())

@customer_bp.route("/<token>/status")
def status(token):
    t = Table.query.filter_by(token=token).first_or_404()
    orders = Order.query.filter_by(table_id=t.id, bill_id=None).order_by(Order.id.desc()).all()
    items = {o.id: [i for i in o.items if not i.cancelled] for o in orders}
    orders = [o for o in orders if items[o.id]]  # ซ่อนออเดอร์ที่จ่ายไปหมดแล้ว
    return render_template("customer/status.html", t=t, orders=orders, items=items, live=True)

# ---------- ลูกค้ารับคิว / จองโต๊ะเอง (ไม่ต้องล็อกอิน) ----------
from ..extensions import db
from ..models import QueueTicket, Reservation
from ..services import reservation_service
from ..sockets.kitchen_events import notify

@customer_bp.route("/queue", methods=["GET", "POST"])
def queue():
    if request.method == "POST":
        name = request.form["name"].strip() + f" ({request.form.get('seats') or 2} คน)"
        t = reservation_service.new_ticket(name); notify("queue:new")
        return redirect(url_for("customer.queue_status", tid=t.id))
    waiting = QueueTicket.query.filter_by(status="waiting").count()
    return render_template("customer/queue.html", waiting=waiting, live=True)

@customer_bp.route("/queue/<int:tid>")
def queue_status(tid):
    t = db.get_or_404(QueueTicket, tid)
    ahead = QueueTicket.query.filter(QueueTicket.status == "waiting", QueueTicket.number < t.number).count()
    cur = QueueTicket.query.filter_by(status="called").order_by(QueueTicket.number.desc()).first()
    return render_template("customer/queue_status.html", t=t, ahead=ahead, cur=cur, live=True)

@customer_bp.route("/reserve", methods=["GET", "POST"])
def reserve():
    if request.method == "POST":
        import re
        from datetime import datetime
        f, errs = request.form, []
        if not re.fullmatch(r"0\d{9}", f["phone"].strip()): errs.append("เบอร์โทรต้องเป็นตัวเลข 10 หลัก ขึ้นต้นด้วย 0")
        if len(f["name"].strip()) < 2: errs.append("กรุณากรอกชื่อ")
        try: when = datetime.strptime(f"{f['date']} {f['time']}", "%Y-%m-%d %H:%M")
        except ValueError: when = None; errs.append("วันเวลาไม่ถูกต้อง")
        if when and when < datetime.now(): errs.append("ต้องจองล่วงหน้า วันเวลาต้องยังมาไม่ถึง")
        try: seats_ok = 1 <= int(f["seats"] or 0) <= 20
        except ValueError: seats_ok = False
        if not seats_ok: errs.append("จำนวนที่นั่งต้อง 1-20")
        if when and not errs:  # เช็คเวลาซ้ำ / โต๊ะเต็ม
            from ..services import slots
            msg = slots.find_conflict([(x.time, x.phone) for x in Reservation.query], when, f["phone"].strip(), Table.query.count())
            if msg: errs.append(msg)
        if errs: return render_template("customer/reserve.html", errs=errs)
        res = Reservation(name=f["name"], phone=f["phone"], time=f"{f['date']} {f['time']}", seats=int(f["seats"] or 2))
        db.session.add(res); db.session.commit(); notify("reservation:new")
        return redirect(url_for("customer.reserve_done", rid=res.id))  # กัน refresh แล้วจองซ้ำ
    return render_template("customer/reserve.html")

@customer_bp.route("/reserve/<int:rid>")
def reserve_done(rid):
    return render_template("customer/reserve_done.html", r=db.get_or_404(Reservation, rid))

@customer_bp.post("/reserve/<int:rid>/cancel")
def reserve_cancel(rid):
    r = db.get_or_404(Reservation, rid)
    if session.get("username") != r.phone: abort(403)  # ยกเลิกได้เฉพาะการจองของตัวเอง
    db.session.delete(r); db.session.commit(); notify("reservation:cancel")
    return redirect("/me")
