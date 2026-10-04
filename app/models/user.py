from ..extensions import db
class User(db.Model):
    __tablename__ = "app_user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)  # ลูกค้า = เบอร์โทร, พนักงาน/แอดมิน = ชื่อผู้ใช้
    name = db.Column(db.String(80)); pw_hash = db.Column(db.String(255)); role = db.Column(db.String(20), default="customer")
class AuditLog(db.Model):  # บันทึกการแก้ไขข้อมูลสำคัญ
    __tablename__ = "audit_log"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.String(20)); user = db.Column(db.String(40)); action = db.Column(db.String(60)); detail = db.Column(db.String(300))
