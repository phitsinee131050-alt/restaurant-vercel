import os, time
from flask import render_template, request, redirect, url_for, current_app, flash, Response, abort
from sqlalchemy import func
from .. import admin_bp
from ...extensions import db
from ...models import MenuItem, MenuOption
from ...shared.utils import to_float
from ...services import audit_service as audit, menu_io

ALLOWED = {"png", "jpg", "jpeg", "gif", "webp"}
SORTS = {"cat": MenuItem.category.asc(), "name": MenuItem.name.asc(), "price_asc": MenuItem.price.asc(), "price_desc": MenuItem.price.desc()}

def check(f, files, exclude_id=None):  # ตรวจข้อมูลนำเข้า
    errs, name, cat = [], f.get("name", "").strip(), f.get("category", "").strip()
    try: price = float(f.get("price", ""))
    except ValueError: price = 0
    if len(name) < 2: errs.append("ชื่อเมนูต้องมีอย่างน้อย 2 ตัวอักษร")
    if not cat: errs.append("กรุณาระบุหมวดหมู่")
    if not 0 < price <= 100000: errs.append("ราคาต้องมากกว่า 0 และไม่เกิน 100,000")
    dup = MenuItem.query.filter(func.lower(MenuItem.name) == name.lower())
    if exclude_id: dup = dup.filter(MenuItem.id != exclude_id)
    if name and dup.first(): errs.append("มีเมนูชื่อนี้อยู่แล้ว")
    img = files.get("image")
    if img and img.filename and img.filename.rsplit(".", 1)[-1].lower() not in ALLOWED: errs.append("รูปต้องเป็นไฟล์ png / jpg / gif / webp")
    return errs, name, cat, price

def save_image(img):  # เก็บรูปเป็นข้อความ (data URI) ในฐานข้อมูล -> ใช้ได้ทั้งในเครื่องและบน Vercel
    if not (img and img.filename): return None
    data = img.read()
    if len(data) > 300_000: flash("รูปใหญ่เกิน 300KB กรุณาย่อรูปก่อน"); return None
    import base64
    return f"data:{img.mimetype or 'image/png'};base64," + base64.b64encode(data).decode()

def categories(): return [c for (c,) in db.session.query(MenuItem.category).distinct().order_by(MenuItem.category)]

@admin_bp.route("/menu", methods=["GET", "POST"])
def menu():
    if request.method == "POST":
        errs, name, cat, price = check(request.form, request.files)
        for e in errs: flash(e)
        if not errs:
            db.session.add(MenuItem(name=name, category=cat, price=price, image=save_image(request.files.get("image")) or ""))
            db.session.commit(); audit.log("เพิ่มเมนู", name); flash("เพิ่มเมนูแล้ว")
        return redirect(url_for("admin.menu"))
    q, cat, sort = request.args.get("q", "").strip(), request.args.get("cat", ""), request.args.get("sort", "cat")
    qs = MenuItem.query
    if q: qs = qs.filter(MenuItem.name.contains(q))
    if cat: qs = qs.filter(MenuItem.category == cat)
    p = qs.order_by(SORTS.get(sort, SORTS["cat"]), MenuItem.id).paginate(page=request.args.get("page", 1, type=int), per_page=8, error_out=False)
    return render_template("admin/menu.html", p=p, q=q, cat=cat, sort=sort, cats=categories())

@admin_bp.route("/menu/<int:mid>/edit", methods=["GET", "POST"])
def menu_edit(mid):
    m = db.get_or_404(MenuItem, mid)
    if request.method == "POST":
        errs, name, cat, price = check(request.form, request.files, mid)
        if errs:
            for e in errs: flash(e)
            return redirect(url_for("admin.menu_edit", mid=mid))
        old = f"{m.name}/{m.category}/{m.price}"
        m.name, m.category, m.price, m.available = name, cat, price, bool(request.form.get("available"))
        img = save_image(request.files.get("image"))
        if img: m.image = img
        db.session.commit(); audit.log("แก้เมนู", f"{old} -> {name}/{cat}/{price}"); flash("บันทึกแล้ว")
        return redirect(url_for("admin.menu"))
    return render_template("admin/menu_edit.html", m=m, cats=categories(), options=MenuOption.query.filter_by(menu_id=mid).all(), presets=menu_io.PRESETS)

@admin_bp.post("/menu/<int:mid>")
def menu_update(mid):
    m, act = db.get_or_404(MenuItem, mid), request.form["act"]
    name = m.name
    if act == "toggle": m.available = not m.available
    elif act == "delete": db.session.delete(m)
    db.session.commit(); audit.log("เมนู: " + act, name)
    return redirect(request.referrer or url_for("admin.menu"))

