import os, time
from datetime import datetime
from flask import render_template, request, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from .. import admin_bp
from ...db import q
from ...services import orders as svc
from ...services.billing import calc
from ... import events

def back(tid): return redirect(url_for("admin.table", tid=tid))

@admin_bp.route("/")
def dashboard():
    return render_template("admin/dashboard.html", tables=q("SELECT * FROM tables"), live=True,
        sales=q("SELECT COALESCE(SUM(total),0) s FROM bills WHERE paid LIKE ?", (datetime.now().strftime("%Y-%m-%d") + "%",), one=True)["s"])

# --- เมนู
@admin_bp.route("/menu", methods=["GET", "POST"])
def menu():
    if request.method == "POST":
        img, f = "", request.files.get("image")
        if f and f.filename:
            img = f"{int(time.time())}_{secure_filename(f.filename)}"
            d = os.path.join(current_app.static_folder, "uploads", "menu"); os.makedirs(d, exist_ok=True)
            f.save(os.path.join(d, img))
        q("INSERT INTO menu(name,category,price,image) VALUES(?,?,?,?)",
          (request.form["name"], request.form["category"], float(request.form["price"]), img))
        return redirect(url_for("admin.menu"))
    return render_template("admin/menu.html", menu=q("SELECT * FROM menu ORDER BY category,id"))

@admin_bp.post("/menu/<int:mid>")
def menu_update(mid):
    act = request.form["act"]
    if act == "toggle": q("UPDATE menu SET available=1-available WHERE id=?", (mid,))
    elif act == "delete": q("DELETE FROM menu WHERE id=?", (mid,))
    elif act == "price": q("UPDATE menu SET price=? WHERE id=?", (float(request.form["price"]), mid))
    return redirect(url_for("admin.menu"))

# --- โต๊ะ / ออเดอร์
@admin_bp.route("/table/<int:tid>")
def table(tid):
    return render_template("admin/table.html", t=q("SELECT * FROM tables WHERE id=?", (tid,), one=True),
        tables=q("SELECT * FROM tables"), items=svc.active_items(tid), menu=q("SELECT * FROM menu WHERE available=1"))

@admin_bp.post("/table/<int:tid>/status")
def set_status(tid):
    q("UPDATE tables SET status=? WHERE id=?", (request.form["status"], tid)); events.bump(); return back(tid)

@admin_bp.post("/table/<int:tid>/add")
def add(tid):
    m = q("SELECT * FROM menu WHERE id=?", (request.form["menu_id"],), one=True)
    svc.create_order(tid, [(m["name"], m["price"], int(request.form["qty"]), "")]); return back(tid)

@admin_bp.post("/item/<int:iid>")
def item(iid):
    it = q("SELECT i.*, o.table_id FROM items i JOIN orders o ON o.id=i.order_id WHERE i.id=?", (iid,), one=True)
    act = request.form["act"]
    if act == "inc": q("UPDATE items SET qty=qty+1 WHERE id=?", (iid,))
    elif act == "dec" and it["qty"] > 1: q("UPDATE items SET qty=qty-1 WHERE id=?", (iid,))
    else: q("UPDATE items SET cancelled=1 WHERE id=?", (iid,))
    events.bump(); return back(it["table_id"])

@admin_bp.post("/table/<int:tid>/move")  # ย้ายโต๊ะ / รวมโต๊ะ
def move(tid):
    to = int(request.form["to"])
    q("UPDATE orders SET table_id=? WHERE table_id=? AND bill_id IS NULL", (to, tid))
    q("UPDATE tables SET status='free' WHERE id=?", (tid,))
    q("UPDATE tables SET status='occupied' WHERE id=?", (to,)); events.bump(); return back(to)

# --- เช็คบิล
def _calc(tid, disc):
    sub = sum(i["price"] * i["qty"] for i in svc.active_items(tid))
    c = current_app.config
    return calc(sub, disc, c["SERVICE_CHARGE"], c["VAT_RATE"])

@admin_bp.route("/table/<int:tid>/checkout", methods=["GET", "POST"])
def checkout(tid):
    disc = float(request.values.get("discount") or 0)
    c = _calc(tid, disc)
    if request.method == "POST" and c["subtotal"] > 0:
        phone = request.form.get("phone", "").strip()
        q("INSERT INTO bills(table_id,subtotal,discount,service,vat,total,phone,paid) VALUES(?,?,?,?,?,?,?,?)",
          (tid, c["subtotal"], disc, c["service"], c["vat"], c["total"], phone, datetime.now().strftime("%Y-%m-%d %H:%M")))
        bid = q("SELECT last_insert_rowid() r", one=True)["r"]
        q("UPDATE orders SET bill_id=? WHERE table_id=? AND bill_id IS NULL", (bid, tid))
        q("UPDATE tables SET status='free' WHERE id=?", (tid,))
        if phone:
            q("INSERT OR IGNORE INTO members(phone) VALUES(?)", (phone,))
            q("UPDATE members SET points=points+? WHERE phone=?", (int(c["total"] // 10), phone))
        events.bump(); return redirect(url_for("admin.receipt", bid=bid))
    return render_template("admin/checkout.html", t=tid, c=c, disc=disc, items=svc.active_items(tid))

@admin_bp.route("/receipt/<int:bid>")
def receipt(bid):
    b = q("SELECT * FROM bills WHERE id=?", (bid,), one=True)
    items = q("SELECT i.* FROM items i JOIN orders o ON o.id=i.order_id WHERE o.bill_id=? AND i.cancelled=0", (bid,))
    m = q("SELECT * FROM members WHERE phone=?", (b["phone"],), one=True) if b["phone"] else None
    return render_template("admin/receipt.html", b=b, items=items, m=m)

# --- รายงาน
@admin_bp.route("/reports")
def reports():
    daily = q("SELECT substr(paid,1,10) d, COUNT(*) n, SUM(total) s FROM bills GROUP BY d ORDER BY d DESC LIMIT 14")
    best = q("""SELECT i.name, SUM(i.qty) n FROM items i JOIN orders o ON o.id=i.order_id
                WHERE i.cancelled=0 AND o.bill_id IS NOT NULL GROUP BY i.name ORDER BY n DESC LIMIT 5""")
    return render_template("admin/reports.html", daily=daily, best=best)
