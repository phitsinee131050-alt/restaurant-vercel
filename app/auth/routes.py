import re
from flask import render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from . import auth_bp
from ..extensions import db
from ..models import User, Member, Bill, Reservation

def _login(u): session.update(uid=u.id, username=u.username, name=u.name, role=u.role)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    err = None
    if request.method == "POST":
        u = User.query.filter_by(username=request.form["username"].strip()).first()
        if u and check_password_hash(u.pw_hash, request.form["password"]):
            _login(u); nxt = request.args.get("next", "")
            if not nxt.startswith("/") or nxt.startswith("//"): nxt = "/me" if u.role == "customer" else "/admin/"
            return redirect(nxt)
        err = "ชื่อผู้ใช้/เบอร์โทร หรือรหัสผ่านไม่ถูกต้อง"
    return render_template("auth/login.html", err=err)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    errs, f = [], request.form
    if request.method == "POST":
        phone, name, pw = f["phone"].strip(), f["name"].strip(), f["password"]
        if not re.fullmatch(r"0\d{9}", phone): errs.append("เบอร์โทรต้องเป็นตัวเลข 10 หลัก ขึ้นต้นด้วย 0")
        if len(name) < 2: errs.append("กรุณากรอกชื่อ")
        if len(pw) < 6: errs.append("รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร")
        if pw != f["confirm"]: errs.append("รหัสผ่านสองช่องไม่ตรงกัน")
        if not errs and User.query.filter_by(username=phone).first(): errs.append("เบอร์นี้สมัครสมาชิกแล้ว")
        if not errs:
            u = User(username=phone, name=name, role="customer", pw_hash=generate_password_hash(pw)); db.session.add(u)
            if not Member.query.filter_by(phone=phone).first(): db.session.add(Member(phone=phone, points=0))
            db.session.commit(); _login(u); return redirect("/me")
    return render_template("auth/register.html", errs=errs)

@auth_bp.route("/logout")
def logout():
    session.clear(); return redirect("/login")

@auth_bp.route("/me")
def me():
    if not session.get("uid"): return redirect("/login?next=/me")
    ph = session["username"]
    return render_template("auth/me.html", res=Reservation.query.filter_by(phone=ph).order_by(Reservation.time).all(), m=Member.query.filter_by(phone=ph).first(), bills=Bill.query.filter_by(phone=ph).order_by(Bill.id.desc()).limit(20).all())
