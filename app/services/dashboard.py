from datetime import date
from sqlalchemy import case, func
from ..extensions import db
from ..models import Transaction


def month_bounds(day=None):
    day = day or date.today()
    start = day.replace(day=1)
    end = date(day.year + (day.month == 12), (day.month % 12) + 1, 1)
    return start, end


def totals_for_user(user_id, start=None, end=None):
    query = db.session.query(
        func.coalesce(func.sum(case((Transaction.transaction_type == "income", Transaction.amount), else_=0)), 0).label("income"),
        func.coalesce(func.sum(case((Transaction.transaction_type == "expense", Transaction.amount), else_=0)), 0).label("expenses"),
    ).filter(Transaction.user_id == user_id)
    if start: query = query.filter(Transaction.transaction_date >= start)
    if end: query = query.filter(Transaction.transaction_date < end)
    row = query.one()
    return {"income": row.income, "expenses": row.expenses, "balance": row.income - row.expenses}
