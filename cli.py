"""เครื่องมือบรรทัดคำสั่งจัดการเมนูผ่านไฟล์ JSON (ใช้ Standard Library เท่านั้น)
ใช้คู่กับหน้าเว็บ: ส่งออกเมนู JSON จากหลังบ้าน -> แก้ด้วยโปรแกรมนี้ -> อัปโหลดกลับ"""
import json

FILE = "menu_backup.json"

def load_menu(path=FILE):
    """โหลดเมนูจากไฟล์ -> list ของ dict (ไม่มีไฟล์/ไฟล์เสีย = รายการว่าง)"""
    try:
        with open(path, encoding="utf-8") as f: data = json.load(f)
    except FileNotFoundError: return []
    except (OSError, ValueError): print("! อ่านไฟล์ไม่ได้ เริ่มจากรายการว่าง"); return []
    return data if isinstance(data, list) else []

def save_menu(items, path=FILE):
    try:
        with open(path, "w", encoding="utf-8") as f: json.dump(items, f, ensure_ascii=False, indent=2)
    except OSError: print("! บันทึกไฟล์ไม่สำเร็จ"); return False
    return True

def ask_text(prompt):
    while True:  # วนจนกว่าจะกรอกไม่ว่าง
        text = input(prompt).strip()
        if len(text) >= 2: return text
        print("! ต้องมีอย่างน้อย 2 ตัวอักษร")

def ask_price(prompt):
    while True:
        try: price = float(input(prompt))
        except ValueError: print("! กรุณากรอกเป็นตัวเลข"); continue
        if 0 < price <= 100000: return price
        print("! ราคาต้องมากกว่า 0 และไม่เกิน 100,000")

def find_item(items, name):
    for it in items:
        if it["name"].lower() == name.lower(): return it
    return None

def show_menu(items, keyword=""):
    shown = 0
    for i, it in enumerate(items, start=1):
        if keyword and keyword.lower() not in it["name"].lower() and keyword.lower() not in it["category"].lower(): continue
        print(f"{i:>2}. {it['name']} ({it['category']}) {it['price']:.2f} บาท"); shown += 1
    if shown == 0: print("(ไม่พบรายการ)")

def add_item(items):
    name = ask_text("ชื่อเมนู: ")
    if find_item(items, name): print("! มีเมนูนี้อยู่แล้ว"); return
    items.append({"name": name, "category": ask_text("หมวดหมู่: "), "price": ask_price("ราคา: ")})
    print("เพิ่มแล้ว")

def edit_price(items):
    it = find_item(items, ask_text("ชื่อเมนูที่จะแก้ราคา: "))
    if it is None: print("! ไม่พบเมนู"); return
    it["price"] = ask_price(f"ราคาใหม่ (เดิม {it['price']}): "); print("แก้แล้ว")

def delete_item(items):
    it = find_item(items, ask_text("ชื่อเมนูที่จะลบ: "))
    if it is not None and input(f"ยืนยันลบ {it['name']}? (y/n): ").strip().lower() == "y": items.remove(it); print("ลบแล้ว")
    else: print("ไม่ได้ลบ")

def summary(items):
    if not items: print("ยังไม่มีเมนู"); return
    cats = {it["category"] for it in items}        # set: หมวดหมู่ไม่ซ้ำ
    count = {}                                                    # dict: นับเมนูต่อหมวด
    for it in items: count[it["category"]] = count.get(it["category"], 0) + 1
    cheap, dear = min(items, key=lambda x: x["price"]), max(items, key=lambda x: x["price"])
    extremes = (cheap["name"], dear["name"])                      # tuple: ค่าคู่คงที่ (ถูกสุด, แพงสุด)
    print(f"ทั้งหมด {len(items)} เมนู · {len(cats)} หมวด · {count}\nถูกสุด: {extremes[0]} · แพงสุด: {extremes[1]}")

MENU_TEXT = "\n=== จัดการเมนู ===\n1 ดูทั้งหมด  2 ค้นหา  3 เพิ่ม  4 แก้ราคา  5 ลบ  6 สรุป  0 บันทึกและออก"

def main():
    items, running = load_menu(), True
    while running:  # เมนูวนซ้ำจนกว่าจะเลือกออก
        print(MENU_TEXT)
        try: choice = input("เลือก: ").strip()
        except (EOFError, KeyboardInterrupt): choice = "0"  # ปิดหน้าต่าง/กด Ctrl+C = บันทึกแล้วออกอย่างสุภาพ
        if choice == "1": show_menu(items)
        elif choice == "2": show_menu(items, ask_text("คำค้นหา: "))
        elif choice == "3": add_item(items)
        elif choice == "4": edit_price(items)
        elif choice == "5": delete_item(items)
        elif choice == "6": summary(items)
        elif choice == "0":
            if save_menu(items): print(f"บันทึกลง {FILE} แล้ว ลาก่อน")
            running = False
        else: print("! เลือก 0-6 เท่านั้น")

if __name__ == "__main__":
    main()
