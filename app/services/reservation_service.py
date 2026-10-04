from ..extensions import db
from ..models import QueueTicket
def new_ticket(name):
    last = db.session.query(db.func.max(QueueTicket.number)).scalar() or 0
    t = QueueTicket(number=last + 1, name=name); db.session.add(t); db.session.commit(); return t
