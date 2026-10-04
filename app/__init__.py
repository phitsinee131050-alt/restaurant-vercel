from flask import Flask, redirect
from config import Config
from .extensions import db
from .shared.enums import TH, NEXT

def create_app():
    app = Flask(__name__); app.config.from_object(Config)
    app.jinja_env.globals.update(TH=TH, NEXT=NEXT)
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)  # หลัง proxy ของ Vercel ให้รู้ว่าเป็น https
    db.init_app(app)
    from .api import api_bp
    from .customer import customer_bp
    from .kitchen import kitchen_bp
    from .admin import admin_bp
    from .auth import auth_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    app.register_blueprint(customer_bp, url_prefix="/t")
    app.register_blueprint(kitchen_bp, url_prefix="/kitchen")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    from .sockets import kitchen_events  # noqa
    with app.app_context():
        from .shared.utils import seed, ensure_users
        db.create_all()
        from sqlalchemy import inspect, text  # เพิ่มคอลัมน์ sku ให้ฐานข้อมูลเดิมโดยไม่ต้องลบไฟล์
        if "sku" not in [c["name"] for c in inspect(db.engine).get_columns("ingredient")]:
            db.session.execute(text("ALTER TABLE ingredient ADD COLUMN sku VARCHAR(40)")); db.session.commit()
        seed(); ensure_users()
    from flask import render_template
    from werkzeug.exceptions import HTTPException
    @app.errorhandler(Exception)  # ผู้ใช้ไม่เห็น Traceback เด็ดขาด (เก็บแค่ข้อความสั้นๆ ไว้ใน Terminal)
    def handle_any(e):
        code = e.code if isinstance(e, HTTPException) else 500
        if code >= 500: app.logger.error("เกิดข้อผิดพลาด: %s: %s", type(e).__name__, e)
        return render_template("error.html", code=code), code
    @app.errorhandler(403)
    def forbidden(e): return render_template("403.html"), 403
    @app.template_filter("img_src")  # รูปเมนู: ข้อมูลรูปในฐานข้อมูล (data:) / ลิงก์ / ชื่อไฟล์เดิม
    def img_src(v): return v if v.startswith(("data:", "http")) else f"/static/uploads/menu/{v}"

    @app.route("/live-version")  # หน้าที่เปิดค้างไว้เรียกทุก 4 วินาที ถ้าค่านี้เปลี่ยน = ข้อมูลเปลี่ยน -> รีเฟรช
    def live_version():
        import hashlib
        from .models import Order, OrderItem, Table, Reservation, QueueTicket
        parts = [[tuple(r) for r in Order.query.with_entities(Order.id, Order.status, Order.bill_id)],
                 [tuple(r) for r in Table.query.with_entities(Table.id, Table.status)],
                 OrderItem.query.count(), OrderItem.query.filter(OrderItem.cancelled.is_(True)).count(),
                 db.session.query(db.func.coalesce(db.func.sum(OrderItem.qty), 0)).scalar(),
                 Reservation.query.count(), [tuple(r) for r in QueueTicket.query.with_entities(QueueTicket.id, QueueTicket.status)]]
        return {"v": hashlib.md5(repr(parts).encode()).hexdigest()}

    app.add_url_rule("/", "index", lambda: redirect("/admin/"))
    return app
