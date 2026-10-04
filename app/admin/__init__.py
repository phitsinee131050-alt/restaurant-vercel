from flask import Blueprint
admin_bp = Blueprint("admin", __name__, template_folder="templates")
from flask import session, redirect, request, abort
ADMIN_ONLY = {"admin.menu", "admin.menu_update", "admin.inventory", "admin.reports", "admin.qr", "admin.qr_page", "admin.qr_print", "admin.logs", "admin.menu_edit", "admin.option_add", "admin.option_delete", "admin.menu_export", "admin.menu_import", "admin.table_add", "admin.table_delete", "admin.inventory_delete", "admin.inventory_import"}

@admin_bp.before_request
def _auth():  # staff ใช้ POS/โต๊ะ/จองคิวได้, ส่วนจัดการข้อมูลเป็น admin เท่านั้น
    if not session.get("uid"): return redirect("/login?next=" + request.path)
    if session.get("role") not in ("admin", "staff"): abort(403)
    if request.endpoint in ADMIN_ONLY and session.get("role") != "admin": abort(403)
from .routes import dashboard, menu, pos, reports, reservations, inventory, logs  # noqa
