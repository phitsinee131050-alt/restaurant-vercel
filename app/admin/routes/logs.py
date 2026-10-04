from flask import render_template, request
from .. import admin_bp
from ...models import AuditLog

@admin_bp.route("/logs")
def logs():
    who, text = request.args.get("user", "").strip(), request.args.get("q", "").strip()
    qs = AuditLog.query
    if who: qs = qs.filter(AuditLog.user == who)
    if text: qs = qs.filter(AuditLog.action.contains(text) | AuditLog.detail.contains(text))
    p = qs.order_by(AuditLog.id.desc()).paginate(page=request.args.get("page", 1, type=int), per_page=15, error_out=False)
    return render_template("admin/logs.html", p=p, who=who, q=text)
