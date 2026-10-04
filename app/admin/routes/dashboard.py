from flask import render_template, request, Response, current_app, flash, redirect, url_for
from .. import admin_bp
from ...extensions import db
from ...models import Table, Order
from ...services import audit_service as audit
from ...services import report_service, qr_service

def base_url():
    if current_app.config.get("BASE_URL"): return current_app.config["BASE_URL"].rstrip("/") + "/"
    host = request.host
    if host.startswith(("127.0.0.1", "localhost")): host = f"{qr_service.lan_ip()}:{host.split(':')[-1]}"
    return f"http://{host}/" if host != request.host else request.host_url

@admin_bp.route("/")
def dashboard():
    return render_template("admin/dashboard.html", tables=Table.query.all(), sales=report_service.sales_today(), live=True, lan=base_url())

@admin_bp.route("/qr/page/<name>.png")  # QR หน้า queue / reserve สำหรับติดหน้าร้าน
def qr_page(name):
    return Response(qr_service.qr_png(qr_base() + f"t/{'queue' if name == 'queue' else 'reserve'}"), mimetype="image/png")

@admin_bp.route("/qr/<int:tid>.png")  # QR สำหรับพิมพ์ตั้งโต๊ะ
def qr(tid):
    t = Table.query.get_or_404(tid)
    return Response(qr_service.qr_png(qr_base() + f"t/{t.token}"), mimetype="image/png")

def qr_base():  # ใส่ ?base=https://... เพื่อทำ QR จากที่อยู่เว็บจริงได้โดยไม่ต้องรีสตาร์ต
    return (request.args.get("base") or base_url()).rstrip("/") + "/"

@admin_bp.route("/qr-print")  # หน้าพิมพ์ QR ทุกโต๊ะ
def qr_print():
    return render_template("admin/qr_print.html", tables=Table.query.all(), base=qr_base())

@admin_bp.post("/tables/add")
def table_add():
    t = Table(token="tmp"); db.session.add(t); db.session.flush(); t.token = f"table{t.id}"
    db.session.commit(); audit.log("เพิ่มโต๊ะ", t.id); flash(f"เพิ่มโต๊ะ {t.id} แล้ว")
    return redirect(url_for("admin.dashboard"))

@admin_bp.post("/tables/<int:tid>/delete")
def table_delete(tid):
    t = db.get_or_404(Table, tid)
    if t.status != "free" or Order.query.filter_by(table_id=tid, bill_id=None).first(): flash("ลบไม่ได้ โต๊ะนี้ยังมีลูกค้า/ออเดอร์ค้างอยู่")
    else: db.session.delete(t); db.session.commit(); audit.log("ลบโต๊ะ", tid); flash(f"ลบโต๊ะ {tid} แล้ว")
    return redirect(url_for("admin.dashboard"))
