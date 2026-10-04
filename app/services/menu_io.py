"""นำเข้า/ส่งออกเมนูเป็นไฟล์ CSV / JSON (ใช้เฉพาะ Standard Library)"""
import csv, io, json, re

PRESETS = {  # รหัส -> (ประเภท, ชื่อ, ตัวเลือก, ราคาเพิ่ม)
    "spicy": ("choice", "ระดับความเผ็ด", "ไม่เผ็ด,เผ็ดน้อย,เผ็ดกลาง,เผ็ดมาก", 0),
    "egg": ("addon", "เพิ่มไข่ดาว", "", 10), "pearl": ("addon", "เพิ่มไข่มุก", "", 10),
    "big": ("addon", "ไซส์พิเศษ", "", 15), "cup": ("addon", "แก้วใหญ่", "", 10),
}
FIELDS = ("name", "category", "price")  # tuple: ลำดับคอลัมน์คงที่ ห้ามเปลี่ยนระหว่างโปรแกรมทำงาน

def parse_rows(filename, raw):
    """อ่านไฟล์ที่อัปโหลด -> (rows, errors) โดย rows เป็น list ของ dict ที่ผ่านการตรวจแล้ว"""
    rows, errors, seen = [], [], set()  # set: เช็คชื่อซ้ำในไฟล์ได้เร็ว
    name = filename.lower()
    try:
        text = raw.decode("utf-8-sig")
        if name.endswith(".json"): data = json.loads(text)
        elif name.endswith(".csv"): data = list(csv.DictReader(io.StringIO(text)))
        else: return [], ["รองรับเฉพาะไฟล์ .csv หรือ .json"]
    except (UnicodeDecodeError, ValueError, csv.Error):
        return [], ["อ่านไฟล์ไม่ได้ ไฟล์อาจเสียหรือรูปแบบไม่ถูกต้อง"]
    if not isinstance(data, list): return [], ["ข้อมูลในไฟล์ต้องเป็นรายการเมนู"]
    for n, item in enumerate(data, start=1):
        if not isinstance(item, dict): errors.append(f"แถว {n}: รูปแบบไม่ถูกต้อง"); continue
        nm, cat = str(item.get("name", "")).strip(), str(item.get("category", "")).strip()
        try: price = float(item.get("price", ""))
        except (TypeError, ValueError): price = 0
        if len(nm) < 2 or not cat or not 0 < price <= 100000: errors.append(f"แถว {n}: ข้อมูลไม่ครบหรือไม่ถูกต้อง ({nm or 'ไม่มีชื่อ'})"); continue
        keys = [k.strip() for k in re.split(r"[|,;]", str(item.get("options") or "")) if k.strip()]
        if any(k not in PRESETS for k in keys): errors.append(f"แถว {n}: ตัวเลือกไม่รู้จัก ({nm}) ใช้ได้: {', '.join(PRESETS)}"); continue
        if nm.lower() in seen: errors.append(f"แถว {n}: ชื่อซ้ำในไฟล์ ({nm})"); continue
        seen.add(nm.lower()); rows.append({"name": nm, "category": cat, "price": price, "options": keys})
    return rows, errors

def to_json(items): return json.dumps(items, ensure_ascii=False, indent=2)

def to_csv(items):
    buf = io.StringIO(); wr = csv.DictWriter(buf, fieldnames=FIELDS); wr.writeheader()
    for it in items: wr.writerow({k: it[k] for k in FIELDS})
    return buf.getvalue()
