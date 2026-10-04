"""ตัวเชื่อมไปยังโปรเจกต์ 3 (ระบบสต็อก) ผ่าน REST API
ถ้าเชื่อมไม่ได้ จะไม่ทำให้การสั่งอาหารล้ม (แค่คืนค่า False)"""
import json, urllib.request

def issue(base_url, sku, qty, ref=""):
    body = json.dumps({"sku": sku, "qty": qty, "reason": "ขายอาหาร", "user": "ระบบร้านอาหาร", "ref": ref}).encode()
    req = urllib.request.Request(base_url.rstrip("/") + "/api/v1/stock/issue", body, {"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=2); return True
    except Exception as e:
        print("[inventory] เบิกสต็อกไม่สำเร็จ:", sku, e); return False

def products(base_url):  # รายการสินค้า + ยอดคงเหลือสดๆ จากโปรเจกต์ 3 (เชื่อมไม่ได้ -> None)
    try:
        return json.load(urllib.request.urlopen(base_url.rstrip("/") + "/api/v1/products", timeout=2))
    except Exception as e:
        print("[inventory] ดึงสินค้าไม่สำเร็จ:", e); return None
