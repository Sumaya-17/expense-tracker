from flask import Blueprint, jsonify, render_template
from flask_login import current_user, login_required
from ..models import Transaction
from ..services.dashboard import month_bounds, totals_for_user

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    return render_template("landing/index.html")


@main_bp.get("/dashboard")
@login_required
def dashboard():
    totals = totals_for_user(current_user.id)
    monthly = totals_for_user(current_user.id, *month_bounds())
    recent = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.transaction_date.desc(), Transaction.id.desc()).limit(6).all()
    return render_template("dashboard/index.html", totals=totals, monthly=monthly, recent=recent)


@main_bp.get("/api/dashboard/summary")
@login_required
def dashboard_summary():
    return jsonify({"success": True, "data": {k: float(v) for k, v in totals_for_user(current_user.id).items()}})
