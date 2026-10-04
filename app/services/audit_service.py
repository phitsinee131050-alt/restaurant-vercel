from datetime import datetime
from flask import session
from ..extensions import db
from ..models import AuditLog
def log(action, detail=""):
    db.session.add(AuditLog(created=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user=session.get("username", "ระบบ"), action=action, detail=str(detail)[:300]))
    db.session.commit()
