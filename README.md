# ระบบจัดการร้านอาหาร (Flask)

รัน: `python -m pip install -r requirements.txt` แล้ว `python run.py` -> http://localhost:5000
บัญชีเริ่มต้น: admin / admin1234 , staff / staff1234 (เปลี่ยนก่อนใช้งานจริง)
เครื่องมือบรรทัดคำสั่ง (Standard Library ล้วน): `python cli.py`

## เกณฑ์ขั้นต่ำ -> อยู่ที่ไหนในโค้ด
| หัวข้อ | ตัวอย่างในโค้ด |
|---|---|
| ตัวแปร/ชนิดข้อมูล/แปลงชนิด | `shared/utils.py` (to_int, to_float), `services/billing_service.py`, `cli.py` (ask_price) |
| การเลือกทำ (if/elif/else, and/or/not) | `cli.py` main(), `admin/routes/menu.py` check(), `auth/routes.py` register() |
| การทำซ้ำ for + while | `cli.py` (while เมนูวนซ้ำ + for แสดงรายการ), `services/menu_io.py` |
| ฟังก์ชัน >= 6 | `cli.py` มี 10 ฟังก์ชัน (load_menu, save_menu, ask_text, ask_price, find_item, show_menu, add_item, edit_price, delete_item, summary) |
| โครงสร้างข้อมูล | list (รายการเมนู), dict (นับต่อหมวด / SORTS), tuple (`menu_io.FIELDS`, ค่าถูกสุด-แพงสุด), set (หมวดไม่ซ้ำ / `ALLOWED` นามสกุลรูป) |
| โมดูล >= 2 ไฟล์ | โปรเจกต์แยกเป็นหลายไฟล์ `.py`; `cli.py` และ `services/menu_io.py` ใช้ Standard Library ล้วน |
| จัดการไฟล์ | นำเข้า/ส่งออกเมนู CSV/JSON (`menu_io.py`), `cli.py` บันทึก `menu_backup.json` ปิดแล้วเปิดใหม่ข้อมูลยังอยู่, ฐานข้อมูล SQLite |
| try/except + ไม่แสดง Traceback | `create_app()` มี errorhandler แสดงหน้าไทยแทน Traceback; `menu_io.py`, `cli.py`, `utils.py` ดักข้อผิดพลาดตอนรับค่า/อ่านไฟล์ |

## ต้องถามอาจารย์
- เกณฑ์ข้อ "โมดูล" เขียนว่าใช้เฉพาะ Standard Library เว้นแต่ได้รับอนุญาต แต่เว็บใช้ Flask, Flask-SQLAlchemy, Flask-SocketIO, qrcode -> ต้องขออนุญาต
- ข้อ "จัดการไฟล์" ระบุ txt/csv/json -> ตรวจว่าการใช้ SQLite ร่วมกับ CSV/JSON ผ่านหรือไม่
