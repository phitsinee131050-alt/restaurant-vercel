from ..extensions import db
class MenuItem(db.Model):
    __tablename__ = "menu_item"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100)); category = db.Column(db.String(50)); price = db.Column(db.Float)
    image = db.Column(db.Text, default=""); available = db.Column(db.Boolean, default=True)

class MenuOption(db.Model):  # ตัวเลือกของแต่ละเมนู (แอดมินตั้งเอง)
    __tablename__ = "menu_option"
    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey("menu_item.id"))
    kind = db.Column(db.String(10), default="addon")   # addon = ติ๊กเพิ่ม(มีราคา), choice = ให้เลือก 1 อย่าง
    name = db.Column(db.String(60)); choices = db.Column(db.String(200), default=""); price = db.Column(db.Float, default=0)
