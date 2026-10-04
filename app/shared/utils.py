from ..extensions import db
import os
from werkzeug.security import generate_password_hash
from ..models import MenuItem, Table, Ingredient, Recipe, User

def seed():
    if MenuItem.query.first(): return
    for n, c, p in [("ผัดกะเพราหมูสับ", "จานเดียว", 60), ("ข้าวมันไก่", "จานเดียว", 50),
                    ("ต้มยำกุ้ง", "ต้ม", 150), ("ส้มตำไทย", "ยำ", 60), ("ชาเย็น", "เครื่องดื่ม", 35)]:
        db.session.add(MenuItem(name=n, category=c, price=p))
    for i in range(1, 7): db.session.add(Table(id=i, token=f"table{i}"))
    db.session.add(Ingredient(id=1, name="หมูสับ", unit="กรัม", stock=2000)); db.session.flush()
    db.session.add(Recipe(menu_id=1, ingredient_id=1, qty=100))
    db.session.commit()

def ensure_users():  # บัญชีเริ่มต้น (เปลี่ยนรหัสผ่านก่อนใช้งานจริง!)
    if User.query.first(): return
    for u, n, r, p in [("admin", "ผู้ดูแลระบบ", "admin", os.getenv("ADMIN_PASSWORD", "admin1234")), ("staff", "พนักงาน", "staff", os.getenv("STAFF_PASSWORD", "staff1234"))]:
        db.session.add(User(username=u, name=n, role=r, pw_hash=generate_password_hash(p)))
    db.session.commit()

def to_int(value, default=0):  # แปลงเป็นจำนวนเต็มอย่างปลอดภัย (ผิดรูปแบบ -> ค่าเริ่มต้น)
    try: return int(value)
    except (TypeError, ValueError): return default

def to_float(value, default=0.0):
    try: return float(value)
    except (TypeError, ValueError): return default
