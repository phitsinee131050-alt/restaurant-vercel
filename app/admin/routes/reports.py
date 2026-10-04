from flask import render_template, request
from .. import admin_bp
from ...models import Bill
from ...services import report_service as r

@admin_bp.route("/reports")
def reports():
    q, sort = request.args.get("q", "").strip(), request.args.get("sort", "new")
    qs = Bill.query
    if q:
        cond = Bill.phone.contains(q)
        if q.isdigit(): cond = cond | (Bill.id == int(q))
        qs = qs.filter(cond)
    order = {"new": Bill.id.desc(), "old": Bill.id.asc(), "high": Bill.total.desc()}.get(sort, Bill.id.desc())
    p = qs.order_by(order).paginate(page=request.args.get("page", 1, type=int), per_page=10, error_out=False)
    return render_template("admin/reports.html", s=r.summary(), daily=r.daily(), best=r.best_sellers(), p=p, q=q, sort=sort)
