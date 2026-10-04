# ขึ้น Vercel ทีละขั้นตอน (ชื่อปุ่มบนเว็บอาจต่างเล็กน้อยตามที่ Vercel ปรับ)

## 0) เตรียมเครื่อง
- ติดตั้ง Git: https://git-scm.com/download/win (กด Next ไปเรื่อยๆ) แล้วปิด-เปิด VS Code ใหม่
- สมัคร GitHub (github.com) และ Vercel (vercel.com -> Sign Up -> Continue with GitHub) ใช้อีเมลเดียวกันได้

## 1) ทดสอบในเครื่องก่อน
python run.py  -> เปิด localhost:5000 ต้องใช้ได้ (ในเครื่องยังใช้ SQLite เหมือนเดิม)

## 2) ส่งโค้ดขึ้น GitHub (ทำใน VS Code)
1. กดไอคอน Source Control ด้านซ้าย (หรือ Ctrl+Shift+G) -> Initialize Repository
2. พิมพ์ข้อความ เช่น "first commit" -> กด Commit (ถ้าถามเรื่อง stage ให้กด Yes/Always)
3. กด Publish Branch -> เลือก Sign in to GitHub -> เลือก Public หรือ Private repository (ตั้งชื่อเช่น restaurant-system)

## 3) สร้างโปรเจกต์บน Vercel
1. vercel.com -> Add New... -> Project -> เลือก repo restaurant-system -> Import
2. Framework ควรขึ้นเป็น Flask เอง (ไม่ต้องแก้ Build/Output)
3. เปิด Environment Variables ใส่ 3 ตัว:
   - SECRET_KEY = ข้อความสุ่มยาวๆ (พิมพ์มั่วๆ 30 ตัวอักษรได้)
   - ADMIN_PASSWORD = รหัสผ่านแอดมินที่คุณตั้งเอง
   - STAFF_PASSWORD = รหัสผ่านพนักงานที่คุณตั้งเอง
4. กด Deploy  (ครั้งแรกอาจ error เพราะยังไม่มีฐานข้อมูล ปกติ ไปขั้นต่อไป)

## 4) ต่อฐานข้อมูล
1. ในโปรเจกต์บน Vercel -> แท็บ Storage (หรือ Integrations / Marketplace) -> เลือก Neon (Postgres) -> Add/Connect -> ทำตามหน้าจอ (แผนฟรี)
2. ตรวจ Settings -> Environment Variables ต้องมี DATABASE_URL โผล่มาเอง
3. แท็บ Deployments -> จุดสามจุดที่ deployment ล่าสุด -> Redeploy

## 5) ใช้งาน
- เปิดลิงก์ https://ชื่อโปรเจกต์.vercel.app -> เข้าสู่ระบบด้วย admin + รหัสที่ตั้งใน ADMIN_PASSWORD
- นำเข้า menu.csv ที่หน้าเมนู
- เมนู "พิมพ์ QR โต๊ะ" จะสร้าง QR จากโดเมนจริงให้เอง พิมพ์ครั้งเดียวใช้ได้ตลอด

## ถ้าพัง
- ดู Deployments -> เลือกอันล่าสุด -> Logs / Runtime Logs (ข้อความ error อยู่ตรงนั้น) แล้วถ่ายภาพส่งมา
- แก้โค้ดแล้ว: Source Control -> Commit -> Sync/Push แล้ว Vercel จะ deploy ใหม่เอง

## ข้อจำกัดของเวอร์ชันออนไลน์
- real-time ใช้การเช็คทุก 4 วินาทีแทน WebSocket (Vercel ไม่รองรับ WebSocket)
- รูปเมนูเก็บในฐานข้อมูล ขนาดไม่เกิน 300KB
- การเชื่อมสต็อกกับโปรเจกต์ 3 (INVENTORY_URL) ใช้ได้เมื่อโปรเจกต์ 3 ออนไลน์ด้วย ตอนนี้โปรเจกต์ 3 ยังใช้ได้แค่ในเครื่อง
