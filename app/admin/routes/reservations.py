from flask import render_template, request, redirect, url_for, flash
from .. import admin_bp
from ...extensions import db
from ...models import Reservation, QueueTicket, Table
from ...services import reservation_service, slots
from ...sockets.kitchen_events import notify

@admin_bp.route("/reservations", methods=["GET", "POST"])
def reservations():
    if request.method == "POST":
        f = request.form
        if f["kind"] == "res":
            try: seats = int(f["seats"] or 0)
            except ValueError: seats = 0
            if not f["name"].strip() or not f["time"].strip() or not 1 <= seats <= 20:
                flash("กรุณากรอกชื่อ วันเวลา และจำนวนที่นั่ง 1-20"); return redirect(url_for("admin.reservations"))
            when = slots.parse_time(f["time"])
            msg = "รูปแบบวันเวลาต้องเป็น ปปปป-ดด-วว ชช:นน เช่น 2026-10-05 18:00" if not when else slots.find_conflict([(x.time, x.phone) for x in Reservation.query], when, f["phone"].strip(), Table.query.count())
            if msg: flash(msg); return redirect(url_for("admin.reservations"))
            db.session.add(Reservation(name=f["name"], phone=f["phone"], time=when.strftime("%Y-%m-%d %H:%M"), seats=seats))
        else: reservation_service.new_ticket(f["name"])
        db.session.commit(); notify(); return redirect(url_for("admin.reservations"))
    return render_template("admin/reservations.html", live=True, res=Reservation.query.order_by(Reservation.time).all(),
                           queue=QueueTicket.query.filter(QueueTicket.status != "done").order_by(QueueTicket.number).all())

@admin_bp.post("/reservations/<kind>/<int:rid>/<act>")
def reservation_act(kind, rid, act):
    if kind == "res": db.session.delete(db.get_or_404(Reservation, rid))
    else: db.get_or_404(QueueTicket, rid).status = act  # called / done
    db.session.commit(); notify(); return redirect(url_for("admin.reservations"))
