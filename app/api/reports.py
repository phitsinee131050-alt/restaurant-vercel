from flask import jsonify
from . import api_bp
from ..services import report_service as r
@api_bp.get("/reports/daily")
def daily(): return jsonify(today=r.sales_today(), best_sellers=[[n, int(c)] for n, c in r.best_sellers()])
