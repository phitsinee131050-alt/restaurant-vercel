from flask import render_template, request, redirect, url_for, current_app, flash
from .. import admin_bp
from ...extensions import db
from ...models import Ingredient, Recipe, MenuItem
from sqlalchemy import func
from ...services import inventory_client, recipe_io
from ...services import audit_service as audit

def num(v):  # ช่องว่างให้นับเป็น 0 แทนที่จะ error
    try: return float(v or 0)
    except ValueError: return 0.0

@admin_bp.route("/inventory", methods=["GET", "POST"])
def inventory():
    url = current_app.config.get("INVENTORY_URL")
    remote = {p["sku"]: p for p in (inventory_client.products(url) or [])} if url else {}
    if request.method == "POST":
        f = request.form
        if f["kind"] == "ing":
            if not f["name"].strip() or num(f.get("stock")) < 0: flash("ชื่อวัตถุดิบห้ามว่าง และจำนวนต้องไม่ติดลบ")
            else: db.session.add(Ingredient(sku=f.get("sku", "").strip() or None, name=f["name"].strip(), unit=f["unit"], stock=num(f.get("stock"))))
        elif f["kind"] == "recipe":
            if num(f.get("qty")) <= 0: flash("ปริมาณต่อจานต้องมากกว่า 0")
            else: db.session.add(Recipe(menu_id=int(f["menu_id"]), ingredient_id=int(f["ingredient_id"]), qty=num(f.get("qty"))))
        elif f["kind"] == "link":  # เลือกสินค้าจากโปรเจกต์ 3 -> ชื่อ/หน่วย/ยอดมาเอง
            p = remote.get(f["sku"])
            if p and not Ingredient.query.filter_by(sku=p["sku"]).first(): db.session.add(Ingredient(sku=p["sku"], name=p["name"], unit=p["unit"], stock=0))
        else: db.get_or_404(Ingredient, int(f["id"])).stock += num(f.get("add"))
        db.session.commit(); audit.log("สต็อก: " + f["kind"], dict(f)); return redirect(url_for("admin.inventory"))
    recipes = [(r, db.session.get(MenuItem, r.menu_id), db.session.get(Ingredient, r.ingredient_id)) for r in Recipe.query]
    return render_template("admin/inventory.html", ings=Ingredient.query.all(), remote=remote, url=url, recipes=recipes, menu=MenuItem.query.all())

@admin_bp.post("/inventory/<kind>/<int:rid>/delete")
def inventory_delete(kind, rid):
    if kind == "recipe": db.session.delete(db.get_or_404(Recipe, rid))
    elif Recipe.query.filter_by(ingredient_id=rid).first():
        flash("ลบไม่ได้ วัตถุดิบนี้ถูกใช้ในสูตรอาหาร (ลบสูตรก่อน)"); return redirect(url_for("admin.inventory"))
    else: db.session.delete(db.get_or_404(Ingredient, rid))
    db.session.commit(); audit.log("ลบ" + kind, rid); return redirect(url_for("admin.inventory"))

@admin_bp.post("/inventory/import")
def inventory_import():  # อัปโหลด recipes.csv -> สร้างวัตถุดิบ (ถ้ายังไม่มี) + ผูกสูตรกับเมนู
    f = request.files.get("file")
    if not f or not f.filename:
        flash("กรุณาเลือกไฟล์ก่อน"); return redirect(url_for("admin.inventory"))
    try: rows, errs = recipe_io.parse_recipes(f.filename, f.read())
    except OSError: rows, errs = [], ["อ่านไฟล์ไม่สำเร็จ"]
    made = linked = 0
    for r in rows:
        menu = MenuItem.query.filter(func.lower(MenuItem.name) == r["menu"].lower()).first()
        if not menu: errs.append(f"ไม่พบเมนู '{r['menu']}' (นำเข้า menu.csv ก่อน)"); continue
        ing = Ingredient.query.filter_by(sku=r["sku"]).first()
        if not ing:
            ing = Ingredient(sku=r["sku"], name=r["name"], unit=r["unit"], stock=0); db.session.add(ing); db.session.flush(); made += 1
        rec = Recipe.query.filter_by(menu_id=menu.id, ingredient_id=ing.id).first()
        if rec: rec.qty = r["qty"]
        else: db.session.add(Recipe(menu_id=menu.id, ingredient_id=ing.id, qty=r["qty"])); linked += 1
    db.session.commit(); audit.log("นำเข้าสูตร", f"{f.filename}: วัตถุดิบใหม่ {made} สูตรใหม่ {linked} ข้าม {len(errs)}")
    for e in errs[:5]: flash(e)
    flash(f"นำเข้าแล้ว: วัตถุดิบใหม่ {made} · สูตรใหม่ {linked} · ข้าม {len(errs)}"); return redirect(url_for("admin.inventory"))
