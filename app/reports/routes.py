from datetime import date
from flask import Blueprint, jsonify, render_template
from flask_login import current_user, login_required
from sqlalchemy import func
from ..models import Category, Transaction
from ..services.dashboard import month_bounds, totals_for_user

reports_bp = Blueprint("reports", __name__)


@reports_bp.get("/")
@login_required
def index():
    return render_template("reports/index.html", totals=totals_for_user(current_user.id))


@reports_bp.get("/api/charts")
@login_required
def chart_data():
    categories = (Transaction.query.with_entities(Category.name, func.sum(Transaction.amount))
        .join(Category).filter(Transaction.user_id == current_user.id, Transaction.transaction_type == "expense")
        .group_by(Category.name).order_by(func.sum(Transaction.amount).desc()).all())
    today = date.today()
    month_starts = []
    for offset in range(11, -1, -1):
        index = today.year * 12 + today.month - 1 - offset
        month_starts.append(date(index // 12, index % 12 + 1, 1))
    monthly = []
    for start in month_starts:
        monthly.append({"label": start.strftime("%b %Y"), **{key: float(value) for key, value in totals_for_user(current_user.id, *month_bounds(start)).items() if key != "balance"}})
    return jsonify({"success": True, "data": {"categories": [{"label": name, "value": float(value)} for name, value in categories], "monthly": monthly}})