@admin_bp.route("/menu/export.<fmt>")
def menu_export(fmt):  # ส่งออกเมนูเป็นไฟล์
    items = [dict(name=x.name, category=x.category, price=x.price) for x in MenuItem.query.order_by(MenuItem.category, MenuItem.id)]
    if fmt == "csv": body, mime = "\ufeff" + menu_io.to_csv(items), "text/csv"
    elif fmt == "json": body, mime = menu_io.to_json(items), "application/json"
    else: abort(404)
    return Response(body, mimetype=mime + "; charset=utf-8", headers={"Content-Disposition": f"attachment; filename=menu.{fmt}"})

@admin_bp.post("/menu/import")
def menu_import():  # อัปโหลดไฟล์เมนู: ชื่อซ้ำ = อัปเดต, ชื่อใหม่ = เพิ่ม
    f = request.files.get("file")
    if not f or not f.filename:
        flash("กรุณาเลือกไฟล์ก่อน"); return redirect(url_for("admin.menu"))
    try: rows, errs = menu_io.parse_rows(f.filename, f.read())
    except OSError: rows, errs = [], ["อ่านไฟล์ไม่สำเร็จ"]
    for e in errs[:10]: flash(e)
    added = updated = 0
    for r in rows:
        x = MenuItem.query.filter(func.lower(MenuItem.name) == r["name"].lower()).first()
        if x: x.category, x.price = r["category"], r["price"]; updated += 1
        else:
            x = MenuItem(name=r["name"], category=r["category"], price=r["price"]); db.session.add(x); db.session.flush(); added += 1
        for key in r["options"]:  # คอลัมน์ options ในไฟล์ = รหัสแบบสำเร็จรูป เช่น spicy|egg
            kind, nm, ch, pr = menu_io.PRESETS[key]
            if not MenuOption.query.filter_by(menu_id=x.id, name=nm).first(): db.session.add(MenuOption(menu_id=x.id, kind=kind, name=nm, choices=ch, price=pr))
    db.session.commit(); audit.log("นำเข้าเมนู", f"{f.filename}: เพิ่ม {added} แก้ {updated} ข้าม {len(errs)}")
    flash(f"นำเข้าแล้ว: เพิ่ม {added} · อัปเดต {updated} · ข้าม {len(errs)}"); return redirect(url_for("admin.menu"))

@admin_bp.post("/menu/<int:mid>/options/add")
def option_add(mid):
    db.get_or_404(MenuItem, mid); f = request.form; key = f.get("preset", "")
    if key in menu_io.PRESETS: kind, name, choices, price = menu_io.PRESETS[key]
    else: kind, name, choices, price = f.get("kind", "addon"), f.get("name", "").strip(), f.get("choices", ""), to_float(f.get("price"))
    choices = ",".join(c.strip() for c in choices.split(",") if c.strip()) if kind == "choice" else ""
    errs = []
    if kind not in ("addon", "choice"): errs.append("ประเภทตัวเลือกไม่ถูกต้อง")
    if len(name) < 2: errs.append("ชื่อตัวเลือกต้องมีอย่างน้อย 2 ตัวอักษร")
    if kind == "choice" and len([c for c in choices.split(",") if c]) < 2: errs.append("แบบให้เลือกต้องมีอย่างน้อย 2 ตัวเลือก (คั่นด้วย ,)")
    if not 0 <= price <= 1000: errs.append("ราคาเพิ่มต้องอยู่ระหว่าง 0-1000")
    if MenuOption.query.filter_by(menu_id=mid, name=name).first(): errs.append("เมนูนี้มีตัวเลือกชื่อนี้แล้ว")
    for e in errs: flash(e)
    if not errs:
        db.session.add(MenuOption(menu_id=mid, kind=kind, name=name, choices=choices, price=price)); db.session.commit()
        audit.log("เพิ่มตัวเลือกเมนู", f"เมนู #{mid}: {name}"); flash("เพิ่มตัวเลือกแล้ว")
    return redirect(url_for("admin.menu_edit", mid=mid))

@admin_bp.post("/menu/options/<int:oid>/delete")
def option_delete(oid):
    o = db.get_or_404(MenuOption, oid); mid, name = o.menu_id, o.name
    db.session.delete(o); db.session.commit(); audit.log("ลบตัวเลือกเมนู", f"เมนู #{mid}: {name}")
    return redirect(url_for("admin.menu_edit", mid=mid))
