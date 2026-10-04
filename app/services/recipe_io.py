"""นำเข้าสูตรอาหารจาก recipes.csv (Standard Library เท่านั้น) คอลัมน์: menu_name, sku, ingredient_name, unit, qty"""
import csv, io, re

def parse_recipes(filename, raw):
    rows, errors, seen = [], [], set()
    if not filename.lower().endswith(".csv"): return [], ["รองรับเฉพาะไฟล์ .csv"]
    try: data = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    except (UnicodeDecodeError, csv.Error): return [], ["อ่านไฟล์ไม่ได้ ไฟล์อาจเสียหรือรูปแบบไม่ถูกต้อง"]
    for n, it in enumerate(data, start=2):
        menu, sku = (it.get("menu_name") or "").strip(), (it.get("sku") or "").strip().upper()
        name, unit = (it.get("ingredient_name") or "").strip(), (it.get("unit") or "").strip()
        try: qty = float(it.get("qty") or 0)
        except ValueError: qty = 0
        if not menu or not re.fullmatch(r"[A-Z0-9-]{2,30}", sku) or not name or qty <= 0: errors.append(f"แถว {n}: ข้อมูลไม่ครบหรือไม่ถูกต้อง"); continue
        if (menu, sku) in seen: errors.append(f"แถว {n}: ซ้ำ ({menu} / {sku})"); continue
        seen.add((menu, sku)); rows.append(dict(menu=menu, sku=sku, name=name, unit=unit, qty=qty))
    return rows, errors
