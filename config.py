import os
BASE = os.path.dirname(os.path.abspath(__file__))

def _db_url():
    url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")  # Vercel + Neon ใส่ให้เองหลังกด Connect
    if url:  # ระบุไดรเวอร์ psycopg (v3) ชัดเจน กันกรณี SQLAlchemy เวอร์ชันใหม่/เก่าเลือกไดรเวอร์ไม่ตรงกับที่ติดตั้ง
        for scheme in ("postgres://", "postgresql://"):
            if url.startswith(scheme): return "postgresql+psycopg://" + url[len(scheme):]
        return url
    return "sqlite:///" + os.path.join(BASE, "restaurant.db")        # รันในเครื่อง = ใช้ SQLite เหมือนเดิม

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    SQLALCHEMY_DATABASE_URI = _db_url()
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 280}
    INVENTORY_URL = os.getenv("INVENTORY_URL", "")
    BASE_URL = os.getenv("BASE_URL", "")
    VAT_RATE = 0.07
    SERVICE_CHARGE = 0.10
