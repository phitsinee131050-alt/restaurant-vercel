from flask import Blueprint
kitchen_bp = Blueprint("kitchen", __name__, template_folder="templates")
from ..shared.decorators import guard
kitchen_bp.before_request(guard(("admin", "staff")))
from . import routes  # noqa
