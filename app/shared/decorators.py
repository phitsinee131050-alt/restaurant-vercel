from flask import session, redirect, request, abort
def guard(roles):  # ใช้กับ blueprint.before_request: ต้องล็อกอินและมีบทบาทที่อนุญาต
    def check():
        if not session.get("uid"): return redirect("/login?next=" + request.path)
        if session.get("role") not in roles: abort(403)
    return check
